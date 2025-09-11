@echo off
setlocal enabledelayedexpansion

:: Set Python path - adjust this to your Python executable path
set PYTHON_PATH=C:\Users\HP\AppData\Local\Programs\Python\Python39\python.exe

:: Set environment variables
set NOTION_TOKEN=test_token
set PYTHONPATH=%~dp0src

:: Run the test file
echo Running tests...
"%PYTHON_PATH%" -m unittest test_notion.py -v

:: Check the error level
if !ERRORLEVEL! EQU 0 (
    echo.
    echo =============================================
    echo  All tests passed successfully!
    echo =============================================
) else (
    echo.
    echo =============================================
    echo  Some tests failed. See output above for details.
    echo =============================================
)

pause
