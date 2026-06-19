#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import xmlrpc.client
import base64
import os
import time

# Odoo connection
url = 'http://localhost:8069'
db = 'odoo_legal_db'
username = 'admin'
password = 'admin'

print("Connecting to Odoo...")

# Authenticate
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})

if not uid:
    print("Authentication failed!")
    exit(1)

print(f"Authenticated as user ID: {uid}")

# Connect to models
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# File path
file_path = r'C:\Users\Ario\Downloads\UU Nomor 11 Tahun 2008.txt'

if not os.path.exists(file_path):
    print(f"File not found: {file_path}")
    exit(1)

print(f"Reading file: {file_path}")

# Read and encode file
with open(file_path, 'rb') as f:
    file_content = f.read()

file_base64 = base64.b64encode(file_content).decode('utf-8')
file_size_kb = len(file_content) / 1024

print(f"File size: {file_size_kb:.2f} KB")

# Delete old test regulation if exists
print("Cleaning up old test data...")
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
    print(f"Deleted {len(old_ids)} old regulation(s)")
else:
    print("No old data found")

# Create new regulation
print("Creating new regulation with TXT file...")

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
    print(f"Created regulation ID: {new_id}")
except Exception as e:
    print(f"Failed to create regulation: {e}")
    exit(1)

# Wait a moment for processing
print("Waiting for text extraction...")
time.sleep(3)

# Retrieve and verify
print("Verifying regulation content...")

regulation = models.execute_kw(
    db, uid, password,
    'legal.regulation', 'search_read',
    [[('id', '=', new_id)]],
    {'fields': ['id', 'nomor', 'tahun', 'judul', 'isi_peraturan']}
)[0]

print(f"ID: {regulation['id']}")
print(f"Nomor: {regulation['nomor']}/{regulation['tahun']}")
print(f"Judul: {regulation['judul']}")

isi = regulation.get('isi_peraturan', '')
print(f"Isi Peraturan Length: {len(isi)} characters")

# Check for penjelasan markers
print("Checking for Penjelasan integration...")

penjelasan_pasal_count = isi.count('[Penjelasan Pasal')
penjelasan_ayat_count = isi.count('[Penjelasan Ayat')
penjelasan_huruf_count = isi.count('[Penjelasan Huruf')

print(f"Penjelasan Pasal: {penjelasan_pasal_count}")
print(f"Penjelasan Ayat: {penjelasan_ayat_count}")
print(f"Penjelasan Huruf: {penjelasan_huruf_count}")
print(f"Total: {penjelasan_pasal_count + penjelasan_ayat_count + penjelasan_huruf_count}")

print()
print("TEST COMPLETE!")
print()
print(f"View at: http://localhost:8069/web#id={new_id}&model=legal.regulation&view_type=form")
