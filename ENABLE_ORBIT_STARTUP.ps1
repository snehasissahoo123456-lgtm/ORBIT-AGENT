$ErrorActionPreference = "Stop"
$startup = [Environment]::GetFolderPath("Startup")
$shortcutPath = Join-Path $startup "ORBIT Agent.lnk"
$target = Join-Path $PSScriptRoot "START_ORBIT.bat"
if (-not (Test-Path $target)) { throw "START_ORBIT.bat was not found in $PSScriptRoot" }
$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $target
$shortcut.WorkingDirectory = $PSScriptRoot
$shortcut.Description = "Start the local ORBIT Founder Agent"
$shortcut.Save()
Write-Host "ORBIT will start when this Windows user signs in. The PC must remain powered on for local tasks."
Write-Host "Shortcut: $shortcutPath"
