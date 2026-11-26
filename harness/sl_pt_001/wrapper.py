"""SL-PT-001 Stage A scheduler wrapper (Strike 3; R4.2i §6.1, §10.2; contract v2 §6 invocation log).

The scheduled task runs THIS file. Before anything else it appends one line to the invocation log
  chain/invocations/<manifest_sha256>.log :  <invocation_instant ns>\\t<pid>\\t<wrapper_sha256>\\n
(write, flush, fsync), then starts the harness for that instant (-E -s: no PYTHON* env, no user site;
-I is not used because it drops the package directory from sys.path). The log is HARNESS-ATTESTED evidence that an
invocation happened even when no chain record follows (U73, U77). It writes nothing else and reads no secrets.
Usage: python -E -s wrapper.py <evidence_root> <manifest_path>
"""
import hashlib
import os
import subprocess
import sys
import time


def wrapper_sha256():
    with open(os.path.abspath(__file__), "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def log_invocation(evidence_root, manifest_sha256, instant_ns, pid, wsha):
    d = os.path.join(evidence_root, "chain", "invocations")
    os.makedirs(d, exist_ok=True)
    line = f"{instant_ns}\t{pid}\t{wsha}\n".encode("ascii")
    with open(os.path.join(d, f"{manifest_sha256}.log"), "ab") as fh:
        fh.write(line)
        fh.flush()
        os.fsync(fh.fileno())
    return line


def main(argv, start=None):
    evidence_root, manifest_path = argv[1], argv[2]
    instant = time.time_ns()                                           # the invocation instant (§6.2)
    with open(manifest_path, "rb") as fh:
        msha = hashlib.sha256(fh.read()).hexdigest()
    log_invocation(evidence_root, msha, instant, os.getpid(), wrapper_sha256())
    cmd = [sys.executable, "-E", "-s", "-m", "sl_pt_001.cli", "invoke", evidence_root, manifest_path, str(instant)]
    pkg_parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return (start or (lambda c: subprocess.run(c, cwd=pkg_parent).returncode))(cmd)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
