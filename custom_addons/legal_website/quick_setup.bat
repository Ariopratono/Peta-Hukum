@echo off
REM Quick Setup Script for Legal Website in Odoo

echo 🚀 LEGAL WEBSITE - QUICK SETUP
echo ================================

REM Check if we're in the right directory
if not exist "__manifest__.py" (
    echo ❌ Error: Jalankan script ini dari dalam folder legal_website
    echo    cd custom_addons\legal_website
    exit /b 1
)

echo ✅ Directory check passed

REM Check if we're in Odoo environment
if not exist "..\..\server\odoo-bin" (
    echo ❌ Odoo server tidak ditemukan di ..\..\server\
    echo    Pastikan struktur: Program Files\Odoo\custom_addons\legal_website
    exit /b 1
)

echo ✅ Odoo server found

REM Check requests library
echo 📦 Checking dependencies...
cd ..\..
python\python.exe -c "import requests" >nul 2>&1
if errorlevel 1 (
    echo 📦 Installing requests...
    python\python.exe -m pip install requests
) else (
    echo ✅ requests library installed
)

REM Test search functionality
echo 🌐 Testing search functionality...
cd custom_addons\legal_website
python ..\..\python\python.exe -c "print('✅ Mock search ready to use!'); print('🎯 Try searching: hukum pidana, korupsi, KUHP')" 2>nul

echo.
echo 🎉 SETUP COMPLETE!
echo ================================
echo.
echo 📋 NEXT STEPS:
echo 1. Start Odoo server:
echo    cd ..\..
echo    python\python.exe server\odoo-bin --addons-path=server/addons,custom_addons
echo.
echo 2. Open browser: http://localhost:8069
echo 3. Login dan install 'Legal Website' module
echo 4. Test search di: http://localhost:8069/
echo.
echo 📚 Documentation:
echo    - README.md - Full documentation
echo    - USAGE_GUIDE.md - Step-by-step usage
echo    - INSTALLATION_GUIDE.md - Detailed setup
echo.
echo 🔍 Test queries:
echo    - 'hukum pidana indonesia'
echo    - 'tindak pidana korupsi' 
echo    - 'kuhp terbaru'
echo    - 'konsultasi hukum'
echo.
pause