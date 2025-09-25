$ErrorActionPreference = 'Stop'

function Resolve-RepoRoot {
    param()
    return (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
}

function Get-PythonCmd {
    param()
    $candidates = @()
    if ($env:VIRTUAL_ENV) {
        $venvPy = Join-Path $env:VIRTUAL_ENV 'Scripts/python.exe'
        if (Test-Path $venvPy) {
            $candidates += ,@($venvPy)
        }
    }
    $candidates += ,@('python')
    $candidates += ,@('py','-3')
    $candidates += ,@('py')

    foreach ($cand in $candidates) {
        try {
            $args = @('-c','import sys; print(sys.executable)')
            $proc = & $cand @args 2>$null
            if ($LASTEXITCODE -eq 0 -and $proc) { return $cand }
        } catch { }
    }
    throw "Python ni najden. Namestite Python 3.9+ in dodajte na PATH."
}

function Invoke-PythonModule {
    param(
        [Parameter(Mandatory)] [string] $Module,
        [string[]] $Args
    )
    $py = Get-PythonCmd
    & $py '-m' $Module @Args
}

# Note: This file is dot-sourced by other scripts; no module export needed.
