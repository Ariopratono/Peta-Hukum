@echo off

REM Install Script untuk Legal Website Module - Windows

echo === Installing Legal Website Module ===

REM Check if we're in Odoo directory
if not exist "odoo-bin" (
    echo Error: Script harus dijalankan dari direktori Odoo server
    pause
    exit /b 1
)

REM Install Python dependencies
echo Installing Python dependencies...

REM Use Python from Odoo installation
set PYTHON_PATH=python\python.exe
if exist "%PYTHON_PATH%" (
    echo Using Odoo Python: %PYTHON_PATH%
    "%PYTHON_PATH%" -m pip install requests --user
) else (
    echo Using system Python...
    python -m pip install requests --user
    if errorlevel 1 (
        echo Error: Gagal install dependencies. Pastikan Python dan pip terinstall.
        pause
        exit /b 1
    )
)

echo Python dependencies installed successfully.

REM Check if custom_addons directory exists
if not exist "custom_addons" (
    echo Creating custom_addons directory...
    mkdir custom_addons
)

echo.
echo === Installation Complete ===
echo.
echo Next steps:
echo 1. Start Odoo server:
echo    odoo-bin -c odoo.conf --addons-path=addons,custom_addons
echo.
echo 2. Login ke Odoo dan update Apps list
echo 3. Install module 'Legal Website' dari Apps menu  
echo 4. Konfigurasi SearXNG di Website Hukum ^> Pencarian ^> Konfigurasi
echo.
echo Default SearXNG instance: https://search.brave4u.com
echo Atau gunakan SearXNG instance lain yang tersedia.
echo.
echo Untuk dokumentasi lengkap, baca file README.md di folder module.

pause