param(
    [string] $Out = 'sample.wav',
    [int] $ChunkMs = 200,
    [ValidateSet('realtime','maxspeed')] [string] $Mode = 'realtime',
    [ValidateSet('on','off')] [string] $Interim = 'on',
    [string] $LogDir = 'logs'
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

. "$PSScriptRoot/common.ps1"

& "$PSScriptRoot/make-sample.ps1" -Out $Out -Seconds 2.0
& "$PSScriptRoot/run-cli.ps1" --file $Out --chunk-ms $ChunkMs --mode $Mode --interim $Interim --log-dir $LogDir
