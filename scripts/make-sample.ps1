param(
    [string] $Out = 'sample.wav',
    [double] $Seconds = 2.0
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

. "$PSScriptRoot/common.ps1"

Invoke-PythonModule -Module 'tools.make_sample_wav' -Args @('--out', $Out, '--seconds', "$Seconds")
