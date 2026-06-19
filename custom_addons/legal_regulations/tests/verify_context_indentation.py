import xmlrpc.client
import re

url = 'http://localhost:8069'
db = 'odoo_legal_db'
username = 'admin'
password = 'admin'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})

models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# Get regulation 100
regulations = models.execute_kw(db, uid, password,
    'legal.regulation', 'search_read',
    [[('id', '=', 100)]],
    {'fields': ['isi_peraturan'], 'limit': 1})

if regulations:
    text = regulations[0]['isi_peraturan']
    
    print("=" * 80)
    print("CHECKING MENIMBANG SECTION (should have NO indentation)")
    print("=" * 80)
    
    # Find Menimbang section
    menimbang_match = re.search(r'<h6[^>]*>.*?Menimbang:.*?</h6>', text, re.IGNORECASE)
    if menimbang_match:
        start = menimbang_match.end()
        # Get 1500 chars after Menimbang
        section = text[start:start + 1500]
        
        print("\nMenimbang section HTML:")
        print(section[:1000])
        
        # Check for huruf with indentation (should be NONE)
        huruf_with_indent = re.findall(r'margin-left:\s*2rem[^>]*>.*?<span[^>]*>([a-z])\.</span>', section, re.DOTALL)
        huruf_all = re.findall(r'<span[^>]*>([a-z])\.</span>', section)
        
        print(f"\n→ Huruf in Menimbang with indentation: {huruf_with_indent} (should be EMPTY)")
        print(f"→ Total huruf in Menimbang: {huruf_all}")
        
        if not huruf_with_indent:
            print("\n✓ CORRECT: Menimbang huruf items have NO indentation")
        else:
            print("\n✗ WRONG: Menimbang huruf items have indentation (should not)")
    
    print("\n" + "=" * 80)
    print("CHECKING PASAL 5 SECTION (should have indentation)")
    print("=" * 80)
    
    # Find Pasal 5
    pasal_5_match = re.search(r'<h5[^>]*>.*?Pasal\s+5\b.*?</h5>', text, re.IGNORECASE)
    if pasal_5_match:
        start = pasal_5_match.end()
        section = text[start:start + 2000]
        
        print("\nPasal 5 section HTML:")
        print(section[:1000])
        
        # Check for huruf with indentation (should be PRESENT)
        huruf_with_indent = re.findall(r'margin-left:\s*2rem[^>]*>.*?<span[^>]*>([a-z])\.</span>', section, re.DOTALL)
        huruf_all = re.findall(r'<span[^>]*>([a-z])\.</span>', section)
        
        print(f"\n→ Huruf in Pasal 5 with indentation: {huruf_with_indent} (should be ['a', 'b'])")
        print(f"→ Total huruf in Pasal 5: {huruf_all}")
        
        if huruf_with_indent:
            print("\n✓ CORRECT: Pasal 5 huruf items HAVE indentation")
        else:
            print("\n✗ WRONG: Pasal 5 huruf items have NO indentation (should have)")
    
    print("\n" + "=" * 80)
    print("FINAL RESULT")
    print("=" * 80)
    
else:
    print("Regulation 100 tidak ditemukan")
