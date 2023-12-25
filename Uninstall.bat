@echo off
setlocal enabledelayedexpansion

:: 删除注册表
echo Deleting registry keys...
reg delete "HKCR\*\shell\compress" /f
reg delete "HKCR\*\shell\decompress" /f
reg delete "HKCR\Directory\shell\compress" /f

:: 删除系统环境变量
reg delete "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v FileToZip /f

:: 获取当前 BAT 文件所在的目录
set "BAT_DIR=%~dp0"

:: 删除目录中的所有文件和文件夹
echo Deleting all files and directories in the directory...
for /d %%i in ("!BAT_DIR!*") do rmdir /s /q "%%i"
del /q "!BAT_DIR!*"

:: 删除 BAT 文件本身
del /f /q "!BAT_DIR!Uninstall.bat"


