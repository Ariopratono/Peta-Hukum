{
    'name': 'Legal Scraper',
    'version': '1.0.0',
    'category': 'Legal/Regulations',
    'summary': 'Scrape legal regulations from peraturan.bpk.go.id',
    'description': """
        Module to scrape legal regulations from https://peraturan.bpk.go.id/
        and store them in the legal.regulation model.
    """,
    'author': 'Jules',
    'license': 'LGPL-3',
    'depends': ['base', 'legal_regulations'],
    'data': [
        'security/ir.model.access.csv',
        'views/legal_scraper_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}