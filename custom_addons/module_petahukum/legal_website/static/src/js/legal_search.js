/* Legal Website JavaScript */

document.addEventListener('DOMContentLoaded', function() {
    
    // Initialize Search Functionality
    initSearchFeatures();
    
    // Initialize Article Features
    initArticleFeatures();
    
    // Initialize UI Enhancements
    initUIEnhancements();
    
});

function initSearchFeatures() {
    
    // Auto-complete Search
    const searchInputs = document.querySelectorAll('input[name="q"]');
    searchInputs.forEach(function(input) {
        input.addEventListener('input', function() {
            debounce(handleSearchSuggestions, 300)(this);
        });
    });
    
    // AJAX Search
    const ajaxSearchBtn = document.getElementById('ajax-search-btn');
    if (ajaxSearchBtn) {
        ajaxSearchBtn.addEventListener('click', function(e) {
            e.preventDefault();
            performAjaxSearch();
        });
    }
    
    // Search History
    trackSearchHistory();
    
    // Advanced Search Toggle
    const advancedSearchToggle = document.getElementById('advanced-search-toggle');
    if (advancedSearchToggle) {
        advancedSearchToggle.addEventListener('click', function() {
            const advancedForm = document.getElementById('advanced-search-form');
            if (advancedForm) {
                advancedForm.style.display = advancedForm.style.display === 'none' ? 'block' : 'none';
            }
        });
    }
    
}

function handleSearchSuggestions(input) {
    const query = input.value.trim();
    
    if (query.length < 3) {
        hideSuggestions();
        return;
    }
    
    // Show loading
    showSearchLoading(input);
    
    // Get suggestions from local articles
    getLocalSuggestions(query).then(function(suggestions) {
        displaySuggestions(input, suggestions);
    }).catch(function(error) {
        console.error('Error fetching suggestions:', error);
        hideSuggestions();
    });
}

function getLocalSuggestions(query) {
    return new Promise(function(resolve, reject) {
        // Mock suggestions - in real implementation, this would be an AJAX call
        const mockSuggestions = [
            'Tindak Pidana Korupsi',
            'Hukum Perdata Indonesia', 
            'KUHP Pasal 338',
            'Undang-Undang Dasar 1945',
            'Hukum Bisnis dan Kontrak'
        ].filter(function(suggestion) {
            return suggestion.toLowerCase().includes(query.toLowerCase());
        });
        
        setTimeout(function() {
            resolve(mockSuggestions);
        }, 200);
    });
}

function displaySuggestions(input, suggestions) {
    // Remove existing suggestions
    hideSuggestions();
    
    if (suggestions.length === 0) return;
    
    // Create suggestions dropdown
    const dropdown = document.createElement('div');
    dropdown.className = 'search-suggestions-dropdown position-absolute bg-white border rounded shadow-sm';
    dropdown.style.top = '100%';
    dropdown.style.left = '0';
    dropdown.style.right = '0';
    dropdown.style.zIndex = '1050';
    dropdown.style.maxHeight = '200px';
    dropdown.style.overflowY = 'auto';
    
    suggestions.forEach(function(suggestion) {
        const item = document.createElement('div');
        item.className = 'search-suggestion-item px-3 py-2 cursor-pointer';
        item.textContent = suggestion;
        item.style.cursor = 'pointer';
        
        item.addEventListener('click', function() {
            input.value = suggestion;
            hideSuggestions();
            // Trigger search
            const form = input.closest('form');
            if (form) {
                form.submit();
            }
        });
        
        item.addEventListener('mouseenter', function() {
            this.style.backgroundColor = '#f8f9fa';
        });
        
        item.addEventListener('mouseleave', function() {
            this.style.backgroundColor = '';
        });
        
        dropdown.appendChild(item);
    });
    
    // Position dropdown relative to input
    const inputGroup = input.closest('.d-flex, .input-group, .search-form');
    if (inputGroup) {
        inputGroup.style.position = 'relative';
        inputGroup.appendChild(dropdown);
    }
    
    // Store reference for cleanup
    input.suggestionsDropdown = dropdown;
}

function hideSuggestions() {
    const dropdowns = document.querySelectorAll('.search-suggestions-dropdown');
    dropdowns.forEach(function(dropdown) {
        dropdown.remove();
    });
}

function showSearchLoading(input) {
    hideSuggestions();
    
    const loading = document.createElement('div');
    loading.className = 'search-loading-indicator position-absolute bg-white border rounded px-2 py-1';
    loading.innerHTML = '<small class="text-muted"><i class="fa fa-spinner fa-spin me-1"></i>Mencari...</small>';
    loading.style.top = '100%';
    loading.style.left = '0';
    loading.style.zIndex = '1050';
    
    const inputGroup = input.closest('.d-flex, .input-group, .search-form');
    if (inputGroup) {
        inputGroup.style.position = 'relative';
        inputGroup.appendChild(loading);
    }
    
    // Remove after delay
    setTimeout(function() {
        if (loading.parentNode) {
            loading.remove();
        }
    }, 1000);
}

function performAjaxSearch() {
    const query = document.querySelector('input[name="q"]').value.trim();
    if (!query) return;
    
    const resultsContainer = document.getElementById('ajax-search-results');
    if (!resultsContainer) return;
    
    // Show loading
    resultsContainer.innerHTML = '<div class="text-center py-4"><i class="fa fa-spinner fa-spin fa-2x text-primary"></i><p class="mt-2">Mencari...</p></div>';
    
    // Perform AJAX search
    fetch('/legal/search/api', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            q: query,
            page: 1,
            per_page: 10
        })
    })
    .then(response => response.json())
    .then(data => {
        displayAjaxResults(data, resultsContainer);
    })
    .catch(error => {
        console.error('Search error:', error);
        resultsContainer.innerHTML = '<div class="alert alert-danger">Terjadi kesalahan saat mencari. Silakan coba lagi.</div>';
    });
}

function displayAjaxResults(data, container) {
    if (data.error) {
        container.innerHTML = `<div class="alert alert-warning">${data.error}</div>`;
        return;
    }
    
    if (!data.results || data.results.length === 0) {
        container.innerHTML = '<div class="alert alert-info">Tidak ada hasil yang ditemukan.</div>';
        return;
    }
    
    let html = `<h6 class="mb-3">Ditemukan ${data.total} hasil</h6>`;
    
    data.results.forEach(function(result) {
        html += `
            <div class="search-result-item mb-3">
                <h6><a href="${result.url}" target="_blank" class="text-decoration-none">${result.title}</a></h6>
                <p class="text-success small mb-1">${result.url}</p>
                <p class="text-muted">${result.content}</p>
                <small class="text-muted">
                    Sumber: ${result.engine} | Skor: ${result.score}
                </small>
            </div>
        `;
    });
    
    container.innerHTML = html;
    
    // Add pagination if needed
    if (data.total > 10) {
        // Add pagination controls
        addPaginationControls(container, data);
    }
}

function addPaginationControls(container, data) {
    const totalPages = Math.ceil(data.total / 10);
    if (totalPages <= 1) return;
    
    let paginationHtml = '<nav class="mt-4"><ul class="pagination justify-content-center">';
    
    for (let i = 1; i <= Math.min(totalPages, 5); i++) {
        paginationHtml += `
            <li class="page-item ${i === data.page ? 'active' : ''}">
                <a class="page-link" href="#" onclick="loadSearchPage(${i}); return false;">${i}</a>
            </li>
        `;
    }
    
    paginationHtml += '</ul></nav>';
    container.innerHTML += paginationHtml;
}

function loadSearchPage(page) {
    const query = document.querySelector('input[name="q"]').value.trim();
    const resultsContainer = document.getElementById('ajax-search-results');
    
    // Update URL without reload
    const newUrl = new URL(window.location);
    newUrl.searchParams.set('page', page);
    window.history.pushState({}, '', newUrl);
    
    performAjaxSearch();
}

function trackSearchHistory() {
    // Track search queries for analytics
    const urlParams = new URLSearchParams(window.location.search);
    const query = urlParams.get('q');
    
    if (query) {
        // Store in localStorage for user experience
        let searchHistory = JSON.parse(localStorage.getItem('legalSearchHistory') || '[]');
        
        // Remove if exists and add to beginning
        searchHistory = searchHistory.filter(item => item !== query);
        searchHistory.unshift(query);
        
        // Keep only last 10 searches
        searchHistory = searchHistory.slice(0, 10);
        
        localStorage.setItem('legalSearchHistory', JSON.stringify(searchHistory));
        
        // Display recent searches if input is focused
        displayRecentSearches();
    }
}

function displayRecentSearches() {
    const searchInputs = document.querySelectorAll('input[name="q"]');
    
    searchInputs.forEach(function(input) {
        input.addEventListener('focus', function() {
            const history = JSON.parse(localStorage.getItem('legalSearchHistory') || '[]');
            if (history.length > 0 && !input.value.trim()) {
                displaySuggestions(input, history);
            }
        });
    });
}

function initArticleFeatures() {
    
    // Article View Tracking
    const articleId = getArticleIdFromUrl();
    if (articleId) {
        trackArticleView(articleId);
    }
    
    // Social Sharing
    initSocialSharing();
    
    // Reading Progress
    initReadingProgress();
    
    // Related Articles Loading
    initRelatedArticles();
    
}

function getArticleIdFromUrl() {
    const match = window.location.pathname.match(/\/legal\/article\/(\d+)/);
    return match ? match[1] : null;
}

function trackArticleView(articleId) {
    // Track article views (this would typically be an AJAX call)
    console.log('Tracking view for article:', articleId);
    
    // Store in localStorage for offline capability
    let viewedArticles = JSON.parse(localStorage.getItem('viewedArticles') || '[]');
    if (!viewedArticles.includes(articleId)) {
        viewedArticles.push(articleId);
        localStorage.setItem('viewedArticles', JSON.stringify(viewedArticles));
    }
}

function initSocialSharing() {
    const shareButtons = {
        facebook: document.querySelector('.social-share .btn:nth-child(1)'),
        twitter: document.querySelector('.social-share .btn:nth-child(2)'),
        whatsapp: document.querySelector('.social-share .btn:nth-child(3)')
    };
    
    const url = encodeURIComponent(window.location.href);
    const title = encodeURIComponent(document.title);
    
    if (shareButtons.facebook) {
        shareButtons.facebook.href = `https://www.facebook.com/sharer/sharer.php?u=${url}`;
    }
    
    if (shareButtons.twitter) {
        shareButtons.twitter.href = `https://twitter.com/intent/tweet?url=${url}&text=${title}`;
    }
    
    if (shareButtons.whatsapp) {
        shareButtons.whatsapp.href = `https://wa.me/?text=${title}%20${url}`;
    }
}

function initReadingProgress() {
    const article = document.querySelector('.article-content');
    if (!article) return;
    
    const progressBar = document.createElement('div');
    progressBar.className = 'reading-progress';
    progressBar.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 0%;
        height: 3px;
        background: #007bff;
        z-index: 1000;
        transition: width 0.3s;
    `;
    document.body.appendChild(progressBar);
    
    window.addEventListener('scroll', function() {
        const articleRect = article.getBoundingClientRect();
        const windowHeight = window.innerHeight;
        const documentHeight = document.documentElement.scrollHeight - windowHeight;
        const scrolled = window.scrollY;
        
        if (articleRect.top <= 0 && articleRect.bottom >= 0) {
            const progress = (scrolled / documentHeight) * 100;
            progressBar.style.width = Math.min(progress, 100) + '%';
        }
    });
}

function initRelatedArticles() {
    // Lazy loading for related articles
    const relatedSection = document.querySelector('.related-articles');
    if (relatedSection) {
        const observer = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    loadMoreRelatedArticles();
                    observer.unobserve(entry.target);
                }
            });
        });
        
        observer.observe(relatedSection);
    }
}

function loadMoreRelatedArticles() {
    // This would typically load more articles via AJAX
    console.log('Loading more related articles...');
}

function initUIEnhancements() {
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(function(anchor) {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Back to top button
    initBackToTop();
    
    // Image lazy loading
    initImageLazyLoading();
    
    // Tooltips
    initTooltips();
    
    // Search form enhancements
    enhanceSearchForms();
    
}

function initBackToTop() {
    const backToTopBtn = document.createElement('button');
    backToTopBtn.innerHTML = '<i class="fa fa-arrow-up"></i>';
    backToTopBtn.className = 'btn btn-primary btn-back-to-top';
    backToTopBtn.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 1000;
        border-radius: 50%;
        width: 50px;
        height: 50px;
        display: none;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    `;
    
    document.body.appendChild(backToTopBtn);
    
    window.addEventListener('scroll', function() {
        if (window.scrollY > 300) {
            backToTopBtn.style.display = 'block';
        } else {
            backToTopBtn.style.display = 'none';
        }
    });
    
    backToTopBtn.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

function initImageLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
                imageObserver.unobserve(img);
            }
        });
    });
    
    images.forEach(function(img) {
        imageObserver.observe(img);
    });
}

function initTooltips() {
    // Initialize Bootstrap tooltips if available
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}

function enhanceSearchForms() {
    const searchForms = document.querySelectorAll('form[action*="search"]');
    
    searchForms.forEach(function(form) {
        const input = form.querySelector('input[name="q"]');
        if (input) {
            // Add search suggestions on focus
            input.addEventListener('focus', function() {
                if (!this.value.trim()) {
                    showPopularSearches(this);
                }
            });
            
            // Clear suggestions on blur (with delay for click handling)
            input.addEventListener('blur', function() {
                setTimeout(hideSuggestions, 200);
            });
        }
        
        // Prevent empty searches
        form.addEventListener('submit', function(e) {
            const query = input.value.trim();
            if (!query) {
                e.preventDefault();
                input.focus();
                input.placeholder = 'Masukkan kata kunci pencarian...';
                input.style.borderColor = '#dc3545';
                
                setTimeout(function() {
                    input.style.borderColor = '';
                    input.placeholder = 'Cari informasi hukum...';
                }, 2000);
            }
        });
    });
}

function showPopularSearches(input) {
    const popularSearches = [
        'Tindak Pidana Korupsi',
        'Hukum Perdata',
        'KUHP',
        'UUD 1945',
        'Hukum Bisnis',
        'Surat Perjanjian',
        'Hukum Keluarga',
        'Warisan'
    ];
    
    displaySuggestions(input, popularSearches);
}

// Utility Functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function highlightSearchTerms(text, query) {
    if (!query) return text;
    
    const terms = query.split(/\s+/).filter(term => term.length > 2);
    let highlightedText = text;
    
    terms.forEach(function(term) {
        const regex = new RegExp(`(${term})`, 'gi');
        highlightedText = highlightedText.replace(regex, '<span class="search-highlight">$1</span>');
    });
    
    return highlightedText;
}

// Export functions for global access
window.LegalWebsite = {
    performAjaxSearch,
    loadSearchPage,
    trackArticleView,
    highlightSearchTerms,
    debounce
};