@echo off
echo Checking Python environment...
where python
echo.
python --version
echo.
pip list
echo.
echo Current directory: %CD%
echo.
echo Directory contents:
dir /b
echo.
if exist src (
    echo src directory exists
    dir /b src
) else (
    echo src directory does not exist
)
echo.
pause
