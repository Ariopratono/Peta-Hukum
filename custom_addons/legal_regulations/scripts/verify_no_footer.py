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

# Extract content after Pasal 54 (last Pasal)
pasal54_match = re.search(r'(Pasal\s+54.*?)($|Pasal\s+\d+)', html, re.DOTALL | re.IGNORECASE)
if pasal54_match:
    # Get text after Pasal 54
    after_pasal54_idx = pasal54_match.end(1)
    after_pasal54_text = html[after_pasal54_idx:after_pasal54_idx+2000]  # Check next 2000 chars
    print(f'Checking content AFTER Pasal 54 (next 2000 chars)...')
    check_text = after_pasal54_text
else:
    print('Could not find Pasal 54, checking entire document...')
    check_text = html

# Check for unwanted footer text
unwanted_patterns = [
    r'Agar\s+setiap\s+orang\s+mengetahuinya',
    r'memerintahkan\s+pengundangan',
    r'Disahkan\s+di\s+Jakarta\s+pada\s+tanggal',
    r'Diundangkan\s+di\s+Jakarta\s+pada\s+tanggal',
    r'PRESIDEN\s+REPUBLIK\s+INDONESIA,',
    r'DR\.\s+H\.\s+SUSILO\s+BAMBANG\s+YUDHOYONO',
    r'MENTERI\s+HUKUM\s+DAN\s*HAK\s+ASASI\s+MANUSIA',
    r'ANDI\s+MATTALATA',
    r'LEMBARAN\s+NEGARA\s+REPUBLIK\s+INDONESIA\s+TAHUN\s+2008'
]

print('Checking for unwanted footer text...')
print('=' * 80)

found_issues = []
for pattern in unwanted_patterns:
    matches = re.findall(pattern, check_text, re.IGNORECASE)
    if matches:
        found_issues.append({
            'pattern': pattern,
            'matches': matches
        })
        print(f'✗ FOUND: {pattern}')
        print(f'  Matches: {matches}')
    else:
        print(f'✓ OK: {pattern} not found')

print('=' * 80)

if found_issues:
    print(f'\n❌ FAIL: Found {len(found_issues)} unwanted footer patterns')
else:
    print('\n✅ PASS: No unwanted footer text found!')

# Also check content length and structure
print(f'\nContent Length: {len(html)} characters')
print(f'Regulation ID: {reg_id}')
