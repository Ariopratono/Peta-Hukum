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
plain = re.sub(r'<[^>]+>', '', html)
plain = re.sub(r'\n+', '\n', plain)

def check_pasal(pasal_num):
    m = re.search(r'(Pasal\s+'+str(pasal_num)+r'[\s\S]*?)(?=\nPasal\s+'+str(pasal_num+1)+r'|\nBAB|$)', plain)
    if not m:
        print(f'Pasal {pasal_num} not found')
        return
    block = m.group(1)
    print('\n'+'='*60)
    print(f'Pasal {pasal_num} snippet:')
    print(block[:1000])
    # locate ayat 1
    ayat1_idx = block.find('(1)')
    penjelasan_ayat_idx = block.find('💡 [Penjelasan Ayat (1)]:')
    first_huruf_idx = None
    # find first huruf like 'a.' newline or 'a.' after '(1)'
    hm = re.search(r'\n\s*a\.', block)
    if hm:
        first_huruf_idx = hm.start()
    print('\nPositions:')
    print('  ayat1_idx:', ayat1_idx)
    print('  penjelasan_ayat_idx:', penjelasan_ayat_idx)
    print('  first_huruf_idx:', first_huruf_idx)
    if penjelasan_ayat_idx != -1:
        if first_huruf_idx and penjelasan_ayat_idx > first_huruf_idx:
            print('❌ Penjelasan Ayat appears AFTER first Huruf (WRONG)')
        else:
            print('✓ Penjelasan Ayat is before Huruf (OK)')
    else:
        print('No Penjelasan Ayat found')

check_pasal(11)
check_pasal(14)
