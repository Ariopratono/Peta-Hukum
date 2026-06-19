#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import xmlrpc.client, re

url = 'http://localhost:8069'
db = 'odoo_legal_db'
username = 'admin'
password = 'admin'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# get latest UU 11/2008
ids = models.execute_kw(db, uid, password, 'legal.regulation', 'search', [[('nomor','=','11'), ('tahun','=',2008)]], {'order':'id desc', 'limit':1})
reg = models.execute_kw(db, uid, password, 'legal.regulation', 'read', [ids, ['isi_peraturan']])[0]
html = reg['isi_peraturan'] or ''

print("="*80)
print("DETAILED CHECK: Pasal 11 Ayat (1)")
print("="*80)

# Find Pasal 11 in HTML
pasal11_match = re.search(r'(Pasal 11.*?)(?=Pasal 12|$)', html, re.DOTALL)
if pasal11_match:
    block = pasal11_match.group(1)
    
    # Show raw HTML snippet around ayat (1)
    ayat1_start = block.find('(1)')
    if ayat1_start != -1:
        snippet = block[ayat1_start:ayat1_start+2000]
        print("\nHTML snippet after '(1)':")
        print(snippet[:1500])
        
        # Check for penjelasan markers
        has_penjelasan_ayat = '💡 [Penjelasan Ayat (1)]:' in block
        has_penjelasan_huruf = '💡 [Penjelasan Huruf' in block
        
        print("\n" + "="*80)
        print("Analysis:")
        print(f"  Has Penjelasan Ayat (1): {has_penjelasan_ayat}")
        print(f"  Has Penjelasan Huruf: {has_penjelasan_huruf}")
        
        if has_penjelasan_ayat:
            ayat_penj_pos = block.find('💡 [Penjelasan Ayat (1)]:')
            # Find first huruf (a., b., etc)
            huruf_a_pos = block.find('a.', ayat1_start)
            
            print(f"\nPositions relative to start of block:")
            print(f"  Ayat (1) at: {ayat1_start}")
            print(f"  First huruf 'a.' at: {huruf_a_pos}")
            print(f"  Penjelasan Ayat (1) at: {ayat_penj_pos}")
            
            if huruf_a_pos != -1 and ayat_penj_pos != -1:
                if ayat_penj_pos < huruf_a_pos:
                    print("\n✓ CORRECT: Penjelasan Ayat appears BEFORE huruf a")
                else:
                    print("\n❌ BUG: Penjelasan Ayat appears AFTER huruf a")
                    print(f"   Distance: {ayat_penj_pos - huruf_a_pos} chars after huruf")

print("\n" + "="*80)
print("DETAILED CHECK: Pasal 14")
print("="*80)

pasal14_match = re.search(r'(Pasal 14.*?)(?=Pasal 15|$)', html, re.DOTALL)
if pasal14_match:
    block = pasal14_match.group(1)
    
    # Pasal 14 might not have ayat, check for direct huruf under pasal
    snippet = block[:1500]
    print("\nHTML snippet start of Pasal 14:")
    print(snippet)
    
    has_penjelasan_pasal = '💡 [Penjelasan Pasal 14]:' in block
    has_penjelasan_huruf = '💡 [Penjelasan Huruf' in block
    
    print("\n" + "="*80)
    print("Analysis:")
    print(f"  Has Penjelasan Pasal 14: {has_penjelasan_pasal}")
    print(f"  Has Penjelasan Huruf: {has_penjelasan_huruf}")
    
    if has_penjelasan_pasal:
        pasal_penj_pos = block.find('💡 [Penjelasan Pasal 14]:')
        huruf_a_pos = block.find('a.')
        
        print(f"\nPositions:")
        print(f"  First huruf 'a.' at: {huruf_a_pos}")
        print(f"  Penjelasan Pasal at: {pasal_penj_pos}")
        
        if huruf_a_pos != -1 and pasal_penj_pos != -1:
            if pasal_penj_pos < huruf_a_pos:
                print("\n✓ CORRECT: Penjelasan Pasal appears BEFORE huruf a")
            else:
                print("\n❌ BUG: Penjelasan Pasal appears AFTER huruf a")
                print(f"   Distance: {pasal_penj_pos - huruf_a_pos} chars after huruf")
