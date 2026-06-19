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
print(f"CHECK PASAL 2 PLACEMENT in regulation ID {reg_id}")
print("="*80)

# strip html tags to simplify
plain = re.sub(r'<[^>]+>', '\n', text)
plain = re.sub(r'\n+', '\n', plain)

# Find Pasal 2 section (before BAB II or Pasal 3)
# Look for exact "Pasal 2" not "Pasal 20", "Pasal 27", etc.
match = re.search(r'(Pasal 2\n[^\n]*Undang-Undang ini berlaku.*?)(?=\nBAB|Pasal 3)', plain, re.DOTALL)
if match:
    block = match.group(1)
    lines = block.split('\n')
    
    # Show snippet
    print("\nPASAL 2 BLOCK (first 30 lines):")
    print("="*80)
    for i, line in enumerate(lines[:30], 1):
        print(f"{i:2}. {line[:100]}")
    
    print("\n" + "="*80)
    
    # Check order
    has_penjelasan = '💡 [Penjelasan Pasal 2]:' in block
    print(f"\nHas Penjelasan marker: {has_penjelasan}")
    
    if has_penjelasan:
        # Find positions
        pasal_idx = block.find('Pasal 2')
        bab_idx = block.find('BAB')
        penjelasan_idx = block.find('💡 [Penjelasan Pasal 2]:')
        
        print(f"\nPosition analysis:")
        print(f"  Pasal 2 starts at: {pasal_idx}")
        print(f"  Penjelasan at: {penjelasan_idx}")
        print(f"  BAB header at: {bab_idx if bab_idx != -1 else 'not in block'}")
        
        # Check if penjelasan is BEFORE BAB (it should NOT be)
        if bab_idx != -1 and penjelasan_idx != -1:
            if penjelasan_idx < bab_idx:
                print(f"\n❌ BUG: Penjelasan appears BEFORE BAB header!")
                print(f"   Penjelasan should be after Pasal 2 content but BEFORE BAB II")
            else:
                print(f"\n✓ Order looks wrong - penjelasan is AFTER BAB (should be before BAB)")
        
        # Show context around penjelasan
        context_start = max(0, penjelasan_idx - 200)
        context_end = min(len(block), penjelasan_idx + 300)
        print(f"\nContext around Penjelasan:")
        print("="*80)
        print(block[context_start:context_end])
        print("="*80)
else:
    print("Pasal 2 block not found with expected pattern")
