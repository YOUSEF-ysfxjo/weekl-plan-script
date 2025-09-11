@echo off
call .venv\Scripts\activate

:: Run the tests with detailed output
python -c "
import sys
import unittest

print('Running tests with Python:', sys.version)
print('Current working directory:', __import__('os').getcwd())
print('Python path:', sys.path)

# Discover and run tests
test_suite = unittest.TestLoader().discover('.')
result = unittest.TextTestRunner(verbosity=2).run(test_suite)

# Exit with appropriate code
sys.exit(not result.wasSuccessful())
"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo =============================================
    echo  Some tests failed. See output above for details.
    echo =============================================
    pause
) else (
    echo.
    echo =============================================
    echo  All tests passed successfully!
    echo =============================================
    pause
)
