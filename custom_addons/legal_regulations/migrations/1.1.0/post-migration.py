# -*- coding: utf-8 -*-

def migrate(cr, version):
    """
    Migration script untuk memastikan kompatibilitas field baru
    """
    # Check if new fields exist, if not create them
    new_fields = [
        ('isi_peraturan', 'TEXT'),
        ('kata_kunci', 'TEXT'),
        ('ringkasan', 'TEXT'),
        ('hierarchy_order', 'INTEGER DEFAULT 999')
    ]
    
    for field_name, field_type in new_fields:
        # Check if field exists
        cr.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='legal_regulation' AND column_name=%s
        """, (field_name,))
        
        if not cr.fetchone():
            # Add field if it doesn't exist
            cr.execute(f"ALTER TABLE legal_regulation ADD COLUMN {field_name} {field_type}")
            print(f"Added missing field: {field_name}")
    
    # Set default values for existing records
    cr.execute("""
        UPDATE legal_regulation 
        SET hierarchy_order = 999 
        WHERE hierarchy_order IS NULL
    """)
    
    cr.execute("""
        UPDATE legal_regulation 
        SET isi_peraturan = '<p>Isi peraturan belum tersedia</p>' 
        WHERE isi_peraturan IS NULL OR isi_peraturan = ''
    """)
    
    cr.execute("""
        UPDATE legal_regulation 
        SET kata_kunci = '' 
        WHERE kata_kunci IS NULL
    """)
    
    cr.execute("""
        UPDATE legal_regulation 
        SET ringkasan = 'Ringkasan belum tersedia' 
        WHERE ringkasan IS NULL OR ringkasan = ''
    """)