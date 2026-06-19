#!/usr/bin/env python3
"""
Test specific regulation ID 43 yang punya Penjelasan
"""
import xmlrpc.client
import re

# Configuration
url = 'http://localhost:8069'
db = 'odoo_legal_db'
username = 'admin'
password = 'admin'

regulation_id = 43  # The one we created with penjelasan

print("=" * 80)
print(f"CHECKING REGULATION ID {regulation_id}")
print("=" * 80)

try:
    # Connect
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(db, username, password, {})
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
    
    print(f"\n1. Reading regulation ID {regulation_id}...")
    regulation = models.execute_kw(
        db, uid, password,
        'legal.regulation', 'read',
        [regulation_id],
        {'fields': ['judul', 'isi_peraturan']}
    )[0]
    
    print(f"   Judul: {regulation['judul']}")
    
    if regulation['isi_peraturan']:
        isi = regulation['isi_peraturan']
        
        print(f"\n2. Checking for Penjelasan markers...")
        has_icon = '💡' in isi
        has_text = '[Penjelasan' in isi
        
        print(f"   Has 💡 icon: {has_icon}")
        print(f"   Has [Penjelasan] text: {has_text}")
        
        if has_icon or has_text:
            print("\n✅ SUCCESS! Penjelasan markers ARE present!")
            
            # Count
            count_icon = isi.count('💡')
            count_text = isi.count('[Penjelasan')
            print(f"   💡 Icon count: {count_icon}")
            print(f"   [Penjelasan] text count: {count_text}")
            
            # Extract samples
            print("\n3. Sample Penjelasan found:")
            print("-" * 80)
            penjelasan_matches = re.findall(r'💡 \[Penjelasan[^\]]+\]:[^<]+', isi)
            for i, match in enumerate(penjelasan_matches, 1):
                clean_match = match.replace('\n', ' ').strip()
                print(f"\n{i}. {clean_match[:200]}...")
            print("-" * 80)
            
            # Show structure around Pasal 13
            print("\n4. Content around 'Pasal 13':")
            print("-" * 80)
            pasal_13_idx = isi.find('Pasal 13')
            if pasal_13_idx > 0:
                snippet = isi[pasal_13_idx:pasal_13_idx+1000]
                # Remove HTML tags for readability
                import html
                from html.parser import HTMLParser
                
                class MLStripper(HTMLParser):
                    def __init__(self):
                        super().__init__()
                        self.reset()
                        self.fed = []
                    def handle_data(self, d):
                        self.fed.append(d)
                    def get_data(self):
                        return ''.join(self.fed)
                
                s = MLStripper()
                s.feed(snippet)
                text_only = s.get_data()
                print(text_only[:500])
            print("-" * 80)
            
        else:
            print("\n❌ No Penjelasan markers found!")
            print("\n   Showing first 1000 chars of content:")
            print("-" * 80)
            print(isi[:1000])
            print("-" * 80)
    else:
        print("\n❌ No isi_peraturan content!")
    
    print(f"\n💡 View in browser: {url}/web#id={regulation_id}&model=legal.regulation&view_type=form")
    print("=" * 80)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
