window.shareRegulation = function() {
    if (navigator.share) {
        navigator.share({
            title: document.title,
            text: 'Lihat peraturan ini',
            url: window.location.href
        });
    } else {
        navigator.clipboard.writeText(window.location.href).then(function() {
            alert('URL berhasil disalin ke clipboard!');
        });
    }
}

// Font size adjustment
let currentFontSize = 16;
window.adjustFontSize = function(delta) {
    currentFontSize = Math.max(12, Math.min(24, currentFontSize + delta));
    document.querySelectorAll('.regulation-content-main').forEach(el => {
        el.style.fontSize = currentFontSize + 'px';
    });
}

// Fullscreen toggle
window.toggleFullscreen = function() {
    const content = document.querySelector('.regulation-content-main');
    if (!content) return;
    if (content.style.maxHeight !== 'none') {
        content.style.maxHeight = 'none';
        content.style.position = 'fixed';
        content.style.top = '0';
        content.style.left = '0';
        content.style.right = '0';
        content.style.bottom = '0';
        content.style.zIndex = '9999';
        content.style.background = 'white';
        content.style.padding = '40px';
    } else {
        content.style.maxHeight = 'calc(100vh - 250px)';
        content.style.position = '';
        content.style.top = '';
        content.style.left = '';
        content.style.right = '';
        content.style.bottom = '';
        content.style.zIndex = '';
        content.style.padding = '';
    }
}

// Store TOC elements globally
window.tocElements = {};

// Toggle collapse for any TOC node
window.toggleTocNode = function(key, containerIdx, evt) {
    if (containerIdx && (containerIdx instanceof Event || typeof containerIdx === 'object')) {
        evt = containerIdx;
        containerIdx = 0;
    }
    if (evt) {
        evt.preventDefault();
        evt.stopPropagation();
    }
    const idx = (containerIdx !== undefined) ? containerIdx : 0;
    const subItems = document.getElementById('sub-' + key + '-' + idx);
    const icon = document.getElementById('icon-' + key + '-' + idx);
    if (subItems) {
        if (subItems.style.display === 'none') {
            subItems.style.display = 'block';
            if (icon) icon.className = 'fa fa-chevron-down fa-fw';
        } else {
            subItems.style.display = 'none';
            if (icon) icon.className = 'fa fa-chevron-right fa-fw';
        }
    }
    return false;
};

// Map old toggleBab to toggleTocNode for backward compatibility
window.toggleBab = function(key, evt) {
    return window.toggleTocNode(key, 0, evt);
};

// Expand all parents of a given key in the TOC tree
window.expandParentsOf = function(key) {
    if (!key) return;
    const parts = key.split('-');
    let currentKey = '';
    for (let i = 0; i < parts.length; i++) {
        if (currentKey) {
            currentKey += '-' + parts[i];
        } else {
            currentKey = parts[i];
        }
        
        // Expand in all possible container instances (up to 5)
        for (let c = 0; c < 5; c++) {
            const subItems = document.getElementById('sub-' + currentKey + '-' + c);
            const icon = document.getElementById('icon-' + currentKey + '-' + c);
            if (subItems) {
                subItems.style.display = 'block';
                if (icon) {
                    icon.className = 'fa fa-chevron-down fa-fw';
                }
            }
        }
    }
};

// Scroll to TOC element, expanding its parents
window.scrollToTocElement = function(key, evt) {
    if (evt) {
        evt.preventDefault();
        evt.stopPropagation();
    }
    
    // Expand parents in the TOC
    window.expandParentsOf(key);
    
    const element = window.tocElements[key];
    const scrollContainer = document.querySelector('.regulation-content-main');
    
    if (element && scrollContainer) {
        const containerRect = scrollContainer.getBoundingClientRect();
        const elementRect = element.getBoundingClientRect();
        const scrollTop = scrollContainer.scrollTop + (elementRect.top - containerRect.top) - 30;
        
        scrollContainer.scrollTo({
            top: scrollTop,
            behavior: 'smooth'
        });
        
        // Update active state in TOC
        document.querySelectorAll('.toc-item-link, .toc-sub-item-link, .toc-item, .toc-sub-item').forEach(l => l.classList.remove('active'));
        if (evt && evt.target) {
            const targetEl = evt.target.closest('a');
            if (targetEl) targetEl.classList.add('active');
        } else {
            // Fallback: search for link by key
            const nodeWrapper = document.querySelector(`.toc-node-wrapper[data-key="${key}"]`);
            if (nodeWrapper) {
                const link = nodeWrapper.querySelector('.toc-item-link, .toc-sub-item-link');
                if (link) link.classList.add('active');
            }
        }
        
        // Close offcanvas if inside mobile TOC
        try {
            const offcanvasEl = document.getElementById('offcanvasToc');
            if (offcanvasEl && window.bootstrap && window.bootstrap.Offcanvas) {
                const bsOffcanvas = window.bootstrap.Offcanvas.getInstance(offcanvasEl);
                if (bsOffcanvas) {
                    bsOffcanvas.hide();
                }
            }
        } catch (err) {
            console.error("Error hiding offcanvas:", err);
        }
    }
    return false;
};

// Recursive node renderer
function renderNode(node, containerIdx) {
    const hasChildren = node.children && node.children.length > 0;
    const isBab = node.type === 'BAB';
    const isPasal = node.type === 'Pasal';
    const isAyat = node.type === 'Ayat';
    const isHuruf = node.type === 'Huruf';
    
    let itemClass = "toc-item-link d-flex align-items-center nav-link py-1";
    if (isBab) {
        itemClass += " toc-bab-title fw-bold text-dark border-bottom-faint";
    } else {
        itemClass += " toc-sub-item-link";
    }
    
    let html = `<div class="toc-node-wrapper" data-key="${node.key}" style="margin-left: 2px;">`;
    html += `<div class="toc-node-row d-flex align-items-center">`;
    
    if (hasChildren) {
        html += `<span class="toc-toggle me-1 text-secondary" style="cursor:pointer; width:16px; display:inline-block; text-align:center;" onclick="window.toggleTocNode('${node.key}', ${containerIdx}, event)">`;
        html += `<i id="icon-${node.key}-${containerIdx}" class="fa fa-chevron-right fa-fw" style="font-size: 0.7rem;"></i>`;
        html += `</span>`;
    } else {
        html += `<span class="toc-indent-spacer" style="width: 16px; display: inline-block;"></span>`;
    }
    
    html += `<a class="${itemClass}" href="javascript:void(0)" onclick="window.scrollToTocElement('${node.key}', event); return false;" style="flex-grow: 1; padding-left: 2px; font-size: 0.8rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${node.title}">`;
    
    if (isBab) {
        // No extra icon needed
    } else if (isPasal) {
        html += `<i class="fa fa-paragraph fa-fw text-muted me-1" style="font-size:0.75rem;"></i> `;
    } else if (isAyat) {
        html += `<i class="fa fa-angle-right fa-fw text-muted me-1"></i> `;
    } else if (isHuruf) {
        html += `<i class="fa fa-circle-o fa-fw text-muted me-1" style="font-size:0.5rem; vertical-align:middle;"></i> `;
    }
    
    html += node.title;
    html += `</a>`;
    html += `</div>`;
    
    if (hasChildren) {
        html += `<div id="sub-${node.key}-${containerIdx}" class="toc-children ps-2 ms-2 border-start-dashed" style="display: none;">`;
        node.children.forEach(child => {
            html += renderNode(child, containerIdx);
        });
        html += `</div>`;
    }
    
    html += `</div>`;
    return html;
}

// Generate dynamic TOC from content
function initTocAndShare() {
    const scrollContainer = document.querySelector('.regulation-content-main');
    const tocNavs = document.querySelectorAll('.toc-nav');
    const tocBabContainers = document.querySelectorAll('.toc-bab-container');
    
    if (!scrollContainer || tocBabContainers.length === 0) return;
    
    const allElements = scrollContainer.querySelectorAll('*');
    const tree = [];
    let currentBab = null;
    let currentPasal = null;
    let currentAyat = null;
    let currentHuruf = null;
    
    // Regex patterns
    const babPattern = /^BAB\s+([IVXLCDM]+|[0-9]+)/i;
    const pasalPattern = /^Pasal\s+(\d+[A-Z]?)/i;
    const ayatPattern = /^\((\d+)\)/;
    const hurufPattern = /^([a-zA-Z]+)\./;
    const angkaPattern = /^(\d+)\./;
    
    const processedElements = new Set();
    
    function getBulletText(el) {
        const span = el.querySelector('span');
        if (span) {
            const spanText = (span.textContent || '').trim();
            if (spanText.match(/^(\(\d+\)|[a-zA-Z]+\.|\d+\.)$/)) {
                return spanText;
            }
        }
        const text = (el.textContent || '').trim();
        const m = text.match(/^(\(\d+\)|[a-zA-Z]+\.|\d+\.)/);
        if (m) {
            return m[1];
        }
        return null;
    }
    
    allElements.forEach(el => {
        if (processedElements.has(el)) return;
        if (el.closest('.toc-item') || el.closest('.share-toolbar') || el.closest('#toc-container')) return;
        
        const isHeading = ['H1', 'H2', 'H3', 'H4', 'H5', 'H6'].includes(el.tagName);
        
        if (isHeading) {
            const text = (el.textContent || '').trim();
            const directText = Array.from(el.childNodes)
                .filter(node => node.nodeType === 3)
                .map(node => (node.textContent || '').trim())
                .join(' ').trim();
            
            const babMatch = directText.match(babPattern) || text.substring(0, 20).match(babPattern);
            const pasalMatch = directText.match(pasalPattern) || text.substring(0, 15).match(pasalPattern);
            
            if (babMatch) {
                const babNum = babMatch[1];
                const babKey = 'BAB-' + babNum;
                const node = {
                    type: 'BAB',
                    num: babNum,
                    title: 'BAB ' + babNum,
                    key: babKey,
                    children: [],
                    element: el
                };
                tree.push(node);
                currentBab = node;
                currentPasal = null;
                currentAyat = null;
                currentHuruf = null;
                
                window.tocElements[babKey] = el;
                el.id = babKey;
                
                el.querySelectorAll('*').forEach(child => processedElements.add(child));
                
            } else if (pasalMatch) {
                const pasalNum = pasalMatch[1];
                const pasalKey = (currentBab ? currentBab.key + '-' : '') + 'Pasal-' + pasalNum;
                const node = {
                    type: 'Pasal',
                    num: pasalNum,
                    title: 'Pasal ' + pasalNum,
                    key: pasalKey,
                    children: [],
                    element: el
                };
                if (currentBab) {
                    currentBab.children.push(node);
                } else {
                    tree.push(node);
                }
                currentPasal = node;
                currentAyat = null;
                currentHuruf = null;
                
                window.tocElements[pasalKey] = el;
                el.id = pasalKey;
                
                el.querySelectorAll('*').forEach(child => processedElements.add(child));
            }
            
        } else if (el.tagName === 'LI' || el.tagName === 'P') {
            const bullet = getBulletText(el);
            if (bullet && currentPasal) {
                let node = null;
                if (bullet.match(ayatPattern)) {
                    const num = bullet.match(ayatPattern)[1];
                    const key = currentPasal.key + '-Ayat-' + num;
                    node = {
                        type: 'Ayat',
                        num: num,
                        title: 'Ayat (' + num + ')',
                        key: key,
                        children: [],
                        element: el
                    };
                    currentPasal.children.push(node);
                    currentAyat = node;
                    currentHuruf = null;
                    
                } else if (bullet.match(hurufPattern)) {
                    const char = bullet.match(hurufPattern)[1];
                    if (['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X'].includes(char.toUpperCase())) {
                        return;
                    }
                    const parent = currentAyat || currentPasal;
                    const key = parent.key + '-Huruf-' + char.toUpperCase();
                    node = {
                        type: 'Huruf',
                        num: char.toUpperCase(),
                        title: 'Huruf ' + char.toUpperCase(),
                        key: key,
                        children: [],
                        element: el
                    };
                    parent.children.push(node);
                    currentHuruf = node;
                    
                } else if (bullet.match(angkaPattern)) {
                    const num = bullet.match(angkaPattern)[1];
                    if (currentHuruf) {
                        const key = currentHuruf.key + '-Angka-' + num;
                        node = {
                            type: 'Angka',
                            num: num,
                            title: 'Angka ' + num,
                            key: key,
                            children: [],
                            element: el
                        };
                        currentHuruf.children.push(node);
                    }
                }
                
                if (node) {
                    window.tocElements[node.key] = el;
                    el.id = node.key;
                    el.querySelectorAll('*').forEach(child => processedElements.add(child));
                }
            }
        }
    });
    
    // Render the tree HTML for each container with its index to ensure unique element IDs
    tocBabContainers.forEach((container, idx) => {
        let tocHtml = '';
        tree.forEach(node => {
            tocHtml += renderNode(node, idx);
        });
        container.innerHTML = tocHtml;
    });
    
    // Handle clicks on static TOC items (Pembukaan, Penjelasan)
    tocNavs.forEach(nav => {
        nav.addEventListener('click', function(e) {
            const link = e.target.closest('a.toc-item[data-search]');
            if (link) {
                e.preventDefault();
                const searchTerms = link.getAttribute('data-search');
                if (searchTerms) {
                    const terms = searchTerms.split(',').map(t => t.trim());
                    
                    for (let el of allElements) {
                        const text = (el.textContent || '').trim().toUpperCase();
                        for (let term of terms) {
                            if (text.startsWith(term.toUpperCase()) || text.includes(term.toUpperCase())) {
                                const containerRect = scrollContainer.getBoundingClientRect();
                                const elementRect = el.getBoundingClientRect();
                                const scrollTop = scrollContainer.scrollTop + (elementRect.top - containerRect.top) - 30;
                                
                                scrollContainer.scrollTo({
                                    top: scrollTop,
                                    behavior: 'smooth'
                                });
                                
                                document.querySelectorAll('.toc-item-link, .toc-sub-item-link, .toc-item, .toc-sub-item').forEach(l => l.classList.remove('active'));
                                link.classList.add('active');
                                
                                // Close offcanvas if inside mobile TOC
                                try {
                                    const offcanvasEl = document.getElementById('offcanvasToc');
                                    if (offcanvasEl && window.bootstrap && window.bootstrap.Offcanvas) {
                                        const bsOffcanvas = window.bootstrap.Offcanvas.getInstance(offcanvasEl);
                                        if (bsOffcanvas) {
                                            bsOffcanvas.hide();
                                        }
                                    }
                                } catch (err) {
                                    console.error("Error hiding offcanvas:", err);
                                }
                                
                                return;
                            }
                        }
                    }
                }
            }
        });
    });
    
    // Assign IDs deterministically to all remaining blocks
    document.querySelectorAll('.regulation-content-main').forEach((scrollContainer, containerIdx) => {
        scrollContainer.style.position = 'relative';
        
        const contentBlocks = scrollContainer.querySelectorAll('p, li, td, h1, h2, h3, h4, h5, h6');
        contentBlocks.forEach((block, index) => {
            if (!block.id) {
                let prefix = "sec";
                const text = (block.textContent || '').trim();
                if (text.match(/^Pasal\s+\d+/i)) prefix = "pasal";
                else if (text.match(/^BAB\s+[IVXLCDM]+/i)) prefix = "bab";
                else if (text.match(/^\(\d+\)/)) prefix = "ayat";
                block.id = prefix + '-' + containerIdx + '-' + index;
            }
        });
        
        // Share toolbar setup
        const shareToolbar = document.createElement('div');
        shareToolbar.className = 'share-toolbar shadow-sm border bg-white';
        shareToolbar.innerHTML = `
            <button class="btn btn-sm btn-light border-0 share-copy" title="Salin Tautan"><i class="fa fa-link text-secondary"></i></button>
            <button class="btn btn-sm btn-light border-0 share-wa" title="Bagikan ke WhatsApp"><i class="fa fa-whatsapp text-success"></i></button>
            <button class="btn btn-sm btn-light border-0 share-tw" title="Bagikan ke Twitter"><i class="fa fa-twitter text-info"></i></button>
            <button class="btn btn-sm btn-light border-0 share-fb" title="Bagikan ke Facebook"><i class="fa fa-facebook text-primary"></i></button>
        `;
        shareToolbar.style.position = 'absolute';
        shareToolbar.style.display = 'none';
        shareToolbar.style.zIndex = '1000';
        shareToolbar.style.borderRadius = '4px';
        shareToolbar.style.padding = '2px';
        shareToolbar.style.gap = '2px';
        scrollContainer.appendChild(shareToolbar);
        
        let currentHoveredBlock = null;
        
        scrollContainer.addEventListener('mousemove', function(e) {
            if (e.target.closest('.share-toolbar')) return;
            
            const block = e.target.closest('p, li, td, h1, h2, h3, h4, h5, h6');
            if (block && (block.textContent || '').trim() && !block.closest('#toc-container')) {
                if (currentHoveredBlock !== block) {
                    if (currentHoveredBlock) currentHoveredBlock.classList.remove('hover-highlight');
                    currentHoveredBlock = block;
                    
                    block.classList.add('hover-highlight');
                    
                    shareToolbar.style.display = 'flex';
                    const containerRect = scrollContainer.getBoundingClientRect();
                    const blockRect = block.getBoundingClientRect();
                    
                    const topPos = (blockRect.top - containerRect.top) + scrollContainer.scrollTop + 5;
                    const tbWidth = shareToolbar.offsetWidth || 135; 
                    const leftPos = (blockRect.right - containerRect.left) - tbWidth - 5;
                    
                    const actualLeft = Math.max(10, Math.min(leftPos, scrollContainer.clientWidth - tbWidth - 10));
                    shareToolbar.style.top = topPos + 'px';
                    shareToolbar.style.left = actualLeft + 'px';
                }
            } else {
                if (currentHoveredBlock) {
                    const blockRect = currentHoveredBlock.getBoundingClientRect();
                    const isNear = (e.clientX >= blockRect.left - 10 && e.clientX <= blockRect.right + 10 &&
                                    e.clientY >= blockRect.top - 10 && e.clientY <= blockRect.bottom + 10);
                    if (!isNear) {
                        currentHoveredBlock.classList.remove('hover-highlight');
                        currentHoveredBlock = null;
                        shareToolbar.style.display = 'none';
                    }
                }
            }
        });
        
        scrollContainer.addEventListener('mouseleave', function() {
            shareToolbar.style.display = 'none';
            if (currentHoveredBlock) {
                currentHoveredBlock.classList.remove('hover-highlight');
                currentHoveredBlock = null;
            }
        });
        
        const baseUrl = window.location.origin + window.location.pathname;
        
        shareToolbar.querySelector('.share-copy').addEventListener('click', function(e) {
            e.preventDefault();
            if (currentHoveredBlock) {
                const url = baseUrl + window.location.search + '#' + currentHoveredBlock.id;
                history.replaceState(null, null, url);
                navigator.clipboard.writeText(url).then(() => {
                    const icon = this.querySelector('i');
                    icon.className = 'fa fa-check text-success';
                    setTimeout(() => icon.className = 'fa fa-link text-secondary', 2000);
                });
            }
        });
        
        shareToolbar.querySelector('.share-wa').addEventListener('click', function(e) {
            e.preventDefault();
            if (currentHoveredBlock) {
                const url = baseUrl + window.location.search + '#' + currentHoveredBlock.id;
                const title = document.title;
                const text = encodeURIComponent(title + '\n\nLihat bagian ini di peraturan:\n' + url);
                window.open('https://api.whatsapp.com/send?text=' + text, '_blank');
            }
        });
        
        shareToolbar.querySelector('.share-tw').addEventListener('click', function(e) {
            e.preventDefault();
            if (currentHoveredBlock) {
                const url = baseUrl + window.location.search + '#' + currentHoveredBlock.id;
                const title = document.title;
                const text = encodeURIComponent(title + ' - Lihat bagian ini: ');
                window.open('https://twitter.com/intent/tweet?text=' + text + '&url=' + encodeURIComponent(url), '_blank');
            }
        });
        
        shareToolbar.querySelector('.share-fb').addEventListener('click', function(e) {
            e.preventDefault();
            if (currentHoveredBlock) {
                const url = baseUrl + window.location.search + '#' + currentHoveredBlock.id;
                window.open('https://www.facebook.com/sharer/sharer.php?u=' + encodeURIComponent(url), '_blank');
            }
        });
    });
    
    // Handle automatic scrolling and expanding of hash key after page load
    if (window.location.hash) {
        const hashKey = window.location.hash.substring(1);
        setTimeout(() => {
            window.expandParentsOf(hashKey);
            const targetEl = document.getElementById(hashKey);
            if (targetEl) {
                const scrollContainer = targetEl.closest('.regulation-content-main');
                if (scrollContainer) {
                    const containerRect = scrollContainer.getBoundingClientRect();
                    const elementRect = targetEl.getBoundingClientRect();
                    const scrollTop = scrollContainer.scrollTop + (elementRect.top - containerRect.top) - 30;
                    
                    scrollContainer.scrollTo({
                        top: scrollTop,
                        behavior: 'smooth'
                    });
                    
                    targetEl.classList.add('hover-highlight');
                    setTimeout(() => targetEl.classList.remove('hover-highlight'), 3000);
                }
            }
        }, 500);
    }
}

// Robust polling initialization to handle dynamic Odoo template rendering
function startTocInitialization() {
    let attempts = 0;
    const interval = setInterval(() => {
        const scrollContainer = document.querySelector('.regulation-content-main');
        const tocBabContainer = document.querySelector('.toc-bab-container') || document.getElementById('toc-bab-container');
        attempts++;
        
        if (scrollContainer && tocBabContainer) {
            clearInterval(interval);
            initTocAndShare();
        } else if (attempts > 50) {
            clearInterval(interval);
        }
    }, 100);
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', startTocInitialization);
} else {
    startTocInitialization();
}