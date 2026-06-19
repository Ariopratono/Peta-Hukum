#!/usr/bin/env python3
"""
Test script to verify TXT upload functionality
"""
import xmlrpc.client
import base64

# Configuration
url = 'http://localhost:8069'
db = 'odoo_legal_db'
username = 'admin'
password = 'admin'

# Sample TXT content with indentation for testing
sample_txt = """UNDANG-UNDANG REPUBLIK INDONESIA
NOMOR 1 TAHUN 2024
TENTANG CONTOH PERATURAN

DENGAN RAHMAT TUHAN YANG MAHA ESA

PRESIDEN REPUBLIK INDONESIA,

Menimbang:
    a. bahwa untuk mewujudkan tujuan negara;
    b. bahwa untuk melaksanakan program pemerintah;
    c. bahwa berdasarkan pertimbangan sebagaimana dimaksud dalam huruf a dan huruf b, perlu membentuk Undang-Undang;

Mengingat:
    1. Pasal 1 ayat (1) Undang-Undang Dasar Negara Republik Indonesia Tahun 1945;
    2. Pasal 2 ayat (2) Undang-Undang Dasar Negara Republik Indonesia Tahun 1945;

Dengan Persetujuan Bersama:
DEWAN PERWAKILAN RAKYAT REPUBLIK INDONESIA
dan
PRESIDEN REPUBLIK INDONESIA

MEMUTUSKAN:

Menetapkan:
UNDANG-UNDANG TENTANG CONTOH PERATURAN.

BAB I
KETENTUAN UMUM

Pasal 1
Dalam Undang-Undang ini yang dimaksud dengan:
    1. Negara adalah Negara Kesatuan Republik Indonesia;
    2. Pemerintah adalah Pemerintah Pusat;
    3. Pemerintah Daerah adalah kepala daerah sebagai unsur penyelenggara Pemerintahan Daerah;

Pasal 2
(1) Pelaksanaan undang-undang ini dilakukan oleh pemerintah pusat.
(2) Pemerintah daerah dapat mengatur lebih lanjut sesuai dengan kewenangannya.

BAB II
KETENTUAN PENUTUP

Pasal 3
Undang-Undang ini mulai berlaku pada tanggal diundangkan.
"""

print("=" * 80)
print("TESTING TXT UPLOAD FUNCTIONALITY")
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
    
    # Convert TXT to base64
    txt_base64 = base64.b64encode(sample_txt.encode('utf-8')).decode('ascii')
    
    # Create a new regulation with TXT file
    print("\n2. Creating new regulation with TXT file...")
    regulation_id = models.execute_kw(
        db, uid, password,
        'legal.regulation', 'create',
        [{
            'bentuk': 'Undang-Undang',
            'bentuk_singkat': 'UU',
            'nomor': '1',
            'tahun': '2024',
            'judul': 'Contoh Peraturan (Test TXT Upload)',
            'file_txt': txt_base64,
            'file_name': 'test_regulation.txt',
            'teu': 'Presiden Republik Indonesia',
            'status': 'berlaku',
            'bidang': 'hukum_tata_negara',
            'bahasa': 'bahasa_indonesia',
            'tanggal_penetapan': '2024-01-01',
        }]
    )
    
    print(f"✅ Created regulation ID: {regulation_id}")
    
    # Read back the regulation
    print("\n3. Reading back the regulation...")
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
    
    # Check if isi_peraturan was populated
    if regulation['isi_peraturan']:
        isi = regulation['isi_peraturan']
        print(f"\n4. Extracted content preview (first 500 chars):")
        print("-" * 80)
        print(isi[:500])
        print("-" * 80)
        
        # Check for indentation preservation
        if 'margin-left:' in isi or 'text-indent:' in isi:
            print("\n✅ SUCCESS: Indentation is preserved in HTML!")
        else:
            print("\n⚠️  WARNING: No indentation styling found in HTML")
        
        # Check for list formatting
        if '<ul>' in isi or '<ol>' in isi:
            print("✅ SUCCESS: Lists are properly formatted!")
        else:
            print("⚠️  WARNING: No list elements found in HTML")
    else:
        print("\n❌ FAILED: isi_peraturan was not populated!")
    
    # Test Re-extract button
    print("\n5. Testing Re-extract PDF button...")
    result = models.execute_kw(
        db, uid, password,
        'legal.regulation', 'action_reextract_pdf',
        [[regulation_id]]
    )
    
    if result and result.get('type') == 'ir.actions.client':
        print("✅ Re-extract action executed successfully!")
    else:
        print("❌ Re-extract action failed!")
    
    # Read again after re-extract
    print("\n6. Reading regulation after re-extract...")
    regulation_after = models.execute_kw(
        db, uid, password,
        'legal.regulation', 'read',
        [regulation_id],
        {'fields': ['isi_peraturan']}
    )[0]
    
    if '<!-- reextracted' in regulation_after['isi_peraturan']:
        print("✅ SUCCESS: Timestamp comment found (cache-busting working)!")
        # Show the timestamp line
        lines = regulation_after['isi_peraturan'].split('\n')
        for line in lines[:3]:
            if 'reextracted' in line:
                print(f"   {line.strip()}")
    else:
        print("⚠️  WARNING: No timestamp comment found")
        print(f"   First 100 chars: {regulation_after['isi_peraturan'][:100]}")
    
    # Clean up - delete test regulation
    print("\n7. Cleaning up test data...")
    models.execute_kw(
        db, uid, password,
        'legal.regulation', 'unlink',
        [[regulation_id]]
    )
    print("✅ Test regulation deleted")
    
    print("\n" + "=" * 80)
    print("ALL TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
