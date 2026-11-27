"""Build the §11.6 coverage matrix from the frozen spec's §14 Stage-A rows and a retained verbose test log.
Usage: python build_matrix.py <spec.md> <verbose_test_log.txt> > matrix.md   (stdlib only; reads, never writes evidence)
A row is HARNESS-EXECUTED only if a test whose name carries its id appears in the log with result 'ok'.
AUDITOR rows are classifications only the FD-6 auditor executes (GPT, synthetic evidence, scope-limited)."""
import hashlib, re, sys

AUDITOR = {"U26", "U27", "U34", "U37", "U38", "U41", "U66", "U68", "U69", "U71", "U103", "U109", "U120"}
BOTH = {"U73", "U74", "U75", "U76", "U77", "U99", "U102", "U104", "U117", "U118", "U19", "U91", "U83"}
NOTE = {
    "U99": "harness half: no CYCLE, orphans kept, chain verifies; classification INCOMPLETE is auditor's. "
           "Finding F-3: §6.3 row 3 makes the successor write CYCLE_OVERRUN for a crashed slot (U103 precedence -> "
           "OVERRUN), while U99 expects INCOMPLETE; reading requested from GPT (waypoint 5)",
    "U117": "(a)(b)(c) harness-executed; (d)(e) kill-before/after-fsync not executable in-process: harness half is "
            "U99 crash test; durability itself is not claimed (§10.4)",
}


def rows(spec):
    L = open(spec, encoding="utf-8").read().split("\n")
    s = next(i for i, l in enumerate(L) if l.startswith("## 14"))
    e = next(i for i, l in enumerate(L) if l.startswith("## 15"))
    out = []
    for l in L[s:e]:
        m = re.match(r"\|\s*(U[\w-]+)\s*\|(.*)\|\s*([^|]*)\|\s*$", l)
        if m and "A" in m.group(3):
            out.append((m.group(1), m.group(2).split("|")[0].strip()))
    return out


def tests(log):
    """unittest -v lines: 'name (mod.Class.name)' then, possibly after a docstring line, '... ok|FAIL|ERROR|skipped'."""
    res, cur = {}, None
    for l in open(log, encoding="utf-8"):
        m = re.match(r"(test\w+) \(([\w.]+)\)", l)
        if m:
            cur = m.group(2).split(".")[-2] + "." + m.group(1)
        r = re.search(r"\.\.\. (ok|FAIL|ERROR|skipped.*)$", l.rstrip()) or re.fullmatch(r"(ok|FAIL|ERROR)", l.strip())
        if r and cur:
            res[cur] = r.group(1)
            cur = None
    return res


def main(spec, log):
    R, Tt = rows(spec), tests(log)
    print("# SL-PT-001 | §11.6 coverage matrix (Stage A) | generated")
    print(f"\nSpec SHA-256 `{hashlib.sha256(open(spec,'rb').read()).hexdigest()}`; test log `{log.split('/')[-1]}` "
          f"SHA-256 `{hashlib.sha256(open(log,'rb').read()).hexdigest()}`; {len(Tt)} test results parsed.\n")
    print("| id | §14 input (abridged) | harness evidence (tests, result) | auditor half | status |\n|---|---|---|---|---|")
    counts = {}
    for uid, inp in R:
        pat = re.compile(r"(?<![A-Za-z0-9])" + re.escape(uid) + r"(?![0-9])")
        hits = [f"`{k}` {v}" for k, v in sorted(Tt.items()) if pat.search(k)]
        ok = hits and all(h.endswith(" ok") for h in hits)
        side = "REQUIRED (GPT)" if uid in AUDITOR or uid in BOTH else "-"
        if uid in AUDITOR:
            st = "AUDITOR-ONLY: pending GPT table"
        elif ok:
            st = "HARNESS-EXECUTED" + (" + auditor half pending" if uid in BOTH else "")
        else:
            st = "OPEN"
        counts[st] = counts.get(st, 0) + 1
        note = NOTE.get(uid, "")
        print(f"| {uid} | {inp[:90].replace('|','/')} | {'<br>'.join(hits) or '-'}{('<br>'+note) if note else ''} | {side} | {st} |")
    print("\n**Totals:** " + "; ".join(f"{k}: {v}" for k, v in sorted(counts.items())) + f"; rows: {len(R)}")
    print("\nAuditor results are synthetic classification checks only: they are not evidence of real scheduler, "
          "concurrency, crash-recovery or filesystem-durability behavior (GPT dispatch, 2026-11-26).")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
