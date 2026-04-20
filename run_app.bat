@echo off
setlocal

REM Oke Creator Web App launcher

cd /d "%~dp0"

echo.
echo ========================================
echo   Oke Creator - Web App Launch
echo ========================================
echo.

set "PYTHON_EXE=%CD%\.venv\Scripts\python.exe"

if not exist "%PYTHON_EXE%" (
  echo [ERROR] Virtual environment was not found.
  echo Create it first:
  echo   python -m venv .venv
  echo   .\.venv\Scripts\python.exe -m pip install --upgrade pip
  echo   .\.venv\Scripts\python.exe -m pip install -r .\src\requirements.txt
  pause
  exit /b 1
)

echo [OK] Using Python:
echo   %PYTHON_EXE%
echo.
echo Starting Streamlit...
echo Open this URL in your browser:
echo   http://127.0.0.1:8501
echo.

"%PYTHON_EXE%" -m streamlit run ".\src\app.py" --server.address 127.0.0.1 --server.port 8501

pause
