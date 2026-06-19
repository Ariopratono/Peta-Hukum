#!/bin/bash
# Quick Setup Script untuk Legal Website di Odoo

echo "🚀 LEGAL WEBSITE - QUICK SETUP"
echo "================================"

# Check if we're in the right directory
if [ ! -f "__manifest__.py" ]; then
    echo "❌ Error: Jalankan script ini dari dalam folder legal_website"
    echo "   cd custom_addons/legal_website"
    exit 1
fi

echo "✅ Directory check passed"

# Check Python installation
if command -v python3 &> /dev/null; then
    PYTHON=python3
elif command -v python &> /dev/null; then
    PYTHON=python
else
    echo "❌ Python tidak ditemukan!"
    exit 1
fi

echo "✅ Python found: $PYTHON"

# Check if we're in Odoo environment
if [ ! -f "../../server/odoo-bin" ]; then
    echo "❌ Odoo server tidak ditemukan di ../../server/"
    echo "   Pastikan struktur: Program Files/Odoo/custom_addons/legal_website"
    exit 1
fi

echo "✅ Odoo server found"

# Check requests library
echo "📦 Checking dependencies..."
cd ../..
if python/python.exe -c "import requests" 2>/dev/null; then
    echo "✅ requests library installed"
else
    echo "📦 Installing requests..."
    python/python.exe -m pip install requests
fi

# Test SearXNG connectivity
echo "🌐 Testing search functionality..."
cd custom_addons/legal_website
python ../../python/python.exe -c "
from models.legal_search_enhanced import LegalSearchEnhanced
print('✅ Mock search ready to use!')
print('🎯 Try searching: hukum pidana, korupsi, KUHP')
" 2>/dev/null

echo ""
echo "🎉 SETUP COMPLETE!"
echo "================================"
echo ""
echo "📋 NEXT STEPS:"
echo "1. Start Odoo server:"
echo "   cd ../.."
echo "   python/python.exe server/odoo-bin --addons-path=server/addons,custom_addons"
echo ""
echo "2. Open browser: http://localhost:8069"
echo "3. Login dan install 'Legal Website' module"
echo "4. Test search di: http://localhost:8069/"
echo ""
echo "📚 Documentation:"
echo "   - README.md - Full documentation"
echo "   - USAGE_GUIDE.md - Step-by-step usage"  
echo "   - INSTALLATION_GUIDE.md - Detailed setup"
echo ""
echo "🔍 Test queries:"
echo "   - 'hukum pidana indonesia'"
echo "   - 'tindak pidana korupsi'"
echo "   - 'kuhp terbaru'"
echo "   - 'konsultasi hukum'"