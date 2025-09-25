param(
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]] $Args
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

. "$PSScriptRoot/common.ps1"

Invoke-PythonModule -Module 'wer_tester.cli' -Args $Args
