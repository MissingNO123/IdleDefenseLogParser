@echo off
python .\setup.py build_ext --inplace
IF %ERRORLEVEL% NEQ 0 (
    echo Error: Cythonization failed.
    goto :end
)
pyinstaller --onefile --name "IdleSaver" --add-binary="idlesaver.cp311-win_amd64.pyd:idlesaver" --hidden-import customtkinter --exclude matplotlib --exclude scipy --exclude pandas --exclude numpy --version-file "version.txt" .\run.py
IF %ERRORLEVEL% NEQ 0 (
    echo Error: PyInstaller build failed.
    goto :end
)
:end