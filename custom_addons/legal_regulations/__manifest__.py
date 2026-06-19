{
    'name': 'Legal Regulations Management',
    'version': '1.2.1',
    'category': 'Legal/Regulations',
    'summary': 'Manajemen peraturan hukum dan perundang-undangan Indonesia',
    'description': """
        Legal Regulations Management v1.2.1
        ====================================
        
        Modul untuk mengelola peraturan hukum dan perundang-undangan dengan fitur:
        - Tambah peraturan hukum
        - Kategori dokumen perundang-undangan
        - Informasi lengkap peraturan (nomor, bentuk, tahun, dll)
        - Status dan validitas peraturan
        - Pencarian dan filter peraturan
        - BARU: Fitur Konsolidasi - Gabungkan UU Induk + UU Perubahan secara otomatis
    """,
    'author': 'Legal Team',
    'license': 'LGPL-3',
    'depends': ['base', 'web', 'mail'],
    'data': [
        'security/legal_regulation_security.xml',
        'security/ir.model.access.csv',
        # 'data/regulation_types.xml',  # Commented out - demo data
        # 'data/compatible_regulations.xml',  # Commented out - demo data
        # 'data/additional_regulations.xml',  # Commented out - demo data
        'views/menu_root.xml',  # Define root menu first (no dependencies)
        'views/legal_regulation_views_minimal.xml',  # Then load views with actions
        'views/legal_regulation_perubahan_views.xml',
        'views/consolidation_views.xml',
        'views/consolidation_v2_views.xml',
        'views/system_control_views.xml',
        'views/menu_views.xml',  # Load child menus last (needs actions)
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