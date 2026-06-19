# Fitur Upload PDF - Legal Regulations Module

## 📋 Ringkasan Fitur

Fitur ini memungkinkan **Administrator** untuk mengupload file PDF peraturan, sementara **User Biasa** hanya bisa melihat dan mendownload file PDF tersebut.

## 🔐 Pembatasan Akses

### Administrator (base.group_system)
- ✅ **Upload** file PDF
- ✅ **Edit/Hapus** file PDF
- ✅ **Download** file PDF
- ✅ **Full CRUD** pada peraturan

### User Biasa (base.group_user)
- ❌ **Tidak bisa Upload** file PDF
- ❌ **Tidak bisa Edit** peraturan
- ✅ **Bisa Lihat** semua peraturan
- ✅ **Bisa Download** file PDF yang tersedia

### Public User (base.group_public)
- ❌ **Tidak bisa Upload** file PDF
- ❌ **Tidak bisa Edit** peraturan
- ✅ **Bisa Lihat** peraturan yang berlaku saja
- ✅ **Bisa Download** file PDF (via website)

## 🎯 Cara Penggunaan

### Untuk Administrator

1. **Login sebagai Admin**
2. Buka menu **Legal Regulations**
3. Pilih atau buat peraturan baru
4. Klik tab **"File PDF"** (tab ini hanya terlihat untuk admin)
5. Klik **"Choose File"** untuk upload PDF
6. Pilih file PDF (max 10 MB)
7. Klik **"Save"**

### Untuk User Biasa

1. **Login sebagai User**
2. Buka menu **Legal Regulations**
3. Pilih peraturan yang ingin dilihat
4. Jika ada file PDF, akan terlihat:
   - Button **"Download PDF"** di header
   - Badge ukuran file di pojok kanan atas
   - Tab **"File PDF"** menampilkan info file
5. Klik **"Download PDF"** untuk mengunduh

## 🛠️ Implementasi Teknis

### Model Changes (legal_regulation.py)

```python
# Field baru untuk upload PDF
file_pdf = fields.Binary('File PDF', attachment=True)
file_name = fields.Char('Nama File PDF')
file_size = fields.Integer('Ukuran File (KB)', compute='_compute_file_size')

# Method untuk download
def action_download_pdf(self):
    return {
        'type': 'ir.actions.act_url',
        'url': f'/web/content?model=legal.regulation&id={self.id}&field=file_pdf...',
        'target': 'self',
    }

# Validasi di create/write
def create(self, vals_list):
    if vals.get('file_pdf') and not self.env.user.has_group('base.group_system'):
        raise AccessError('Hanya Administrator yang dapat mengupload file PDF.')

def write(self, vals):
    if 'file_pdf' in vals and not self.env.user.has_group('base.group_system'):
        raise AccessError('Hanya Administrator yang dapat mengupload file PDF.')
```

### View Changes

#### Admin View (legal_regulation_views.xml)
- Tab "File PDF" dengan `groups="base.group_system"` 
- Field upload: `<field name="file_pdf" filename="file_name"/>`
- Button download di header
- Stat button ukuran file

#### User View (legal_regulation_views_user.xml)
- Form `create="false" edit="false" delete="false"`
- Tab "File PDF" hanya untuk display info
- Button download di header
- Semua field readonly

### Security Rules (legal_regulation_security.xml)

```xml
<!-- User: Read Only -->
<record id="legal_regulation_user_rule" model="ir.rule">
    <field name="perm_read" eval="True"/>
    <field name="perm_write" eval="False"/>
    <field name="perm_create" eval="False"/>
    <field name="perm_unlink" eval="False"/>
</record>

<!-- Admin: Full Access -->
<record id="legal_regulation_admin_rule" model="ir.rule">
    <field name="perm_read" eval="True"/>
    <field name="perm_write" eval="True"/>
    <field name="perm_create" eval="True"/>
    <field name="perm_unlink" eval="True"/>
</record>
```

### Access Rights (ir.model.access.csv)

```csv
access_legal_regulation_user,legal.regulation.user,model_legal_regulation,base.group_user,1,0,0,0
access_legal_regulation_manager,legal.regulation.manager,model_legal_regulation,base.group_system,1,1,1,1
```

## 🔒 Keamanan

### Lapisan Keamanan yang Diterapkan:

1. **Record Rules** - Mengatur siapa bisa read/write/create/delete
2. **Access Rights** - Pembatasan di level model
3. **Field Groups** - Tab PDF hanya muncul untuk admin
4. **Form Attributes** - `create="false" edit="false"` untuk user
5. **Code Validation** - Error jika user coba upload via API/RPC
6. **View Inheritance** - View berbeda untuk admin vs user

### Error Messages:

- Jika user coba upload: **"Hanya Administrator yang dapat mengupload file PDF."**
- Jika download file kosong: **"File PDF tidak tersedia untuk peraturan ini."**

## 📊 Field Baru di Database

| Field Name | Type | Description |
|------------|------|-------------|
| `file_pdf` | Binary | File PDF dalam format base64 |
| `file_name` | Char | Nama file asli (e.g., "UU_1_2023.pdf") |
| `file_size` | Integer | Ukuran file dalam KB (computed) |

## 🎨 UI/UX Features

### Di List View:
- Kolom PDF dengan icon download (hanya muncul jika ada file)

### Di Form View (Admin):
- Tab "File PDF" untuk upload
- Button "Download PDF" di header
- Stat button ukuran file
- Info panel tentang pembatasan

### Di Form View (User):
- Button "Download PDF" di header
- Stat button ukuran file (readonly)
- Tab "File PDF" dengan alert sukses jika ada file
- Semua field readonly

## 🧪 Testing

### Test Case 1: Admin Upload PDF
1. Login sebagai admin
2. Buka peraturan
3. Upload PDF → ✅ Berhasil
4. File tersimpan dan ukuran terdeteksi

### Test Case 2: User Coba Upload
1. Login sebagai user
2. Buka peraturan
3. Tab "File PDF" tidak terlihat → ✅ Correct
4. Form dalam mode readonly → ✅ Correct

### Test Case 3: User Download PDF
1. Login sebagai user
2. Buka peraturan dengan PDF
3. Klik "Download PDF" → ✅ File terdownload
4. Ukuran file terlihat → ✅ Correct

### Test Case 4: API Upload Attempt
```python
# User coba upload via RPC/API
regulation.write({'file_pdf': base64_content})
# → AccessError: "Hanya Administrator yang dapat mengupload file PDF."
```

## 📦 Files Modified

1. `models/legal_regulation.py` - Field baru + validasi
2. `views/legal_regulation_views.xml` - Admin view + upload
3. `views/legal_regulation_views_user.xml` - User readonly view
4. `security/legal_regulation_security.xml` - Record rules
5. `security/ir.model.access.csv` - Access rights
6. `__manifest__.py` - Version bump + new data files

## 🚀 Deployment

```bash
# Upgrade module
cd "/c/Program Files/Odoo"
python/python.exe server/odoo-bin -c server/odoo.conf -d odoo19 -u legal_regulations --stop-after-init

# Restart service
net stop odoo-server-19.0
net start odoo-server-19.0
```

## 📝 Notes

- File disimpan sebagai **attachment** (tidak langsung di DB record)
- Ukuran file dihitung otomatis dari base64 string
- Format yang diperbolehkan: **PDF only**
- Ukuran maksimal: **10 MB** (dapat dikonfigurasi)
- User tidak bisa edit via form, API, atau RPC
- Download menggunakan URL direct dari Odoo web controller

## ✨ Future Enhancements

- [ ] Preview PDF di dalam Odoo (menggunakan PDF viewer)
- [ ] Bulk upload multiple PDFs
- [ ] PDF versioning (multiple versions per regulation)
- [ ] OCR untuk extract text dari PDF
- [ ] Integration dengan peraturan_merger module
- [ ] Watermark untuk downloaded PDFs
- [ ] Download statistics/tracking
