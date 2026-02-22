@echo off
setlocal

set PYINSTALLER=%LOCALAPPDATA%\Packages\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\LocalCache\local-packages\Python313\Scripts\pyinstaller.exe

echo Building Desktop Version (Tkinter)...
"%PYINSTALLER%" --noconfirm --onefile --windowed ^
    --name "91929_Desktop" ^
    --add-data "assets;assets" ^
    --add-data "src;src" ^
    --hidden-import tkinter ^
    --hidden-import tkinter.filedialog ^
    --hidden-import tkinter.messagebox ^
    desktop_main.py

echo Build complete: dist\91929_Desktop.exe
pause
