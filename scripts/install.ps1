param()
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

. "$PSScriptRoot/common.ps1"

$root = Resolve-RepoRoot
Push-Location $root
try {
    $py = Get-PythonCmd
    & $py -m pip install --upgrade pip
    & $py -m pip install -e .
} finally { Pop-Location }
Write-Host "Namestitev končana." -ForegroundColor Green
