@echo off
setlocal

rem Get the directory where this script is located
set "script_dir=%~dp0"

rem Define the path to the virtual environment
set "venv_path=%script_dir%ex_extracta"

rem Check if the virtual environment already exists
if exist "%venv_path%\Scripts\activate.bat" (
    echo Virtual environment already exists. Activating...
    call "%venv_path%\Scripts\activate.bat"
) else (
    echo Creating virtual environment at "%venv_path%"...
    py -3.11 -m venv "%venv_path%"
    call "%venv_path%\Scripts\activate.bat"

    echo Installing required packages...
    call "%venv_path%\Scripts\python.exe" -m pip install --upgrade pip
    call "%venv_path%\Scripts\python.exe" -m pip install -r "%script_dir%requirements.txt"

    echo Installing Jupyter Notebook with compatible versions...
    call "%venv_path%\Scripts\python.exe" -m pip install jupyter notebook==6.5.2 traitlets==5.9.0 ipython==7.31.1
)

rem Launch Jupyter Notebook
call "%venv_path%\Scripts\jupyter-notebook.exe"

pause
