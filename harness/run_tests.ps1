# SL-PT-001 Strike 1a: run the deterministic-core unit tests on Windows and retain the result log.
# One command, from anywhere:
#   powershell -ExecutionPolicy Bypass -File "$HOME\Sentinel_EAR\harness\run_tests.ps1"
# Scope: exact.py and decide.py (signal + mapping) only. No network, no credentials, no market data.

$repo = Split-Path -Parent $PSScriptRoot
Set-Location $repo

& py -3.12 -c "import sys" 2>$null
if ($LASTEXITCODE -ne 0) {
  "STOP: Python 3.12 not found via the py launcher. Install Python 3.12 from python.org (keep 3.14), then rerun."
  exit 2
}
$ver    = (& py -3.12 -c "import sys; print(sys.version.split()[0])").Trim()
$commit = (git rev-parse HEAD).Trim()
$dirty  = git status --porcelain -- harness
$stamp  = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
New-Item -ItemType Directory -Force "harness\tests\results" | Out-Null
$log    = "harness\tests\results\windows_$stamp.txt"

$hdr = @(
  "SL-PT-001 Strike 1a test run (Windows, founder machine)",
  "UTC: $stamp",
  "Python: $ver",
  "Repo HEAD: $commit",
  ("Harness tree uncommitted changes: " + $(if ($dirty) { "YES - this run is not tied to a commit" } else { "none" })),
  "File SHA-256:"
)
Get-ChildItem harness\sl_pt_001\*.py, harness\tests\test_*.py | Sort-Object FullName | ForEach-Object {
  $hdr += ("  " + (Get-FileHash -Algorithm SHA256 $_.FullName).Hash.ToLower() + "  " + (Resolve-Path -Relative $_.FullName))
}
$hdr | Set-Content -Encoding ascii $log

cmd /c "py -3.12 -I -m unittest discover -s harness\tests -v >> `"$log`" 2>&1"
$rc = $LASTEXITCODE
"Exit code: $rc" | Add-Content -Encoding ascii $log

Get-Content $log -Tail 6
""
"Result log: $log"
if ($rc -eq 0) { "ALL TESTS PASSED. Commit the log (see the instructions)." } else { "TESTS FAILED. Do not edit anything; send the log." }
exit $rc
