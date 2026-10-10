@echo off
chcp 65001 >nul
echo [1/3] 停止已运行的旧程序...
taskkill /f /im "WWMI_MOD面板助手.exe" >nul 2>&1
echo [2/3] 清理旧构建...
rmdir /s /q build dist 2>nul
del /q *.spec 2>nul
echo [3/3] 打包中...
pyinstaller --noconfirm --onefile --windowed --name "WWMI_MOD面板助手" src/main.py
echo.
echo 完成！产物在 dist\WWMI_MOD面板助手.exe
pause
