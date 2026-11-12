@echo off
title Push Axiom to GitHub
cd /d "%~dp0"

echo ============================================================
echo   PUSHING AXIOM TO GITHUB (Itachii0707/Axiom)
echo ============================================================
echo.
echo Remote target: https://github.com/Itachii0707/Axiom.git
echo Commit author: Itachii0707
echo.
echo If your browser opens a GitHub login window, simply click 'Authorize Git Credential Manager'.
echo.

git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo ============================================================
    echo   SUCCESS! Axiom is now live on your GitHub repository:
    echo   https://github.com/Itachii0707/Axiom
    echo ============================================================
) else (
    echo.
    echo If authentication failed, please ensure you are signed into GitHub in your browser.
)

echo.
pause
