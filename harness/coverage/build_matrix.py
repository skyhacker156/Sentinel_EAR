"""Build the §11.6 coverage matrix from the frozen spec's §14 Stage-A rows and a retained verbose test log.
Usage: python build_matrix.py <spec.md> <verbose_test_log.txt> <out.md> [auditor_coverage.csv ...]  (writes UTF-8 itself)
Auditor CSVs (GPT, FD-6 v2.3) are merged per row; their scope_and_limits text is carried verbatim.   (stdlib only; reads, never writes evidence)
A row is HARNESS-EXECUTED only if a test whose name carries its id appears in the log with result 'ok'.
AUDITOR rows are classifications only the FD-6 auditor executes (GPT, synthetic evidence, scope-limited)."""
import csv, hashlib, re, sys

AUDITOR = {"X11", "U26", "U27", "U34", "U37", "U38", "U41", "U66", "U68", "U69", "U71", "U103", "U109", "U120"}
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
        m = re.match(r"\|\s*([UX]\d+[\w-]*)\s*\|(.*)\|\s*([^|]*)\|\s*$", l)
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


def auditor_rows(paths):
    by = {}
    for pth in paths:
        name = pth.replace(chr(92), "/").split("/")[-1]
        with open(pth, encoding="utf-8", newline="") as fh:
            for r in csv.DictReader(fh):
                if r["spec_id"]:
                    by.setdefault(r["spec_id"], []).append((name, r["case_id"], r["status"], r["scope_and_limits"]))
    return by


def main(spec, log, out_path, csvs=()):
    out = open(out_path, "w", encoding="utf-8", newline="\n")

    def print(*a):
        out.write(" ".join(str(x) for x in a) + "\n")
    R, Tt, AU = rows(spec), tests(log), auditor_rows(csvs)
    print("# SL-PT-001 | §11.6 coverage matrix (Stage A) | generated")
    print(f"\nSpec SHA-256 `{hashlib.sha256(open(spec,'rb').read()).hexdigest()}`; test log `{log.replace(chr(92), '/').split('/')[-1]}` "
          f"SHA-256 `{hashlib.sha256(open(log,'rb').read()).hexdigest()}`; {len(Tt)} test results parsed.\n")
    for c in csvs:
        print(f"Auditor CSV `{c.replace(chr(92), '/').split('/')[-1]}` SHA-256 `{hashlib.sha256(open(c,'rb').read()).hexdigest()}`")
    print("\n| id | §14 input (abridged) | harness evidence (tests, result) | auditor evidence (GPT synthetic; limits verbatim) | status |\n|---|---|---|---|---|")
    counts = {}
    for uid, inp in R:
        pat = re.compile(r"(?<![A-Za-z0-9])" + re.escape(uid) + r"(?![0-9])")
        hits = [f"`{k}` {v}" for k, v in sorted(Tt.items()) if pat.search(k)]
        ok = hits and all(h.endswith(" ok") for h in hits)
        au = AU.get(uid, [])
        au_ok = bool(au) and all(a[2] == "PASS" for a in au)
        need = uid in AUDITOR or uid in BOTH
        side = ("<br>".join(f"{a[1]} {a[2]}: {a[3][:140]}" for a in au) if au else ("REQUIRED, none supplied" if need else "-"))
        if uid in AUDITOR:
            st = "AUDITOR-EXECUTED (synthetic classification only)" if au_ok else "OPEN (auditor)"
        elif not ok:
            st = "OPEN (harness)"
        elif uid in BOTH:
            st = "BOTH HALVES EXECUTED" if au_ok else "OPEN (auditor half)"
        else:
            st = "HARNESS-EXECUTED" + (" + auditor assertions" if au_ok else "")
        counts[st] = counts.get(st, 0) + 1
        note = NOTE.get(uid, "")
        print(f"| {uid} | {inp[:90].replace('|','/')} | {'<br>'.join(hits) or '-'}{('<br>'+note) if note else ''} | {side} | {st} |")
    print("\n**Totals:** " + "; ".join(f"{k}: {v}" for k, v in sorted(counts.items())) + f"; rows: {len(R)}")
    print("\nAuditor results are synthetic classification checks only: they are not evidence of real scheduler, "
          "concurrency, crash-recovery or filesystem-durability behavior (GPT dispatch, 2026-11-26).")
    out.close()
    return counts


if __name__ == "__main__":
    c = main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:])
    sys.stdout.write("rows " + str(sum(c.values())) + "; " + "; ".join(f"{k}: {v}" for k, v in sorted(c.items())) + "\n")
