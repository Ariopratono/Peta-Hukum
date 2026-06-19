{
    "name": "Peraturan Integration with Legal Regulations & Website",
    "version": "1.0.0",
    "summary": "Integrasi hasil peraturan_merger ke modul legal_regulations dan legal_website",
    "author": "Indonesian Legal Assistant",
    "license": "AGPL-3",
    "depends": ["peraturan_merger", "legal_regulations", "legal_website"],
    "data": [
        "security/ir.model.access.csv",
        "views/regulation_view_inherit.xml",
        "views/website_templates.xml",
        "data/sync_consolidation_cron.xml",
    ],
    "installable": True,
    "application": False,
}
