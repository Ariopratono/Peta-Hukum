# -*- coding: utf-8 -*-
from odoo import models, fields, api
import requests
import json
import logging

_logger = logging.getLogger(__name__)

class LegalSearch(models.Model):
    _name = 'legal.search'
    _description = 'Legal Search Configuration'
    
    name = fields.Char('Nama Konfigurasi', required=True)
    searxng_url = fields.Char('SearXNG URL', required=True, default='https://search.brave4u.com')
    search_engines = fields.Text('Search Engines', default='google,bing,duckduckgo')
    categories = fields.Text('Categories', default='general')
    language = fields.Char('Language', default='id')
    safe_search = fields.Selection([
        ('0', 'None'),
        ('1', 'Moderate'),
        ('2', 'Strict')
    ], default='1', string='Safe Search')
    timeout = fields.Float('Timeout (seconds)', default=5.0)
    active = fields.Boolean('Active', default=True)

    @api.model
    def get_active_config(self):
        """Get the active search configuration"""
        config = self.search([('active', '=', True)], limit=1)
        if not config:
            # Create default config if none exists
            config = self.create({
                'name': 'Default SearXNG Config',
                'searxng_url': 'https://search.brave4u.com',
                'search_engines': 'google,bing,duckduckgo',
                'categories': 'general',
                'language': 'id',
                'safe_search': '1',
                'active': True
            })
        return config

    def search_web(self, query, page=1, per_page=10):
        """Search web using SearXNG API"""
        try:
            params = {
                'q': query,
                'format': 'json',
                'engines': self.search_engines,
                'categories': self.categories,
                'language': self.language,
                'safesearch': self.safe_search,
                'pageno': page,
            }
            
            response = requests.get(
                f"{self.searxng_url}/search",
                params=params,
                timeout=self.timeout,
                headers={'User-Agent': 'Legal Website Search Bot'}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Filter and enhance results for legal content
                enhanced_results = []
                for result in data.get('results', []):
                    enhanced_result = {
                        'title': result.get('title', ''),
                        'url': result.get('url', ''),
                        'content': result.get('content', ''),
                        'engine': result.get('engine', ''),
                        'category': result.get('category', ''),
                        'score': self._calculate_legal_relevance(result, query)
                    }
                    enhanced_results.append(enhanced_result)
                
                # Sort by relevance score
                enhanced_results.sort(key=lambda x: x['score'], reverse=True)
                
                return {
                    'results': enhanced_results[:per_page],
                    'total': len(enhanced_results),
                    'query': query,
                    'page': page,
                    'suggestions': data.get('suggestions', [])
                }
            else:
                _logger.error(f"SearXNG API error: {response.status_code}")
                return {'error': f'Search service error: {response.status_code}'}
                
        except requests.RequestException as e:
            _logger.error(f"SearXNG connection error: {str(e)}")
            return {'error': f'Connection error: {str(e)}'}
        except Exception as e:
            _logger.error(f"SearXNG search error: {str(e)}")
            return {'error': f'Search error: {str(e)}'}
    
    def _calculate_legal_relevance(self, result, query):
        """Calculate relevance score for legal content"""
        score = 0
        title = result.get('title', '').lower()
        content = result.get('content', '').lower()
        url = result.get('url', '').lower()
        query_lower = query.lower()
        
        # Legal keywords boost
        legal_keywords = [
            'hukum', 'undang-undang', 'peraturan', 'pidana', 'perdata', 
            'konstitusi', 'mahkamah', 'pengadilan', 'jaksa', 'advokat',
            'kuhp', 'kuhap', 'kitab', 'pasal', 'ayat', 'sanksi', 'denda',
            'penjara', 'tindak pidana', 'perbuatan melawan hukum'
        ]
        
        for keyword in legal_keywords:
            if keyword in title:
                score += 10
            if keyword in content:
                score += 5
            if keyword in url:
                score += 3
        
        # Query term matching
        query_terms = query_lower.split()
        for term in query_terms:
            if term in title:
                score += 8
            if term in content:
                score += 4
        
        # Domain authority for legal sites
        legal_domains = [
            'mahkamahagung.go.id', 'bphn.go.id', 'kemenag.go.id',
            'kemenkumham.go.id', 'kpk.go.id', 'kejaksaan.go.id',
            'hukumonline.com', 'legalakses.com'
        ]
        
        for domain in legal_domains:
            if domain in url:
                score += 15
                break
        
        return score

class LegalSearchHistory(models.Model):
    _name = 'legal.search.history'
    _description = 'Legal Search History'
    _order = 'create_date desc'
    
    query = fields.Char('Search Query', required=True)
    user_id = fields.Many2one('res.users', 'User', default=lambda self: self.env.user)
    results_count = fields.Integer('Results Count')
    ip_address = fields.Char('IP Address')
    user_agent = fields.Text('User Agent')
    create_date = fields.Datetime('Search Date', default=fields.Datetime.now)
    
    @api.model
    def log_search(self, query, results_count=0, request=None):
        """Log search query"""
        values = {
            'query': query,
            'results_count': results_count,
        }
        
        if request:
            values.update({
                'ip_address': request.httprequest.remote_addr,
                'user_agent': request.httprequest.headers.get('User-Agent', '')
            })
        
        return self.create(values)