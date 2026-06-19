#!/usr/bin/env python3
"""
Script to fix additional_regulations.xml by adding required fields
"""

import re
from datetime import datetime

def fix_xml_file():
    file_path = r"c:\Program Files\Odoo\custom_addons\legal_regulations\data\additional_regulations.xml"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern untuk mendeteksi record yang tidak memiliki tanggal_penetapan
    records_to_fix = []
    
    # Temukan semua record
    record_pattern = r'<record id="([^"]+)" model="legal\.regulation">(.*?)</record>'
    records = re.findall(record_pattern, content, re.DOTALL)
    
    for record_id, record_content in records:
        # Cek apakah record sudah memiliki tanggal_penetapan
        if 'tanggal_penetapan' not in record_content:
            print(f"Record {record_id} needs tanggal_penetapan")
            
            # Cek tahun untuk menentukan tanggal yang tepat
            tahun_match = re.search(r'<field name="tahun">(\d+)</field>', record_content)
            if tahun_match:
                tahun = tahun_match.group(1)
                tanggal = f"{tahun}-12-31"
            else:
                tanggal = "2000-01-01"  # Default jika tidak ada tahun
            
            # Tambahkan field yang diperlukan sebelum tag penutup record
            additional_fields = f"""            <field name="tempat_penetapan">Jakarta</field>
            <field name="tanggal_penetapan">{tanggal}</field>
            <field name="tanggal_pengundangan">{tanggal}</field>
            <field name="bahasa">bahasa_indonesia</field>"""
            
            # Ganti record dengan versi yang diperbaiki
            old_record = f'<record id="{record_id}" model="legal.regulation">{record_content}</record>'
            
            # Cari posisi sebelum penutup tag
            insert_pos = record_content.rfind('</record>')
            if insert_pos == -1:
                insert_pos = len(record_content) - 10  # Sebelum tag penutup
            
            # Insert additional fields sebelum </record>
            new_content = record_content[:-9] + additional_fields + '\n        </record>'
            new_record = f'<record id="{record_id}" model="legal.regulation">{new_content}'
            
            content = content.replace(old_record, new_record)
    
    # Tulis file yang sudah diperbaiki
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("File additional_regulations.xml telah diperbaiki!")

if __name__ == "__main__":
    fix_xml_file()