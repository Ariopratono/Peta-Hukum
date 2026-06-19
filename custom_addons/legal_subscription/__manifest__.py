{
    'name': 'Legal Subscription Website',
    'version': '1.0.0',
    'category': 'Website',
    'summary': 'Legal website with subscription system',
    'description': """
        Legal Subscription Website
        =========================
        
        A complete legal website with subscription system featuring:
        - Legal search functionality
        - Subscription management
        - Pricing plans
        - User dashboard
    """,
    'author': 'Legal Team',
    'license': 'LGPL-3',
    'depends': ['website', 'portal'],
    'data': [
        'security/ir.model.access.csv',
        'data/subscription_plans.xml',
        'views/website_templates.xml',
        'views/subscription_views.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'legal_subscription/static/src/css/style.css',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}