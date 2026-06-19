#!/usr/bin/env python3
"""
Test upload TXT dengan struktur Pasal-Ayat-Penjelasan ke Odoo
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
print("TESTING TXT UPLOAD DENGAN STRUKTUR PASAL-AYAT-PENJELASAN")
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
    
    # Read TXT file dengan penjelasan
    txt_path = Path(__file__).parent / 'contoh_dengan_penjelasan.txt'
    if not txt_path.exists():
        print(f"❌ File tidak ditemukan: {txt_path}")
        exit(1)
    
    print(f"\n2. Membaca file: {txt_path.name}")
    txt_content = txt_path.read_bytes()
    txt_base64 = base64.b64encode(txt_content).decode('ascii')
    
    # Create regulation with TXT file
    print("\n3. Creating regulation dengan TXT (Pasal + Penjelasan)...")
    regulation_id = models.execute_kw(
        db, uid, password,
        'legal.regulation', 'create',
        [{
            'bentuk': 'Undang-Undang',
            'bentuk_singkat': 'UU',
            'nomor': '1',
            'tahun': '2024',
            'judul': 'Test Upload dengan Struktur Pasal-Ayat-Penjelasan',
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
    
    # Read back the regulation
    print("\n4. Reading back the regulation...")
    regulation = models.execute_kw(
        db, uid, password,
        'legal.regulation', 'read',
        [regulation_id],
        {'fields': ['judul', 'file_txt', 'file_size', 'isi_peraturan']}
    )[0]
    
    print(f"   Judul: {regulation['judul']}")
    print(f"   File Size: {regulation['file_size']} KB")
    print(f"   Has TXT file: {bool(regulation['file_txt'])}")
    print(f"   Has isi_peraturan: {bool(regulation['isi_peraturan'])}")
    
    # Check for structured HTML
    if regulation['isi_peraturan']:
        isi = regulation['isi_peraturan']
        
        print(f"\n5. Checking structured HTML...")
        
        checks = {
            'TOC (Daftar Isi)': 'toc-sidebar' in isi or 'Daftar Isi' in isi,
            'Pasal Cards': 'pasal-card' in isi,
            'Accordion': 'pasal-header' in isi,
            'Ayat Structure': 'ayat' in isi and '<strong>(' in isi,
            'Penjelasan Umum': 'penjelasan-umum' in isi or 'Penjelasan Pasal' in isi,
            'Penjelasan Ayat': 'Penjelasan ayat' in isi,
            'CSS Styling': '<style>' in isi,
        }
        
        for check_name, check_result in checks.items():
            status = "✅" if check_result else "❌"
            print(f"   {status} {check_name}")
        
        # Count pasals
        pasal_count = isi.count('pasal-card')
        print(f"\n   📊 Total Pasal Cards: {pasal_count}")
        
        # Save HTML for inspection
        output_path = Path(__file__).parent / f'regulation_{regulation_id}_output.html'
        output_path.write_text(isi, encoding='utf-8')
        print(f"   💾 HTML saved to: {output_path}")
        
        # Show preview
        print(f"\n6. Preview (first 500 chars):")
        print("-" * 80)
        print(isi[:500])
        print("-" * 80)
    else:
        print("\n❌ FAILED: isi_peraturan was not populated!")
    
    print(f"\n✅ SUCCESS! Regulation ID {regulation_id} created with structured HTML")
    print(f"\n💡 Tip: Buka di browser Odoo untuk melihat:")
    print(f"   {url}/web#id={regulation_id}&model=legal.regulation&view_type=form")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
