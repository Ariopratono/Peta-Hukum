# 🔗 Fitur Konsolidasi Peraturan

## Deskripsi

Fitur **Konsolidasi Peraturan** memungkinkan pengguna untuk menggabungkan beberapa versi peraturan (UU Induk + UU Perubahan) menjadi satu dokumen terpadu dengan tracking perubahan yang detail.

### Contoh Kasus

**UU ITE (Informasi dan Transaksi Elektronik):**
- ✅ UU 11/2008 - Versi Asli
- ✅ UU 19/2016 - Perubahan Pertama
- ✅ UU 1/2024 - Perubahan Kedua

**Hasil:** Naskah terpadu yang menampilkan:
- Pasal mana yang ditambah (highlight biru 🔵)
- Pasal mana yang diubah (highlight kuning 🟡)
- Pasal mana yang dihapus (strikethrough merah 🔴)
- Riwayat lengkap setiap perubahan

---

## 🎯 Fitur Utama

### 1. **Mode Tampilan**

#### Mode Anotasi (Recommended) ⭐
- Menampilkan versi **terbaru** dengan anotasi perubahan
- Setiap pasal diberi badge status:
  - ✅ **DITAMBAH** - Pasal baru yang tidak ada di versi sebelumnya
  - ⚠️ **DIUBAH** - Pasal yang mengalami perubahan isi
  - ❌ **DIHAPUS** - Pasal yang dihapus di versi terbaru
  - ✓ **TIDAK BERUBAH** - Pasal yang tetap sama
- Menampilkan riwayat perubahan untuk setiap pasal yang dimodifikasi

#### Mode Final
- Hanya menampilkan versi **terbaru** tanpa anotasi
- Cocok untuk membaca dokumen clean tanpa highlight

#### Mode Riwayat
- Menampilkan **semua versi** per pasal
- Cocok untuk analisis mendalam perubahan per pasal
- Setiap versi ditampilkan secara berurutan

#### Mode Perbandingan (Side by Side)
- Menampilkan **perbandingan kolom** semua versi
- Tabel dengan kolom untuk setiap UU
- Cocok untuk melihat perbedaan secara visual

---

## 📋 Cara Menggunakan

### Metode 1: Dari Menu (Recommended)

1. **Buka Menu:** `Legal Regulations` → `Konsolidasi Peraturan`
2. **Klik:** Tombol `BUAT` (Create)
3. **Isi Form:**
   - **Nama Konsolidasi:** Misal "UU ITE Terpadu (2008-2024)"
   - **Deskripsi:** Opsional, jelaskan konsolidasi ini
   - **Peraturan yang Digabung:** Pilih UU Induk + UU Perubahan
   - **Mode Tampilan:** Pilih salah satu (default: Anotasi)
4. **Preview (Opsional):** Klik `🔍 Preview` untuk melihat hasil sebelum save
5. **Generate:** Klik `✅ Generate & Simpan`

### Metode 2: Dari List Peraturan

1. **Buka:** `Legal Regulations` → `Peraturan Hukum`
2. **Pilih Multiple Records:** Centang UU Induk + UU Perubahan
3. **Klik:** Menu `Action` → `🔗 Buat Konsolidasi`
4. **Otomatis terisi:** Wizard akan terbuka dengan peraturan yang sudah dipilih
5. **Generate:** Klik `✅ Generate & Simpan`

---

## 🎨 Visualisasi Hasil

Hasil konsolidasi akan menampilkan:

```html
📋 Naskah Konsolidasi: UU ITE Terpadu (2008-2024)
Mode: Anotasi
Peraturan: UU 11/2008, UU 19/2016, UU 1/2024
Tanggal Generate: 26 Januari 2026

═══════════════════════════════════════

Pasal 1
├─ ✓ Tidak berubah
└─ (Isi pasal...)

Pasal 5
├─ ⚠️ Diubah oleh UU 19/2016
├─ 📜 Riwayat Perubahan:
│   ├─ UU 11/2008 (Original)
│   └─ UU 19/2016 (Current)
└─ (Isi pasal versi terbaru...)

Pasal 45
├─ ✅ Ditambahkan oleh UU 1/2024
└─ (Isi pasal baru...)

Pasal 52
├─ ❌ Dihapus pada versi selanjutnya
└─ (Isi pasal yang dihapus - strikethrough)
```

---

## 📊 Statistik Perubahan

Dashboard menampilkan:
- **Total Pasal:** Jumlah total pasal di semua versi
- **Pasal Ditambah:** Jumlah pasal baru yang ditambahkan
- **Pasal Diubah:** Jumlah pasal yang mengalami perubahan
- **Pasal Dihapus:** Jumlah pasal yang dihapus

---

## 🔧 Opsi Lanjutan

### Auto-Save sebagai Peraturan Baru

Jika opsi **"Simpan sebagai Peraturan Baru"** dicentang:
- Hasil konsolidasi akan disimpan sebagai record `legal.regulation` baru
- Tipe dokumen: **"Naskah Kompilasi/Gabungan"**
- Nomor: **"KONSOLIDASI-{nomor_asli}"**
- Isi peraturan: HTML hasil konsolidasi
- Relasi: Link ke semua peraturan sumber

**Keuntungan:**
- Hasil konsolidasi dapat diakses seperti peraturan biasa
- Dapat di-search, di-filter, dan di-export
- Memiliki semua field metadata peraturan

---

## 🔄 Workflow

```
┌─────────────────────┐
│ Pilih Peraturan     │
│ (UU Induk +         │
│  UU Perubahan)      │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Pilih Mode Tampilan │
│ (Anotasi/Final/     │
│  Riwayat/Compare)   │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Preview (Opsional)  │
│ Lihat hasil         │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Generate Konsolidasi│
│ Parse struktur pasal│
│ Detect perubahan    │
│ Generate HTML       │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Hasil Disimpan      │
│ - Consolidation     │
│   record            │
│ - (Optional) New    │
│   regulation record │
└─────────────────────┘
```

---

## 🛠️ Teknologi

### Algoritma Perbandingan

- **difflib.SequenceMatcher:** Menghitung similarity ratio antara dua text
- **Threshold:** 0.95 (95% sama = tidak berubah)
- **Regex Parsing:** Extract struktur pasal dari HTML

### Struktur Data

```python
{
    'regulation': <legal.regulation record>,
    'structure': {
        '1': {
            'number': '1',
            'content': '<HTML content>',
            'clean_content': 'Plain text',
            'ayat': [
                {'number': '1', 'text': '...'},
                {'number': '2', 'text': '...'}
            ]
        },
        '2': { ... },
        ...
    }
}
```

---

## 📝 Best Practices

### 1. Urutan Peraturan

Selalu pilih peraturan dalam urutan kronologis:
1. **UU Induk** (versi asli/original)
2. **UU Perubahan Pertama**
3. **UU Perubahan Kedua**
4. ...dan seterusnya

**Sistem akan mengurutkan otomatis berdasarkan tahun**, tapi lebih baik pilih dengan urutan yang benar.

### 2. Nama Konsolidasi

Gunakan naming convention yang jelas:
- ✅ **Good:** "UU ITE Terpadu (2008-2024)"
- ✅ **Good:** "Konsolidasi UU 11/2008 s.d. UU 1/2024"
- ❌ **Bad:** "Gabungan UU"

### 3. Preview Sebelum Save

Selalu klik **Preview** untuk:
- Memastikan peraturan yang dipilih sudah benar
- Melihat hasil sebelum disimpan
- Mengecek apakah mode tampilan sudah sesuai

### 4. Dokumentasi

Isi field **Deskripsi** dengan informasi berguna:
- Tujuan konsolidasi
- Perubahan penting yang terjadi
- Catatan khusus

---

## ⚠️ Troubleshooting

### Pasal Tidak Terdeteksi

**Masalah:** Pasal di UU tidak terdeteksi atau tidak muncul di hasil konsolidasi

**Solusi:**
1. Pastikan format HTML di `isi_peraturan` menggunakan class `pasal-header`
2. Check regex pattern: `<h[23][^>]*pasal-header[^>]*>.*?Pasal\s+(\d+)`
3. Re-extract dari TXT/DOCX jika perlu

### Perubahan Tidak Terdeteksi

**Masalah:** Pasal yang seharusnya "Diubah" malah terdeteksi sebagai "Tidak Berubah"

**Solusi:**
1. Check similarity threshold (default 0.95)
2. Mungkin perubahan terlalu minor (whitespace, formatting)
3. Periksa clean_content (tanpa HTML tags)

### Error saat Generate

**Masalah:** Error ketika klik "Generate & Simpan"

**Solusi:**
1. Check log Odoo: `server/odoo.log`
2. Pastikan semua peraturan memiliki `isi_peraturan` yang valid
3. Pastikan field `tahun` dan `nomor` terisi

---

## 🎓 Contoh Lengkap

### Skenario: Konsolidasi UU ITE

**Input:**
- UU 11/2008 - UU ITE (Original) - 54 Pasal
- UU 19/2016 - Perubahan UU ITE - Mengubah Pasal 5, 26-37, menambah Pasal 45A
- UU 1/2024 - Perubahan Kedua - Mengubah Pasal 27, menghapus Pasal 45

**Proses:**
1. Pilih ketiga UU di tree view
2. Action → Buat Konsolidasi
3. Nama: "UU ITE Terpadu (2008-2024)"
4. Mode: Anotasi
5. Preview → OK → Generate

**Output:**
- **Total Pasal:** 54
- **Ditambah:** 1 (Pasal 45A)
- **Diubah:** 13 (Pasal 5, 26-37, 27)
- **Dihapus:** 1 (Pasal 45)
- **Tidak Berubah:** 40

**Hasil HTML:**
- Setiap pasal diberi badge status
- Pasal 5: Badge kuning "⚠️ Diubah"
- Pasal 45A: Badge biru "✅ Ditambah"
- Pasal 45: Badge merah strikethrough "❌ Dihapus"
- Riwayat perubahan di bawah setiap pasal yang modified

---

## 📚 Referensi Teknis

### Models

- **legal.regulation.consolidation:** Model utama untuk menyimpan hasil konsolidasi
- **consolidation.wizard:** Wizard untuk membuat konsolidasi
- **consolidation.preview.wizard:** Wizard untuk preview

### Views

- `view_consolidation_wizard_form`: Form wizard
- `view_legal_regulation_consolidation_form`: Form hasil konsolidasi
- `view_legal_regulation_consolidation_tree`: Tree view list konsolidasi

### Actions

- `action_consolidation_wizard`: Open wizard dari menu
- `action_create_consolidation_from_selection`: Create dari multi-select
- `action_legal_regulation_consolidation`: List semua konsolidasi

### Security

- `access_legal_regulation_consolidation_user`: Read/Write untuk user
- `access_consolidation_wizard_user`: Full access wizard

---

## 🚀 Roadmap

### Future Enhancements

- [ ] Export ke DOCX/PDF
- [ ] Diff visualization dengan color-coding per kalimat
- [ ] AI-powered summary of changes
- [ ] Timeline view untuk tracking perubahan
- [ ] Notification ketika ada UU Perubahan baru
- [ ] Auto-suggest peraturan yang related
- [ ] Batch consolidation untuk multiple regulations
- [ ] Version control dengan Git-like interface

---

## 📞 Support

Jika mengalami masalah atau memiliki pertanyaan:
1. Check dokumentasi ini
2. Check log Odoo: `server/odoo.log`
3. Hubungi tim developer

---

**Dibuat:** Januari 2026  
**Versi:** 1.0  
**Module:** legal_regulations  
**Author:** Legal Team
