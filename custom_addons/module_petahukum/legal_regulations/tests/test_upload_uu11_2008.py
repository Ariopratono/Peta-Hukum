#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Upload UU Nomor 11 Tahun 2008 dengan Penjelasan yang Kompleks
"""

import xmlrpc.client
import base64
import os
import sys

# Odoo connection
url = 'http://localhost:8069'
db = 'odoo_legal_db'
username = 'dimasramadhan98@gmail.com'
password = 'admin'

print("=" * 80)
print("TEST UPLOAD UU NOMOR 11 TAHUN 2008")
print("=" * 80)

# Authenticate
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})

if not uid:
    print("❌ Authentication failed!")
    sys.exit(1)

print(f"✅ Authenticated as user ID: {uid}\n")

# Connect to models
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# File path - adjust to user's download folder
file_path = r'C:\Users\Ario\Downloads\UU Nomor 11 Tahun 2008.txt'

if not os.path.exists(file_path):
    print(f"❌ File not found: {file_path}")
    print("Please adjust the file_path variable in the script")
    sys.exit(1)

print(f"1. Reading file: {file_path}")

# Read and encode file
with open(file_path, 'rb') as f:
    file_content = f.read()

file_base64 = base64.b64encode(file_content).decode('utf-8')
file_size_kb = len(file_content) / 1024

print(f"   File size: {file_size_kb:.2f} KB")
print(f"   ✅ File encoded to base64\n")

# Check if file contains "Penjelasan" section
file_text = file_content.decode('utf-8', errors='ignore')
has_penjelasan = 'PENJELASAN ATAS' in file_text or 'Penjelasan' in file_text

print(f"2. Checking file structure...")
print(f"   Has 'PENJELASAN ATAS' section: {has_penjelasan}")

if has_penjelasan:
    # Count Pasal mentions in Penjelasan
    penjelasan_start = max(
        file_text.find('PENJELASAN ATAS') if 'PENJELASAN ATAS' in file_text else -1,
        file_text.find('Penjelasan\n') if 'Penjelasan\n' in file_text else -1
    )
    if penjelasan_start > 0:
        penjelasan_section = file_text[penjelasan_start:]
        pasal_count = penjelasan_section.count('Pasal ')
        ayat_count = penjelasan_section.count('Ayat (')
        huruf_count = penjelasan_section.count('Huruf ')
        print(f"   Penjelasan section contains:")
        print(f"   - ~{pasal_count} Pasal references")
        print(f"   - ~{ayat_count} Ayat references")
        print(f"   - ~{huruf_count} Huruf references")

print()

# Delete old test regulation if exists
print("3. Cleaning up old test data...")
old_ids = models.execute_kw(
    db, uid, password,
    'legal.regulation', 'search',
    [[('nomor', '=', '11'), ('tahun', '=', 2008)]]
)

if old_ids:
    models.execute_kw(
        db, uid, password,
        'legal.regulation', 'unlink',
        [old_ids]
    )
    print(f"   ✅ Deleted {len(old_ids)} old regulation(s)\n")
else:
    print(f"   No old data found\n")

# Create new regulation
print("4. Creating new regulation with TXT file...")

vals = {
    'tipe_dokumen': 'undang_undang',
    'nomor': '11',
    'tahun': 2008,
    'judul': 'INFORMASI DAN TRANSAKSI ELEKTRONIK',
    'bentuk': 'Undang-Undang',
    'bentuk_singkat': 'UU',
    'tanggal_penetapan': '2008-04-21',
    'tanggal_pengundangan': '2008-04-21',
    'status': 'berlaku',
    'file_txt': file_base64,
}

try:
    new_id = models.execute_kw(
        db, uid, password,
        'legal.regulation', 'create',
        [vals]
    )
    print(f"   ✅ Created regulation ID: {new_id}\n")
except Exception as e:
    print(f"   ❌ Failed to create regulation: {e}")
    sys.exit(1)

# Wait a moment for processing
print("5. Waiting for text extraction...")
import time
time.sleep(3)

# Retrieve and verify
print("\n6. Verifying regulation content...")

regulation = models.execute_kw(
    db, uid, password,
    'legal.regulation', 'search_read',
    [[('id', '=', new_id)]],
    {'fields': ['id', 'nomor', 'tahun', 'judul', 'isi_peraturan']}
)[0]

print(f"   ID: {regulation['id']}")
print(f"   Nomor: {regulation['nomor']}/{regulation['tahun']}")
print(f"   Judul: {regulation['judul']}")

isi = regulation.get('isi_peraturan', '')
print(f"   Isi Peraturan Length: {len(isi)} characters\n")

# Check for penjelasan markers
print("7. Checking for Penjelasan integration...")

has_icon = '💡' in isi
has_penjelasan_text = '[Penjelasan' in isi

print(f"   Has 💡 icon: {has_icon}")
print(f"   Has [Penjelasan] text: {has_penjelasan_text}")

if has_icon and has_penjelasan_text:
    print("\n   ✅ PENJELASAN MARKERS FOUND!")
    
    # Count different types
    icon_count = isi.count('💡')
    penjelasan_pasal_count = isi.count('[Penjelasan Pasal')
    penjelasan_ayat_count = isi.count('[Penjelasan Ayat')
    penjelasan_huruf_count = isi.count('[Penjelasan Huruf')
    
    print(f"\n   📊 Statistics:")
    print(f"      💡 Icons total: {icon_count}")
    print(f"      Penjelasan Pasal: {penjelasan_pasal_count}")
    print(f"      Penjelasan Ayat: {penjelasan_ayat_count}")
    print(f"      Penjelasan Huruf: {penjelasan_huruf_count}")
    
    # Find sample penjelasan
    print(f"\n   📝 Sample Penjelasan entries:")
    print("   " + "-" * 76)
    
    import re
    samples = re.findall(r'💡 \[Penjelasan[^\]]+\]:[^\n]{0,100}', isi)
    for idx, sample in enumerate(samples[:5], 1):
        print(f"   {idx}. {sample}...")
    
    if len(samples) > 5:
        print(f"   ... and {len(samples) - 5} more")
    
    print("   " + "-" * 76)
    
else:
    print("\n   ⚠️ NO PENJELASAN MARKERS FOUND!")
    print("   This might indicate:")
    print("   - Parser didn't detect Penjelasan section")
    print("   - Format mismatch between TXT and parser expectations")
    print("   - Module not upgraded yet")

# Save HTML for inspection
output_file = r'C:\Program Files\Odoo\custom_addons\legal_regulations\tests\uu_11_2008_result.html'
try:
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>UU Nomor 11 Tahun 2008 - Test Result</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 40px; line-height: 1.6; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; margin-bottom: 30px; }}
        .content {{ max-width: 900px; margin: 0 auto; }}
        .penjelasan {{ background: #e8f4f8; border-left: 4px solid #3498db; padding: 10px; margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>UU Nomor 11 Tahun 2008</h1>
        <p>INFORMASI DAN TRANSAKSI ELEKTRONIK</p>
    </div>
    <div class="content">
        {isi}
    </div>
</body>
</html>""")
    print(f"\n   💾 HTML saved to: {output_file}")
    print(f"      Open this file in browser to see the complete regulation")
except Exception as e:
    print(f"\n   ⚠️ Could not save HTML file: {e}")

print()
print("=" * 80)
print("✅ TEST COMPLETE!")
print("=" * 80)
print()
print("To view in Odoo web interface:")
print(f"   http://localhost:8069/web#id={new_id}&model=legal.regulation&view_type=form")
print()
print("Next steps:")
print("   1. Open the URL above in your browser")
print("   2. Scroll to 'Isi Peraturan' field")
print("   3. Look for 💡 [Penjelasan ...] markers")
print("   4. Or open the HTML file in your browser")
print()
print("=" * 80)
