#!/usr/bin/env python3
"""
Test re-extract regulation yang sudah ada untuk melihat perubahan
"""
import xmlrpc.client

# Configuration
url = 'http://localhost:8069'
db = 'odoo_legal_db'
username = 'admin'
password = 'admin'

print("=" * 80)
print("RE-EXTRACT EXISTING REGULATION TO SEE CHANGES")
print("=" * 80)

try:
    # Connect to Odoo
    print("\n1. Connecting to Odoo...")
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(db, username, password, {})
    
    if not uid:
        print("❌ Authentication failed!")
        exit(1)
    
    print(f"✅ Authenticated as user ID: {uid}")
    
    # Get models proxy
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
    
    # Find regulation with TXT file
    print("\n2. Searching for regulations with TXT file...")
    regulation_ids = models.execute_kw(
        db, uid, password,
        'legal.regulation', 'search',
        [[('file_txt', '!=', False)]],
        {'limit': 5}
    )
    
    if not regulation_ids:
        print("❌ No regulations with TXT file found!")
        print("💡 Please upload a TXT file first via Odoo web interface")
        exit(1)
    
    print(f"✅ Found {len(regulation_ids)} regulation(s) with TXT file")
    print(f"   IDs: {regulation_ids}")
    
    # Read first regulation
    regulation_id = regulation_ids[0]
    print(f"\n3. Reading regulation ID {regulation_id}...")
    regulation = models.execute_kw(
        db, uid, password,
        'legal.regulation', 'read',
        [regulation_id],
        {'fields': ['judul', 'file_txt', 'isi_peraturan']}
    )[0]
    
    print(f"   Judul: {regulation['judul']}")
    print(f"   Has TXT: {bool(regulation['file_txt'])}")
    print(f"   Has isi_peraturan: {bool(regulation['isi_peraturan'])}")
    
    # Check current content
    if regulation['isi_peraturan']:
        isi = regulation['isi_peraturan']
        has_penjelasan = '💡' in isi or '[Penjelasan' in isi
        print(f"   Has Penjelasan markers: {has_penjelasan}")
        
        if not has_penjelasan:
            print("\n⚠️  WARNING: No penjelasan markers found in current content!")
            print("   This means the re-extraction hasn't been run yet.")
    
    # Re-extract using the button action
    print(f"\n4. Triggering re-extraction for regulation ID {regulation_id}...")
    try:
        result = models.execute_kw(
            db, uid, password,
            'legal.regulation', 'action_reextract_pdf',
            [[regulation_id]]
        )
        print(f"✅ Re-extraction triggered successfully!")
        print(f"   Result: {result}")
    except Exception as e:
        print(f"❌ Re-extraction failed: {e}")
    
    # Read again after re-extraction
    print(f"\n5. Reading regulation again after re-extraction...")
    regulation_after = models.execute_kw(
        db, uid, password,
        'legal.regulation', 'read',
        [regulation_id],
        {'fields': ['isi_peraturan']}
    )[0]
    
    if regulation_after['isi_peraturan']:
        isi_after = regulation_after['isi_peraturan']
        has_penjelasan_after = '💡' in isi_after or '[Penjelasan' in isi_after
        
        print(f"   Has Penjelasan markers NOW: {has_penjelasan_after}")
        
        if has_penjelasan_after:
            print("\n✅ SUCCESS! Penjelasan markers found!")
            
            # Count occurrences
            count_icon = isi_after.count('💡')
            count_text = isi_after.count('[Penjelasan')
            print(f"   💡 Icon count: {count_icon}")
            print(f"   [Penjelasan] count: {count_text}")
            
            # Show sample
            print("\n6. Sample content with penjelasan:")
            print("-" * 80)
            # Find and show first penjelasan
            import re
            penjelasan_matches = re.findall(r'💡 \[Penjelasan[^\]]+\]:[^\<]+', isi_after)
            for i, match in enumerate(penjelasan_matches[:3], 1):
                print(f"\n{i}. {match[:150]}...")
            print("-" * 80)
        else:
            print("\n⚠️  Still no penjelasan markers found after re-extraction!")
            print("   Checking if 'Penjelasan' section exists in source...")
            
            # Check raw TXT content
            import base64
            if regulation['file_txt']:
                txt_bytes = base64.b64decode(regulation['file_txt'])
                txt_content = txt_bytes.decode('utf-8', errors='ignore')
                has_penjelasan_section = 'Penjelasan' in txt_content
                print(f"   'Penjelasan' in source TXT: {has_penjelasan_section}")
                
                if not has_penjelasan_section:
                    print("\n💡 TIP: The TXT file doesn't have a 'Penjelasan' section!")
                    print("   Please upload a TXT with this format:")
                    print("""
   Pasal 13
   (1) Ayat text...
   
   Penjelasan
   
   Pasal 13
   Penjelasan text for pasal...
   
   Penjelasan (1): Penjelasan for ayat 1...
                    """)
    
    print("\n" + "=" * 80)
    print(f"💡 To see in browser: {url}/web#id={regulation_id}&model=legal.regulation&view_type=form")
    print("=" * 80)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
