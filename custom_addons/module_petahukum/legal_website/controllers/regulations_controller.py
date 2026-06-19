# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class LegalRegulationWebsiteController(http.Controller):

    @http.route('/regulations', type='http', auth='public', website=True)
    def regulations_list(self, **kw):
        """Halaman daftar peraturan hukum"""
        try:
            # Cek apakah model legal.regulation tersedia
            if 'legal.regulation' not in request.env:
                return request.render('legal_website.regulations_empty_template')
            
            # Filter dan search
            domain = []
            
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
                
            if kw.get('search'):
                search_term = kw.get('search')
                # cek field yang tersedia
                search_fields = [
                    ('judul', 'ilike', search_term),
                    ('nomor', 'ilike', search_term), 
                    ('bentuk_singkat', 'ilike', search_term),
                    ('subjek', 'ilike', search_term),
                    ('keterangan', 'ilike', search_term),
                    ('bentuk', 'ilike', search_term)
                ]
                
                # Tambahkan field enhanced jika ada
                try:
                    model_fields = request.env['legal.regulation']._fields
                    if 'isi_peraturan' in model_fields:
                        search_fields.append(('isi_peraturan', 'ilike', search_term))
                    if 'kata_kunci' in model_fields:
                        search_fields.append(('kata_kunci', 'ilike', search_term))
                    if 'ringkasan' in model_fields:
                        search_fields.append(('ringkasan', 'ilike', search_term))
                except:
                    pass
                
                # Build domain dengan OR conditions
                if len(search_fields) > 1:
                    or_conditions = ['|'] * (len(search_fields) - 1)
                    domain.extend(or_conditions + search_fields)

            # Pagination
            limit = 20
            page = int(kw.get('page', 1))
            offset = (page - 1) * limit

            regulations = request.env['legal.regulation'].sudo().search(domain, limit=limit, offset=offset, order='hierarchy_order, tahun desc, nomor')
            total_count = request.env['legal.regulation'].sudo().search_count(domain)
            
            # Pagination info (manual pagination instead of Odoo pager to avoid debug output)
            total_pages = (total_count - 1) // limit + 1 if total_count > 0 else 1
            current_page = page

            # Data untuk filter dengan error handling
            try:
                bidang_options = request.env['legal.regulation']._fields['bidang'].selection
                tipe_options = request.env['legal.regulation']._fields['tipe_dokumen'].selection
            except (KeyError, AttributeError):
                # Fallback options jika field tidak ditemukan
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
                'search': kw.get('search', ''),
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
            }
            
            return request.render('legal_website.regulations_list_template', values)
        
        except Exception as e:
            # Log error and return 404 if something goes wrong
            import logging
            _logger = logging.getLogger(__name__)
            _logger.error(f"Error in regulations_list: {str(e)}")
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

            values = {
                'regulation': regulation,
                'related_regulations': related_regulations,
            }
            
            return request.render('legal_website.regulation_detail_template', values)
            
        except Exception as e:
            # Log error and return 404 if something goes wrong
            import logging
            _logger = logging.getLogger(__name__)
            _logger.error(f"Error in regulation_detail: {str(e)}")
            return request.render('website.404')

    @http.route('/regulations/search', type='json', auth='public', website=True)
    def regulations_search_ajax(self, **kw):
        """AJAX search untuk autocomplete"""
        try:
            # Cek apakah model legal.regulation tersedia
            if 'legal.regulation' not in request.env:
                return {'results': []}
                
            query = kw.get('query', '')
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
            except:
                pass
            
            # Build domain
            if len(search_fields) > 1:
                or_conditions = ['|'] * (len(search_fields) - 1)
                domain = or_conditions + search_fields
            else:
                domain = search_fields

            regulations = request.env['legal.regulation'].sudo().search(domain, limit=10)
            
            results = []
            for reg in regulations:
                results.append({
                    'id': reg.id,
                    'title': reg.judul,
                    'number': f"{reg.bentuk_singkat} No. {reg.nomor}/{reg.tahun}",
                    'url': f"/regulations/{reg.id}"
                })

            return {'results': results}
            
        except Exception as e:
            # Log error and return empty results
            import logging
            _logger = logging.getLogger(__name__)
            _logger.error(f"Error in regulations_search_ajax: {str(e)}")
            return {'results': []}