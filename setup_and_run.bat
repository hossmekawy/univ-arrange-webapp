@echo off
setlocal enabledelayedexpansion
color 0b

echo =================================================================
echo                University Course Organizer v1.2
echo =================================================================
echo.
echo      [][][][][]  Starting Setup Process  [][][][][]
echo.
echo =================================================================

:: Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [*] Installing Python...
    mkdir temp_downloads 2>nul
    cd temp_downloads
    echo [*] Downloading installer...
    powershell -Command "(New-Object Net.WebClient).DownloadFile('https://www.python.org/ftp/python/3.10.8/python-3.10.8-amd64.exe', 'python_installer.exe')"
    echo [*] Running installer...
    start /wait python_installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
    del python_installer.exe
    cd ..
    rmdir /S /Q temp_downloads
    echo [+] Python installed successfully!
) else (
    echo [+] Python is ready!
)

:: Virtual environment setup
if not exist venv (
    echo [*] Creating virtual environment...
    python -m venv venv
    echo [+] Virtual environment created!
)

echo [*] Activating virtual environment...
call venv\Scripts\activate.bat
echo [+] Virtual environment activated!

:: Package installation
echo [*] Installing required packages...
pip install flask werkzeug qrcode pillow
echo [+] Packages installed successfully!

:: Directory setup
if not exist uploads (
    echo [*] Creating uploads directory...
    mkdir uploads
)

if not exist data (
    echo [*] Creating data directory...
    mkdir data
)

if not exist data\courses.json (
    echo [*] Initializing courses database...
    echo {"courses": []} > data\courses.json
)

cls
color 0a

echo =================================================================
echo                University Course Organizer v1.2
echo =================================================================
echo.
echo  [+] System initialized
echo  [+] Dependencies installed
echo  [+] Database ready
echo.
echo  The application will open in your browser automatically...
echo.
echo  Press Ctrl+C to stop the server when finished
echo.
echo =================================================================
echo            Created by ENG / HUSSIEN MEKAWY © 2025 
echo				HAPPY RAMADAN 2025
echo =================================================================
echo.

:: Run Flask app
python app.py

:: Cleanup
call venv\Scripts\deactivate.bat
pause
