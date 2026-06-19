import xmlrpc.client

# Connection details
url = "http://localhost:8069"
db = "odoo_legal_db"
username = "admin"
password = "admin"

# Connect
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# Get latest regulation
regulation_id = 94

regulation = models.execute_kw(db, uid, password,
    'legal.regulation', 'read', [[regulation_id]], 
    {'fields': ['isi_peraturan']})

if regulation:
    isi = regulation[0]['isi_peraturan']
    
    # Find where Penjelasan Umum ends
    start_marker = 'PENJELASAN UMUM]:</div><div style="margin-top: 4px;">'
    
    start = isi.find(start_marker)
    if start > 0:
        start = start + len(start_marker)
        # Find the closing tags
        end = isi.find('</div></div>', start)
        
        if end > start:
            # Get some context after the closing tag
            after_box = isi[end:end+500]
            
            print("Content immediately after Penjelasan Umum box:")
            print("=" * 100)
            print(after_box)
            print("=" * 100)
            
            # Check if Menimbang appears right after
            if 'Menimbang' in after_box[:200]:
                print("\n✓ Menimbang appears right after Penjelasan Umum box")
            else:
                print("\n✗ Menimbang NOT found right after box")
                
            # Also check the end of Penjelasan Umum content
            penjelasan_content = isi[start:end]
            print(f"\n\nLast 300 chars of Penjelasan Umum:")
            print("=" * 100)
            print(penjelasan_content[-300:])
            print("=" * 100)
            
            if 'tidak optimal' in penjelasan_content[-100:]:
                print("\n✓ Penjelasan Umum ends correctly with 'tidak optimal'")
            else:
                print("\n✗ Ending might be cut off")
