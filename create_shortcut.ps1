$s = (New-Object -ComObject WScript.Shell).CreateShortcut("$env:USERPROFILE\Desktop\Invoice Monitor.lnk")
$s.TargetPath = "cmd.exe"
$s.Arguments = "/c start_monitor.bat"
$s.WorkingDirectory = "C:\Users\Test user 1\FileAttachment"
$s.Save()
Write-Host "Shortcut created on Desktop"