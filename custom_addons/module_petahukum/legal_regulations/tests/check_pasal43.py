#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check specific Pasal 43 Ayat (5) Huruf h placement
"""

import xmlrpc.client
import re

# Odoo connection
url = 'http://localhost:8069'
db = 'odoo_legal_db'
username = 'admin'
password = 'admin'

# Authenticate
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})

print("="*80)
print("CHECKING PASAL 43 AYAT (5) STRUCTURE")
print("="*80)

# Get regulation
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
regulations = models.execute_kw(
    db, uid, password,
    'legal.regulation', 'search_read',
    [[('id', '=', 48)]],
    {'fields': ['isi_peraturan']}
)

isi = regulations[0]['isi_peraturan']

# Extract Pasal 43 section
import html
from html.parser import HTMLParser

class HTMLTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []
    
    def handle_data(self, data):
        self.text.append(data)
    
    def get_text(self):
        return ''.join(self.text)

extractor = HTMLTextExtractor()
extractor.feed(isi)
plain_text = extractor.get_text()

# Find Pasal 43
pasal_43_match = re.search(r'Pasal 43(.*?)(?=Pasal 44|$)', plain_text, re.DOTALL)

if pasal_43_match:
    pasal_43_text = pasal_43_match.group(1)
    
    print("\n📋 PASAL 43 CONTENT (first 3000 chars):\n")
    print("-"*80)
    print(pasal_43_text[:3000])
    print("-"*80)
    
    # Check for ayat (5)
    ayat_5_match = re.search(r'\(5\)(.*?)(?=\(6\)|\(7\)|Pasal 44|$)', pasal_43_text, re.DOTALL)
    if ayat_5_match:
        ayat_5_text = ayat_5_match.group(1)
        print("\n📋 AYAT (5) CONTENT:\n")
        print("-"*80)
        print(ayat_5_text[:2000])
        print("-"*80)
        
        # Check for huruf h
        if 'h.' in ayat_5_text:
            huruf_h_match = re.search(r'h\.(.*?)(?=i\.|Ayat \(6\)|$)', ayat_5_text, re.DOTALL)
            if huruf_h_match:
                huruf_h_text = huruf_h_match.group(1)
                print("\n📋 HURUF h CONTENT:\n")
                print("-"*80)
                print(huruf_h_text[:500])
                print("-"*80)
                
                # Check for penjelasan marker
                if '💡' in huruf_h_text and '[Penjelasan Huruf h]' in huruf_h_text:
                    print("\n✅ PENJELASAN HURUF h FOUND!")
                    penjelasan_match = re.search(r'💡 \[Penjelasan Huruf h\]:(.*?)(?=i\.|Ayat|$)', huruf_h_text, re.DOTALL)
                    if penjelasan_match:
                        print(f"\nPenjelasan content: {penjelasan_match.group(1)[:200]}...")
                else:
                    print("\n❌ NO PENJELASAN HURUF h FOUND")
    
    # Count all penjelasan in Pasal 43
    penjelasan_count = pasal_43_text.count('💡')
    ayat_penjelasan = re.findall(r'💡 \[Penjelasan Ayat \((\d+)\)\]', pasal_43_text)
    huruf_penjelasan = re.findall(r'💡 \[Penjelasan Huruf ([a-z])\]', pasal_43_text)
    
    print(f"\n\n📊 STATISTICS FOR PASAL 43:")
    print(f"   Total 💡 markers: {penjelasan_count}")
    print(f"   Ayat penjelasan: {len(ayat_penjelasan)} → Ayat: {ayat_penjelasan}")
    print(f"   Huruf penjelasan: {len(huruf_penjelasan)} → Huruf: {huruf_penjelasan}")
    
else:
    print("❌ Pasal 43 not found!")

print("\n" + "="*80)
