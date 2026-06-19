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
    
    # Search for pattern: "(1)" followed by "a." later
    import re
    
    # Find Pasal 5 specifically
    pasal_5_match = re.search(r'<h5[^>]*>.*?Pasal\s+5\b.*?</h5>', text, re.IGNORECASE)
    
    if pasal_5_match:
        print("\n✓ Found Pasal 5")
        print("-" * 80)
        
        start = pasal_5_match.end()
        # Get next 4000 chars
        section = text[start:start + 4000]
        
        print("HTML Content:")
        print(section[:2000])
        print("\n...")
        
        # Check for ayat pattern
        ayat_pattern = re.findall(r'<span[^>]*>\((\d+)\)</span>', section)
        print(f"\nAyat numbers found: {ayat_pattern}")
        
        # Check for huruf pattern with indentation
        huruf_pattern = re.findall(r'<li[^>]*margin-left:\s*2rem[^>]*>.*?<span[^>]*>([a-z])\.</span>', section, re.DOTALL)
        print(f"Huruf with indentation: {huruf_pattern}")
        
        # Check for huruf pattern without indentation
        huruf_all = re.findall(r'<span[^>]*>([a-z])\.</span>', section)
        print(f"All huruf found: {huruf_all}")
        
        if huruf_pattern:
            print("\n✓✓ SUCCESS: Huruf indentation applied!")
        elif huruf_all:
            print("\n✗ Huruf found but NO indentation applied")
        else:
            print("\n? No huruf items found in this section")
    else:
        print("Pasal 5 not found")
    
else:
    print("Regulation 99 tidak ditemukan")
