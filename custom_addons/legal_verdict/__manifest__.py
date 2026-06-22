{
    'name': 'Legal Verdict Management',
    'version': '1.0.0',
    'category': 'Legal/Verdict',
    'summary': 'Indonesia Legal Verdict Management and Scraper',
    'description': """
        Module to store and scrape Indonesian Legal Verdicts:
        - Constitutional Court (MK) Verdicts
        - Supreme Court (MA) Verdicts
    """,
    'author': 'Jules',
    'license': 'LGPL-3',
    'depends': ['base', 'legal_website'],
    'data': [
        'security/ir.model.access.csv',
        'views/legal_verdict_views.xml',
        'views/legal_verdict_website_templates.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
