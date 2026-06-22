{
    'name': 'Auth Signup Role',
    'version': '1.0',
    'category': 'Website',
    'summary': 'Add Role field to signup form',
    'depends': ['auth_signup', 'website', 'legal_expert_directory'],
    'data': [
        'views/auth_signup_login_templates.xml',
        'views/res_users_views.xml', # << Tambahkan baris ini
    ],
    'installable': True,
    'application': False,
}
