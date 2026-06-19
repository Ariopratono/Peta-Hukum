#!/usr/bin/env python3
"""Re-extract all corrupted regulations via XML-RPC"""
import xmlrpc.client
import sys

url = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8069'
db = sys.argv[2] if len(sys.argv) > 2 else 'legal_db'
user = sys.argv[3] if len(sys.argv) > 3 else 'admin'
pwd = sys.argv[4] if len(sys.argv) > 4 else 'admin'

print(f"Connecting to {url}, db={db}...")
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, user, pwd, {})
print(f"Logged in as uid: {uid}")

models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# Get all regulations
regs = models.execute_kw(db, uid, pwd, 'legal.regulation', 'search_read', [[]],
    {'fields': ['judul', 'isi_peraturan', 'file_txt', 'file_docx', 'file_pdf'], 'limit': 500})
print(f"Found {len(regs)} regulations\n")

fixed = 0
for reg in regs:
    rid = reg['id']
    title = reg.get('judul', '?')
    content = reg.get('isi_peraturan') or ''
    has_file = reg.get('file_txt') or reg.get('file_docx') or reg.get('file_pdf')
    is_bad = '%PDF' in content or 'stream' in content[:300] or 'obj' in content[:100] or content.startswith('<p>Isi peraturan belum')

    if is_bad and has_file:
        print(f"  RE-EXTRACT: ID={rid} - {title}")
        try:
            models.execute_kw(db, uid, pwd, 'legal.regulation', 'action_reextract_pdf', [[rid]])
            print(f"     -> OK")
            fixed += 1
        except Exception as e:
            print(f"     -> ERROR: {e}")
    elif is_bad:
        print(f"  BAD (no file): ID={rid} - {title}")
    else:
        snippet = content[:80].replace('\n', ' ')
        print(f"  OK: ID={rid} - {title[:50]} [{snippet}...]")

print(f"\n=== DONE: Re-extracted {fixed} of {len(regs)} regulations ===")
