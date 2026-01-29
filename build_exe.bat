@echo off
echo ========================================
echo Nexuzy Publisher Desk - Build System
echo ========================================
echo.

echo [1/5] Checking Python...
python --version
echo.

echo [2/5] Installing PyInstaller...
pip install pyinstaller
echo.

echo [3/5] Installing dependencies...
pip install -r requirements.txt
echo.

echo [4/5] Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist\NexuzyPublisher rmdir /s /q dist\NexuzyPublisher
echo.

echo [5/5] Building executable...
pyinstaller nexuzy_publisher.spec

echo.
echo Build complete!
echo Executable: dist\NexuzyPublisher\NexuzyPublisher.exe
echo.
pause
