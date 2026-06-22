# -*- coding: utf-8 -*-
{
    'name': 'Legal Expert Directory',
    'version': '1.1.0',
    'category': 'Website',
    'summary': 'Directory of Legal Experts (Lawyer, Notary, Judge, etc.)',
    'description': """
        Module to store and show registered Legal Expert roles.
        Manage Legal Expert data and show them in a list directory on the website.
    """,
    'author': 'Legal Team',
    'website': 'https://yourwebsite.com',
    'depends': ['base', 'website', 'portal'],
    'data': [
        'security/ir.model.access.csv',
        'views/legal_expert_views.xml',
        'views/website_expert_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'legal_expert_directory/static/src/css/legal_expert.css',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
