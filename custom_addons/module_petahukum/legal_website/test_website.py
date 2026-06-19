# -*- coding: utf-8 -*-
"""
Legal Website Demo Test Script

Test semua fitur website hukum termasuk search functionality
"""

import requests
import json
import time
from urllib.parse import urljoin, quote_plus

class LegalWebsiteTest:
    def __init__(self, base_url="http://localhost:8069"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Legal Website Test Client'
        })
    
    def test_homepage(self):
        """Test homepage accessibility"""
        print("🏠 Testing Homepage...")
        
        try:
            response = self.session.get(self.base_url)
            
            if response.status_code == 200:
                content = response.text
                
                # Check for key elements
                checks = [
                    ("Portal Hukum Indonesia" in content, "Homepage title"),
                    ("Cari informasi hukum" in content, "Search form"),
                    ("Kategori Hukum" in content, "Categories section"),
                    ("Artikel Terpopuler" in content, "Featured articles")
                ]
                
                all_passed = True
                for check, description in checks:
                    status = "✅" if check else "❌"
                    print(f"  {status} {description}")
                    if not check:
                        all_passed = False
                
                if all_passed:
                    print("  ✅ Homepage test PASSED")
                    return True
                else:
                    print("  ❌ Homepage test FAILED")
                    return False
                    
            else:
                print(f"  ❌ Homepage returned status {response.status_code}")
                return False
                
        except Exception as e:
            print(f"  ❌ Homepage test error: {str(e)}")
            return False
    
    def test_search_page(self):
        """Test search page"""
        print("\n🔍 Testing Search Page...")
        
        try:
            # Test search page access
            search_url = urljoin(self.base_url, "/legal/search")
            response = self.session.get(search_url)
            
            if response.status_code == 200:
                print("  ✅ Search page accessible")
                
                # Test search with query
                search_with_query = f"{search_url}?q=hukum+pidana&type=web"
                response = self.session.get(search_with_query)
                
                if response.status_code == 200:
                    content = response.text
                    
                    checks = [
                        ("Hasil pencarian untuk" in content, "Search results display"),
                        ("Pencarian Web" in content, "Web search tab"),
                        ("Artikel Lokal" in content, "Local articles tab"),
                        ("Tips Pencarian" in content, "Search tips sidebar")
                    ]
                    
                    all_passed = True
                    for check, description in checks:
                        status = "✅" if check else "❌"
                        print(f"  {status} {description}")
                        if not check:
                            all_passed = False
                    
                    return all_passed
                else:
                    print(f"  ❌ Search with query returned status {response.status_code}")
                    return False
            else:
                print(f"  ❌ Search page returned status {response.status_code}")
                return False
                
        except Exception as e:
            print(f"  ❌ Search page test error: {str(e)}")
            return False
    
    def test_search_api(self):
        """Test search API endpoint"""
        print("\n🔧 Testing Search API...")
        
        try:
            api_url = urljoin(self.base_url, "/legal/search/api")
            
            # Test API call
            payload = {
                "q": "tindak pidana korupsi",
                "page": 1,
                "per_page": 5
            }
            
            response = self.session.post(
                api_url,
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    # Check response structure
                    checks = [
                        ("results" in data, "Results array present"),
                        ("query" in data, "Query echo present"),
                        ("total" in data, "Total count present"),
                        (isinstance(data.get("results"), list), "Results is array"),
                        (len(data.get("results", [])) > 0, "Has search results")
                    ]
                    
                    all_passed = True
                    for check, description in checks:
                        status = "✅" if check else "❌"
                        print(f"  {status} {description}")
                        if not check:
                            all_passed = False
                    
                    if all_passed and data.get("results"):
                        # Show sample result
                        sample_result = data["results"][0]
                        print(f"  📄 Sample result: {sample_result.get('title', 'N/A')[:50]}...")
                        print(f"  📊 Total results: {data.get('total', 0)}")
                    
                    return all_passed
                    
                except json.JSONDecodeError:
                    print("  ❌ API returned invalid JSON")
                    return False
            else:
                print(f"  ❌ API returned status {response.status_code}")
                return False
                
        except Exception as e:
            print(f"  ❌ Search API test error: {str(e)}")
            return False
    
    def test_articles_page(self):
        """Test articles listing page"""
        print("\n📚 Testing Articles Page...")
        
        try:
            articles_url = urljoin(self.base_url, "/legal/articles")
            response = self.session.get(articles_url)
            
            if response.status_code == 200:
                content = response.text
                
                checks = [
                    ("Semua Artikel Hukum" in content, "Articles page title"),
                    ("Cari artikel" in content, "Article search form"),
                    ("Kategori" in content, "Categories sidebar"),
                    ("legal-article-card" in content, "Article cards present")
                ]
                
                all_passed = True
                for check, description in checks:
                    status = "✅" if check else "❌"
                    print(f"  {status} {description}")
                    if not check:
                        all_passed = False
                
                return all_passed
            else:
                print(f"  ❌ Articles page returned status {response.status_code}")
                return False
                
        except Exception as e:
            print(f"  ❌ Articles page test error: {str(e)}")
            return False
    
    def test_static_assets(self):
        """Test CSS and JS assets loading"""
        print("\n🎨 Testing Static Assets...")
        
        assets_to_test = [
            "/legal_website/static/src/css/legal_website.css",
            "/legal_website/static/src/js/legal_search.js"
        ]
        
        all_passed = True
        for asset_path in assets_to_test:
            try:
                asset_url = urljoin(self.base_url, asset_path)
                response = self.session.get(asset_url)
                
                if response.status_code == 200:
                    print(f"  ✅ {asset_path}")
                else:
                    print(f"  ❌ {asset_path} (status {response.status_code})")
                    all_passed = False
                    
            except Exception as e:
                print(f"  ❌ {asset_path} (error: {str(e)})")
                all_passed = False
        
        return all_passed
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Legal Website Tests...\n")
        
        tests = [
            ("Homepage", self.test_homepage),
            ("Search Page", self.test_search_page), 
            ("Search API", self.test_search_api),
            ("Articles Page", self.test_articles_page),
            ("Static Assets", self.test_static_assets)
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            print(f"\n{'='*50}")
            results[test_name] = test_func()
            time.sleep(1)  # Brief pause between tests
        
        # Summary
        print(f"\n{'='*50}")
        print("📊 TEST SUMMARY:")
        print(f"{'='*50}")
        
        passed = 0
        total = len(tests)
        
        for test_name, result in results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"  {test_name:20} {status}")
            if result:
                passed += 1
        
        print(f"\n🎯 Result: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED! Website is ready to use.")
        else:
            print("⚠️  Some tests failed. Check Odoo server and module installation.")
        
        return passed == total

def main():
    """Main test function"""
    print("Legal Website Test Suite")
    print("="*50)
    
    # Check if custom base URL provided
    import sys
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8069"
    
    print(f"Testing website at: {base_url}")
    print("Make sure Odoo server is running with legal_website module installed.")
    print("="*50)
    
    tester = LegalWebsiteTest(base_url)
    success = tester.run_all_tests()
    
    if success:
        print(f"\n🌐 Website ready at: {base_url}")
        print("📖 Try searching for: 'hukum pidana', 'korupsi', 'KUHP'")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)