param()
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

. "$PSScriptRoot/common.ps1"

Invoke-PythonModule -Module 'wer_tester.gui'
