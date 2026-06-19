# -*- coding: utf-8 -*-
"""
Konsolidasi Peraturan V2 - Membaca dari File TXT
================================================
Modul ini membaca file TXT induk dan file TXT perubahan,
lalu membuat naskah konsolidasi dengan menampilkan perubahan.
"""
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64
import re
from difflib import SequenceMatcher, unified_diff
import logging

_logger = logging.getLogger(__name__)


class LegalRegulationConsolidationV2(models.Model):
    """
    Model untuk konsolidasi berbasis file TXT.
    Membaca file_txt dari peraturan induk dan file_txt_perubahan dari perubahan.
    """
    _name = 'legal.regulation.consolidation.v2'
    _description = 'Konsolidasi Peraturan (File TXT)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    _rec_name = 'name'

    name = fields.Char(
        string='Nama Konsolidasi',
        required=True
    )
    
    # Peraturan Induk
    peraturan_induk_id = fields.Many2one(
        'legal.regulation',
        string='Peraturan Induk',
        required=True,
        help='Pilih UU/Peraturan induk (versi asli)'
    )
    
    # Info dari induk
    file_txt_induk = fields.Binary(
        string='File TXT Induk',
        related='peraturan_induk_id.file_txt',
        readonly=True
    )
    
    # Perubahan yang akan digabung (dari tab Perubahan UU)
    perubahan_ids = fields.Many2many(
        'legal.regulation.perubahan',
        'consolidation_v2_perubahan_rel',
        'consolidation_id',
        'perubahan_id',
        string='Perubahan yang Digabung',
        help='Pilih perubahan yang akan dikonsolidasi'
    )
    
    # Mode tampilan
    display_mode = fields.Selection([
        ('annotated', 'Mode Anotasi (Tampilkan Semua Perubahan)'),
        ('sidebyside', 'Mode Side-by-Side (Perbandingan)'),
        ('final', 'Mode Final (Versi Terbaru Saja)'),
        ('diff', 'Mode Diff (Seperti Git)'),
    ], string='Mode Tampilan', default='annotated', required=True)
    
    # Hasil konsolidasi
    consolidated_html = fields.Html(
        string='Hasil Konsolidasi',
        sanitize=False
    )
    
    # Statistik
    total_pasal = fields.Integer(string='Total Pasal')
    pasal_berubah = fields.Integer(string='Pasal Berubah')
    pasal_ditambah = fields.Integer(string='Pasal Ditambah')
    pasal_dihapus = fields.Integer(string='Pasal Dihapus')
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('generated', 'Sudah Digenerate'),
    ], string='Status', default='draft')

    def _decode_txt_file(self, binary_data):
        """Decode binary file TXT ke string"""
        if not binary_data:
            return ""
        try:
            decoded = base64.b64decode(binary_data)
            # Coba UTF-8 dulu, fallback ke latin-1
            try:
                return decoded.decode('utf-8')
            except UnicodeDecodeError:
                return decoded.decode('latin-1')
        except Exception as e:
            _logger.error(f"Error decoding TXT: {e}")
            return ""

    def _parse_pasal_from_text(self, text):
        """
        Parse text menjadi struktur pasal.
        Returns: dict {nomor_pasal: {'judul': str, 'isi': str, 'raw': str}}
        """
        if not text:
            return {}
        
        pasal_dict = {}
        
        # Pattern untuk mendeteksi awal Pasal
        # Format: "Pasal X" atau "Pasal X."
        pasal_pattern = re.compile(
            r'^[\s]*(Pasal\s+(\d+[A-Z]?))\s*[\.\n]?',
            re.MULTILINE | re.IGNORECASE
        )
        
        matches = list(pasal_pattern.finditer(text))
        
        if not matches:
            # Jika tidak ada pasal terdeteksi, return kosong
            _logger.warning("Tidak ada pasal terdeteksi dalam teks")
            return {}
        
        for i, match in enumerate(matches):
            pasal_judul = match.group(1)  # "Pasal 1"
            pasal_no = match.group(2)     # "1"
            
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            
            isi = text[start:end].strip()
            
            pasal_dict[pasal_no] = {
                'judul': pasal_judul,
                'nomor': pasal_no,
                'isi': isi,
                'raw': f"{pasal_judul}\n{isi}"
            }
        
        _logger.info(f"Parsed {len(pasal_dict)} pasal dari teks")
        return pasal_dict

    def action_generate_consolidation(self):
        """Generate konsolidasi dari file TXT induk + perubahan"""
        self.ensure_one()
        
        # Validasi
        if not self.peraturan_induk_id:
            raise UserError(_('Pilih Peraturan Induk terlebih dahulu.'))
        
        if not self.peraturan_induk_id.file_txt:
            raise UserError(_('Peraturan Induk tidak memiliki file TXT. Upload file TXT terlebih dahulu.'))
        
        if not self.perubahan_ids:
            raise UserError(_('Pilih minimal satu perubahan untuk dikonsolidasi.'))
        
        # Cek setiap perubahan punya file TXT
        for perubahan in self.perubahan_ids:
            if not perubahan.file_txt_perubahan and not (perubahan.peraturan_pengubah_id and perubahan.peraturan_pengubah_id.file_txt):
                raise UserError(_(f'Perubahan "{perubahan.nama_perubahan or perubahan.name}" tidak memiliki file TXT.'))
        
        try:
            # 1. Baca file TXT induk
            txt_induk = self._decode_txt_file(self.peraturan_induk_id.file_txt)
            pasal_induk = self._parse_pasal_from_text(txt_induk)
            
            _logger.info(f"Parsed {len(pasal_induk)} pasal dari induk: {self.peraturan_induk_id.nama_lengkap}")
            
            # 2. Baca file TXT setiap perubahan
            perubahan_data = []
            for perubahan in self.perubahan_ids.sorted('sequence'):
                # Prioritas: file_txt_perubahan langsung, atau dari peraturan pengubah
                if perubahan.file_txt_perubahan:
                    txt_perubahan = self._decode_txt_file(perubahan.file_txt_perubahan)
                    nama = perubahan.nama_perubahan or perubahan.file_txt_perubahan_name
                elif perubahan.peraturan_pengubah_id and perubahan.peraturan_pengubah_id.file_txt:
                    txt_perubahan = self._decode_txt_file(perubahan.peraturan_pengubah_id.file_txt)
                    nama = perubahan.peraturan_pengubah_id.nama_lengkap
                else:
                    continue
                
                pasal_perubahan = self._parse_pasal_from_text(txt_perubahan)
                perubahan_data.append({
                    'nama': nama,
                    'tahun': perubahan.tahun_perubahan,
                    'pasal': pasal_perubahan,
                    'raw_text': txt_perubahan
                })
                _logger.info(f"Parsed {len(pasal_perubahan)} pasal dari perubahan: {nama}")
            
            # 3. Generate HTML berdasarkan mode
            if self.display_mode == 'annotated':
                html = self._generate_annotated_html(pasal_induk, perubahan_data)
            elif self.display_mode == 'sidebyside':
                html = self._generate_sidebyside_html(pasal_induk, perubahan_data)
            elif self.display_mode == 'final':
                html = self._generate_final_html(pasal_induk, perubahan_data)
            else:  # diff
                html = self._generate_diff_html(txt_induk, perubahan_data)
            
            self.consolidated_html = html
            self.state = 'generated'
            
            # Hitung statistik
            self._compute_statistics(pasal_induk, perubahan_data)
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Sukses'),
                    'message': _('Konsolidasi berhasil digenerate!'),
                    'type': 'success',
                    'sticky': False,
                }
            }
            
        except Exception as e:
            _logger.error(f"Error generating consolidation: {str(e)}", exc_info=True)
            raise UserError(_('Error saat generate konsolidasi: %s') % str(e))

    def _compute_statistics(self, pasal_induk, perubahan_data):
        """Hitung statistik perubahan"""
        all_pasal = set(pasal_induk.keys())
        
        pasal_berubah = 0
        pasal_ditambah = 0
        pasal_dihapus = 0
        
        for data in perubahan_data:
            pasal_perubahan = data['pasal']
            
            for no in pasal_perubahan:
                if no not in pasal_induk:
                    pasal_ditambah += 1
                    all_pasal.add(no)
                else:
                    # Cek apakah isi berubah
                    if pasal_perubahan[no]['isi'] != pasal_induk[no]['isi']:
                        pasal_berubah += 1
        
        # Pasal dihapus = pasal di induk yang tidak ada di perubahan terakhir
        if perubahan_data:
            last_perubahan = perubahan_data[-1]['pasal']
            for no in pasal_induk:
                # Jika pasal induk tidak ada di perubahan terakhir DAN tidak ada di semua perubahan
                found_in_any = any(no in d['pasal'] for d in perubahan_data)
                if not found_in_any:
                    # Pasal tetap dari induk, tidak dihapus
                    pass
        
        self.total_pasal = len(all_pasal)
        self.pasal_berubah = pasal_berubah
        self.pasal_ditambah = pasal_ditambah
        self.pasal_dihapus = pasal_dihapus

    def _generate_annotated_html(self, pasal_induk, perubahan_data):
        """
        Generate HTML dengan anotasi perubahan per pasal.
        Menampilkan versi terbaru dengan highlight perubahan.
        """
        html_parts = [self._get_css_styles()]
        
        # Header
        perubahan_names = ', '.join([d['nama'] for d in perubahan_data])
        html_parts.append(f"""
        <div class="consolidated-document">
            <div class="consolidated-header">
                <h1>📋 {self.name}</h1>
                <p><strong>Peraturan Induk:</strong> {self.peraturan_induk_id.nama_lengkap}</p>
                <p><strong>Perubahan:</strong> {perubahan_names}</p>
                <p><strong>Mode:</strong> Anotasi (Menampilkan Perubahan)</p>
                
                <div class="legend">
                    <span class="legend-item"><span class="badge badge-original">Asli</span> Isi dari UU Induk</span>
                    <span class="legend-item"><span class="badge badge-modified">Diubah</span> Pasal yang dimodifikasi</span>
                    <span class="legend-item"><span class="badge badge-added">Baru</span> Pasal ditambahkan</span>
                    <span class="legend-item"><span class="badge badge-deleted">Dihapus</span> Pasal dihapus</span>
                </div>
            </div>
        """)
        
        # Kumpulkan semua nomor pasal
        all_pasal_numbers = set(pasal_induk.keys())
        for data in perubahan_data:
            all_pasal_numbers.update(data['pasal'].keys())
        
        # Sort - handle mixed alphanumeric like 1, 1A, 2, 10
        def sort_key(x):
            match = re.match(r'(\d+)([A-Z]?)', x, re.IGNORECASE)
            if match:
                return (int(match.group(1)), match.group(2))
            return (0, x)
        
        sorted_numbers = sorted(all_pasal_numbers, key=sort_key)
        
        # Process setiap pasal
        for pasal_no in sorted_numbers:
            induk_pasal = pasal_induk.get(pasal_no)
            
            # Cari versi terbaru dari perubahan
            latest_version = None
            version_history = []
            
            for data in perubahan_data:
                if pasal_no in data['pasal']:
                    latest_version = data['pasal'][pasal_no]
                    version_history.append({
                        'nama': data['nama'],
                        'tahun': data['tahun'],
                        'isi': data['pasal'][pasal_no]['isi']
                    })
            
            # Tentukan status dan tampilan
            if induk_pasal and not latest_version:
                # Pasal tetap dari induk, tidak ada perubahan
                status_class = 'article-unchanged'
                badge = '<span class="badge badge-original">Asli</span>'
                content = induk_pasal['isi']
                note = None
            elif induk_pasal and latest_version:
                # Pasal ada di induk DAN ada perubahan
                if induk_pasal['isi'].strip() == latest_version['isi'].strip():
                    status_class = 'article-unchanged'
                    badge = '<span class="badge badge-original">Asli</span>'
                    content = induk_pasal['isi']
                    note = None
                else:
                    status_class = 'article-modified'
                    badge = '<span class="badge badge-modified">Diubah</span>'
                    content = latest_version['isi']
                    # Tampilkan perbandingan
                    note = self._generate_change_note(induk_pasal['isi'], latest_version['isi'], version_history)
            elif not induk_pasal and latest_version:
                # Pasal baru ditambahkan
                status_class = 'article-added'
                badge = '<span class="badge badge-added">Baru</span>'
                content = latest_version['isi']
                note = f'<div class="change-note">✅ Pasal ini ditambahkan oleh {version_history[0]["nama"]}</div>'
            else:
                continue
            
            # Render pasal
            html_parts.append(f"""
            <div class="pasal-container {status_class}">
                <h2 class="pasal-header">{badge} Pasal {pasal_no}</h2>
                <div class="pasal-content">
                    {self._format_content_html(content)}
                </div>
                {note or ''}
            </div>
            """)
        
        html_parts.append('</div>')  # Close consolidated-document
        
        return '\n'.join(html_parts)

    def _generate_change_note(self, old_text, new_text, version_history):
        """Generate catatan perubahan dengan diff"""
        html = ['<div class="change-note">']
        html.append('<strong>📝 Riwayat Perubahan:</strong>')
        
        for vh in version_history:
            html.append(f'<br/>• Diubah oleh <strong>{vh["nama"]}</strong> ({vh["tahun"] or "?"})')
        
        # Simple diff highlighting
        html.append('<details class="diff-details">')
        html.append('<summary>Lihat perbandingan teks asli vs terbaru</summary>')
        html.append('<div class="diff-container">')
        
        html.append('<div class="diff-old">')
        html.append('<strong>Teks Asli:</strong><br/>')
        html.append(f'<pre>{self._escape_html(old_text[:1000])}</pre>')
        html.append('</div>')
        
        html.append('<div class="diff-new">')
        html.append('<strong>Teks Terbaru:</strong><br/>')
        html.append(f'<pre>{self._escape_html(new_text[:1000])}</pre>')
        html.append('</div>')
        
        html.append('</div></details>')
        html.append('</div>')
        
        return '\n'.join(html)

    def _generate_sidebyside_html(self, pasal_induk, perubahan_data):
        """Generate HTML perbandingan side-by-side"""
        html_parts = [self._get_css_styles()]
        
        # Header
        html_parts.append(f"""
        <div class="consolidated-document">
            <div class="consolidated-header">
                <h1>📋 {self.name} - Perbandingan</h1>
                <p><strong>Mode:</strong> Side-by-Side</p>
            </div>
            
            <table class="comparison-table">
                <thead>
                    <tr>
                        <th>Pasal</th>
                        <th>UU Induk: {self.peraturan_induk_id.nama_lengkap}</th>
        """)
        
        for data in perubahan_data:
            html_parts.append(f'<th>Perubahan: {data["nama"]}</th>')
        
        html_parts.append('</tr></thead><tbody>')
        
        # Kumpulkan semua pasal
        all_pasal = set(pasal_induk.keys())
        for data in perubahan_data:
            all_pasal.update(data['pasal'].keys())
        
        def sort_key(x):
            match = re.match(r'(\d+)([A-Z]?)', x, re.IGNORECASE)
            if match:
                return (int(match.group(1)), match.group(2))
            return (0, x)
        
        for pasal_no in sorted(all_pasal, key=sort_key):
            html_parts.append(f'<tr><td class="pasal-no">Pasal {pasal_no}</td>')
            
            # Kolom induk
            if pasal_no in pasal_induk:
                html_parts.append(f'<td class="content-cell">{self._escape_html(pasal_induk[pasal_no]["isi"][:500])}</td>')
            else:
                html_parts.append('<td class="content-cell empty">-</td>')
            
            # Kolom perubahan
            for data in perubahan_data:
                if pasal_no in data['pasal']:
                    isi = data['pasal'][pasal_no]['isi']
                    # Highlight jika berbeda dari induk
                    if pasal_no in pasal_induk and isi.strip() != pasal_induk[pasal_no]['isi'].strip():
                        html_parts.append(f'<td class="content-cell modified">{self._escape_html(isi[:500])}</td>')
                    else:
                        html_parts.append(f'<td class="content-cell">{self._escape_html(isi[:500])}</td>')
                else:
                    html_parts.append('<td class="content-cell empty">-</td>')
            
            html_parts.append('</tr>')
        
        html_parts.append('</tbody></table></div>')
        
        return '\n'.join(html_parts)

    def _generate_final_html(self, pasal_induk, perubahan_data):
        """Generate HTML versi final (terbaru saja tanpa anotasi)"""
        html_parts = [self._get_css_styles()]
        
        html_parts.append(f"""
        <div class="consolidated-document final-mode">
            <div class="consolidated-header">
                <h1>📋 {self.name}</h1>
                <p><strong>Mode:</strong> Versi Final (Konsolidasi)</p>
                <p>Naskah ini merupakan gabungan dari UU Induk dan semua perubahannya.</p>
            </div>
        """)
        
        # Merge: pasal induk + override dari perubahan
        final_pasal = dict(pasal_induk)
        for data in perubahan_data:
            for pasal_no, pasal_data in data['pasal'].items():
                final_pasal[pasal_no] = pasal_data
        
        def sort_key(x):
            match = re.match(r'(\d+)([A-Z]?)', x, re.IGNORECASE)
            if match:
                return (int(match.group(1)), match.group(2))
            return (0, x)
        
        for pasal_no in sorted(final_pasal.keys(), key=sort_key):
            pasal = final_pasal[pasal_no]
            html_parts.append(f"""
            <div class="pasal-container">
                <h2 class="pasal-header">Pasal {pasal_no}</h2>
                <div class="pasal-content">
                    {self._format_content_html(pasal['isi'])}
                </div>
            </div>
            """)
        
        html_parts.append('</div>')
        
        return '\n'.join(html_parts)

    def _generate_diff_html(self, txt_induk, perubahan_data):
        """Generate HTML seperti diff (unified diff)"""
        html_parts = [self._get_css_styles()]
        
        html_parts.append(f"""
        <div class="consolidated-document diff-mode">
            <div class="consolidated-header">
                <h1>📋 {self.name} - Diff</h1>
                <p><strong>Mode:</strong> Diff (Perbandingan Baris)</p>
            </div>
        """)
        
        # Generate diff untuk setiap perubahan
        current_text = txt_induk
        
        for data in perubahan_data:
            perubahan_text = data.get('raw_text', '')
            
            html_parts.append(f"""
            <div class="diff-section">
                <h3>Perubahan: {data['nama']}</h3>
                <pre class="diff-output">
            """)
            
            # Generate unified diff
            diff = unified_diff(
                current_text.splitlines(keepends=True),
                perubahan_text.splitlines(keepends=True),
                fromfile='UU Induk',
                tofile=data['nama'],
                lineterm=''
            )
            
            for line in diff:
                if line.startswith('+') and not line.startswith('+++'):
                    html_parts.append(f'<span class="diff-added">{self._escape_html(line)}</span>')
                elif line.startswith('-') and not line.startswith('---'):
                    html_parts.append(f'<span class="diff-removed">{self._escape_html(line)}</span>')
                elif line.startswith('@@'):
                    html_parts.append(f'<span class="diff-info">{self._escape_html(line)}</span>')
                else:
                    html_parts.append(self._escape_html(line))
            
            html_parts.append('</pre></div>')
            
            # Update current untuk diff berikutnya
            current_text = perubahan_text
        
        html_parts.append('</div>')
        
        return '\n'.join(html_parts)

    def _format_content_html(self, text):
        """Format plain text menjadi HTML yang readable"""
        if not text:
            return ""
        
        # Escape HTML
        text = self._escape_html(text)
        
        # Format ayat (1), (2), dst
        text = re.sub(r'\((\d+)\)', r'<br/><strong>(\1)</strong>', text)
        
        # Format huruf a., b., dst
        text = re.sub(r'\n([a-z])\.\s', r'<br/>&nbsp;&nbsp;&nbsp;&nbsp;<strong>\1.</strong> ', text)
        
        # Newlines
        text = text.replace('\n', '<br/>')
        
        return text

    def _escape_html(self, text):
        """Escape HTML special characters"""
        if not text:
            return ""
        return (text
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;'))

    def _get_css_styles(self):
        """Return CSS styles untuk hasil konsolidasi"""
        return """
        <style>
            .consolidated-document {
                font-family: 'Segoe UI', Tahoma, Geneva, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }
            .consolidated-header {
                background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                color: white;
                padding: 25px;
                border-radius: 10px;
                margin-bottom: 25px;
            }
            .consolidated-header h1 {
                margin: 0 0 15px 0;
            }
            .consolidated-header p {
                margin: 5px 0;
                opacity: 0.9;
            }
            .legend {
                margin-top: 15px;
                padding-top: 15px;
                border-top: 1px solid rgba(255,255,255,0.3);
            }
            .legend-item {
                margin-right: 20px;
                display: inline-block;
            }
            .badge {
                display: inline-block;
                padding: 3px 10px;
                border-radius: 15px;
                font-size: 0.8em;
                font-weight: bold;
                margin-right: 5px;
            }
            .badge-original {
                background: #28a745;
                color: white;
            }
            .badge-modified {
                background: #ffc107;
                color: #000;
            }
            .badge-added {
                background: #17a2b8;
                color: white;
            }
            .badge-deleted {
                background: #dc3545;
                color: white;
            }
            .pasal-container {
                background: white;
                border-radius: 8px;
                margin-bottom: 20px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                overflow: hidden;
            }
            .pasal-header {
                background: #343a40;
                color: white;
                padding: 12px 20px;
                margin: 0;
                font-size: 1.1em;
            }
            .pasal-content {
                padding: 20px;
                line-height: 1.8;
            }
            .article-unchanged {
                border-left: 5px solid #28a745;
            }
            .article-modified {
                border-left: 5px solid #ffc107;
                background: #fffde7;
            }
            .article-modified .pasal-header {
                background: #f57c00;
            }
            .article-added {
                border-left: 5px solid #17a2b8;
                background: #e3f2fd;
            }
            .article-added .pasal-header {
                background: #0288d1;
            }
            .article-deleted {
                border-left: 5px solid #dc3545;
                background: #ffebee;
                opacity: 0.7;
            }
            .article-deleted .pasal-content {
                text-decoration: line-through;
            }
            .change-note {
                background: #fff3e0;
                border-left: 4px solid #ff9800;
                padding: 15px;
                margin: 15px 20px 20px 20px;
                border-radius: 0 5px 5px 0;
                font-size: 0.9em;
            }
            .diff-details {
                margin-top: 10px;
            }
            .diff-details summary {
                cursor: pointer;
                color: #1976d2;
            }
            .diff-container {
                display: flex;
                gap: 20px;
                margin-top: 10px;
            }
            .diff-old, .diff-new {
                flex: 1;
                padding: 10px;
                border-radius: 5px;
            }
            .diff-old {
                background: #ffebee;
            }
            .diff-new {
                background: #e8f5e9;
            }
            .diff-old pre, .diff-new pre {
                white-space: pre-wrap;
                word-wrap: break-word;
                font-size: 0.85em;
                max-height: 300px;
                overflow-y: auto;
            }
            /* Side by side table */
            .comparison-table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }
            .comparison-table th, .comparison-table td {
                border: 1px solid #ddd;
                padding: 12px;
                text-align: left;
                vertical-align: top;
            }
            .comparison-table th {
                background: #343a40;
                color: white;
            }
            .comparison-table .pasal-no {
                font-weight: bold;
                background: #f5f5f5;
                width: 100px;
            }
            .comparison-table .content-cell {
                font-size: 0.9em;
            }
            .comparison-table .content-cell.modified {
                background: #fff3cd;
            }
            .comparison-table .content-cell.empty {
                background: #f8f9fa;
                color: #999;
                text-align: center;
            }
            /* Diff mode */
            .diff-output {
                background: #263238;
                color: #eceff1;
                padding: 15px;
                border-radius: 5px;
                overflow-x: auto;
                font-size: 0.85em;
            }
            .diff-added {
                color: #69f0ae;
                display: block;
            }
            .diff-removed {
                color: #ff5252;
                display: block;
            }
            .diff-info {
                color: #64b5f6;
                display: block;
            }
        </style>
        """
