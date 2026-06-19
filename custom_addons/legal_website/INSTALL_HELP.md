# 🚀 PANDUAN INSTALL LEGAL WEBSITE DI ODOO - MANUAL

## ❗ PENJELASAN ERROR "from odoo import models, fields, api"

Error ini NORMAL karena:
- File `legal_article.py` adalah **Odoo module**, bukan Python script biasa
- Import `from odoo import models, fields, api` hanya berfungsi di dalam **environment Odoo**
- File ini akan otomatis ter-load ketika Odoo server berjalan

## 📋 LANGKAH-LANGKAH INSTALL (MUDAH)

### **Step 1: Start Odoo Server**
```bash
# Buka Command Prompt/Terminal
cd "C:\Program Files\Odoo"

# Start Odoo server
python/python.exe server/odoo-bin server --addons-path=server/addons,custom_addons
```

Server akan start di `http://localhost:8069`

### **Step 2: Setup Database (First Time)**
1. **Buka browser**: `http://localhost:8069`
2. Akan muncul **Database Manager**
3. **Create Database:**
   - Database Name: `legal_website`
   - Email: `admin@example.com` 
   - Password: `admin123`
   - Language: `English`
   - Country: `Indonesia`
4. Klik **Create Database**
5. **Tunggu proses selesai** (2-5 menit)

### **Step 3: Install Legal Website Module**
1. Setelah database ready, login dengan admin/admin123
2. Pergi ke **Apps** menu
3. Klik **Update Apps List** (PENTING!)
4. Search: **"Legal Website"** atau **"legal_website"**
5. Klik **Install**
6. **Tunggu instalasi selesai** (30-60 detik)

### **Step 4: Verifikasi Installation**
Setelah install berhasil, akan muncul:
- **Main menu** baru: **"Website Hukum"**
- **Sub-menu**: Konten, Pencarian, dll

### **Step 5: Test Website**
1. **Homepage**: `http://localhost:8069/` 
2. **Search test**: Ketik "hukum pidana" dan klik Cari
3. **Hasil**: Mock search results akan muncul!

## 🛠️ TROUBLESHOOTING

### **Problem 1: Module tidak muncul di Apps**
**Solution:**
```bash
# Restart Odoo dengan update
python/python.exe server/odoo-bin server --addons-path=server/addons,custom_addons --update=all --database=legal_website
```

### **Problem 2: Import error saat edit file**
**Explanation:**
- ✅ **NORMAL**: Error import saat edit file di VS Code/editor
- ✅ **AKAN HILANG**: Ketika Odoo server berjalan
- ✅ **FILE TETAP VALID**: Odoo akan load dengan benar

### **Problem 3: Database connection error**
**Solution:**
```bash
# Install PostgreSQL jika belum ada
# Atau gunakan SQLite (built-in)
```

### **Problem 4: Module install failed**
**Solution:**
1. Check file permissions di `custom_addons/legal_website/`
2. Pastikan semua file ada (check dengan `dir` atau `ls`)
3. Restart Odoo server

## 🎯 QUICK START (5 MENIT)

### **Opsi 1: Manual Install**
```bash
# Terminal 1: Start server
cd "C:\Program Files\Odoo"
python/python.exe server/odoo-bin server --addons-path=server/addons,custom_addons

# Browser: http://localhost:8069
# Create database → Install Legal Website → Test
```

### **Opsi 2: Command Line Install**
```bash
# Create database + install module sekaligus
python/python.exe server/odoo-bin server \
  --addons-path=server/addons,custom_addons \
  --database=legal_db \
  --init=legal_website \
  --stop-after-init

# Start server normal
python/python.exe server/odoo-bin server \
  --addons-path=server/addons,custom_addons \
  --database=legal_db
```

## ✅ VERIFICATION CHECKLIST

Setelah install berhasil, cek:

- [ ] **Odoo server running** di http://localhost:8069
- [ ] **Login berhasil** dengan admin credentials  
- [ ] **Main menu "Website Hukum"** muncul
- [ ] **Apps → Legal Website** status = Installed
- [ ] **Website accessible** di http://localhost:8069/
- [ ] **Search berfungsi** dengan query "hukum pidana"
- [ ] **Mock results** muncul dengan benar

## 🎉 HASIL YANG DIHARAPKAN

Setelah semuanya berhasil:

### **Backend (Admin):**
```
🏠 Website Hukum (Main Menu)
├── 📝 Konten
│   ├── 📄 Artikel (Sample articles)
│   ├── 🏷️ Kategori (Pidana, Perdata, dll)
│   └── 🏷️ Tag (KUHP, UUD, dll)
└── 🔍 Pencarian  
    ├── ⚙️ Konfigurasi Enhanced
    └── 📊 Riwayat & Analitik
```

### **Frontend (Website):**
- **Homepage**: Modern legal website design
- **Search box**: Prominent di header
- **Categories**: Grid dengan artikel count
- **Articles**: Sample legal content
- **Search results**: Mock data yang realistis

### **Search Test Results:**
Query: "hukum pidana"
```
🏛️ Hukum Pidana Indonesia - Mahkamah Agung RI (Score: 95)
📚 Hukum Pidana Indonesia - BPHN Kemenkumham (Score: 90)  
📰 Hukum Pidana Indonesia - HukumOnline (Score: 85)
📖 Wikipedia: Hukum Pidana (Score: 70)
```

## 📞 BANTUAN LEBIH LANJUT

Jika masih ada masalah:
1. **Check Odoo logs** di terminal/command prompt
2. **Restart server** dengan parameter `--dev=xml`
3. **Clear browser cache** (Ctrl+F5)
4. **Check file permissions** di custom_addons folder

**Import error "from odoo import models" adalah NORMAL saat editing file. Module akan berfungsi dengan benar ketika Odoo server running!** ✅