# jdih_bpk_connector/models/jdih_bpk.py
import re
import requests
import logging
import time
from bs4 import BeautifulSoup
from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

BASE_URL = "https://peraturan.bpk.go.id"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; jdih_bpk_connector/1.0; +https://your-org.example/)"
}

class JdihBpkFetch(models.Model):
    _name = "jdih.bpk.fetch"
    _description = "Connector JDIH BPK (scraper helper)"

    name = fields.Char(string="Name")

    def _request_get(self, url, params=None, max_retries=2, backoff=1.0):
        """Simple GET with retries and logging"""
        for attempt in range(max_retries+1):
            try:
                resp = requests.get(url, params=params, headers=HEADERS, timeout=30)
                if resp.status_code == 200:
                    return resp
                else:
                    _logger.warning("Request %s returned status %s", url, resp.status_code)
            except Exception as e:
                _logger.exception("Error fetching %s: %s", url, e)
            time.sleep(backoff * (attempt+1))
        return None

    def _parse_details_page(self, html):
        """
        Parse the Details page HTML and return a dict:
        {
            'title': str,
            'nomor': str,
            'tahun': str,
            'materi_pokok': str,
            'metadata': dict,
            'uji_materi': str,
            'status': str,
            'files': [ { 'label': str, 'url': str, 'mimetype': str } ]
        }
        Heuristics: find headings by visible text and take following element (card body).
        """
        soup = BeautifulSoup(html, "lxml")

        # title (from <h1> or <h2>)
        title_tag = soup.find(['h1','h2','h3'], text=True)
        title = title_tag.get_text(strip=True) if title_tag else ''

        # attempt to extract nomor/tahun from title using regex
        nomor = ''
        tahun = ''
        m = re.search(r'No\.\s*([0-9A-Za-z\-/\.]+)\s*Tah(u?n)?\s*([0-9]{4})', title, re.IGNORECASE)
        if not m:
            # alternative: search within metadata table later
            pass
        else:
            nomor = m.group(1)
            tahun = m.group(3)

        def find_section_by_heading_text(label_texts):
            """
            Find first element whose text matches any label_texts (case-insensitive substring).
            Return the next element sibling or parent card-body text.
            """
            # Try to find header elements
            for hdr_tag in soup.find_all(['h2','h3','h4','strong','b']):
                txt = hdr_tag.get_text(" ", strip=True)
                if not txt:
                    continue
                for lbl in label_texts:
                    if lbl.lower() in txt.lower():
                        # heuristics: next sibling that has substantial text
                        # Common page structure: <div class="card"><div class="card-header"> <h4>LABEL</h4></div><div class="card-body">...</div></div>
                        parent = hdr_tag
                        # check for card-body in ancestors
                        card = hdr_tag.find_parent(class_=re.compile(r'card', re.I))
                        if card:
                            body = card.find(class_=re.compile(r'card-body|card-content|card-text|card-body', re.I))
                            if body:
                                return body
                        # else, search for next sibling
                        nxt = hdr_tag.find_next_sibling()
                        if nxt and nxt.get_text(strip=True):
                            return nxt
                        # fallback: next element in document
                        nxt2 = hdr_tag.find_next()
                        if nxt2 and nxt2.get_text(strip=True):
                            return nxt2
            return None

        # Materi Pokok
        mp_elem = find_section_by_heading_text(['MATERI POKOK PERATURAN','MATERI POKOK'])
        materi_pokok = mp_elem.get_text("\n", strip=True) if mp_elem else ''

        # Metadata Peraturan - try to parse as key: value pairs in a table or dl
        md_elem = find_section_by_heading_text(['METADATA PERATURAN','METADATA'])
        metadata = {}
        if md_elem:
            # if a table present
            table = md_elem.find('table')
            if table:
                for row in table.find_all('tr'):
                    cols = [c.get_text(" ", strip=True) for c in row.find_all(['th','td'])]
                    if len(cols) >= 2:
                        key = cols[0]
                        val = cols[1]
                        metadata[key] = val
            else:
                # try definition lists or lines like "Label : Value"
                text_lines = md_elem.get_text("\n", strip=True).splitlines()
                for line in text_lines:
                    if ':' in line:
                        k, v = line.split(':',1)
                        metadata[k.strip()] = v.strip()

        # Uji Materi
        um_elem = find_section_by_heading_text(['UJI MATERI', 'UJI'])
        uji_materi = um_elem.get_text("\n", strip=True) if um_elem else ''

        # Status
        status_elem = find_section_by_heading_text(['STATUS PERATURAN','STATUS'])
        status = status_elem.get_text(" ", strip=True) if status_elem else ''

        # Files: look for anchor tags under a section 'FILE-FILE PERATURAN' or inside page where href ends with .pdf/.docx
        files = []
        ff_elem = find_section_by_heading_text(['FILE-FILE PERATURAN','FILE PERATURAN','FILE'])
        candidates = []
        if ff_elem:
            candidates = ff_elem.find_all('a', href=True)
        else:
            # fallback: scan the whole page for pdf/docx links that include '/Download/' or '.pdf'
            candidates = soup.find_all('a', href=True)
        for a in candidates:
            href = a['href']
            if not href:
                continue
            href_low = href.lower()
            if any(ext in href_low for ext in ['.pdf', '.doc', '.docx']):
                # make absolute
                if href.startswith('/'):
                    file_url = BASE_URL.rstrip('/') + href
                elif href.startswith('http'):
                    file_url = href
                else:
                    file_url = BASE_URL.rstrip('/') + '/' + href.lstrip('/')
                label = a.get_text(" ", strip=True) or a.get('title') or 'file'
                mime = 'application/pdf' if '.pdf' in href_low else 'application/msword'
                files.append({'label': label, 'url': file_url, 'mimetype': mime})

        return {
            'title': title,
            'nomor': nomor,
            'tahun': tahun,
            'materi_pokok': materi_pokok,
            'metadata': metadata,
            'uji_materi': uji_materi,
            'status': status,
            'files': files,
        }

    def _download_file_bytes(self, url):
        resp = self._request_get(url)
        if not resp or resp.status_code != 200:
            _logger.warning("Failed to download file: %s", url)
            return None
        return resp.content

    @api.model
    def fetch_and_import_batch(self, max_pages=3, per_page=20, sleep_between=1.0):
        """
        Crawl search/listing pages and import many regulations.
        - max_pages: number of listing pages to crawl (pagination)
        - per_page: items per page (if supported)
        This function will:
         - parse listing pages to find Details links
         - for each Details: parse sections and download files
         - create peraturan.rule (if not exists) and peraturan.version via create_from_bytes()
        """
        # listing/search URL: try /Search or /Home/Search
        # We'll iterate pages param 'page' if present as querystring '?page=N'
        listing_urls = [
            f"{BASE_URL}/Home/Search",
            f"{BASE_URL}/Search"
        ]
        found_detail_urls = set()

        for listing_url in listing_urls:
            for page in range(1, max_pages+1):
                params = {'page': page}
                _logger.info("Crawling listing: %s page=%s", listing_url, page)
                r = self._request_get(listing_url, params=params)
                if not r:
                    continue
                soup = BeautifulSoup(r.text, "lxml")
                # find all anchors that link to /Details/<id>/...
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    if '/Details/' in href:
                        if href.startswith('/'):
                            u = BASE_URL.rstrip('/') + href
                        elif href.startswith('http'):
                            u = href
                        else:
                            u = BASE_URL.rstrip('/') + '/' + href.lstrip('/')
                        found_detail_urls.add(u)
                time.sleep(sleep_between)

        _logger.info("Found %s details URLs", len(found_detail_urls))
        # For each detail URL: parse and import
        for detail_url in sorted(found_detail_urls):
            _logger.info("Processing detail: %s", detail_url)
            r = self._request_get(detail_url)
            if not r:
                _logger.warning("Skipping, cannot fetch: %s", detail_url)
                continue
            try:
                parsed = self._parse_details_page(r.text)
            except Exception as e:
                _logger.exception("Error parsing detail page %s: %s", detail_url, e)
                continue

            # determine or create rule
            title = parsed.get('title') or 'Peraturan tanpa judul'
            # attempt to derive nomor/tahun from metadata keys if not captured
            nomor = parsed.get('nomor') or parsed.get('metadata', {}).get('Nomor') or parsed.get('metadata', {}).get('No.')
            tahun = parsed.get('tahun') or parsed.get('metadata', {}).get('Tahun') or parsed.get('metadata', {}).get('Tahun Pembuatan')
            # search existing peraturan.rule by nomor+tahun or title
            domain = []
            if nomor:
                domain.append(('nomor','=',nomor))
            if tahun:
                domain.append(('tahun','=',tahun))
            rule = None
            if domain:
                rule = self.env['peraturan.rule'].search(domain, limit=1)
            if not rule:
                # fallback search by title substring
                rule = self.env['peraturan.rule'].search([('name','ilike', title[:80])], limit=1)
            if not rule:
                rule = self.env['peraturan.rule'].create({
                    'name': title,
                    'nomor': nomor or False,
                    'tahun': tahun or False,
                    'description': parsed.get('materi_pokok') or False,
                })

            # create version record(s)
            files = parsed.get('files') or []
            if not files:
                # if no files, still create a version with metadata and page snapshot (optional)
                # We'll create a version record with name based on detail_url and store snapshot on 'sumber'
                try:
                    # create empty "version" to record metadata
                    version_model = self.env['peraturan.version']
                    # create minimal version (no file)
                    ver = version_model.create({
                        'rule_id': rule.id,
                        'name': f"Imported from BPK ({detail_url.split('/')[-1]})",
                        'sumber': detail_url,
                    })
                except Exception as e:
                    _logger.exception("Failed create version without file: %s", e)
            else:
                for f in files:
                    file_url = f.get('url')
                    label = f.get('label') or file_url.split('/')[-1]
                    content = self._download_file_bytes(file_url)
                    if not content:
                        _logger.warning("Failed to download file %s, skipping", file_url)
                        continue
                    # call peraturan.version.create_from_bytes (expects raw bytes)
                    try:
                        version_model = self.env['peraturan.version']
                        # create version (this method defined in peraturan_merger)
                        ver = version_model.create_from_bytes(rule.id, content, filename=label, sumber=file_url, tanggal=False)
                    except Exception as e:
                        _logger.exception("Failed to create peraturan.version for %s: %s", file_url, e)
            # be polite to site
            time.sleep(sleep_between)

        return True
