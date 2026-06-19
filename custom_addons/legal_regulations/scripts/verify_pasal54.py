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
    print('No regulation found matching 11/2008')
    exit(0)
reg_id = ids[0]
record = models.execute_kw(DB, uid, PASSWORD, 'legal.regulation', 'read', [ids, ['isi_peraturan']])[0]
html = record['isi_peraturan'] or ''

# Simple check: look for Pasal 54 block and penjelasan marker
pasal54_section = None
pattern = re.compile(r'(Pasal\s+54)(.*?)Pasal\s+55', re.DOTALL)
match = pattern.search(html)
if match:
    pasal54_section = match.group(2)
else:
    # fallback: grab tail from Pasal 54 to end
    pattern_tail = re.compile(r'(Pasal\s+54)(.*)$', re.DOTALL)
    match_tail = pattern_tail.search(html)
    if match_tail:
        pasal54_section = match_tail.group(2)

if not pasal54_section:
    print('Pasal 54 section not found in HTML output.')
    exit(0)

# Count penjelasan markers within Pasal 54
penjelasan_markers = re.findall(r'Penjelasan\s+Pasal\s+54|Penjelasan\s+Ayat', pasal54_section)

# Check that footer line was not captured
footer_present = re.search(r'TAMBAHAN\s+LEMBARAN\s+NEGARA\s+REPUBLIK\s+INDONESIA', pasal54_section)

print('Pasal 54 Penjelasan markers count:', len(penjelasan_markers))
print('Footer present inside Pasal 54 penjelasan area:', bool(footer_present))

# Expectations:
# - Either 0 penjelasan markers (if the official explanation was "Cukup jelas")
# - Footer should NOT be present within penjelasan area.
if len(penjelasan_markers) == 0 and not footer_present:
    print('[OK] Pasal 54 has no penjelasan and footer not captured.')
elif footer_present:
    print('[FAIL] Footer text was captured as penjelasan for Pasal 54.')
else:
    print('[WARN] Pasal 54 has penjelasan markers; verify if this is expected.')
