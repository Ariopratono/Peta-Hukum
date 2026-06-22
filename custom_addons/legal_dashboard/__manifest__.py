# -*- coding: utf-8 -*-
{
    'name': 'Legal Dashboard',
    'version': '1.0',
    'category': 'Dashboard',
    'summary': 'Dashboard for Legal Expert and User Website Statistics',
    'description': """
        This module provides a centralized dashboard for:
        - Legal Expert Directory statistics
        - User Website (Subscriptions & Search) statistics
    """,
    'author': 'Your Company',
    'depends': ['board', 'legal_expert_directory', 'legal_website'],
    'data': [
        'views/legal_expert_dashboard_views.xml',
        'views/user_website_dashboard_views.xml',
        'views/legal_dashboard_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'legal_dashboard/static/src/css/legal_dashboard.css',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
