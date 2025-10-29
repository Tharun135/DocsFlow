@echo off
REM DocsFlow Development Helper Script for Windows
REM This script activates the virtual environment and runs MkDocs commands

setlocal

REM Check if virtual environment exists
if not exist ".venv\Scripts\python.exe" (
    echo ❌ Virtual environment not found!
    echo Run 'make install' or 'pip install -r requirements.txt' first
    exit /b 1
)

REM Get the command argument
set CMD=%1

if "%CMD%"=="" (
    echo 📘 DocsFlow Helper - Available Commands:
    echo.
    echo   serve     - Start development server
    echo   build     - Build documentation
    echo   lint      - Run documentation linting
    echo   validate  - Validate YAML files
    echo   deploy    - Deploy to Fluid Topics
    echo.
    echo Usage: docs.bat [command]
    echo Example: docs.bat serve
    exit /b 0
)

if "%CMD%"=="serve" (
    echo 🚀 Starting MkDocs development server...
    .venv\Scripts\python.exe -m mkdocs serve --dev-addr localhost:8000
    goto end
)

if "%CMD%"=="build" (
    echo 🏗️ Building documentation...
    .venv\Scripts\python.exe -m mkdocs build --clean --strict
    goto end
)

if "%CMD%"=="lint" (
    echo 🔍 Running documentation linting...
    .venv\Scripts\python.exe scripts\lint_docs.py
    goto end
)

if "%CMD%"=="validate" (
    echo 📋 Validating YAML files...
    .venv\Scripts\python.exe scripts\validate_yaml.py
    goto end
)

if "%CMD%"=="deploy" (
    echo 🚀 Deploying to Fluid Topics...
    .venv\Scripts\python.exe -m mkdocs build --clean --strict
    .venv\Scripts\python.exe scripts\upload_to_fluidtopics.py
    goto end
)

echo ❌ Unknown command: %CMD%
echo Run 'docs.bat' without arguments to see available commands.
exit /b 1

:end
endlocal