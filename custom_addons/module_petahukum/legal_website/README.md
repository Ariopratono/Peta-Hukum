# Website Hukum dengan Integrasi SearXNG

Website hukum yang dibangun dengan Odoo yang menyediakan fitur pencarian canggih menggunakan SearXNG.

## Fitur Utama

### 1. Pencarian Web dengan SearXNG
- Integrasi dengan SearXNG untuk pencarian seperti Google
- Dukungan multiple search engines (Google, Bing, DuckDuckGo)
- Filtering hasil khusus untuk konten hukum
- Scoring system untuk relevansi hasil pencarian
- Search history dan analytics

### 2. Manajemen Konten Hukum
- Artikel hukum dengan kategori dan tags
- Editor HTML untuk konten yang kaya
- SEO optimization untuk artikel
- Sistem publikasi dan view tracking

### 3. Kategori Hukum
- Hukum Pidana
- Hukum Perdata  
- Hukum Tata Negara
- Hukum Bisnis
- Dan kategori lainnya

### 4. Fitur Website
- Responsive design
- Search suggestions dan autocomplete
- Social sharing
- Related articles
- Reading progress indicator
- Back to top button

## Instalasi

1. Copy folder `legal_website` ke direktori `addons` atau `custom_addons` Odoo
2. Update apps list di Odoo
3. Install modul "Legal Website" dari Apps menu
4. Konfigurasi SearXNG URL di menu Pencarian > Konfigurasi

## Konfigurasi SearXNG

1. Buka menu **Website Hukum > Pencarian > Konfigurasi**
2. Edit konfigurasi default atau buat yang baru:
   - **SearXNG URL**: URL instance SearXNG (default: https://search.brave4u.com)
   - **Search Engines**: Mesin pencari yang digunakan (google,bing,duckduckgo)
   - **Categories**: Kategori pencarian (general)
   - **Language**: Bahasa pencarian (id untuk Indonesia)
   - **Safe Search**: Level safe search (0=None, 1=Moderate, 2=Strict)

## Penggunaan

### Admin/Content Manager
1. Buat kategori hukum di **Website Hukum > Konten > Kategori**
2. Buat tags di **Website Hukum > Konten > Tag**  
3. Buat artikel di **Website Hukum > Konten > Artikel**
4. Publikasikan artikel dengan mengaktifkan "Website Published"

### Pengguna Website
1. Akses homepage untuk melihat artikel terpopuler dan kategori
2. Gunakan search box untuk mencari informasi hukum
3. Browse artikel berdasarkan kategori
4. Baca artikel detail dengan fitur sharing dan related articles

## Fitur Pencarian

### Pencarian Web
- Menggunakan SearXNG untuk pencarian dari multiple sources
- Hasil diprioritaskan berdasarkan relevansi hukum
- Kata kunci hukum mendapat boost score
- Domain hukum resmi mendapat prioritas tinggi

### Pencarian Lokal
- Pencarian di artikel website sendiri
- Indexing pada judul, konten, dan ringkasan
- Suggestions berdasarkan artikel populer

### Analytics
- Tracking query pencarian
- Statistik penggunaan fitur pencarian
- Graph dan pivot views untuk analisis

## Customization

### Menambah Search Engine
Edit file `models/legal_search.py` dan tambahkan mesin pencari baru di parameter `search_engines`.

### Menambah Kategori Legal Keywords
Edit method `_calculate_legal_relevance` di `models/legal_search.py` untuk menambah kata kunci hukum yang akan di-boost.

### Styling
Edit file `static/src/css/legal_website.css` untuk customisasi tampilan.

### JavaScript Features  
Edit file `static/src/js/legal_search.js` untuk menambah fitur interaktif.

## Troubleshooting

### SearXNG Connection Error
- Periksa URL SearXNG instance
- Pastikan instance dapat diakses dari server Odoo
- Check firewall dan proxy settings

### Artikel Tidak Muncul di Website
- Pastikan artikel di-publish (Website Published = True)
- Clear website cache di Settings > Technical > Website

### Search Tidak Menampilkan Hasil
- Periksa konfigurasi SearXNG
- Check log error di developer console browser
- Verify search configuration is active

## API Endpoints

### Search API
```
POST /legal/search/api
Content-Type: application/json

{
  "q": "query string",
  "page": 1,
  "per_page": 10
}
```

### Response Format
```json
{
  "results": [
    {
      "title": "Result Title",
      "url": "https://example.com",
      "content": "Result content snippet",
      "engine": "google",
      "score": 85
    }
  ],
  "total": 100,
  "query": "search query",
  "page": 1,
  "suggestions": ["suggestion1", "suggestion2"]
}
```

## Dependencies

- Python packages: `requests`
- Odoo modules: `website`, `portal`
- External: SearXNG instance

## License

This module is licensed under LGPL-3.

## Support

Untuk support dan development lebih lanjut, hubungi developer team.