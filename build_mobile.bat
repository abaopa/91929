@echo off
setlocal

set PYINSTALLER=%LOCALAPPDATA%\Packages\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\LocalCache\local-packages\Python313\Scripts\pyinstaller.exe

echo Building Mobile Version (Flet)...
"%PYINSTALLER%" --noconfirm --onefile --windowed ^
    --name "91929_Mobile" ^
    --add-data "assets;assets" ^
    --add-data "src;src" ^
    --hidden-import flet ^
    --hidden-import flet.cli ^
    --collect-all flet ^
    mobile_main.py

echo Build complete: dist\91929_Mobile.exe
pause
