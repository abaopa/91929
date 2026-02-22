@echo off
setlocal

echo Finding PyInstaller path...
for /f "delims=" %%i in ('powershell -NoProfile -Command "$env:LOCALAPPDATA\Packages\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\LocalCache\local-packages\Python313\Scripts\pyinstaller.exe"') do set PYINSTALLER=%%i

if not exist "%PYINSTALLER%" (
    set PYINSTALLER=%LOCALAPPDATA%\Packages\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\LocalCache\local-packages\Python313\Scripts\pyinstaller.exe
)

echo Using PyInstaller: %PYINSTALLER%

echo.
echo ========================================
echo Building Desktop Version (Tkinter)...
echo =================local=======================
"%PYINSTALLER%" --noconfirm --onefile --windowed ^
    --name "91929_Desktop" ^
    --add-data "assets;assets" ^
    --add-data "src;src" ^
    --hidden-import tkinter ^
    --hidden-import tkinter.filedialog ^
    --hidden-import tkinter.messagebox ^
    desktop_main.py

echo.
echo ========================================
echo Building Mobile Version (Flet)...
echo ========================================
"%PYINSTALLER%" --noconfirm --onefile --windowed ^
    --name "91929_Mobile" ^
    --add-data "assets;assets" ^
    --add-data "src;src" ^
    --hidden-import flet ^
    --hidden-import flet.cli ^
    --collect-all flet ^
    mobile_main.py

echo.
echo Build process complete. Check the 'dist' folder for:
echo - 91929_Desktop.exe
echo - 91929_Mobile.exe
pause
