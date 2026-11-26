"""SL-PT-001 Stage A command line (Strike 4). Every chain write goes through controller.Harness.

  python -m sl_pt_001.cli write-policy <evidence_root>
  python -m sl_pt_001.cli genesis      <evidence_root>
  python -m sl_pt_001.cli invoke       <evidence_root> <manifest_path> <invocation_instant_ns>     (run by wrapper.py)
  python -m sl_pt_001.cli inject       <evidence_root> <manifest_path> <plan_path> <fixture_path> <intended_rule>
  python -m sl_pt_001.cli stop         <evidence_root> <manifest_path>
  python -m sl_pt_001.cli close        <evidence_root> <manifest_path> <task_xml_path>

Exit codes: 0 a record was written (or the policy file exists unchanged); 2 usage; 3 refused by §6.3/§6.4/§6.5;
4 evidence or pre-flight error (nothing written). `invoke` contacts data.alpaca.markets: it is run only by the
scheduled task after the pre-live gate. The harness configuration file is harness/config.json (§6.4 step 1).
"""
import os
import sys
import time

from . import controller as C
from . import decide as D
from . import evidence as E
from . import market as M
from . import validate as V

PKG_PARENT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(PKG_PARENT, "config.json")
POLICY_REL = os.path.join("policy", "P-0.2.json")


def _read(path):
    with open(path, "rb") as fh:
        return fh.read()


def repo_root(evidence_root):
    """The evidence root is <repo>/experiments/sl-pt-001 (contract §5)."""
    return os.path.dirname(os.path.dirname(os.path.abspath(evidence_root)))


def check_policy_file(evidence_root, policy_sha256):
    """The pinned policy file must exist, hash to the manifest's policy_sha256, hold exactly the contract §4 values
    (CC-02: any layout) and equal the harness's in-code constants (§7.4). Raises EvidenceError otherwise."""
    p = os.path.join(evidence_root, POLICY_REL)
    if not os.path.exists(p):
        raise E.EvidenceError("policy file missing")
    raw = _read(p)
    if E.sha256_hex(raw) != policy_sha256:
        raise E.EvidenceError("policy file hash differs from the manifest's policy_sha256")
    try:
        doc = V.parse_json_tokens(raw)
    except ValueError as exc:
        raise E.EvidenceError(f"policy file is not strict JSON: {exc}")
    if doc != E.POLICY_DOC or any(isinstance(x, V.NumTok) for x in _leaves(doc)):
        raise E.EvidenceError("policy file values differ from contract v2.1 §4")
    E.check_policy_matches_harness(D.POLICY)


def _leaves(x):
    if isinstance(x, dict):
        for v in x.values():
            yield from _leaves(v)
    else:
        yield x


def boundary(client, environ=None, config_path=CONFIG_PATH):
    """V12a on this process's own observations: env NAMES only, the config file bytes, the client's allowlist."""
    names = list((os.environ if environ is None else environ).keys())
    try:
        cfg = _read(config_path)
    except OSError:
        cfg = None
    r, ev, keep = V.boundary_check(names, cfg, client.allowlist)
    return r, ev, (cfg if keep else None)


def _sleep(s):
    time.sleep(s.numerator / s.denominator)                            # wait duration only; not a decision value


def main(argv, clock=time.time_ns, client=None, environ=None, out=sys.stdout):
    if len(argv) < 3:
        print(__doc__, file=out)
        return 2
    cmd, root = argv[1], argv[2]
    h = C.Harness(root, clock, _sleep)
    try:
        if cmd == "write-policy" and len(argv) == 3:
            p = os.path.join(root, POLICY_REL)
            want = E.policy_bytes()
            if os.path.exists(p):
                if _read(p) != want:
                    raise E.EvidenceError("a different policy file is already pinned; never rewrite it (CC-02)")
            else:
                os.makedirs(os.path.dirname(p), exist_ok=True)
                with open(p, "wb") as fh:
                    fh.write(want)
            print(f"policy {E.sha256_hex(want)}  {POLICY_REL}", file=out)
            return 0
        if cmd == "genesis" and len(argv) == 3:
            spec = os.path.join(repo_root(root), *E.SPEC_PATH.split("/"))
            if E.sha256_hex(_read(spec)) != E.SPEC_SHA256:
                raise E.EvidenceError("the R4.2i file in the repository does not match its pinned hash")
            if E.read_chain(root):
                raise E.EvidenceError("the chain already exists; GENESIS is written once")
            rec = h.genesis({E.SPEC_PATH: E.SPEC_SHA256})
        elif cmd == "invoke" and len(argv) == 5:
            manifest = _read(argv[3])
            m, _ = E.validate_manifest(manifest)
            check_policy_file(root, m["policy_sha256"])
            cl = client or M.Client(clock=clock)
            rec = h.invoke(manifest, int(argv[4]), lambda: boundary(cl, environ), cl.fetch_bars, cl.fetch_quote)
        elif cmd == "inject" and len(argv) == 7:
            manifest = _read(argv[3])
            m, _ = E.validate_manifest(manifest)
            check_policy_file(root, m["policy_sha256"])
            cl = client or M.Client(clock=clock)                       # never used for I/O: allowlist for V12a only
            rec = h.inject(manifest, _read(argv[4]), _read(argv[5]), argv[6], clock(), lambda: boundary(cl, environ))
        elif cmd == "stop" and len(argv) == 4:
            rec = h.run_stopped(_read(argv[3]))
        elif cmd == "close" and len(argv) == 5:
            m, mh = E.validate_manifest(_read(argv[3]))
            log = os.path.join(root, "chain", "invocations", f"{mh}.log")
            rec = h.run_close(_read(argv[3]), _read(log), _read(argv[4]))
        else:
            print(__doc__, file=out)
            return 2
    except C.Refused as exc:
        print(f"REFUSED: {exc}", file=out)
        return 3
    except (E.EvidenceError, OSError, ValueError) as exc:
        print(f"ERROR (nothing written): {exc}", file=out)
        return 4
    term = rec["body"].get("terminal_state") if rec["type"] in ("CYCLE", "INJECTION") else ""
    print(f"{rec['seq']}  {rec['type']}  {term}  {rec['hash']}", file=out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
