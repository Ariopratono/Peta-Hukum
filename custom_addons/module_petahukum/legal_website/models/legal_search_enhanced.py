# -*- coding: utf-8 -*-
from odoo import models, fields, api
import requests
import json
import logging
from urllib.parse import quote_plus

_logger = logging.getLogger(__name__)

class LegalSearchEnhanced(models.Model):
    _name = 'legal.search.enhanced'
    _description = 'Enhanced Legal Search Configuration'
    
    name = fields.Char('Nama Konfigurasi', required=True)
    search_type = fields.Selection([
        ('searxng', 'SearXNG Instance'),
        ('duckduckgo', 'DuckDuckGo API'),
        ('custom', 'Custom Search'),
        ('mock', 'Mock Search (Demo)')
    ], default='mock', string='Tipe Pencarian')
    
    # SearXNG Configuration
    searxng_url = fields.Char('SearXNG URL')
    search_engines = fields.Text('Search Engines', default='google,bing,duckduckgo')
    categories = fields.Text('Categories', default='general')
    
    # DuckDuckGo Configuration  
    duckduckgo_api = fields.Char('DuckDuckGo API URL', default='https://api.duckduckgo.com')
    
    # General Configuration
    language = fields.Char('Language', default='id')
    safe_search = fields.Selection([
        ('0', 'None'),
        ('1', 'Moderate'),
        ('2', 'Strict')
    ], default='1', string='Safe Search')
    timeout = fields.Float('Timeout (seconds)', default=10.0)
    max_results = fields.Integer('Max Results', default=20)
    active = fields.Boolean('Active', default=True)

    @api.model
    def get_active_config(self):
        """Get the active search configuration"""
        config = self.search([('active', '=', True)], limit=1)
        if not config:
            # Create default mock config if none exists
            config = self.create({
                'name': 'Demo Search Config',
                'search_type': 'mock',
                'active': True
            })
        return config

    def search_web(self, query, page=1, per_page=10):
        """Search web using configured method"""
        try:
            if self.search_type == 'searxng':
                return self._search_searxng(query, page, per_page)
            elif self.search_type == 'duckduckgo':
                return self._search_duckduckgo(query, page, per_page)
            elif self.search_type == 'mock':
                return self._search_mock(query, page, per_page)
            else:
                return self._search_custom(query, page, per_page)
                
        except Exception as e:
            _logger.error(f"Search error: {str(e)}")
            return {'error': f'Search error: {str(e)}'}

    def _search_searxng(self, query, page=1, per_page=10):
        """Search using SearXNG API"""
        if not self.searxng_url:
            return {'error': 'SearXNG URL not configured'}
            
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
            headers={
                'User-Agent': 'Legal Website Search Bot',
                'Accept': 'application/json'
            },
            verify=False  # Skip SSL verification for demo
        )
        
        if response.status_code == 200:
            data = response.json()
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
            
            enhanced_results.sort(key=lambda x: x['score'], reverse=True)
            
            return {
                'results': enhanced_results[:per_page],
                'total': len(enhanced_results),
                'query': query,
                'page': page,
                'suggestions': data.get('suggestions', [])
            }
        else:
            return {'error': f'SearXNG API error: {response.status_code}'}

    def _search_duckduckgo(self, query, page=1, per_page=10):
        """Search using DuckDuckGo Instant Answer API"""
        try:
            params = {
                'q': query + ' hukum indonesia',
                'format': 'json',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            response = requests.get(
                self.duckduckgo_api or 'https://api.duckduckgo.com',
                params=params,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                
                results = []
                
                # Add instant answer if available
                if data.get('Answer'):
                    results.append({
                        'title': 'DuckDuckGo Instant Answer',
                        'url': data.get('AbstractURL', '#'),
                        'content': data.get('Answer', ''),
                        'engine': 'duckduckgo',
                        'category': 'instant',
                        'score': 95
                    })
                
                # Add related topics
                for topic in data.get('RelatedTopics', [])[:5]:
                    if isinstance(topic, dict) and topic.get('Text'):
                        results.append({
                            'title': topic.get('Text', '')[:60] + '...',
                            'url': topic.get('FirstURL', '#'),
                            'content': topic.get('Text', ''),
                            'engine': 'duckduckgo',
                            'category': 'related',
                            'score': 80
                        })
                
                return {
                    'results': results[:per_page],
                    'total': len(results),
                    'query': query,
                    'page': page,
                    'suggestions': []
                }
            else:
                return {'error': f'DuckDuckGo API error: {response.status_code}'}
                
        except Exception as e:
            return {'error': f'DuckDuckGo search error: {str(e)}'}

    def _search_mock(self, query, page=1, per_page=10):
        """Mock search for demo purposes"""
        
        # Generate mock results based on query
        mock_results = []
        
        legal_keywords = ['hukum', 'pidana', 'perdata', 'kuhp', 'undang', 'pasal', 'sanksi']
        query_lower = query.lower()
        
        # Legal websites mock data
        legal_sites = [
            {
                'domain': 'mahkamahagung.go.id',
                'name': 'Mahkamah Agung RI',
                'desc': 'Portal resmi Mahkamah Agung Republik Indonesia'
            },
            {
                'domain': 'bphn.go.id', 
                'name': 'BPHN Kemenkumham',
                'desc': 'Badan Pembinaan Hukum Nasional'
            },
            {
                'domain': 'hukumonline.com',
                'name': 'HukumOnline',
                'desc': 'Portal hukum terlengkap di Indonesia'
            },
            {
                'domain': 'legalakses.com',
                'name': 'Legal Akses',
                'desc': 'Platform konsultasi hukum online'
            }
        ]
        
        # Generate results for each site
        for i, site in enumerate(legal_sites):
            score = 85 - (i * 5)
            
            # Boost score if query matches legal keywords
            for keyword in legal_keywords:
                if keyword in query_lower:
                    score += 10
                    break
            
            # Create different content based on query
            if 'pidana' in query_lower:
                content = f"Informasi lengkap tentang hukum pidana Indonesia dari {site['name']}. Termasuk KUHP, sanksi pidana, dan prosedur peradilan."
                title = f"Hukum Pidana Indonesia - {site['name']}"
            elif 'perdata' in query_lower:
                content = f"Panduan hukum perdata dari {site['name']}. Mencakup kontrak, warisan, dan sengketa perdata lainnya."
                title = f"Hukum Perdata Indonesia - {site['name']}"
            elif 'kuhp' in query_lower:
                content = f"Kitab Undang-Undang Hukum Pidana (KUHP) terbaru dari {site['name']}. Pasal-pasal pidana dan penjelasannya."
                title = f"KUHP Terbaru - {site['name']}"
            else:
                content = f"Informasi hukum terkait '{query}' dari {site['name']}. {site['desc']}"
                title = f"{query.title()} - {site['name']}"
            
            mock_results.append({
                'title': title,
                'url': f"https://{site['domain']}/search?q={quote_plus(query)}",
                'content': content,
                'engine': 'mock',
                'category': 'legal',
                'score': score
            })
        
        # Add some general results
        general_results = [
            {
                'title': f'Wikipedia: {query.title()}',
                'url': f'https://id.wikipedia.org/wiki/{quote_plus(query)}',
                'content': f'Artikel Wikipedia tentang {query} dalam bahasa Indonesia.',
                'engine': 'mock',
                'category': 'encyclopedia', 
                'score': 70
            },
            {
                'title': f'Konsultasi Hukum: {query.title()}',
                'url': f'https://konsultasihukum.com/topic/{quote_plus(query)}',
                'content': f'Forum diskusi dan konsultasi hukum tentang {query}.',
                'engine': 'mock',
                'category': 'forum',
                'score': 65
            }
        ]
        
        mock_results.extend(general_results)
        
        # Sort by score
        mock_results.sort(key=lambda x: x['score'], reverse=True)
        
        # Pagination
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        page_results = mock_results[start_idx:end_idx]
        
        return {
            'results': page_results,
            'total': len(mock_results),
            'query': query,
            'page': page,
            'suggestions': [
                'hukum pidana indonesia',
                'kuhp terbaru 2024',
                'sanksi hukum korupsi',
                'konsultasi hukum gratis'
            ]
        }

    def _search_custom(self, query, page=1, per_page=10):
        """Custom search implementation"""
        return {
            'results': [],
            'total': 0,
            'query': query,
            'page': page,
            'error': 'Custom search not implemented'
        }

    def _calculate_legal_relevance(self, result, query):
        """Calculate relevance score for legal content"""
        score = 50  # Base score
        
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
                score += 15
            if keyword in content:
                score += 8
            if keyword in url:
                score += 5
        
        # Query term matching
        query_terms = query_lower.split()
        for term in query_terms:
            if len(term) > 2:  # Skip short words
                if term in title:
                    score += 12
                if term in content:
                    score += 6
                if term in url:
                    score += 3
        
        # Domain authority for legal sites
        legal_domains = [
            'mahkamahagung.go.id', 'bphn.go.id', 'kemenag.go.id',
            'kemenkumham.go.id', 'kpk.go.id', 'kejaksaan.go.id',
            'hukumonline.com', 'legalakses.com', 'detik.com',
            'kompas.com', 'tempo.co'
        ]
        
        for domain in legal_domains:
            if domain in url:
                score += 20
                break
        
        # Government domain boost
        if '.go.id' in url:
            score += 25
        
        return min(score, 100)  # Cap at 100