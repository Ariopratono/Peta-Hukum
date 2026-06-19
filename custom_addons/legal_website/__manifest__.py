{
    'name': 'Legal Website',
    'version': '1.0.0',
    'category': 'Website',
    'summary': 'Website hukum dengan fitur pencarian menggunakan SearXNG',
    'description': """
        Website Hukum
        =============
        
        Website hukum dengan fitur-fitur:
        - Pencarian menggunakan SearXNG
        - Database hukum pidana
        - Artikel hukum
        - Konsultasi hukum
    """,
    'author': 'Legal Team',
    'website': 'https://yourwebsite.com',
    'depends': ['website', 'portal', 'legal_regulations'],
    'data': [
        'security/ir.model.access.csv',
        'views/legal_article_views.xml',
        'views/legal_search_views.xml', 
        'views/legal_search_enhanced_views.xml',
        'views/subscription_views.xml',
        'data/website_data.xml',
        'data/subscription_data.xml',
        'views/website_legal_templates.xml',
        'views/subscription_website_templates.xml',
        'views/subscription_success_template.xml',
        'views/website_menu.xml',
        'views/regulations_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'legal_website/static/src/css/legal_website.css',
            'legal_website/static/src/js/legal_search.js',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}