# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import re
import html as html_lib
import logging
from markupsafe import Markup

_logger = logging.getLogger(__name__)


class LegalRegulationWebsiteController(http.Controller):

    def _strip_html_tags(self, text):
        """Remove HTML tags from text, returning plain text"""
        if not text:
            return ''
        return re.sub(r'<[^>]+>', ' ', str(text)).strip()

    def _highlight_keyword(self, text, keyword):
        """Highlight keyword in text with <mark> tag (case-insensitive)"""
        if not text or not keyword:
            return text
        escaped = re.escape(keyword)
        return re.sub(
            f'({escaped})',
            r'<mark class="bg-warning text-dark px-1 rounded">\1</mark>',
            str(text),
            flags=re.IGNORECASE
        )

    def _get_snippet_around_keyword(self, text, keyword, context_chars=200):
        """Extract a snippet of text around the keyword with context"""
        if not text or not keyword:
            return ''
        plain = self._strip_html_tags(text)
        lower_plain = plain.lower()
        lower_kw = keyword.lower()
        idx = lower_plain.find(lower_kw)
        if idx == -1:
            return ''
        start = max(0, idx - context_chars)
        end = min(len(plain), idx + len(keyword) + context_chars)
        snippet = plain[start:end].strip()
        if start > 0:
            snippet = '...' + snippet
        if end < len(plain):
            snippet = snippet + '...'
        return snippet

    def _search_pasal_matches(self, regulation_ids, search_term, limit_per_reg=5):
        """
        Search inside pasal, ayat, huruf for a keyword.
        Returns dict: { regulation_id: [ {pasal_info}, ... ] }
        Uses savepoint to prevent SQL errors from corrupting the transaction.
        """
        matches = {}
        if not search_term or not regulation_ids:
            return matches

        # Fallback to isi_peraturan if pasal model doesn't exist
        has_pasal = 'legal.regulation.pasal' in request.env

        if has_pasal:
            cr = request.env.cr
            cr.execute("SAVEPOINT pasal_match_sp")
            try:
                Pasal = request.env['legal.regulation.pasal'].sudo()
                Ayat = request.env['legal.regulation.ayat'].sudo()
                Huruf = request.env['legal.regulation.huruf'].sudo()

                # 1) Search in pasal (isi_pasal, judul_pasal)
                pasal_domain = [
                    ('regulation_id', 'in', regulation_ids),
                    '|', '|',
                    ('isi_pasal', 'ilike', search_term),
                    ('judul_pasal', 'ilike', search_term),
                    ('nomor_pasal', 'ilike', search_term),
                ]
                found_pasals = Pasal.search(pasal_domain, order='regulation_id, sequence, nomor_pasal')
                for pasal in found_pasals:
                    reg_id = pasal.regulation_id.id
                    if reg_id not in matches:
                        matches[reg_id] = []
                    if len(matches[reg_id]) >= limit_per_reg:
                        continue
                    plain_isi = self._strip_html_tags(pasal.isi_pasal)
                    snippet = self._get_snippet_around_keyword(plain_isi, search_term)
                    matches[reg_id].append({
                        'type': 'pasal',
                        'bab': pasal.bab or '',
                        'pasal_nomor': pasal.nomor_pasal,
                        'pasal_judul': pasal.judul_pasal or '',
                        'ayat_nomor': '',
                        'huruf': '',
                        'snippet': snippet,
                        'display': f"Pasal {pasal.nomor_pasal}" + (f" - {pasal.judul_pasal}" if pasal.judul_pasal else ''),
                    })

                # 2) Search in ayat (isi_ayat)
                ayat_domain = [
                    ('regulation_id', 'in', regulation_ids),
                    ('isi_ayat', 'ilike', search_term),
                ]
                found_ayats = Ayat.search(ayat_domain, order='regulation_id, pasal_id, sequence, nomor_ayat')
                for ayat in found_ayats:
                    reg_id = ayat.regulation_id.id
                    if reg_id not in matches:
                        matches[reg_id] = []
                    if len(matches[reg_id]) >= limit_per_reg:
                        continue
                    pasal = ayat.pasal_id
                    plain_isi = self._strip_html_tags(ayat.isi_ayat)
                    snippet = self._get_snippet_around_keyword(plain_isi, search_term)
                    matches[reg_id].append({
                        'type': 'ayat',
                        'bab': pasal.bab or '',
                        'pasal_nomor': pasal.nomor_pasal,
                        'pasal_judul': pasal.judul_pasal or '',
                        'ayat_nomor': ayat.nomor_ayat,
                        'huruf': '',
                        'snippet': snippet,
                        'display': f"Pasal {pasal.nomor_pasal} Ayat {ayat.nomor_ayat}",
                    })

                # 3) Search in huruf (isi)
                huruf_domain = [
                    ('regulation_id', 'in', regulation_ids),
                    ('isi', 'ilike', search_term),
                ]
                found_hurufs = Huruf.search(huruf_domain, order='regulation_id, pasal_id, ayat_id, sequence, huruf')
                for h in found_hurufs:
                    reg_id = h.regulation_id.id
                    if reg_id not in matches:
                        matches[reg_id] = []
                    if len(matches[reg_id]) >= limit_per_reg:
                        continue
                    pasal = h.pasal_id
                    ayat = h.ayat_id
                    plain_isi = self._strip_html_tags(h.isi)
                    snippet = self._get_snippet_around_keyword(plain_isi, search_term)
                    matches[reg_id].append({
                        'type': 'huruf',
                        'bab': pasal.bab or '' if pasal else '',
                        'pasal_nomor': pasal.nomor_pasal if pasal else '',
                        'pasal_judul': pasal.judul_pasal or '' if pasal else '',
                        'ayat_nomor': ayat.nomor_ayat if ayat else '',
                        'huruf': h.huruf,
                        'snippet': snippet,
                        'display': f"Pasal {pasal.nomor_pasal} Ayat {ayat.nomor_ayat} huruf {h.huruf}" if ayat else f"Pasal {pasal.nomor_pasal} huruf {h.huruf}",
                    })
                cr.execute("RELEASE SAVEPOINT pasal_match_sp")
            except Exception as e:
                cr.execute("ROLLBACK TO SAVEPOINT pasal_match_sp")
                _logger.warning(f"Structured search inside pasal/ayat failed (rolled back): {e}")

        # Fallback/Unstructured search:
        # Check if any regulation lacks matches, and look in its `isi_peraturan`
        remaining_ids = [rid for rid in regulation_ids if rid not in matches]
        if remaining_ids:
            try:
                regs = request.env['legal.regulation'].sudo().browse(remaining_ids)
                for reg in regs:
                    if reg.isi_peraturan and search_term.lower() in str(reg.isi_peraturan).lower():
                        plain_isi = self._strip_html_tags(reg.isi_peraturan)
                        snippet = self._get_snippet_around_keyword(plain_isi, search_term)
                        if snippet:
                            matches[reg.id] = [{
                                'type': 'regulation',
                                'bab': '',
                                'pasal_nomor': '',
                                'pasal_judul': '',
                                'ayat_nomor': '',
                                'huruf': '',
                                'snippet': snippet,
                                'display': 'Dokumen',
                            }]
            except Exception as e:
                _logger.error(f"Fallback search in isi_peraturan failed: {e}")

        return matches

    @http.route('/regulations', type='http', auth='public', website=True)
    def regulations_list(self, **kw):
        """Halaman daftar peraturan hukum dengan pencarian mendalam ke pasal/ayat"""
        try:
            # Cek apakah model legal.regulation tersedia
            if 'legal.regulation' not in request.env:
                return request.render('legal_website.regulations_empty_template')
            
            # Filter dan search
            domain = []
            search_term = kw.get('search', '').strip()
            pasal_matches = {}
            
            # Filter berdasarkan parameter
            if kw.get('bidang'):
                domain.append(('bidang', '=', kw.get('bidang')))
            
            if kw.get('tipe'):
                domain.append(('tipe_dokumen', '=', kw.get('tipe')))
                
            if kw.get('tahun'):
                try:
                    domain.append(('tahun', '=', int(kw.get('tahun'))))
                except (ValueError, TypeError):
                    pass
                    
            if kw.get('status'):
                domain.append(('status', '=', kw.get('status')))
                
            # --- Deep search: regulation fields + pasal/ayat/huruf ---
            regulation_ids_from_pasal = set()
            if search_term:
                # 1) Standard regulation-level search fields
                search_fields = [
                    ('judul', 'ilike', search_term),
                    ('nomor', 'ilike', search_term), 
                    ('bentuk_singkat', 'ilike', search_term),
                    ('subjek', 'ilike', search_term),
                    ('keterangan', 'ilike', search_term),
                    ('bentuk', 'ilike', search_term)
                ]
                
                try:
                    model_fields = request.env['legal.regulation']._fields
                    if 'isi_peraturan' in model_fields:
                        search_fields.append(('isi_peraturan', 'ilike', search_term))
                    if 'kata_kunci' in model_fields:
                        search_fields.append(('kata_kunci', 'ilike', search_term))
                    if 'ringkasan' in model_fields:
                        search_fields.append(('ringkasan', 'ilike', search_term))
                except Exception:
                    pass
                
                # 2) Deep search inside pasal/ayat/huruf to find regulation IDs
                if 'legal.regulation.pasal' in request.env:
                    try:
                        # Use savepoint to isolate potential SQL errors
                        # (e.g., table doesn't exist yet)
                        cr = request.env.cr
                        cr.execute("SAVEPOINT deep_search_sp")
                        try:
                            Pasal = request.env['legal.regulation.pasal'].sudo()
                            Ayat = request.env['legal.regulation.ayat'].sudo()
                            Huruf = request.env['legal.regulation.huruf'].sudo()
                            
                            pasal_reg_ids = Pasal.search([
                                '|', '|',
                                ('isi_pasal', 'ilike', search_term),
                                ('judul_pasal', 'ilike', search_term),
                                ('nomor_pasal', 'ilike', search_term),
                            ]).mapped('regulation_id.id')
                            
                            ayat_reg_ids = Ayat.search([
                                ('isi_ayat', 'ilike', search_term),
                            ]).mapped('regulation_id.id')
                            
                            huruf_reg_ids = Huruf.search([
                                ('isi', 'ilike', search_term),
                            ]).mapped('regulation_id.id')
                            
                            regulation_ids_from_pasal = set(pasal_reg_ids) | set(ayat_reg_ids) | set(huruf_reg_ids)
                            cr.execute("RELEASE SAVEPOINT deep_search_sp")
                        except Exception as e:
                            cr.execute("ROLLBACK TO SAVEPOINT deep_search_sp")
                            _logger.warning(f"Deep search in pasal/ayat failed (rolled back): {e}")
                    except Exception as e:
                        _logger.warning(f"Deep search setup failed: {e}")
                
                # 3) Build combined domain: regulation fields OR regulation ID in pasal matches
                if len(search_fields) > 1:
                    or_conditions = ['|'] * (len(search_fields) - 1)
                    reg_field_domain = or_conditions + search_fields
                else:
                    reg_field_domain = list(search_fields)
                
                if regulation_ids_from_pasal:
                    # Combine: '|' + (id in pasal_ids) + (reg_field_domain...)
                    # In Odoo prefix notation, '|' takes 2 operands
                    # reg_field_domain is already a complete sub-expression
                    domain.append('|')
                    domain.append(('id', 'in', list(regulation_ids_from_pasal)))
                    domain.extend(reg_field_domain)
                else:
                    domain.extend(reg_field_domain)

            # Pagination
            limit = 20
            page = int(kw.get('page', 1))
            offset = (page - 1) * limit

            regulations = request.env['legal.regulation'].sudo().search(
                domain, limit=limit, offset=offset, 
                order='hierarchy_order, tahun desc, nomor'
            )
            total_count = request.env['legal.regulation'].sudo().search_count(domain)
            
            # --- Get pasal matches for displayed regulations ---
            if search_term and regulations:
                try:
                    pasal_matches = self._search_pasal_matches(
                        regulations.ids, search_term, limit_per_reg=5
                    )
                except Exception as e:
                    _logger.warning(f"Pasal match search failed: {e}")
                    pasal_matches = {}
                # Highlight keyword in snippets
                for reg_id, match_list in pasal_matches.items():
                    for m in match_list:
                        if m.get('snippet'):
                            m['snippet'] = Markup(self._highlight_keyword(
                                html_lib.escape(m['snippet']), search_term
                            ))
            
            # Pagination info
            total_pages = (total_count - 1) // limit + 1 if total_count > 0 else 1
            current_page = page

            # Data untuk filter dengan error handling
            try:
                bidang_options = request.env['legal.regulation']._fields['bidang'].selection
                tipe_options = request.env['legal.regulation']._fields['tipe_dokumen'].selection
            except (KeyError, AttributeError):
                bidang_options = [
                    ('hukum_pidana', 'HUKUM PIDANA'),
                    ('hukum_perdata', 'HUKUM PERDATA'),
                    ('hukum_administrasi_negara', 'HUKUM ADMINISTRASI NEGARA'),
                    ('hukum_tata_negara', 'HUKUM TATA NEGARA'),
                    ('hukum_internasional', 'HUKUM INTERNASIONAL'),
                    ('hukum_bisnis', 'HUKUM BISNIS'),
                    ('hukum_keluarga', 'HUKUM KELUARGA'),
                    ('hukum_lingkungan', 'HUKUM LINGKUNGAN'),
                    ('hukum_tenaga_kerja', 'HUKUM TENAGA KERJA'),
                    ('hukum_pajak', 'HUKUM PAJAK'),
                ]
                tipe_options = [
                    ('uud_1945', 'Undang-undang Dasar 1945'),
                    ('tap_mpr', 'Ketetapan MPR'),
                    ('undang_undang', 'Undang-Undang'),
                    ('perpu', 'Peraturan Pemerintah Pengganti Undang-Undang'),
                    ('peraturan_pemerintah', 'Peraturan Pemerintah'),
                    ('peraturan_presiden', 'Peraturan Presiden'),
                    ('keputusan_presiden', 'Keputusan Presiden'),
                    ('instruksi_presiden', 'Instruksi Presiden'),
                    ('peraturan_menteri', 'Peraturan Menteri'),
                    ('keputusan_menteri', 'Keputusan Menteri'),
                    ('peraturan_daerah', 'Peraturan Daerah'),
                    ('peraturan_gubernur', 'Peraturan Gubernur'),
                ]
        
            years = request.env['legal.regulation'].sudo().search([]).mapped('tahun')
            year_options = sorted(set(years), reverse=True) if years else []

            values = {
                'regulations': regulations,
                'search': search_term,
                'selected_bidang': kw.get('bidang', ''),
                'selected_tipe': kw.get('tipe', ''),
                'selected_tahun': kw.get('tahun', ''),
                'selected_status': kw.get('status', ''),
                'bidang_options': bidang_options,
                'tipe_options': tipe_options,
                'year_options': year_options,
                'total_count': total_count,
                'total_pages': total_pages,
                'current_page': current_page,
                'pasal_matches': pasal_matches,
            }
            
            return request.render('legal_website.regulations_list_template', values)
        
        except Exception as e:
            _logger.error(f"Error in regulations_list: {str(e)}", exc_info=True)
            return request.render('website.404')

    @http.route('/regulations/<int:regulation_id>', type='http', auth='public', website=True)
    def regulation_detail(self, regulation_id, **kw):
        """Halaman detail peraturan hukum"""
        try:
            # Cek apakah model legal.regulation tersedia
            if 'legal.regulation' not in request.env:
                return request.render('website.404')
                
            regulation = request.env['legal.regulation'].sudo().browse(regulation_id)
            
            if not regulation.exists():
                return request.render('website.404')

            # Related regulations (berdasarkan bidang yang sama)
            related_regulations = request.env['legal.regulation'].sudo().search([
                ('bidang', '=', regulation.bidang),
                ('id', '!=', regulation.id)
            ], limit=5, order='hierarchy_order, tahun desc')

            # Data Konsolidasi - perubahan UU
            perubahan_list = []
            has_perubahan = False
            konsolidasi_html = None
            
            import logging
            _logger = logging.getLogger(__name__)
            _logger.info(f"=== KONSOLIDASI DEBUG untuk regulation {regulation_id} ===")
            _logger.info(f"Regulation judul: {regulation.judul[:50] if regulation.judul else 'N/A'}...")
            _logger.info(f"Has file_txt: {bool(regulation.file_txt)}")
            _logger.info(f"Has perubahan_dari_ids attr: {hasattr(regulation, 'perubahan_dari_ids')}")
            
            try:
                # Cek apakah ada field perubahan_dari_ids
                if hasattr(regulation, 'perubahan_dari_ids'):
                    _logger.info(f"Perubahan count: {len(regulation.perubahan_dari_ids)}")
                    if regulation.perubahan_dari_ids:
                        has_perubahan = True
                        for perubahan in regulation.perubahan_dari_ids.sorted('sequence'):
                            _logger.info(f"  Perubahan: {perubahan.nama_perubahan}, file_txt: {bool(perubahan.file_txt_perubahan)}")
                            perubahan_data = {
                                'nama': perubahan.nama_perubahan or 'Perubahan',
                                'tahun': perubahan.tahun_perubahan,
                                'tanggal': perubahan.tanggal_perubahan,
                                'keterangan': perubahan.keterangan,
                                'isi_txt': None,
                                'isi_html': None,  # HTML terformat
                            }
                        
                            # Decode file TXT dan format dengan fungsi yang sama seperti UU Induk
                            if perubahan.file_txt_perubahan:
                                try:
                                    # Gunakan fungsi _extract_text_from_txt dari model yang sama dengan UU Induk
                                    # Ini akan menghasilkan format HTML yang konsisten
                                    formatted_html = regulation._extract_text_from_txt(perubahan.file_txt_perubahan)
                                    perubahan_data['isi_html'] = formatted_html
                                    perubahan_data['isi_txt'] = 'TXT_PROCESSED'  # Marker untuk debug
                                    _logger.info(f"HTML formatted using model function, length: {len(formatted_html) if formatted_html else 0}")
                                except Exception as format_err:
                                    _logger.error(f"Error formatting with model function: {str(format_err)}")
                                    # Fallback: decode manual
                                    import base64
                                    try:
                                        decoded = base64.b64decode(perubahan.file_txt_perubahan)
                                        raw_txt = decoded.decode('utf-8', errors='replace')
                                        perubahan_data['isi_txt'] = raw_txt
                                        perubahan_data['isi_html'] = f'<pre style="white-space: pre-wrap;">{raw_txt}</pre>'
                                    except:
                                        perubahan_data['isi_txt'] = None
                                        perubahan_data['isi_html'] = None
                            elif perubahan.peraturan_pengubah_id and perubahan.peraturan_pengubah_id.isi_peraturan:
                                perubahan_data['isi_txt'] = perubahan.peraturan_pengubah_id.isi_peraturan
                                perubahan_data['isi_html'] = perubahan.peraturan_pengubah_id.isi_peraturan
                            
                            perubahan_list.append(perubahan_data)
                        
                        # Generate konsolidasi on-the-fly jika ada perubahan
                        _logger.info(f"perubahan_list count: {len(perubahan_list)}")
                        if perubahan_list and regulation.file_txt:
                            konsolidasi_html = self._generate_consolidation_html(regulation, perubahan_list)
                            _logger.info(f"konsolidasi_html generated: {bool(konsolidasi_html)}")
                else:
                    _logger.info("No perubahan_dari_ids found")
            except Exception as e:
                import logging
                _logger = logging.getLogger(__name__)
                _logger.warning(f"Error loading perubahan data: {str(e)}")

            values = {
                'regulation': regulation,
                'related_regulations': related_regulations,
                'has_perubahan': has_perubahan,
                'perubahan_list': perubahan_list,
                'konsolidasi_html': konsolidasi_html,
            }
            
            return request.render('legal_website.regulation_detail_template', values)
            
        except Exception as e:
            # Log error and return 404 if something goes wrong
            import logging
            _logger = logging.getLogger(__name__)
            _logger.error(f"Error in regulation_detail: {str(e)}")
            return request.render('website.404')

    def _format_txt_to_html(self, txt_content):
        """Convert plain text to structured HTML like UU Induk format"""
        import re
        import html
        
        if not txt_content:
            return ""
        
        # Escape HTML characters first
        txt_content = html.escape(txt_content)
        
        lines = txt_content.split('\n')
        html_parts = []
        in_list_type = None  # 'ul' or 'ol' or None
        in_menimbang = False  # Track if we're in Menimbang/Mengingat section
        in_penjelasan = False  # Track if we're in Penjelasan section
        
        def close_list():
            nonlocal in_list_type
            if in_list_type == 'ul':
                html_parts.append('</ul>')
            elif in_list_type == 'ol':
                html_parts.append('</ol>')
            in_list_type = None
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                close_list()
                html_parts.append('<div style="height: 8px;"></div>')
                continue
            
            # === PENJELASAN SECTION ===
            # Detect "PENJELASAN" as main header
            if re.match(r'^PENJELASAN$', line, re.IGNORECASE):
                close_list()
                in_penjelasan = True
                html_parts.append(f'<div class="alert alert-info mt-4 mb-3"><h4 class="mb-0 text-center"><i class="fa fa-info-circle"></i> {line}</h4></div>')
                continue
            
            # Detect "PENJELASAN ATAS" or similar
            if re.match(r'^PENJELASAN\s+ATAS', line, re.IGNORECASE):
                close_list()
                in_penjelasan = True
                html_parts.append(f'<div class="alert alert-info mt-4 mb-2"><h5 class="mb-0 text-center">{line}</h5></div>')
                continue
            
            # Detect I. UMUM or II. PASAL DEMI PASAL in penjelasan
            if in_penjelasan and re.match(r'^[IVX]+\.\s+(UMUM|PASAL)', line, re.IGNORECASE):
                close_list()
                html_parts.append(f'<h5 class="mt-3 mb-2 fw-bold text-primary">{line}</h5>')
                continue
            
            # Detect "Penjelasan Pasal X" inline
            if re.match(r'^Penjelasan\s+Pasal\s+\d+', line, re.IGNORECASE):
                close_list()
                html_parts.append(f'<div class="alert alert-secondary mt-2 mb-2 py-2"><strong>{line}</strong></div>')
                continue
            
            # Detect [Penjelasan...] format
            if re.match(r'^\[Penjelasan', line, re.IGNORECASE):
                close_list()
                html_parts.append(f'<div class="bg-light border-start border-info border-4 p-2 mt-2 mb-2"><em class="text-muted">{line}</em></div>')
                continue
            
            # Detect "Cukup jelas" or similar penjelasan text
            if re.match(r'^Cukup\s+jelas', line, re.IGNORECASE):
                close_list()
                html_parts.append(f'<p class="text-muted fst-italic ps-4">{line}</p>')
                continue
            
            # === HEADER UTAMA ===
            if re.match(r'^(UNDANG-UNDANG|PERATURAN PEMERINTAH|PERATURAN PRESIDEN)', line, re.IGNORECASE):
                close_list()
                in_menimbang = False
                html_parts.append(f'<h3 class="text-center fw-bold text-uppercase mt-3">{line}</h3>')
                continue
            
            if re.match(r'^(PRESIDEN|REPUBLIK INDONESIA|NOMOR\s+\d+|TENTANG|SALINAN|DENGAN RAHMAT|PERUBAHAN ATAS)', line, re.IGNORECASE):
                close_list()
                html_parts.append(f'<p class="text-center fw-bold mb-1">{line}</p>')
                continue
            
            # === BAB, BAGIAN, PARAGRAF ===
            if re.match(r'^BAB\s+[IVXLCDM]+', line, re.IGNORECASE):
                close_list()
                in_menimbang = False
                html_parts.append(f'<h4 class="mt-4 mb-2 text-primary fw-bold text-center">{line}</h4>')
                continue
            
            if re.match(r'^Bagian\s+(Ke)?', line, re.IGNORECASE):
                close_list()
                html_parts.append(f'<h5 class="mt-3 mb-2 text-info fw-bold text-center">{line}</h5>')
                continue
            
            if re.match(r'^Paragraf\s+\d+', line, re.IGNORECASE):
                close_list()
                html_parts.append(f'<h6 class="mt-3 mb-2 text-secondary fw-bold">{line}</h6>')
                continue
            
            # === PASAL ===
            if re.match(r'^Pasal\s+\d+[A-Z]?$', line, re.IGNORECASE):
                close_list()
                in_menimbang = False
                html_parts.append(f'<p class="mt-4 mb-2 fw-bold text-dark" style="border-left: 4px solid #007bff; padding-left: 12px; font-size: 1.1em;">{line}</p>')
                continue
            
            # === MENIMBANG, MENGINGAT, MEMUTUSKAN ===
            menimbang_match = re.match(r'^(Menimbang|Mengingat|Memutuskan|Menetapkan)\s*:', line, re.IGNORECASE)
            if menimbang_match:
                close_list()
                in_menimbang = True
                html_parts.append(f'<p class="mt-3 mb-1 fw-bold">{line}</p>')
                continue
            
            # === HURUF a., b., c., etc. (with proper indentation) ===
            huruf_match = re.match(r'^([a-z])\.\s*(.*)$', line)
            if huruf_match:
                if in_list_type != 'ul':
                    close_list()
                    # Extra indent if inside Menimbang section
                    indent_class = "ps-5" if in_menimbang else "ps-4"
                    html_parts.append(f'<ul class="list-unstyled {indent_class} mb-0">')
                    in_list_type = 'ul'
                huruf = huruf_match.group(1)
                huruf_text = huruf_match.group(2)
                html_parts.append(f'<li class="mb-2" style="text-indent: -1.5em; padding-left: 1.5em;"><strong>{huruf}.</strong> {huruf_text}</li>')
                continue
            
            # === AYAT (1), (2), etc. ===
            ayat_match = re.match(r'^\((\d+)\)\s*(.*)$', line)
            if ayat_match:
                close_list()
                in_menimbang = False
                ayat_num = ayat_match.group(1)
                ayat_text = ayat_match.group(2)
                html_parts.append(f'<p class="mb-2 ps-3" style="text-indent: -2em; padding-left: 2.5em;"><strong>({ayat_num})</strong> {ayat_text}</p>')
                continue
            
            # === NUMBERED LIST 1., 2., etc. ===
            num_match = re.match(r'^(\d+)\.\s+(.+)$', line)
            if num_match:
                num = num_match.group(1)
                num_text = num_match.group(2)
                if len(num_text) < 150:
                    if in_list_type != 'ol':
                        close_list()
                        indent_class = "ps-5" if in_menimbang else "ps-4"
                        html_parts.append(f'<ol class="{indent_class} mb-0" style="list-style-position: outside;">')
                        in_list_type = 'ol'
                    html_parts.append(f'<li class="mb-2">{num_text}</li>')
                    continue
                else:
                    close_list()
                    html_parts.append(f'<p class="mb-2 ps-4"><strong>{num}.</strong> {num_text}</p>')
                    continue
            
            # === REGULAR PARAGRAPH ===
            close_list()
            # Add indent if in menimbang section
            if in_menimbang:
                html_parts.append(f'<p class="mb-2 ps-4">{line}</p>')
            else:
                html_parts.append(f'<p class="mb-2">{line}</p>')
        
        close_list()
        
        # Wrap everything in a container with proper styling
        result = '<div class="formatted-regulation" style="line-height: 1.7; text-align: justify;">\n' + '\n'.join(html_parts) + '\n</div>'
        return result

    def _generate_consolidation_html(self, regulation, perubahan_list):
        """Generate HTML konsolidasi dari UU Induk + Perubahan"""
        import base64
        import re
        
        try:
            # Decode file TXT induk
            txt_induk = ""
            if regulation.file_txt:
                decoded = base64.b64decode(regulation.file_txt)
                try:
                    txt_induk = decoded.decode('utf-8')
                except UnicodeDecodeError:
                    txt_induk = decoded.decode('latin-1')
            
            if not txt_induk:
                return None
            
            # Parse pasal dari induk
            pasal_induk = self._parse_pasal_from_text(txt_induk)
            
            # Parse pasal dari setiap perubahan
            perubahan_pasal_list = []
            for perubahan in perubahan_list:
                if perubahan.get('isi_txt'):
                    # Jika isi_txt adalah HTML, strip tags
                    isi = perubahan['isi_txt']
                    if '<' in str(isi) and '>' in str(isi):
                        isi = re.sub(r'<[^>]+>', ' ', str(isi))
                    pasal_perubahan = self._parse_pasal_from_text(isi)
                    perubahan_pasal_list.append({
                        'nama': perubahan['nama'],
                        'tahun': perubahan['tahun'],
                        'pasal': pasal_perubahan
                    })
            
            # Generate HTML konsolidasi
            return self._build_consolidation_html(regulation, pasal_induk, perubahan_pasal_list)
            
        except Exception as e:
            import logging
            _logger = logging.getLogger(__name__)
            _logger.error(f"Error generating consolidation: {str(e)}")
            return None

    def _parse_pasal_from_text(self, text):
        """Parse text menjadi struktur pasal"""
        import re
        
        if not text:
            return {}
        
        pasal_dict = {}
        
        # Pattern untuk mendeteksi awal Pasal
        pasal_pattern = re.compile(
            r'(?:^|\n)\s*(Pasal\s+(\d+[A-Z]?))\s*[\.\n]?',
            re.MULTILINE | re.IGNORECASE
        )
        
        matches = list(pasal_pattern.finditer(text))
        
        if not matches:
            return {}
        
        for i, match in enumerate(matches):
            pasal_judul = match.group(1)
            pasal_no = match.group(2)
            
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            
            isi = text[start:end].strip()
            
            pasal_dict[pasal_no] = {
                'judul': pasal_judul,
                'nomor': pasal_no,
                'isi': isi
            }
        
        return pasal_dict

    def _build_consolidation_html(self, regulation, pasal_induk, perubahan_pasal_list):
        """Build HTML konsolidasi dengan highlight perubahan"""
        import re
        
        html_parts = []
        
        # CSS Styles
        html_parts.append("""
        <style>
            .konsolidasi-container { font-family: 'Segoe UI', sans-serif; }
            .konsolidasi-legend { 
                background: #f8f9fa; 
                padding: 15px; 
                border-radius: 8px; 
                margin-bottom: 20px;
                border: 1px solid #dee2e6;
            }
            .legend-item { 
                display: inline-flex; 
                align-items: center; 
                margin-right: 20px; 
                margin-bottom: 5px;
            }
            .legend-badge { 
                display: inline-block; 
                width: 20px; 
                height: 20px; 
                border-radius: 4px; 
                margin-right: 8px;
            }
            .badge-unchanged { background: #28a745; }
            .badge-modified { background: #ffc107; }
            .badge-added { background: #17a2b8; }
            .badge-deleted { background: #dc3545; }
            
            .pasal-item {
                margin-bottom: 20px;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .pasal-header {
                padding: 12px 15px;
                font-weight: bold;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            .pasal-content {
                padding: 15px;
                background: white;
                line-height: 1.8;
            }
            
            .pasal-unchanged { border-left: 5px solid #28a745; }
            .pasal-unchanged .pasal-header { background: #d4edda; color: #155724; }
            
            .pasal-modified { border-left: 5px solid #ffc107; }
            .pasal-modified .pasal-header { background: #fff3cd; color: #856404; }
            
            .pasal-added { border-left: 5px solid #17a2b8; }
            .pasal-added .pasal-header { background: #d1ecf1; color: #0c5460; }
            
            .pasal-deleted { border-left: 5px solid #dc3545; }
            .pasal-deleted .pasal-header { background: #f8d7da; color: #721c24; }
            .pasal-deleted .pasal-content { text-decoration: line-through; opacity: 0.7; }
            
            .status-badge {
                font-size: 0.75em;
                padding: 3px 8px;
                border-radius: 12px;
                font-weight: normal;
            }
            .status-unchanged { background: #28a745; color: white; }
            .status-modified { background: #ffc107; color: #000; }
            .status-added { background: #17a2b8; color: white; }
            .status-deleted { background: #dc3545; color: white; }
            
            .change-info {
                background: #fff3cd;
                border-left: 3px solid #ffc107;
                padding: 10px;
                margin-top: 10px;
                font-size: 0.9em;
                border-radius: 0 4px 4px 0;
            }
        </style>
        """)
        
        # Header
        html_parts.append(f"""
        <div class="konsolidasi-container">
            <div class="konsolidasi-legend">
                <strong>🏷️ Keterangan Warna:</strong>
                <div class="mt-2">
                    <span class="legend-item"><span class="legend-badge badge-unchanged"></span> Tidak Berubah (Asli)</span>
                    <span class="legend-item"><span class="legend-badge badge-modified"></span> Diubah</span>
                    <span class="legend-item"><span class="legend-badge badge-added"></span> Ditambahkan</span>
                    <span class="legend-item"><span class="legend-badge badge-deleted"></span> Dihapus</span>
                </div>
            </div>
        """)
        
        # Kumpulkan semua pasal
        all_pasal = set(pasal_induk.keys())
        for data in perubahan_pasal_list:
            all_pasal.update(data['pasal'].keys())
        
        # Sort pasal numbers
        def sort_key(x):
            match = re.match(r'(\d+)([A-Z]?)', str(x), re.IGNORECASE)
            if match:
                return (int(match.group(1)), match.group(2))
            return (0, str(x))
        
        sorted_pasal = sorted(all_pasal, key=sort_key)
        
        # Process setiap pasal
        for pasal_no in sorted_pasal:
            induk = pasal_induk.get(pasal_no)
            
            # Cari versi terbaru dari perubahan
            latest_version = None
            change_info = []
            
            for data in perubahan_pasal_list:
                if pasal_no in data['pasal']:
                    latest_version = data['pasal'][pasal_no]
                    change_info.append(f"Diubah oleh {data['nama']} ({data['tahun'] or '?'})")
            
            # Tentukan status
            if induk and not latest_version:
                # Pasal tetap dari induk
                status = 'unchanged'
                status_text = 'Tidak Berubah'
                content = self._escape_html(induk['isi'])
                info = None
            elif induk and latest_version:
                # Pasal ada di induk DAN ada perubahan
                if induk['isi'].strip() == latest_version['isi'].strip():
                    status = 'unchanged'
                    status_text = 'Tidak Berubah'
                    content = self._escape_html(induk['isi'])
                    info = None
                else:
                    status = 'modified'
                    status_text = 'Diubah'
                    content = self._escape_html(latest_version['isi'])
                    info = '<br>'.join(change_info)
            elif not induk and latest_version:
                # Pasal baru
                status = 'added'
                status_text = 'Ditambahkan'
                content = self._escape_html(latest_version['isi'])
                info = '<br>'.join(change_info)
            else:
                continue
            
            # Format content
            content = self._format_pasal_content(content)
            
            # Build HTML
            html_parts.append(f"""
            <div class="pasal-item pasal-{status}">
                <div class="pasal-header">
                    <span>Pasal {pasal_no}</span>
                    <span class="status-badge status-{status}">{status_text}</span>
                </div>
                <div class="pasal-content">
                    {content}
                    {f'<div class="change-info">📝 {info}</div>' if info else ''}
                </div>
            </div>
            """)
        
        html_parts.append('</div>')
        
        return '\n'.join(html_parts)

    def _escape_html(self, text):
        """Escape HTML characters"""
        if not text:
            return ""
        return (str(text)
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;'))

    def _format_pasal_content(self, text):
        """Format plain text menjadi HTML yang readable"""
        import re
        if not text:
            return ""
        
        # Format ayat (1), (2), dst
        text = re.sub(r'\((\d+)\)', r'<br/><strong>(\1)</strong>', text)
        
        # Format huruf a., b., dst
        text = re.sub(r'\n([a-z])\.\s', r'<br/>&nbsp;&nbsp;&nbsp;&nbsp;<strong>\1.</strong> ', text)
        
        # Newlines
        text = text.replace('\n', '<br/>')
        
        return text

    @http.route('/regulations/search', type='json', auth='public', website=True)
    def regulations_search_ajax(self, **kw):
        """AJAX search untuk autocomplete - termasuk pencarian dalam pasal/ayat"""
        try:
            # Cek apakah model legal.regulation tersedia
            if 'legal.regulation' not in request.env:
                return {'results': []}
                
            query = kw.get('query', '').strip()
            if len(query) < 3:
                return {'results': []}

            # Enhanced search for AJAX
            search_fields = [
                ('judul', 'ilike', query),
                ('nomor', 'ilike', query),
                ('bentuk_singkat', 'ilike', query),
                ('subjek', 'ilike', query),
                ('keterangan', 'ilike', query),
                ('bentuk', 'ilike', query)
            ]
            
            # Tambahkan field enhanced jika ada
            try:
                model_fields = request.env['legal.regulation']._fields
                if 'isi_peraturan' in model_fields:
                    search_fields.append(('isi_peraturan', 'ilike', query))
                if 'kata_kunci' in model_fields:
                    search_fields.append(('kata_kunci', 'ilike', query))
                if 'ringkasan' in model_fields:
                    search_fields.append(('ringkasan', 'ilike', query))
            except Exception:
                pass
            
            # Deep search in pasal/ayat/huruf
            regulation_ids_from_pasal = set()
            try:
                Pasal = request.env['legal.regulation.pasal'].sudo()
                Ayat = request.env['legal.regulation.ayat'].sudo()
                Huruf = request.env['legal.regulation.huruf'].sudo()
                
                pasal_reg_ids = Pasal.search([
                    '|', '|',
                    ('isi_pasal', 'ilike', query),
                    ('judul_pasal', 'ilike', query),
                    ('nomor_pasal', 'ilike', query),
                ]).mapped('regulation_id.id')
                
                ayat_reg_ids = Ayat.search([
                    ('isi_ayat', 'ilike', query),
                ]).mapped('regulation_id.id')
                
                huruf_reg_ids = Huruf.search([
                    ('isi', 'ilike', query),
                ]).mapped('regulation_id.id')
                
                regulation_ids_from_pasal = set(pasal_reg_ids) | set(ayat_reg_ids) | set(huruf_reg_ids)
            except Exception:
                pass
            
            # Build domain
            if len(search_fields) > 1:
                or_conditions = ['|'] * (len(search_fields) - 1)
                reg_field_domain = or_conditions + search_fields
            else:
                reg_field_domain = list(search_fields)
            
            if regulation_ids_from_pasal:
                domain = ['|', ('id', 'in', list(regulation_ids_from_pasal))]
                domain.extend(reg_field_domain)
            else:
                domain = reg_field_domain

            regulations = request.env['legal.regulation'].sudo().search(domain, limit=10)
            
            # Get pasal matches for each result
            pasal_matches = {}
            if regulations:
                pasal_matches = self._search_pasal_matches(
                    regulations.ids, query, limit_per_reg=3
                )
            
            results = []
            for reg in regulations:
                result = {
                    'id': reg.id,
                    'title': reg.judul,
                    'number': f"{reg.bentuk_singkat} No. {reg.nomor}/{reg.tahun}",
                    'url': f"/regulations/{reg.id}",
                    'pasal_matches': [],
                }
                # Add pasal match info
                if reg.id in pasal_matches:
                    for m in pasal_matches[reg.id]:
                        result['pasal_matches'].append({
                            'display': m.get('display', ''),
                            'bab': m.get('bab', ''),
                            'snippet': self._get_snippet_around_keyword(
                                m.get('snippet', ''), query, context_chars=80
                            ),
                        })
                results.append(result)

            return {'results': results}
            
        except Exception as e:
            _logger.error(f"Error in regulations_search_ajax: {str(e)}")
            return {'results': []}