import xmlrpc.client

url = 'http://localhost:8069'
db = 'odoo_legal_db'
username = 'admin'
password = 'admin'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})

models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# Get regulation 99
regulations = models.execute_kw(db, uid, password,
    'legal.regulation', 'search_read',
    [[('id', '=', 99)]],
    {'fields': ['isi_peraturan'], 'limit': 1})

if regulations:
    regulation = regulations[0]
    text = regulation['isi_peraturan']
    
    # Find a section with Ayat and huruf (e.g., Pasal 5)
    pasal_5 = text.find('Pasal 5')
    if pasal_5 != -1:
        # Get 3000 characters after Pasal 5
        section = text[pasal_5:pasal_5 + 3000]
        
        print("=" * 80)
        print("PASAL 5 - AYAT DAN HURUF INDENTATION CHECK")
        print("=" * 80)
        print(section)
        print()
        
        # Count indented huruf items
        import re
        huruf_with_indent = re.findall(r'margin-left: 2rem[^>]*>[^<]*<span[^>]*>[a-z]\.</span>', section)
        huruf_without_indent = re.findall(r'<span[^>]*>[a-z]\.</span>', section)
        
        print("=" * 80)
        print(f"Huruf items with margin-left:2rem indentation: {len(huruf_with_indent)}")
        print(f"Total huruf items found: {len(huruf_without_indent)}")
        
        # Check ayat numbering
        ayat_items = re.findall(r'<span[^>]*>\(\d+\)</span>', section)
        print(f"Ayat items found: {len(ayat_items)}")
        
        if huruf_with_indent:
            print("\n✓ Huruf indentation applied successfully!")
        else:
            print("\n✗ No huruf indentation found")
else:
    print("Regulation 99 tidak ditemukan")
