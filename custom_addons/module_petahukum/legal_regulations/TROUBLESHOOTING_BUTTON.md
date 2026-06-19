# Troubleshooting: Button Re-extract PDF Tidak Muncul

## Checklist Verifikasi

### ✅ Yang Sudah Dikonfirmasi Berhasil:
1. ✅ Method `action_reextract_pdf()` ada di `legal_regulation.py`
2. ✅ Button ada di `legal_regulation_views.xml`
3. ✅ Button ada di `legal_regulation_views_minimal.xml` (file aktif)
4. ✅ View ter-load di database (verified via XML-RPC)
5. ✅ Module sudah di-upgrade
6. ✅ Service Odoo sudah restart

### 🔍 Yang Perlu Dicek di Browser:

## Langkah 1: Hard Refresh Browser
**CARA PALING MUDAH - COBA INI DULU!**

1. Buka form peraturan yang ada PDF-nya
2. Tekan: **Ctrl + Shift + R** (Windows/Linux)
   atau: **Cmd + Shift + R** (Mac)
3. Tunggu halaman reload
4. Cek apakah button muncul

## Langkah 2: Cek Console Browser untuk Error

1. Buka form peraturan
2. Tekan **F12** (Developer Tools)
3. Klik tab **Console**
4. Cari error berwarna merah
5. Screenshot dan kirim ke saya

## Langkah 3: Cek Network Tab

1. F12 → Tab **Network**
2. Refresh halaman (F5)
3. Cari request ke `/web/webclient/load_menus` atau `/web/action/load`
4. Cek status code (harus 200 OK)

## Langkah 4: Clear Cache & Cookies

### Chrome/Edge:
1. Ctrl + Shift + Delete
2. Pilih: "Cached images and files" + "Cookies"
3. Time range: "All time"
4. Clear data
5. Login ulang ke Odoo

### Firefox:
1. Ctrl + Shift + Delete
2. Pilih: "Cache" + "Cookies"
3. Clear
4. Login ulang

## Langkah 5: Cek dengan Incognito/Private

1. **Chrome/Edge**: Ctrl + Shift + N
2. **Firefox**: Ctrl + Shift + P
3. Buka: http://localhost:8069
4. Login
5. Buka form peraturan
6. Cek apakah button muncul

Jika muncul di Incognito tapi tidak di normal → **CACHE PROBLEM**

## Langkah 6: Cek Inspeksi Element

1. Buka form peraturan
2. Klik kanan di area header (dekat button Download PDF)
3. Pilih **Inspect** atau **Inspect Element**
4. Di HTML tree, cari:
   ```html
   <button name="action_reextract_pdf"
   ```
5. Jika TIDAK KETEMU → problem di view load
6. Jika KETEMU tapi button tidak terlihat → problem CSS (invisible/display:none)

## Langkah 7: Force Update View dari Database

Jalankan command ini untuk force update view:

```bash
"/c/Program Files/Odoo/python/python.exe" "/c/Program Files/Odoo/server/odoo-bin" \
  -c "/c/Program Files/Odoo/server/odoo.conf" \
  -d odoo_legal_db \
  -u legal_regulations \
  --stop-after-init
```

Lalu restart service:
```bash
net stop odoo-server-19.0
net start odoo-server-19.0
```

## Langkah 8: Cek Developer Mode

1. Buka Odoo
2. Aktifkan Developer Mode:
   - Settings → General Settings
   - Scroll ke bawah
   - Klik **Activate Developer Mode**
3. Buka form peraturan
4. Klik icon **🐛 (bug)** di kanan atas form
5. Pilih **Edit View: Form**
6. Cari text: `action_reextract_pdf`
7. Jika TIDAK ADA → view belum ter-update

## Langkah 9: Manual SQL Check

Jika semua gagal, cek langsung di database:

```sql
SELECT name, arch_db 
FROM ir_ui_view 
WHERE model = 'legal.regulation' 
  AND type = 'form'
  AND arch_db LIKE '%action_reextract_pdf%';
```

## Langkah 10: Cek File Visibility Condition

Button hanya muncul jika **ada file PDF**. Pastikan:
1. Record peraturan yang Anda buka **PUNYA file_pdf**
2. Field `file_pdf` tidak kosong
3. File size > 0

Button punya kondisi:
```xml
invisible="not file_pdf"
```

Artinya: **button hidden jika tidak ada PDF**

## Quick Test

Buka Python console dan test:

```python
# Test 1: Cek method exists
from odoo import api, registry

db_name = 'odoo_legal_db'
reg = registry(db_name)

with reg.cursor() as cr:
    env = api.Environment(cr, 2, {})  # 2 = admin user ID
    LegalRegulation = env['legal.regulation']
    
    # Check method
    has_method = hasattr(LegalRegulation, 'action_reextract_pdf')
    print(f"Method exists: {has_method}")
    
    # Check view
    views = env['ir.ui.view'].search([
        ('model', '=', 'legal.regulation'),
        ('type', '=', 'form')
    ])
    
    for view in views:
        if 'action_reextract_pdf' in (view.arch_db or ''):
            print(f"Found in view: {view.name}")
```

## Kemungkinan Penyebab

| Masalah | Solusi |
|---------|--------|
| Browser cache | Hard refresh (Ctrl+Shift+R) |
| Session lama | Logout & login ulang |
| View tidak update | Upgrade module: -u legal_regulations |
| File tidak ada | Pastikan record punya file_pdf |
| CSS conflict | Inspect element, cek display/visibility |
| JavaScript error | Cek console browser (F12) |

## Jika Semua Gagal

Kirim info ini:

1. **Screenshot** halaman form peraturan (full screen)
2. **Console errors** (F12 → Console tab)
3. **Inspect element** HTML di area header button
4. **Output** dari script verify_button.py
5. **Browser** yang digunakan (Chrome/Firefox/Edge?)
6. **Odoo log** terakhir:
   ```bash
   tail -n 50 "/c/Program Files/Odoo/server/odoo.log"
   ```
