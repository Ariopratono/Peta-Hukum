import xmlrpc.client

url = 'http://localhost:8069'
db = 'odoo19'
username = 'admin'
password = 'admin'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})

models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# Get regulation 94
regulation = models.execute_kw(db, uid, password,
    'legal.regulation', 'search_read',
    [[('id', '=', 94)]],
    {'fields': ['formatted_text']})

if regulation:
    text = regulation[0]['formatted_text']
    
    # Find Penjelasan Umum section
    start = text.find('[PENJELASAN UMUM]:')
    if start != -1:
        # Find the end (where Menimbang starts)
        end = text.find('<h6 class="mt-3 mb-2"><strong>Menimbang:</strong></h6>', start)
        if end != -1:
            penjelasan_section = text[start:end]
            
            # Extract just the text content (between > and <)
            import re
            # Get content between the div tags
            content_match = re.search(r'<div class="penjelasan-content">(.*?)</div></div>', penjelasan_section, re.DOTALL)
            if content_match:
                content = content_match.group(1)
                print("=" * 80)
                print("ISI PENJELASAN UMUM (HTML):")
                print("=" * 80)
                print(content[:2000])  # First 2000 chars
                print("\n...")
                print(content[-500:])  # Last 500 chars
                print("\n" + "=" * 80)
                print(f"Total panjang konten: {len(content)} karakter")
                
                # Check for <br> or <p> tags
                br_count = content.count('<br')
                p_count = content.count('<p>')
                print(f"Jumlah <br> tags: {br_count}")
                print(f"Jumlah <p> tags: {p_count}")
    else:
        print("Penjelasan Umum tidak ditemukan")
else:
    print("Regulation 94 tidak ditemukan")
