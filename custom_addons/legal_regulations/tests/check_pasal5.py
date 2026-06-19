#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check Pasal 5 structure
"""

import xmlrpc.client
import re

url = 'http://localhost:8069'
db = 'odoo_legal_db'
username = 'admin'
password = 'admin'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})

models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
# get latest UU 11/2008
ids = models.execute_kw(
    db, uid, password,
    'legal.regulation', 'search',
    [[('nomor','=','11'), ('tahun','=',2008)]],
    {'order': 'id desc', 'limit': 1}
)
reg = models.execute_kw(
    db, uid, password,
    'legal.regulation', 'read',
    [ids],
    {'fields': ['isi_peraturan']}
)

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
extractor.feed(reg[0]['isi_peraturan'])
plain_text = extractor.get_text()

# Find Pasal 5 in BAB III section (the one about Informasi Elektronik)
bab3_match = re.search(r'BAB III.*?INFORMASI.*?(Pasal 5.*?Pasal 6)', plain_text, re.DOTALL | re.IGNORECASE)
if not bab3_match:
    # Fallback: find Pasal 5 after "KETENTUAN UMUM"
    pasal5_match = re.search(r'KETENTUAN UMUM.*?(Pasal 5.*?Pasal 6)', plain_text, re.DOTALL)
else:
    pasal5_match = bab3_match

if pasal5_match:
    if hasattr(pasal5_match, 'group'):
        if pasal5_match.lastindex and pasal5_match.lastindex >= 1:
            pasal5_text = pasal5_match.group(1)
        else:
            pasal5_text = pasal5_match.group(0)
    else:
        pasal5_text = "NOT FOUND"
    
    print("="*80)
    print("PASAL 5 CONTENT")
    print("="*80)
    print(pasal5_text[:1500])
    print("="*80)
    
    has_pasal_penjelasan = 'Penjelasan Pasal 5' in pasal5_text
    has_ayat_penjelasan = 'Penjelasan Ayat' in pasal5_text
    has_huruf_penjelasan = 'Penjelasan Huruf' in pasal5_text
    
    print(f"\nHas Penjelasan Pasal 5: {has_pasal_penjelasan}")
    print(f"Has Penjelasan Ayat: {has_ayat_penjelasan}")
    print(f"Has Penjelasan Huruf a: {has_huruf_penjelasan}")
    
    if 'Penjelasan Pasal 5' in pasal5_text:
        penjelasan_match = re.search(r'💡 \[Penjelasan Pasal 5\]:(.*?)(?=Ayat|\(1\)|$)', pasal5_text, re.DOTALL)
        if penjelasan_match:
            print(f"\nPenjelasan Pasal 5 content (first 300 chars):")
            print(penjelasan_match.group(1)[:300])
    
    if 'Penjelasan Huruf' in pasal5_text:
        huruf_match = re.search(r'💡 \[Penjelasan Huruf a\]:(.*?)(?=Huruf b|\(2\)|$)', pasal5_text, re.DOTALL)
        if huruf_match:
            print(f"\nPenjelasan Huruf a content (first 300 chars):")
            print(huruf_match.group(1)[:300])
else:
    print("Pasal 5 not found!")
