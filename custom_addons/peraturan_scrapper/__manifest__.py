# jdih_bpk_connector/__manifest__.py
{
    "name": "JDIH BPK Connector",
    "version": "1.0.0",
    "summary": "Scraper JDIH BPK (peraturan.bpk.go.id) dan connector ke peraturan_merger",
    "description": "Scrapes peraturan.bpk.go.id Details pages and imports metadata + files into peraturan_merger.",
    "author": "Indonesian Legal Assistant",
    "license": "AGPL-3",
    "depends": ["base", "document", "peraturan_merger"],
    "data": [
        "security/ir.model.access.csv",
        "data/cron_jobs.xml",
    ],
    "installable": True,
    "application": False,
}
