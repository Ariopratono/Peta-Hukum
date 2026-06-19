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
regulation_id = 93

regulation = models.execute_kw(db, uid, password,
    'legal.regulation', 'read', [[regulation_id]], 
    {'fields': ['isi_peraturan']})

if regulation:
    isi = regulation[0]['isi_peraturan']
    
    # Find Penjelasan Umum section
    start_marker = 'PENJELASAN UMUM]:</div><div style="margin-top: 4px;">'
    end_marker = '</div></div>'
    
    start = isi.find(start_marker)
    if start > 0:
        start = start + len(start_marker)
        # Find the closing tags
        end = isi.find(end_marker, start)
        
        if end > start:
            penjelasan_umum_content = isi[start:end]
            
            print("Penjelasan Umum Content:")
            print("=" * 100)
            print(penjelasan_umum_content)
            print("=" * 100)
            print(f"\nLength: {len(penjelasan_umum_content)} characters")
            
            # Check if it ends with expected text
            expected_endings = [
                "pemanfaatan teknologi informasi menjadi tidak optimal",
                "teknologi informasi menjadi tidak optimal",
                "menjadi tidak optimal"
            ]
            
            found = False
            for ending in expected_endings:
                if ending.lower() in penjelasan_umum_content.lower():
                    print(f"\n✓ Found expected ending: '{ending}'")
                    found = True
                    break
            
            if not found:
                print("\n✗ Expected ending NOT found!")
                print(f"Last 200 chars: ...{penjelasan_umum_content[-200:]}")
        else:
            print("Could not find end marker")
    else:
        print("Could not find Penjelasan Umum content")
