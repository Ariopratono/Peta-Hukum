#!/bin/bash

# Install Script untuk Legal Website Module

echo "=== Installing Legal Website Module ==="

# Check if we're in Odoo directory
if [ ! -f "odoo-bin" ]; then
    echo "Error: Script harus dijalankan dari direktori Odoo server"
    exit 1
fi

# Install Python dependencies
echo "Installing Python dependencies..."

# Check if pip is available
if command -v pip3 &> /dev/null; then
    PIP=pip3
elif command -v pip &> /dev/null; then
    PIP=pip
else
    echo "Error: pip tidak ditemukan. Install Python pip terlebih dahulu."
    exit 1
fi

# Install requests library for SearXNG integration
$PIP install requests --user

echo "Python dependencies installed successfully."

# Check if custom_addons directory exists
if [ ! -d "custom_addons" ]; then
    echo "Creating custom_addons directory..."
    mkdir custom_addons
fi

# Copy module if it's not already there
if [ -d "../legal_website" ] && [ ! -d "custom_addons/legal_website" ]; then
    echo "Copying legal_website module to custom_addons..."
    cp -r ../legal_website custom_addons/
fi

echo ""
echo "=== Installation Complete ==="
echo ""
echo "Next steps:"
echo "1. Start Odoo server:"
echo "   ./odoo-bin -c odoo.conf --addons-path=addons,custom_addons"
echo ""
echo "2. Login ke Odoo dan update Apps list"
echo "3. Install module 'Legal Website' dari Apps menu"  
echo "4. Konfigurasi SearXNG di Website Hukum > Pencarian > Konfigurasi"
echo ""
echo "Default SearXNG instance: https://search.brave4u.com"
echo "Atau gunakan SearXNG instance lain yang tersedia."
echo ""
echo "Untuk dokumentasi lengkap, baca file README.md di folder module."