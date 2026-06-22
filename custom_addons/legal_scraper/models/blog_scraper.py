# -*- coding: utf-8 -*-
import requests
import xml.etree.ElementTree as ET
import logging
import base64
import json
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from odoo import models, fields, api

_logger = logging.getLogger(__name__)

class LegalBlogScraper(models.Model):
    _name = 'legal.blog.scraper'
    _description = 'Automatic Blog Scraper for website_blog'

    name = fields.Char(string='Scraper Name', default='Berita Hukum RSS Scraper')
    rss_url = fields.Char(string='RSS URL', default='https://www.antaranews.com/rss/hukum')
    active = fields.Boolean(default=True)
    last_run = fields.Datetime(string='Last Run')
    
    def action_scrape_blog(self):
        blog = self.env['blog.blog'].search([], limit=1)
        if not blog:
            # Create a default blog if it doesn't exist
            blog = self.env['blog.blog'].create({'name': 'Berita Hukum'})
            
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
            
        for scraper in self.search([('active', '=', True)]):
            try:
                _logger.info("Starting scrape job for RSS/URL: %s", scraper.rss_url)
                response = requests.get(scraper.rss_url, headers=headers, timeout=15)
                if response.status_code != 200:
                    _logger.warning("Scraper URL returned status code %s", response.status_code)
                    continue
                
                items = []
                try:
                    # Attempt standard XML RSS parsing
                    root = ET.fromstring(response.content)
                    _logger.info("Successfully parsed URL as XML RSS feed.")
                    for item in root.findall('./channel/item'):
                        title = item.find('title').text if item.find('title') is not None else ''
                        link = item.find('link').text if item.find('link') is not None else ''
                        description = item.find('description').text if item.find('description') is not None else ''
                        pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ''
                        
                        image_url = None
                        enclosure = item.find('enclosure')
                        if enclosure is not None and enclosure.get('type', '').startswith('image'):
                            image_url = enclosure.get('url')
                        
                        if not image_url:
                            for child in item:
                                if child.tag.endswith('content') and child.get('type', '').startswith('image'):
                                    image_url = child.get('url')
                                    break
                                    
                        items.append({
                            'title': title,
                            'link': link,
                            'description': description,
                            'pub_date': pub_date,
                            'image_url': image_url,
                        })
                except Exception as xml_err:
                    _logger.info("URL is not valid XML RSS, falling back to HTML scraping. Parse error: %s", xml_err)
                    # Parse standard HTML page (like hukumonline.com/berita/)
                    soup = BeautifulSoup(response.content, 'html.parser')
                    for a in soup.find_all('a', href=True):
                        href = a['href']
                        # Standardize URL
                        if href.startswith('/'):
                            parsed_rss = urlparse(scraper.rss_url)
                            href = f"{parsed_rss.scheme}://{parsed_rss.netloc}{href}"
                            
                        # Filter for article links (e.g. hukumonline /berita/a/ or /berita/baca/)
                        if '/berita/a/' in href or '/berita/baca/' in href:
                            title_text = a.text.strip()
                            if not title_text or len(title_text) < 10:
                                title_text = a.get('title') or ""
                                if not title_text:
                                    h_tag = a.find(['h1', 'h2', 'h3', 'h4', 'h5', 'span'])
                                    if h_tag:
                                        title_text = h_tag.text.strip()
                            
                            title_text = ' '.join(title_text.split())
                            if title_text and len(title_text) >= 10:
                                if href not in [x['link'] for x in items]:
                                    items.append({
                                        'title': title_text,
                                        'link': href,
                                        'description': title_text,
                                        'pub_date': '',
                                        'image_url': None,
                                    })
                
                _logger.info("Found %s article links to scrape.", len(items))
                created_count = 0
                
                for item in items:
                    title = item['title']
                    link = item['link']
                    description = item['description']
                    pub_date = item['pub_date']
                    image_url = item['image_url']
                    
                    if not title:
                        continue
                        
                    # Check if blog post already exists by matching title
                    existing = self.env['blog.post'].search([('name', '=', title)], limit=1)
                    if not existing:
                        clean_content = ""
                        
                        if link:
                            try:
                                article_res = requests.get(link, headers=headers, timeout=10)
                                if article_res.status_code == 200:
                                    soup = BeautifulSoup(article_res.content, 'html.parser')
                                    
                                    # Extract og:image if not already found
                                    if not image_url:
                                        og_image = soup.find('meta', property='og:image') or soup.find('meta', name='twitter:image')
                                        if og_image:
                                            image_url = og_image.get('content')
                                            
                                    # Remove scripts, styles, iframe, and other structural junk
                                    for junk in soup(["script", "style", "nav", "header", "footer", "aside", "iframe", "form"]):
                                        junk.decompose()
                                        
                                    # Try selectors for main content area
                                    content_div = None
                                    selectors = [
                                        'article',
                                        'div.post-content', 
                                        'div.entry-content', 
                                        'div.detail-text', 
                                        'div.read__content', 
                                        'div.post-body',
                                        'div.content-wrapper',
                                        'div.detail__body-text',
                                        'div.article-content',
                                        'div.article__content',
                                        'div.detail__content',
                                        'div.detail-content',
                                        '.content-detail',
                                        '.post-detail',
                                        '.article-body',
                                        '.entry-body'
                                    ]
                                    for selector in selectors:
                                        found = soup.select_one(selector)
                                        if found:
                                            content_div = found
                                            break
                                            
                                    if content_div:
                                        # Try to find images inside article if we still don't have one
                                        if not image_url:
                                            img_tag = content_div.find('img')
                                            if img_tag:
                                                image_url = img_tag.get('src') or img_tag.get('data-src')

                                        # Clean up elements within content_div (e.g. ads, share buttons)
                                        for ad in content_div.select('.advertisement, .ads, .share, .social-share, .comments, .related-posts'):
                                            ad.decompose()

                                        # Extract paragraph tags
                                        paragraphs = content_div.find_all('p')
                                        if paragraphs:
                                            clean_content = "".join(str(p) for p in paragraphs if len(p.text.strip()) > 10)
                                        else:
                                            clean_content = str(content_div)
                                    else:
                                        # Fallback
                                        paragraphs = soup.find_all('p')
                                        clean_content = "".join(str(p) for p in paragraphs if len(p.text.strip()) > 15)
                                        
                            except Exception as web_e:
                                _logger.warning("Failed to fetch/parse web page %s: %s", link, web_e)
                        
                        # Fallback if page parsing failed or yielded empty content
                        if not clean_content:
                            clean_content = f"<p>{description}</p>"
                            
                        # Append 'Read More' link
                        clean_content += f"<br/><br/><a href='{link}' target='_blank' class='btn btn-primary'>Baca selengkapnya di sumber asli</a>"
                        
                        # 2. Create the Blog Post
                        blog_post = self.env['blog.post'].create({
                            'name': title,
                            'subtitle': pub_date,
                            'content': clean_content,
                            'blog_id': blog.id,
                            'is_published': True,
                        })
                        
                        # 3. Fetch image and set as thumbnail cover if present
                        if image_url:
                            # Standardize relative URL
                            if image_url.startswith('//'):
                                image_url = 'https:' + image_url
                            elif image_url.startswith('/') and not image_url.startswith('//'):
                                parsed_link = urlparse(link)
                                image_url = f"{parsed_link.scheme}://{parsed_link.netloc}{image_url}"
                                
                            try:
                                img_res = requests.get(image_url, headers=headers, timeout=10)
                                if img_res.status_code == 200:
                                    image_data_b64 = base64.b64encode(img_res.content)
                                    
                                    # Create attachment linked to this blog post
                                    attachment = self.env['ir.attachment'].create({
                                        'name': f"cover_{blog_post.id}",
                                        'type': 'binary',
                                        'datas': image_data_b64,
                                        'public': True,
                                        'res_model': 'blog.post',
                                        'res_id': blog_post.id,
                                    })
                                    
                                    # Write cover properties to blog post
                                    cover_properties = {
                                        "background-image": f"url('/web/image/{attachment.id}')",
                                        "resize_class": "o_record_has_cover o_half_screen_height",
                                        "opacity": "0.2",
                                    }
                                    
                                    # Inject image HTML at the top of content
                                    img_html = f'<div class="o_wblog_post_content_image mb-4 text-center"><img src="/web/image/{attachment.id}" class="img img-fluid rounded shadow" style="max-height: 500px; width: 100%; object-fit: cover;" alt="{title}"/></div>'
                                    
                                    blog_post.write({
                                        'cover_properties': json.dumps(cover_properties),
                                        'content': img_html + clean_content
                                    })
                            except Exception as img_e:
                                _logger.warning("Failed to download or attach cover image %s: %s", image_url, img_e)
                                
                        created_count += 1
                        
                scraper.last_run = fields.Datetime.now()
                _logger.info("Successfully scraped %s articles from %s", created_count, scraper.rss_url)
            except Exception as e:
                _logger.error("Failed to scrape blog RSS %s: %s", scraper.rss_url, str(e))

    @api.model
    def cron_scrape_blog(self):
        """Method called by scheduled action"""
        scrapers = self.search([('active', '=', True)])
        if not scrapers:
            # Create default scraper if none exist
            scrapers = self.create({})
        scrapers.action_scrape_blog()
