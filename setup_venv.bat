@echo off
echo Creating virtual environment...

python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing GPU requirements...
pip install --upgrade pip
pip install -r requirements-gpu.txt

echo Setup complete.
pause
