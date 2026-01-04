@echo off
REM Oke Creator Web App 起動スクリプト

echo.
echo ========================================
echo   Oke Creator - Web App Launch
echo ========================================
echo.

REM 仮想環境を有効化
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
    echo [OK] 仮想環境を有効化しました
) else (
    echo [ERROR] 仮想環境が見つかりません
    echo venv を作成してください:
    echo   python -m venv .venv
    pause
    exit /b 1
)

echo.
echo Streamlitアプリを起動中...
echo ブラウザで http://localhost:8501 を開いてください
echo.

REM Streamlitアプリ起動
streamlit run src/app.py

pause
