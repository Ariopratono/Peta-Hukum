import xmlrpc.client

url = 'http://localhost:8069'
db = 'odoo_legal_db'
username = 'admin'
password = 'admin'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

regs = models.execute_kw(db, uid, password,'legal.regulation','search_read',[[]],{'fields':['id','isi_peraturan','judul'],'limit':1,'order':'id desc'})
if not regs:
    print('No regulation found')
    exit()
rec = regs[0]
html = rec.get('isi_peraturan') or ''
print(f"ID: {rec['id']} | title: {rec['judul']} | length: {len(html)}")
print('--- First 400 chars ---')
print(html[:400])
print('\n--- Last 400 chars ---')
print(html[-400:])
