param([string]$Repository = "mfreeze77/statement-ledger")
$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")
if ($Repository -notmatch "^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$") { throw "Expected owner/new-repository-name." }
if (-not (Get-Command git -ErrorAction SilentlyContinue)) { throw "Install Git first." }
$ProjectRoot = (Get-Location).Path
$GitRoot = & git rev-parse --show-toplevel 2>$null
if ($LASTEXITCODE -eq 0 -and [System.IO.Path]::GetFullPath($GitRoot) -ne $ProjectRoot) { throw "Refusing: this directory is inside a different Git repository." }
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) { throw "Install GitHub CLI and run gh auth login first." }
& gh auth status
if ($LASTEXITCODE -ne 0) { throw "GitHub authentication is required." }
& git rev-parse --is-inside-work-tree *> $null
if ($LASTEXITCODE -ne 0) { & git init -b main }
& git remote get-url origin *> $null
if ($LASTEXITCODE -eq 0) { throw "Refusing: origin already exists. Use a new repository." }
if (& git status --porcelain) { throw "Commit or remove outstanding changes before publishing." }
& git rev-parse HEAD *> $null
if ($LASTEXITCODE -ne 0) { throw "Create the initial Git commit before publishing." }
& gh repo create $Repository --private --source . --remote origin --push
if ($LASTEXITCODE -ne 0) { throw "GitHub repository creation failed; existing projects were not modified." }
