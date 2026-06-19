import xmlrpc.client

url = 'http://localhost:8069'
db = 'odoo19'
username = 'admin'
password = 'admin'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})

models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# Get all regulations
regulations = models.execute_kw(db, uid, password,
    'legal.regulation', 'search_read',
    [[]],
    {'fields': ['id', 'nomor', 'judul'], 'limit': 10, 'order': 'id desc'})

print("Latest regulations:")
for reg in regulations:
    print(f"ID: {reg['id']}, Nomor: {reg.get('nomor', 'N/A')}, Judul: {reg.get('judul', 'N/A')[:50]}")
