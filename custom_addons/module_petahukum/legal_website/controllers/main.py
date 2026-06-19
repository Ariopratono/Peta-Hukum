# -*- coding: utf-8 -*-
# pylint: disable=import-error

from odoo import http
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)

class LegalWebsiteController(http.Controller):
    
    @http.route('/test-subscription', type='http', auth='public', website=True)
    def test_subscription(self, **kw):
        """Test subscription route"""
        return "<h1>Test Subscription Route Working!</h1><p>If you see this, routes are working.</p><a href='/subscription/pricing'>Go to Pricing</a>"
    
    @http.route('/subscription/pricing', type='http', auth='public', website=True)
    def subscription_pricing_main(self, **kw):
        """Backup subscription pricing route"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Subscription Pricing - Legal Website</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        </head>
        <body>
            <nav class="navbar navbar-expand-lg navbar-dark" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                <div class="container">
                    <a class="navbar-brand" href="/"><i class="fas fa-balance-scale"></i> Legal Website</a>
                    <div class="navbar-nav ms-auto">
                        <a class="nav-link" href="/">Home</a>
                        <a class="nav-link" href="/legal">Search</a>
                        <a class="nav-link active" href="/subscription/pricing">Pricing</a>
                    </div>
                </div>
            </nav>

            <div class="container my-5">
                <div class="text-center mb-5">
                    <h1 class="display-4">Choose Your Plan</h1>
                    <p class="lead text-muted">Select the perfect subscription plan for your legal needs</p>
                </div>

                <div class="row g-4">
                    <div class="col-md-6 col-lg-3">
                        <div class="card h-100 shadow-sm">
                            <div class="card-body text-center">
                                <h5 class="card-title">Free</h5>
                                <h2 class="text-primary">Rp 0<small class="text-muted fs-6">/month</small></h2>
                                <ul class="list-unstyled">
                                    <li><i class="fas fa-check text-success"></i> 5 searches/day</li>
                                    <li><i class="fas fa-check text-success"></i> Basic search</li>
                                    <li><i class="fas fa-times text-danger"></i> No consultation</li>
                                </ul>
                                <a href="/legal" class="btn btn-outline-primary">Get Started</a>
                            </div>
                        </div>
                    </div>

                    <div class="col-md-6 col-lg-3">
                        <div class="card h-100 shadow-sm">
                            <div class="card-body text-center">
                                <h5 class="card-title">Basic</h5>
                                <h2 class="text-primary">Rp 99K<small class="text-muted fs-6">/month</small></h2>
                                <ul class="list-unstyled">
                                    <li><i class="fas fa-check text-success"></i> 50 searches/day</li>
                                    <li><i class="fas fa-check text-success"></i> Advanced search</li>
                                    <li><i class="fas fa-times text-danger"></i> No consultation</li>
                                </ul>
                                <button class="btn btn-primary" onclick="alert('Coming soon!')">Subscribe</button>
                            </div>
                        </div>
                    </div>

                    <div class="col-md-6 col-lg-3">
                        <div class="card h-100 shadow border-warning">
                            <div class="card-header bg-warning text-dark text-center">
                                <i class="fas fa-star"></i> MOST POPULAR
                            </div>
                            <div class="card-body text-center">
                                <h5 class="card-title">Professional</h5>
                                <h2 class="text-primary">Rp 299K<small class="text-muted fs-6">/month</small></h2>
                                <ul class="list-unstyled">
                                    <li><i class="fas fa-check text-success"></i> 200 searches/day</li>
                                    <li><i class="fas fa-check text-success"></i> Advanced search</li>
                                    <li><i class="fas fa-check text-success"></i> Legal consultation</li>
                                    <li><i class="fas fa-check text-success"></i> Priority support</li>
                                </ul>
                                <button class="btn btn-warning" onclick="alert('Coming soon!')">Subscribe</button>
                            </div>
                        </div>
                    </div>

                    <div class="col-md-6 col-lg-3">
                        <div class="card h-100 shadow-sm">
                            <div class="card-body text-center">
                                <h5 class="card-title">Enterprise</h5>
                                <h2 class="text-primary">Rp 999K<small class="text-muted fs-6">/month</small></h2>
                                <ul class="list-unstyled">
                                    <li><i class="fas fa-check text-success"></i> Unlimited searches</li>
                                    <li><i class="fas fa-check text-success"></i> All features</li>
                                    <li><i class="fas fa-check text-success"></i> 24/7 consultation</li>
                                    <li><i class="fas fa-check text-success"></i> Dedicated support</li>
                                </ul>
                                <button class="btn btn-success" onclick="alert('Coming soon!')">Contact Sales</button>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="row mt-5">
                    <div class="col-12">
                        <div class="alert alert-info text-center">
                            <h5><i class="fas fa-info-circle"></i> Status: Working!</h5>
                            <p class="mb-0">This page is now working! The subscription controller is loaded correctly.</p>
                        </div>
                    </div>
                </div>
            </div>

            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
        </body>
        </html>
        """
    
    @http.route('/', type='http', auth='public', website=True)
    def legal_home(self, **kw):
        """Homepage website hukum"""
        # Get featured articles
        featured_articles = request.env['legal.article'].sudo().search([
            ('website_published', '=', True)
        ], limit=6, order='view_count desc, create_date desc')
        
        # Get categories
        categories = request.env['legal.category'].sudo().search([])
        
        return request.render('legal_website.legal_homepage', {
            'featured_articles': featured_articles,
            'categories': categories,
        })
    
    @http.route('/legal/search', type='http', auth='public', website=True)
    def legal_search_page(self, **kw):
        """Halaman pencarian hukum"""
        query = kw.get('q', '')
        page = int(kw.get('page', 1))
        search_type = kw.get('type', 'web')  # web, articles
        
        results = {}
        local_articles = []
        
        if query:
            # Search local articles
            local_articles = request.env['legal.article'].sudo().search([
                ('website_published', '=', True),
                '|', '|',
                ('name', 'ilike', query),
                ('content', 'ilike', query),
                ('summary', 'ilike', query)
            ], limit=5)
            
            # Search web if requested
            if search_type == 'web':
                search_config = request.env['legal.search.enhanced'].sudo().get_active_config()
                results = search_config.search_web(query, page=page)
                
                # Log search
                request.env['legal.search.history'].sudo().log_search(
                    query, 
                    results.get('total', 0),
                    request
                )
        
        return request.render('legal_website.legal_search_page', {
            'query': query,
            'results': results,
            'local_articles': local_articles,
            'page': page,
            'search_type': search_type,
        })
    
    @http.route('/legal/search/api', type='json', auth='public', csrf=False)
    def legal_search_api(self, **kw):
        """API endpoint untuk pencarian AJAX"""
        query = kw.get('q', '')
        page = int(kw.get('page', 1))
        per_page = int(kw.get('per_page', 10))
        
        if not query:
            return {'error': 'Query is required'}
        
        try:
            search_config = request.env['legal.search.enhanced'].sudo().get_active_config()
            results = search_config.search_web(query, page=page, per_page=per_page)
            
            # Log search
            request.env['legal.search.history'].sudo().log_search(
                query, 
                results.get('total', 0),
                request
            )
            
            return results
            
        except Exception as e:
            _logger.error(f"Search API error: {str(e)}")
            return {'error': str(e)}
    
    @http.route('/legal/articles', type='http', auth='public', website=True)
    def legal_articles(self, page=1, category=None, tag=None, search=None, **kw):
        """Halaman daftar artikel hukum"""
        # Odoo domain format
        domain = [('website_published', '=', True)]
        
        # Filter by category
        if category:
            category_id = int(category)
            category_obj = request.env['legal.category'].sudo().browse(category_id)
            domain.append(('category_id', '=', category_id))
        else:
            category_obj = None
        
        # Filter by tag  
        if tag:
            domain.append(('tag_ids', 'in', int(tag)))
        
        # Search filter
        if search:
            domain.extend([
                '|', '|',
                ('name', 'ilike', search),
                ('content', 'ilike', search),
                ('summary', 'ilike', search)
            ])
        
        # Pagination
        per_page = 12
        articles_count = request.env['legal.article'].sudo().search_count(domain)
        offset = (int(page) - 1) * per_page
        
        articles = request.env['legal.article'].sudo().search(
            domain, 
            limit=per_page, 
            offset=offset,
            order='create_date desc'
        )
        
        # Get all categories and tags
        categories = request.env['legal.category'].sudo().search([])
        popular_tags = request.env['legal.tag'].sudo().search([], limit=10)
        
        # Pagination info
        total_pages = (articles_count + per_page - 1) // per_page
        
        return request.render('legal_website.legal_articles', {
            'articles': articles,
            'categories': categories,
            'popular_tags': popular_tags,
            'current_category': category_obj,
            'current_page': int(page),
            'total_pages': total_pages,
            'articles_count': articles_count,
            'search': search,
        })
    
    @http.route('/legal/article/<int:article_id>', type='http', auth='public', website=True)
    def legal_article_detail(self, article_id, **kw):
        """Detail artikel hukum"""
        article = request.env['legal.article'].sudo().browse(article_id)
        
        if not article.exists() or not article.website_published:
            return request.not_found()
        
        # Increment view count
        article.increment_view_count()
        
        # Get related articles
        related_articles = request.env['legal.article'].sudo().search([
            ('id', '!=', article_id),
            ('category_id', '=', article.category_id.id),
            ('website_published', '=', True)
        ], limit=4)
        
        return request.render('legal_website.legal_article_detail', {
            'article': article,
            'related_articles': related_articles,
        })
    
    @http.route('/legal/category/<int:category_id>', type='http', auth='public', website=True)
    def legal_category_page(self, category_id, **kw):
        """Halaman kategori hukum"""
        return self.legal_articles(category=category_id, **kw)