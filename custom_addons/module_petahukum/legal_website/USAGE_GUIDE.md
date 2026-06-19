# 🎯 TUTORIAL PENGGUNAAN WEBSITE HUKUM DI ODOO

## 📋 Setelah Install Module

### **1. Menu yang Muncul:**

```
🏠 Website Hukum (Main Menu)
├── 📝 Konten
│   ├── 📄 Artikel        # Manage artikel hukum
│   ├── 🏷️ Kategori       # Manage kategori (Pidana, Perdata, dll)  
│   └── 🏷️ Tag           # Manage tags artikel
│
└── 🔍 Pencarian
    ├── ⚙️ Konfigurasi Enhanced  # Setup search engine
    ├── ⚙️ Konfigurasi          # Basic search config
    └── 📊 Riwayat & Analitik   # Search analytics
```

## 🔧 **LANGKAH SETUP AWAL:**

### **Step 1: Cek Search Configuration**
1. Pergi ke **Website Hukum → Pencarian → Konfigurasi Enhanced**
2. Pastikan ada config "Demo Search (Mock Data)" yang **Active = True**
3. Jika belum ada, klik **Create** dan buat:
   ```
   Name: Demo Search
   Search Type: Mock Search (Demo)  
   Language: id
   Active: ✓
   ```

### **Step 2: Cek Sample Data**
1. Pergi ke **Website Hukum → Konten → Artikel**
2. Pastikan ada artikel sample yang sudah di-create
3. Pastikan **Website Published = True** untuk artikel yang ingin tampil

### **Step 3: Cek Categories**  
1. Pergi ke **Website Hukum → Konten → Kategori**
2. Pastikan ada kategori: Hukum Pidana, Perdata, Tata Negara, Bisnis
3. Set warna berbeda untuk setiap kategori

## 🌐 **AKSES WEBSITE:**

### **Frontend URLs:**
- **Homepage**: `http://localhost:8069/`
- **Pencarian**: `http://localhost:8069/legal/search`
- **Artikel**: `http://localhost:8069/legal/articles`
- **API Search**: `http://localhost:8069/legal/search/api`

### **Test Search:**
1. Buka `http://localhost:8069/`
2. Di search box, ketik: **"hukum pidana"**
3. Klik **Cari**
4. Akan muncul hasil mock search yang realistis!

## 📝 **MEMBUAT KONTEN BARU:**

### **Buat Artikel Baru:**
1. **Website Hukum → Konten → Artikel → Create**
2. Isi form:
   ```
   Judul: "Panduan Hukum Kontrak Bisnis"
   Kategori: Hukum Bisnis
   Tags: Kontrak, Bisnis, Perusahaan
   Penulis: [Auto-filled dengan user login]
   ```
3. Di tab **Konten**:
   - **Ringkasan**: Brief description artikel
   - **Konten**: Full content dengan HTML editor
4. Di tab **SEO**:
   - Meta Title, Description untuk SEO
5. **Centang "Website Published"** untuk publish
6. **Save**

### **Buat Kategori Baru:**
1. **Website Hukum → Konten → Kategori → Create**
2. Isi:
   ```
   Nama: Hukum Keluarga
   Deskripsi: Artikel tentang hukum keluarga Indonesia
   Sequence: 50
   Warna: 5 (pilih warna)
   ```

## 🎨 **CUSTOMISASI TAMPILAN:**

### **Edit Menu Website:**
1. Pergi ke **Website** app
2. Klik **Edit** di website
3. Customize navigation menu, colors, dll

### **Edit Template:**
Files yang bisa diedit:
- `views/website_legal_templates.xml` - Layout website
- `static/src/css/legal_website.css` - Styling
- `static/src/js/legal_search.js` - JavaScript functionality

## 🔍 **SETUP SEARCH PRODUCTION:**

### **Untuk SearXNG Real:**
1. **Website Hukum → Pencarian → Konfigurasi Enhanced → Create**
2. Setup:
   ```
   Name: Production SearXNG
   Search Type: SearXNG Instance
   SearXNG URL: https://search.your-domain.com
   Search Engines: google,bing,duckduckgo
   Categories: general
   Language: id
   Safe Search: Moderate
   Active: ✓
   ```
3. **Deactivate** config demo/mock

### **Untuk DuckDuckGo:**
1. **Create** new config:
   ```
   Name: DuckDuckGo Search  
   Search Type: DuckDuckGo API
   DuckDuckGo API: https://api.duckduckgo.com
   Language: id
   Active: ✓
   ```

## 📊 **MONITORING & ANALYTICS:**

### **Search Analytics:**
1. **Website Hukum → Pencarian → Riwayat & Analitik**
2. View semua search queries dari users
3. Graph view untuk trends
4. Pivot view untuk detailed analysis

### **Article Performance:**
1. **Website Hukum → Konten → Artikel**
2. Sort by **View Count** untuk lihat artikel populer
3. Track performance per kategori

## 🚀 **DEPLOY TO PRODUCTION:**

### **1. Domain Setup:**
Edit `odoo.conf`:
```ini
[options]
db_host = localhost
db_port = 5432
db_name = legal_production
xmlrpc_port = 80
xmlrpc_interface = 0.0.0.0
```

### **2. SSL Setup:**
```bash
# Install SSL certificate
# Configure nginx/apache proxy
```

### **3. Performance Optimization:**
1. Enable caching in odoo.conf
2. Optimize database queries
3. CDN for static assets

## 🛠️ **TROUBLESHOOTING:**

### **Module tidak muncul di Apps:**
1. **Apps → Update Apps List**
2. Restart Odoo server
3. Check addons-path includes custom_addons

### **Website tidak accessible:**
1. Check module **website** is installed
2. Check **legal_website** depends on website
3. Restart server dengan `-u legal_website`

### **Search tidak berfungsi:**
1. Check **Konfigurasi Enhanced** ada yang Active
2. Test dengan query sederhana: "hukum"
3. Check browser console untuk JS errors

### **Static files tidak load:**
1. Restart server dengan `--dev=xml`
2. Check file permissions
3. Force reload browser (Ctrl+F5)

## ✅ **CHECKLIST GO-LIVE:**

- [ ] Odoo server running stable
- [ ] Legal Website module installed
- [ ] Sample articles created & published
- [ ] Search configuration active
- [ ] Website accessible di domain
- [ ] SSL certificate configured
- [ ] Search analytics working
- [ ] Mobile responsive tested
- [ ] SEO meta tags configured
- [ ] Error handling tested

**🎉 Website siap digunakan!**