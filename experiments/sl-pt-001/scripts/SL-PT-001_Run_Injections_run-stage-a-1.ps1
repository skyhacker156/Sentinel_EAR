# SL-PT-001 run-stage-a-1: run the six planned BUY injections (R4.2i section 6.5), founder-commanded.
# Run with:  powershell -ExecutionPolicy Bypass -File "$HOME\Downloads\SL-PT-001_Run_Injections_run-stage-a-1.ps1"
# It writes ONLY through the harness CLI 'inject' command. It edits no file, commits nothing and contacts no host.
# Each injection starts only between 60 s and 240 s after a slot's T_d, which keeps it clear of the 30 s rule before
# the next T_d and away from the slot's own cycle. It stops at the first unexpected result.

$repo = "$HOME\Sentinel_EAR"
$ev   = "$repo\experiments\sl-pt-001"
$man  = "$ev\runs\run-stage-a-1.json"
$plan = "$ev\injections\plan-stage-a.json"
$t0   = [DateTimeOffset]::Parse("2026-11-27T02:01:00Z")
$last = $t0.AddSeconds(35 * 300 + 240)          # no injection after 240 s into the final slot (23:56 EST + 4 min)

# Guard 1: pinned files untouched since the run manifest commit.
Set-Location $repo
$dirty = git status --porcelain -- harness experiments/sl-pt-001/policy experiments/sl-pt-001/runs experiments/sl-pt-001/injections
if ($dirty) { "STOP: uncommitted changes in pinned paths:"; $dirty; exit 1 }

# Guard 2: the plan file is the committed plan.
$ph = (Get-FileHash -Algorithm SHA256 $plan).Hash.ToLower()
if ($ph -ne "a6efadc1c27d92c760c1d8e68011d5fce1365b46c501a5128de36f2b5ca193ed") { "STOP: plan hash $ph"; exit 1 }

$list = @(
  @("810549f64fc54e4e899af2ff9e76951b23bd623ed365eba0c9c24ab23f15bae4", "R1"),
  @("5d46d9f5e48f675a71ff80d1003d465d9196e2917004735b3ec1134d747128ed", "R4"),
  @("cc6f00e38ac8e61ab83976213cc922df5f67e96959386c50ab7e3df55d6822a4", "R5"),
  @("e7b1b5da65290f413837f381c8704fdc6859f33b4c8c9cbe1ee2e57608b62bc2", "R10"),
  @("e7251bc24e9491efc59641e27e5a10bf060f82fd26e0d16a56ea55790a113be5", "R12"),
  @("db17c2cb11d985eb9987db239fe001f31ae5a2a620e59fa6914b384e32e9441e", "R13")
)

# Skip any injection already recorded in the chain (safe to re-run this script).
$done = @{}
Get-Content "$ev\chain\events.jsonl" | ForEach-Object {
  $r = $_ | ConvertFrom-Json
  if ($r.type -eq "INJECTION") { $done[$r.body.injection.fixture_sha256] = $true }
}

Set-Location "$repo\harness"
foreach ($item in $list) {
  $h = $item[0]; $rule = $item[1]
  if ($done.ContainsKey($h)) { "SKIP $rule (already recorded)"; continue }
  $fx = "$ev\injections\fixtures\$h.json"
  if ((Get-FileHash -Algorithm SHA256 $fx).Hash.ToLower() -ne $h) { "STOP: fixture hash mismatch for $rule"; exit 1 }

  while ($true) {
    $now = [DateTimeOffset]::UtcNow
    if ($now -gt $last) { "STOP: past the last injection window; $rule not run"; exit 1 }
    $off = (($now - $t0).TotalSeconds) % 300
    if ($now -ge $t0 -and $off -ge 60 -and $off -le 240) { break }
    Start-Sleep -Seconds 5
  }

  $out  = & py -3.12 -E -s -m sl_pt_001.cli inject $ev $man $plan $fx $rule
  $code = $LASTEXITCODE
  "$rule -> $out (exit $code)"
  if ($code -ne 0 -or -not ("$out" -match "INJECTION\s+REJECTED")) { "STOP: unexpected result for $rule. Send this output to Claude."; exit 1 }
  Start-Sleep -Seconds 2
}

""
"Verification (intended rule vs failing rules recorded in each INJECTION):"
Get-Content "$ev\chain\events.jsonl" | ForEach-Object {
  $r = $_ | ConvertFrom-Json
  if ($r.type -eq "INJECTION") {
    $fails = ($r.body.rule_results | Where-Object { $_.result -eq "FAIL" } | ForEach-Object { $_.rule }) -join ","
    "{0,3}  intended {1,-4} terminal {2,-9} failed [{3}]" -f $r.seq, $r.body.injection.intended_rule, $r.body.terminal_state, $fails
  }
}
"DONE"
