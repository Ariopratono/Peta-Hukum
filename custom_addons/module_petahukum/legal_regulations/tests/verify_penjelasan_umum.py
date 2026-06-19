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

# Get latest regulation (ID 94)
regulation_id = 94

regulation = models.execute_kw(db, uid, password,
    'legal.regulation', 'read', [[regulation_id]], 
    {'fields': ['nomor', 'judul', 'isi_peraturan']})

if regulation:
    reg = regulation[0]
    isi = reg['isi_peraturan']
    
    print(f"Regulation: {reg['nomor']} - {reg['judul']}")
    print(f"Total length: {len(isi)} characters")
    print("=" * 80)
    
    # Check for Penjelasan Umum section
    if 'PENJELASAN UMUM' in isi:
        print("✓ PENJELASAN UMUM section found!")
        
        # Find its position
        umum_pos = isi.find('PENJELASAN UMUM')
        menimbang_pos = isi.find('Menimbang')
        
        print(f"  Position of PENJELASAN UMUM: {umum_pos}")
        print(f"  Position of Menimbang: {menimbang_pos}")
        
        if menimbang_pos > 0 and umum_pos < menimbang_pos:
            print("  ✓ PENJELASAN UMUM appears BEFORE Menimbang")
        else:
            print("  ✗ PENJELASAN UMUM appears AFTER Menimbang")
        
        # Show snippet around Penjelasan Umum
        print("\n" + "=" * 80)
        print("Content around PENJELASAN UMUM:")
        print("=" * 80)
        start = max(0, umum_pos - 100)
        end = min(len(isi), umum_pos + 500)
        print(isi[start:end])
        
    else:
        print("✗ PENJELASAN UMUM section NOT found")
        
        # Check if the content exists
        if 'Pemanfaatan Teknologi Informasi' in isi:
            print("  BUT the actual content exists in text")
            pos = isi.find('Pemanfaatan Teknologi Informasi')
            print(f"  Position: {pos}")
            print("\nContent around it:")
            start = max(0, pos - 100)
            end = min(len(isi), pos + 300)
            print(isi[start:end])
        else:
            print("  Content also not found in text")
    
    print("\n" + "=" * 80)
    print("First 1000 characters of regulation:")
    print("=" * 80)
    print(isi[:1000])
