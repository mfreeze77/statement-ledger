param([Parameter(Position=0)][string]$Action="check", [Parameter(ValueFromRemainingArguments=$true)][string[]]$Rest)
$ErrorActionPreference = "Stop"
$Runner = Join-Path $PSScriptRoot "dev.py"
if (Get-Command py -ErrorAction SilentlyContinue) { & py -3 $Runner $Action @Rest }
else { & python $Runner $Action @Rest }
exit $LASTEXITCODE
