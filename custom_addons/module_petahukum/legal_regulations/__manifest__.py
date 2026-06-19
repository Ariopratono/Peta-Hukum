{
    'name': 'Legal Regulations Management',
    'version': '1.2.1',
    'category': 'Legal/Regulations',
    'summary': 'Manajemen peraturan hukum dan perundang-undangan Indonesia',
    'description': """
        Legal Regulations Management v1.1.0
        ====================================
        
        Modul untuk mengelola peraturan hukum dan perundang-undangan dengan fitur:
        - Tambah peraturan hukum
        - Kategori dokumen perundang-undangan
        - Informasi lengkap peraturan (nomor, bentuk, tahun, dll)
        - Status dan validitas peraturan
        - Pencarian dan filter peraturan
        - Manajemen peraturan (nomor, bentuk, tahun, status).
        - Fitur Konsolidasi: Menggabungkan UU Induk dengan UU Perubahan (Revisi) secara otomatis.
        - Relasi Antar Pasal: Deteksi otomatis referensi pasal (Cross-referencing).
        - Manajemen Penjelasan: Integrasi teks penjelasan ke dalam batang tubuh.
        - Support parsing dokumen hukum (.txt & .docx).
    """,
    'author': 'Legal Team',
    'license': 'LGPL-3',
    'depends': ['base', 'web', 'mail','portal'],
    'data': [
        'security/legal_regulation_security.xml',
        'security/ir.model.access.csv',
        'data/regulation_types.xml',
        'data/compatible_regulations.xml',
        'data/additional_regulations.xml',
        'views/legal_regulation_views.xml',
        'views/legal_regulation_views_minimal.xml',
        'views/consolidation_views.xml',
        'views/menu_views.xml',
        'views/system_control_views.xml',
    ],
    'pre_init_hook': 'pre_init_hook',
    'post_init_hook': 'post_init_hook',
    'external_dependencies': {
        'python': [],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}