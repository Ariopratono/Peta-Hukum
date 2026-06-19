import xmlrpc.client

url = 'http://localhost:8069'
db = 'odoo_legal_db'
username = 'admin'
password = 'admin'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})

models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# Get latest regulation (ID will vary)
regulations = models.execute_kw(db, uid, password,
    'legal.regulation', 'search_read',
    [[('nomor', '=', '11'), ('tahun', '=', 2008)]],
    {'fields': ['isi_peraturan'], 'limit': 1})

if regulations:
    regulation = regulations[0]
    text = regulation['isi_peraturan']
    
    # Find Penjelasan Umum section in HTML
    start = text.find('[PENJELASAN UMUM]:')
    if start != -1:
        # Find the end (where closing div is)
        end = text.find('</div></div>', start)
        if end != -1:
            penjelasan_section = text[start:end + 12]  # +12 for </div></div>
            
            # Count <br><br> tags (paragraph separators)
            br_count = penjelasan_section.count('<br><br>')
            
            print("=" * 80)
            print("PENJELASAN UMUM - PARAGRAPH ANALYSIS")
            print("=" * 80)
            print(f"Total <br><br> tags (paragraph separators): {br_count}")
            print(f"Estimated paragraphs: {br_count + 1}")
            print()
            
            # Show first 1500 characters to see structure
            print("First 1500 characters of Penjelasan Umum HTML:")
            print("-" * 80)
            print(penjelasan_section[:1500])
            print()
            print("..." if len(penjelasan_section) > 1500 else "")
            print()
            
            # Show last 800 characters
            print("Last 800 characters:")
            print("-" * 80)
            print(penjelasan_section[-800:])
            print()
            
            # Extract just text content (remove HTML tags) to show readable format
            import re
            text_only = re.sub(r'<[^>]+>', '', penjelasan_section)
            text_only = text_only.replace('[PENJELASAN UMUM]:', '').strip()
            
            # Split by double newlines to show paragraphs
            paragraphs = [p.strip() for p in text_only.split('\n\n') if p.strip()]
            
            print("=" * 80)
            print("TEXT-ONLY PARAGRAPHS (first 3):")
            print("=" * 80)
            for i, para in enumerate(paragraphs[:3], 1):
                print(f"\nParagraph {i}:")
                print("-" * 40)
                print(para[:300] + "..." if len(para) > 300 else para)
            
            if len(paragraphs) > 3:
                print(f"\n... and {len(paragraphs) - 3} more paragraphs")
            
            print(f"\nTotal paragraphs found: {len(paragraphs)}")
            
    else:
        print("Penjelasan Umum tidak ditemukan")
else:
    print("Regulation UU 11/2008 tidak ditemukan")
