$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Script = Join-Path $Root "codex_woodling.py"

if (Get-Command py -ErrorAction SilentlyContinue) {
  py $Script @args
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
  python3 $Script @args
} else {
  python $Script @args
}
