# Panduan Instalasi Website Hukum dengan SearXNG

## Ringkasan

Saya telah berhasil membuat modul website hukum lengkap dengan fitur pencarian canggih menggunakan SearXNG untuk Odoo. Website ini menyediakan:

### ✅ Fitur yang Sudah Dibuat:

1. **Website Hukum Lengkap**
   - Homepage dengan hero section dan kategori hukum
   - Sistem artikel dengan kategori (Pidana, Perdata, Tata Negara, Bisnis)
   - Tags system untuk artikel
   - SEO optimization

2. **Fitur Pencarian Canggih**
   - **Mock Search**: Demo search tanpa perlu internet (SUDAH AKTIF)
   - **SearXNG Integration**: Pencarian web seperti Google
   - **DuckDuckGo API**: Alternative search provider
   - **Dual Search**: Website lokal + web search bersamaan

3. **UI/UX Modern**
   - Responsive design with Bootstrap
   - AJAX search dengan autocomplete
   - Social sharing buttons
   - Reading progress indicator
   - Search suggestions dan history

4. **Backend Management**
   - Admin panel untuk manage artikel, kategori, tags
   - Search analytics dan history
   - Multiple search configuration
   - View tracking untuk artikel

## Cara Instalasi & Setup

### 1. Install Modul di Odoo

```bash
# Masuk ke direktori Odoo
cd "C:\Program Files\Odoo"

# Start Odoo server
odoo-bin -c odoo.conf --addons-path=addons,custom_addons

# Atau menggunakan file bat yang disediakan
.\install.bat
```

### 2. Install Modul via Odoo Interface

1. Login ke Odoo sebagai administrator
2. Pergi ke **Apps** menu
3. Klik **Update Apps List** 
4. Cari "Legal Website"
5. Klik **Install**

### 3. Akses Website

Setelah terinstall, website dapat diakses di:
- **Homepage**: `http://localhost:8069/`
- **Artikel**: `http://localhost:8069/legal/articles`
- **Pencarian**: `http://localhost:8069/legal/search`

### 4. Konfigurasi Pencarian

1. Login ke Odoo backend
2. Pergi ke **Website Hukum > Pencarian > Konfigurasi Enhanced**
3. Pilih jenis pencarian:
   - **Mock Search**: Demo tanpa internet (DEFAULT - SUDAH AKTIF)
   - **SearXNG**: Untuk pencarian web real 
   - **DuckDuckGo**: API gratis alternative

## Demo & Testing

### Test Pencarian Mock (Sudah Aktif)

Website sudah include demo search yang berfungsi tanpa internet:

1. Buka `http://localhost:8069/`
2. Ketik di search box: "hukum pidana"
3. Klik **Cari** 
4. Anda akan melihat hasil mock search yang realistis

### Test dengan Query Lain:
- "tindak pidana korupsi"
- "hukum perdata indonesia"  
- "KUHP"
- "undang-undang dasar"

## Struktur File Lengkap

```
legal_website/
├── __manifest__.py          # Modul configuration
├── __init__.py
├── README.md                # Dokumentasi lengkap
├── install.bat              # Windows installer
├── install.sh               # Linux installer  
├── test_searxng.py          # Test script
│
├── controllers/
│   ├── __init__.py
│   └── main.py              # Website controllers & API
│
├── models/
│   ├── __init__.py
│   ├── legal_article.py     # Artikel & kategori models
│   ├── legal_search.py      # Basic search config
│   └── legal_search_enhanced.py  # Enhanced search dengan mock
│
├── views/
│   ├── legal_article_views.xml      # Admin views untuk artikel
│   ├── legal_search_views.xml       # Admin views untuk search
│   ├── legal_search_enhanced_views.xml # Enhanced search admin
│   ├── website_legal_templates.xml   # Website templates
│   └── website_menu.xml             # Website menu structure
│
├── data/
│   └── website_data.xml     # Sample data & configurations
│
├── security/
│   └── ir.model.access.csv  # Security permissions
│
└── static/src/
    ├── css/
    │   └── legal_website.css     # Custom styling
    └── js/
        └── legal_search.js       # Interactive features
```

## Fitur Utama yang Berfungsi

### 1. Homepage
- Hero section dengan search box utama
- Kategori hukum dengan counter artikel
- Artikel terpopuler
- Fitur unggulan section

### 2. Sistem Pencarian Multi-Level
```
Search Input → Dual Search:
├── Local Articles (dari database website)
└── Web Search (SearXNG/Mock/DuckDuckGo)
```

### 3. Artikel Management
- WYSIWYG editor untuk konten
- Kategori: Pidana, Perdata, Tata Negara, Bisnis
- Tags system
- View counter
- SEO fields

### 4. Advanced Search Features
- Auto-suggestions
- Search history (localStorage)
- Popular searches
- Result scoring untuk legal content
- Error handling dan fallback

## Customization Guide

### Menambah Kategori Hukum
1. Backend: **Website Hukum > Konten > Kategori**
2. Klik **Create**
3. Isi nama, deskripsi, pilih warna
4. Save

### Menambah Artikel
1. Backend: **Website Hukum > Konten > Artikel**
2. Klik **Create**
3. Isi judul, pilih kategori, tags
4. Tulis konten dengan HTML editor
5. Centang **Website Published**
6. Save

### Mengaktifkan SearXNG Real
1. Setup SearXNG instance atau gunakan public instance
2. Backend: **Website Hukum > Pencarian > Konfigurasi Enhanced**
3. Create new record:
   - Name: "SearXNG Production"
   - Search Type: "SearXNG Instance"  
   - SearXNG URL: "https://your-searxng-instance.com"
   - Active: True
4. Deactivate mock search config

## API Endpoints

### Search API
```bash
curl -X POST http://localhost:8069/legal/search/api \
  -H "Content-Type: application/json" \
  -d '{"q": "hukum pidana", "page": 1, "per_page": 10}'
```

### Response Format
```json
{
  "results": [
    {
      "title": "Hukum Pidana Indonesia - Mahkamah Agung RI",
      "url": "https://mahkamahagung.go.id/search?q=hukum+pidana", 
      "content": "Informasi lengkap tentang hukum pidana Indonesia...",
      "engine": "mock",
      "score": 95
    }
  ],
  "total": 6,
  "query": "hukum pidana",
  "page": 1,
  "suggestions": ["hukum pidana indonesia", "kuhp terbaru 2024"]
}
```

## Status & Next Steps

### ✅ Sudah Selesai:
- [x] Website hukum complete dengan design modern
- [x] Mock search system yang realistis (AKTIF)
- [x] Admin panel untuk content management
- [x] Responsive design + JavaScript interactivity
- [x] Sample articles dan kategori
- [x] SEO optimization
- [x] Search analytics

### 🔄 Optional Enhancements:
- [ ] SearXNG production setup
- [ ] User registration & login
- [ ] Comment system untuk artikel
- [ ] Newsletter subscription
- [ ] Advanced search filters
- [ ] Multi-language support

## Troubleshooting

### Website tidak muncul
```bash
# Restart Odoo dengan force update
odoo-bin -c odoo.conf -u legal_website --addons-path=addons,custom_addons
```

### Search tidak berfungsi
1. Check konfigurasi di **Website Hukum > Pencarian > Konfigurasi Enhanced**
2. Pastikan ada config yang active=True
3. Test dengan query sederhana seperti "hukum"

### Error saat install
1. Pastikan requests library terinstall:
   ```bash
   python/python.exe -m pip install requests
   ```
2. Check file permissions di custom_addons folder

## Kesimpulan

Website hukum dengan SearXNG sudah **SIAP DIGUNAKAN** dengan fitur:
- ✅ Search seperti Google (mock data)  
- ✅ Database artikel hukum
- ✅ Admin panel lengkap
- ✅ Modern responsive design
- ✅ API endpoints

Untuk production, tinggal ganti mock search dengan SearXNG instance atau DuckDuckGo API real.