import xmlrpc.client, re

url = 'http://localhost:8069'
db = 'odoo_legal_db'
username = 'admin'
password = 'admin'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# Use latest regulation (assume created by simple_test)
reg = models.execute_kw(db, uid, password,'legal.regulation','search_read',[[]],{'fields':['id','isi_peraturan'],'limit':1,'order':'id desc'})
if not reg:
    print('No regulation found')
    exit()
rec = reg[0]
text = rec['isi_peraturan'] or ''
print(f"Using regulation ID {rec['id']}")

pasal12 = re.search(r'<h5[^>]*><strong>Pasal 12</strong></h5>', text)
if not pasal12:
    print('Pasal 12 header not found')
    exit()
start = pasal12.end()
segment = text[start:start+8000]  # take chunk
# Narrow to Ayat (2)
ayat2 = re.search(r'<span[^>]*>\(2\)</span>', segment)
if not ayat2:
    print('Ayat (2) not found in extracted segment')
    print(segment[:1500])
    exit()
seg2 = segment[ayat2.start():]
# Find huruf c.
huruf_c = re.search(r'<span[^>]*>c\.</span>', seg2)
if not huruf_c:
    print('Huruf c. not found after Ayat (2)')
    print(seg2[:2000])
    exit()
sub = seg2[huruf_c.start():huruf_c.start()+3000]
print('='*80)
print('Pasal 12 Ayat (2) Huruf c RAW HTML snippet (first 2000 chars)')
print('='*80)
print(sub[:2000])
# Count numeric list items following huruf c
numeric_items = re.findall(r'<span[^>]*>(\d+)\.</span>', sub)
print(f"\nNumeric items detected under huruf c: {numeric_items}")
# Check indentation style
indented_numeric = re.findall(r'margin-left:\s*(?:3\.5rem|4rem)[^>]*>.*?<span[^>]*>\d+\.</span>', sub, re.DOTALL)
print(f"Indented numeric items count: {len(indented_numeric)}")
