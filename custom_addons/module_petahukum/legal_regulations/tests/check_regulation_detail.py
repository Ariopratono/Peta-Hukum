#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check Regulation Detail - Verifikasi isi regulation dengan detail
"""

import xmlrpc.client

# Odoo connection
url = 'http://localhost:8069'
db = 'odoo_legal_db'
username = 'admin'
password = 'admin'

# Authenticate
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})

if not uid:
    print("❌ Authentication failed!")
    exit(1)

print(f"✅ Authenticated as user ID: {uid}\n")

# Get regulation
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
regulations = models.execute_kw(
    db, uid, password,
    'legal.regulation', 'search_read',
    [[('id', '=', 44)]],
    {'fields': ['id', 'nomor', 'tahun', 'judul', 'isi_peraturan', 'file_txt', 'file_docx', 'file_pdf']}
)

if not regulations:
    print("❌ Regulation ID 44 not found!")
    exit(1)

reg = regulations[0]

print("=" * 80)
print("REGULATION DETAIL - ID 44")
print("=" * 80)
print(f"ID: {reg['id']}")
print(f"Nomor: {reg['nomor']}")
print(f"Tahun: {reg['tahun']}")
print(f"Judul: {reg['judul']}")
print()
print(f"Has file_txt: {bool(reg.get('file_txt'))}")
print(f"Has file_docx: {bool(reg.get('file_docx'))}")
print(f"Has file_pdf: {bool(reg.get('file_pdf'))}")
print()

isi = reg.get('isi_peraturan', '')
if isi:
    print(f"Isi Peraturan Length: {len(isi)} characters")
    print()
    
    # Check for penjelasan markers
    has_icon = '💡' in isi
    has_penjelasan_text = '[Penjelasan' in isi
    
    print(f"Has 💡 icon: {has_icon}")
    print(f"Has [Penjelasan] text: {has_penjelasan_text}")
    print()
    
    if has_icon and has_penjelasan_text:
        print("✅ PENJELASAN MARKERS FOUND!")
        
        # Count markers
        icon_count = isi.count('💡')
        penjelasan_pasal = isi.count('[Penjelasan Pasal')
        penjelasan_ayat = isi.count('[Penjelasan Ayat')
        penjelasan_huruf = isi.count('[Penjelasan Huruf')
        
        print(f"\nStatistics:")
        print(f"  💡 Icons: {icon_count}")
        print(f"  Penjelasan Pasal: {penjelasan_pasal}")
        print(f"  Penjelasan Ayat: {penjelasan_ayat}")
        print(f"  Penjelasan Huruf: {penjelasan_huruf}")
    else:
        print("⚠️ NO PENJELASAN MARKERS FOUND!")
    
    print()
    print("=" * 80)
    print("FIRST 1000 CHARACTERS OF ISI PERATURAN:")
    print("=" * 80)
    print(isi[:1000])
    print("=" * 80)
    
    # Save to file for inspection
    output_file = r'C:\Program Files\Odoo\custom_addons\legal_regulations\tests\regulation_44_content.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(isi)
    print(f"\n✅ Full content saved to: {output_file}")
    print("   Open this file in browser to see the complete regulation with penjelasan")
    
else:
    print("❌ ISI PERATURAN IS EMPTY!")

print()
print("=" * 80)
print("TO VIEW IN ODOO WEB INTERFACE:")
print("=" * 80)
print(f"1. Open: http://localhost:8069/web#id={reg['id']}&model=legal.regulation&view_type=form")
print(f"2. Look for field 'Isi Peraturan' (it's an HTML field)")
print(f"3. You should see 💡 [Penjelasan ...] markers")
print("=" * 80)
