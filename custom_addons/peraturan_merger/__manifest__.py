# peraturan_merger/__manifest__.py
{
    "name": "Peraturan Merger",
    "version": "1.0.0",
    "summary": "Menggabungkan beberapa versi peraturan menjadi badan peraturan konsolidasi",
    "description": """
Module to parse, diff and merge multiple versions of legal regulations into a consolidated document.
Features:
- Import PDF/DOCX versions
- Parse Pasal/Ayat structure
- Detect additions/deletions/changes
- Export consolidated DOCX (annotated / final / history)
- Cron connector scaffold for external sources
""",
    "author": "Indonesian Legal Assistant",
    "license": "AGPL-3",
    "category": "Tools",
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "views/peraturan_views.xml",
        "views/wizard_merge_views.xml",
        "data/cron_jobs.xml",
        "reports/templates.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
