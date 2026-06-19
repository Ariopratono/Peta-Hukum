#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import xmlrpc.client
import re

url = 'http://localhost:8069'
db = 'odoo_legal_db'
username = 'admin'
password = 'admin'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# Find latest UU 11/2008
ids = models.execute_kw(db, uid, password, 'legal.regulation', 'search', [[('nomor','=','11'), ('tahun','=',2008)]], {'order':'id desc', 'limit':1})
reg_id = ids[0]
reg = models.execute_kw(db, uid, password, 'legal.regulation', 'read', [ids, ['isi_peraturan']])[0]
text = reg['isi_peraturan'] or ''

print("="*80)
print(f"CHECK PASAL 2 in regulation ID {reg_id}")
print("="*80)

# strip html tags to simplify
plain = re.sub(r'<[^>]+>', '', text)

# find Pasal 2 block
m = re.search(r'(?:^|\n)(Pasal\s+2\b(?!\d)[\s\S]*?)(?:\nPasal\s+3\b(?!\d)|$)', plain)
if not m:
    print("Pasal 2 block not found; scanning occurrences...")
    for mm in re.finditer(r'Pasal\s+2', plain):
        start = max(0, mm.start()-120)
        end = min(len(plain), mm.end()+200)
        context = plain[start:end]
        print("...", context.replace('\n',' ')[:300], "...")
    exit(1)
block = m.group(1)

# show snippet
print(block[:1200])

# checks
before = '💡 [Penjelasan Pasal 2]' in block.splitlines()[0]
contains = '💡 [Penjelasan Pasal 2]' in block
print("\nHas Penjelasan marker in Pasal 2 block:", contains)

# heuristic: marker should appear AFTER the first Ayat or the end of pasal
first_marker_idx = block.find('💡 [Penjelasan Pasal 2]') if contains else -1
first_ayat_idx = block.find('(1)')
print("Marker index:", first_marker_idx, "First Ayat index:", first_ayat_idx)
print("Correct order (ayat first then marker):", (first_ayat_idx == -1 or (first_marker_idx == -1 or first_ayat_idx < first_marker_idx)))
