#!/usr/bin/env python3
"""
Script untuk upload TXT dengan Penjelasan dan test hasilnya
"""
import xmlrpc.client
import base64
from pathlib import Path

# Configuration
url = 'http://localhost:8069'
db = 'odoo_legal_db'
username = 'admin'
password = 'admin'

print("=" * 80)
print("UPLOAD TXT DENGAN PENJELASAN - FULL TEST")
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
    
    # Delete old test regulations if exist
    print("\n2. Cleaning up old test regulations...")
    old_ids = models.execute_kw(
        db, uid, password,
        'legal.regulation', 'search',
        [[('judul', 'ilike', 'Test Upload dengan Struktur')]]
    )
    if old_ids:
        models.execute_kw(
            db, uid, password,
            'legal.regulation', 'unlink',
            [old_ids]
        )
        print(f"✅ Deleted {len(old_ids)} old test regulation(s)")
    else:
        print("   No old test regulations to delete")
    
    # Read TXT file with Penjelasan
    txt_path = Path(__file__).parent / 'contoh_dengan_penjelasan.txt'
    if not txt_path.exists():
        print(f"❌ File not found: {txt_path}")
        exit(1)
    
    print(f"\n3. Reading file: {txt_path.name}")
    txt_content = txt_path.read_bytes()
    txt_base64 = base64.b64encode(txt_content).decode('ascii')
    print(f"   File size: {len(txt_content)} bytes")
    
    # Verify file has Penjelasan section
    txt_text = txt_content.decode('utf-8', errors='ignore')
    if 'Penjelasan' not in txt_text:
        print("⚠️  WARNING: File doesn't have 'Penjelasan' section!")
    else:
        print("✅ File contains 'Penjelasan' section")
    
    # Create new regulation
    print("\n4. Creating new regulation with TXT file...")
    regulation_id = models.execute_kw(
        db, uid, password,
        'legal.regulation', 'create',
        [{
            'bentuk': 'Undang-Undang',
            'bentuk_singkat': 'UU',
            'nomor': '99',
            'tahun': '2024',
            'judul': 'Test Upload dengan Struktur Pasal-Ayat-Penjelasan (FINAL)',
            'file_txt': txt_base64,
            'file_name': 'contoh_dengan_penjelasan.txt',
            'teu': 'Presiden Republik Indonesia',
            'status': 'berlaku',
            'bidang': 'hukum_tata_negara',
            'bahasa': 'bahasa_indonesia',
            'tanggal_penetapan': '2024-01-01',
        }]
    )
    
    print(f"✅ Created regulation ID: {regulation_id}")
    
    # Wait a moment for processing
    import time
    print("\n5. Waiting for processing...")
    time.sleep(2)
    
    # Read back and verify
    print("\n6. Verifying regulation content...")
    regulation = models.execute_kw(
        db, uid, password,
        'legal.regulation', 'read',
        [regulation_id],
        {'fields': ['judul', 'nomor', 'tahun', 'file_txt', 'file_size', 'isi_peraturan']}
    )[0]
    
    print(f"   Nomor: {regulation['nomor']}")
    print(f"   Tahun: {regulation['tahun']}")
    print(f"   Judul: {regulation['judul']}")
    print(f"   File Size: {regulation['file_size']} KB")
    print(f"   Has TXT file: {bool(regulation['file_txt'])}")
    print(f"   Has isi_peraturan: {bool(regulation['isi_peraturan'])}")
    
    # Check for Penjelasan markers
    if regulation['isi_peraturan']:
        isi = regulation['isi_peraturan']
        
        print("\n7. Checking for Penjelasan integration...")
        
        has_icon = '💡' in isi
        has_bracket = '[Penjelasan' in isi
        
        print(f"   Has 💡 icon: {has_icon}")
        print(f"   Has [Penjelasan] text: {has_bracket}")
        
        if has_icon or has_bracket:
            print("\n✅ SUCCESS! Penjelasan has been integrated!")
            
            # Count occurrences
            count_icon = isi.count('💡')
            count_bracket = isi.count('[Penjelasan')
            count_pasal = isi.count('[Penjelasan Pasal')
            count_ayat = isi.count('[Penjelasan Ayat')
            count_huruf = isi.count('[Penjelasan Huruf')
            
            print(f"\n   📊 Statistics:")
            print(f"      💡 Icons: {count_icon}")
            print(f"      [Penjelasan] total: {count_bracket}")
            print(f"      ├─ Pasal: {count_pasal}")
            print(f"      ├─ Ayat: {count_ayat}")
            print(f"      └─ Huruf: {count_huruf}")
            
            # Extract and show samples
            import re
            print(f"\n   📝 Sample Penjelasan found:")
            print("   " + "-" * 76)
            
            penjelasan_matches = re.findall(r'💡 \[Penjelasan[^\]]+\]:[^<]+', isi)
            for i, match in enumerate(penjelasan_matches[:5], 1):
                clean = match.replace('\n', ' ').strip()
                if len(clean) > 100:
                    clean = clean[:100] + '...'
                print(f"   {i}. {clean}")
            
            print("   " + "-" * 76)
            
            # Save HTML for inspection
            output_path = Path(__file__).parent / f'regulation_{regulation_id}_final.html'
            output_path.write_text(isi, encoding='utf-8')
            print(f"\n   💾 HTML saved to: {output_path}")
            
        else:
            print("\n❌ FAILED: No Penjelasan markers found!")
            print("\n   First 500 chars of content:")
            print("   " + "-" * 76)
            print("   " + isi[:500].replace('\n', ' '))
            print("   " + "-" * 76)
    else:
        print("\n❌ FAILED: isi_peraturan is empty!")
    
    # Final instructions
    print("\n" + "=" * 80)
    print("✅ DONE! To view the result:")
    print("=" * 80)
    print(f"\n1. Open in browser:")
    print(f"   {url}/web#id={regulation_id}&model=legal.regulation&view_type=form")
    print(f"\n2. Scroll to 'Isi Peraturan' field")
    print(f"3. Look for 💡 [Penjelasan ...] text")
    print(f"\n4. Or open the saved HTML file in browser:")
    print(f"   {Path(__file__).parent / f'regulation_{regulation_id}_final.html'}")
    print("\n" + "=" * 80)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
