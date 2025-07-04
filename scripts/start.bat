@echo off
chcp 65001
powershell.exe -command "& {Start-Process -WindowStyle hidden -FilePath './run.bat'}"