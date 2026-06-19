# -*- coding: utf-8 -*-

def pre_init_hook(cr):
    """Hook yang dijalankan sebelum install module"""
    print("[LEGAL_REGULATIONS] Starting compatibility check...")
    
    # Check if table exists
    cr.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_name='legal_regulation'
    """)
    
    if cr.fetchone():
        print("[LEGAL_REGULATIONS] Table exists, checking fields...")
        
        # Add missing fields if needed
        required_fields = [
            ('isi_peraturan', 'TEXT'),
            ('kata_kunci', 'TEXT'),
            ('ringkasan', 'TEXT'),
            ('hierarchy_order', 'INTEGER DEFAULT 999')
        ]
        
        for field_name, field_type in required_fields:
            cr.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='legal_regulation' AND column_name=%s
            """, (field_name,))
            
            if not cr.fetchone():
                try:
                    cr.execute(f"ALTER TABLE legal_regulation ADD COLUMN {field_name} {field_type}")
                    print(f"[LEGAL_REGULATIONS] Added field: {field_name}")
                except Exception as e:
                    print(f"[LEGAL_REGULATIONS] Warning: Could not add {field_name}: {e}")
    else:
        print("[LEGAL_REGULATIONS] New installation, table will be created.")

def post_init_hook(cr, registry):
    """Hook yang dijalankan setelah install module"""
    print("[LEGAL_REGULATIONS] Running post-install compatibility updates...")
    
    # Set default values for existing records
    try:
        cr.execute("""
            UPDATE legal_regulation 
            SET hierarchy_order = 999 
            WHERE hierarchy_order IS NULL
        """)
        
        cr.execute("""
            UPDATE legal_regulation 
            SET isi_peraturan = COALESCE(isi_peraturan, '<p>Isi peraturan belum tersedia</p>')
            WHERE isi_peraturan IS NULL OR isi_peraturan = ''
        """)
        
        cr.execute("""
            UPDATE legal_regulation 
            SET kata_kunci = COALESCE(kata_kunci, '')
            WHERE kata_kunci IS NULL
        """)
        
        cr.execute("""
            UPDATE legal_regulation 
            SET ringkasan = COALESCE(ringkasan, 'Ringkasan belum tersedia')
            WHERE ringkasan IS NULL OR ringkasan = ''
        """)
        
        print("[LEGAL_REGULATIONS] Post-install compatibility updates completed.")
        
    except Exception as e:
        print(f"[LEGAL_REGULATIONS] Warning during post-install: {e}")