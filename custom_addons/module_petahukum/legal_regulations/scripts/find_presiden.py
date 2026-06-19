import xmlrpc.client
import re

URL = 'http://localhost:8069'
DB = 'odoo_legal_db'
USERNAME = 'admin'
PASSWORD = 'admin'

common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
uid = common.authenticate(DB, USERNAME, PASSWORD, {})
models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')

# Fetch latest regulation record
ids = models.execute_kw(DB, uid, PASSWORD, 'legal.regulation', 'search', [[('judul', 'ilike', 'INFORMASI')]], {'order': 'id desc', 'limit': 1})
if not ids:
    print('No regulation found')
    exit(0)

reg_id = ids[0]
record = models.execute_kw(DB, uid, PASSWORD, 'legal.regulation', 'read', [ids, ['isi_peraturan']])[0]
html = record['isi_peraturan'] or ''

# Find context around "PRESIDEN REPUBLIK INDONESIA"
pattern = r'.{100}PRESIDEN\s+REPUBLIK\s+INDONESIA.{200}'
matches = re.findall(pattern, html, re.DOTALL | re.IGNORECASE)

print('Context around "PRESIDEN REPUBLIK INDONESIA":')
print('=' * 80)
for i, match in enumerate(matches):
    print(f'\nMatch {i+1}:')
    print(match)
    print('-' * 80)
