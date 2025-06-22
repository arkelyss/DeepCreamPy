@echo off
REM ------------------------------------------------------------
REM  Arkelyss DPC – bootstrap + launcher
REM ------------------------------------------------------------

setlocal

REM --- 0. Try PATH first ------------------------------------------------------
where conda >nul 2>&1
if errorlevel 1 (
    REM --- 1. Look in the most common single-user install folder ---------------
    if exist "%USERPROFILE%\Miniconda3\Scripts\conda.exe" (
        set "CONDA_EXE=%USERPROFILE%\Miniconda3\Scripts\conda.exe"
    ) else if exist "C:\ProgramData\Miniconda3\Scripts\conda.exe" (
        REM --- 2. Common all-users location -----------------------------------
        set "CONDA_EXE=C:\ProgramData\Miniconda3\Scripts\conda.exe"
    ) else (
        echo.
        echo =========================================================
        echo   Conda was not found.
        echo.
        echo   • Install Miniconda or Anaconda first
        echo     https://docs.conda.io/en/latest/miniconda.html
        echo   • OR open a "Miniconda Prompt" and run:
        echo       conda init cmd.exe
        echo     then re-open this window.
        echo =========================================================
        echo.
        pause
        goto :eof
    )
) else (
    REM PATH version
    for /f "delims=" %%i in ('where conda') do set "CONDA_EXE=%%i" & goto :found
)

:found
REM --- Bootstrap conda in this shell -----------------------------------------
for %%i in ("%CONDA_EXE%") do set "CONDA_BASE=%%~dpi\..\"
call "%CONDA_BASE%\Scripts\activate.bat"

set "ENV_NAME=arkelyssdpc"

REM --- Create env if missing --------------------------------------------------
conda env list | findstr /R /C:"^%ENV_NAME% " >nul 2>&1
if errorlevel 1 (
    echo Creating env "%ENV_NAME%" with Python 3.9...
    conda create -y -n %ENV_NAME% python=3.9
) else (
    echo Environment "%ENV_NAME%" already exists.
)

REM --- Activate and install deps ---------------------------------------------
echo Activating "%ENV_NAME%"...
call conda activate %ENV_NAME%

echo Checking packages...
call pip install -r requirements-gpu.txt

REM --- Launch DPC -------------------------------------------------
echo.
echo Launching Arkelyss DPC...
python main.py %*

echo.
pause
