# Button "Re-extract PDF" - Panduan Penggunaan

## Fungsi
Button "Re-extract PDF" digunakan untuk **mengekstrak ulang isi PDF** dengan metode terbaru yang **menjaga layout asli** (layout-preserving extraction).

## Kapan Menggunakan?
1. **PDF lama yang isinya berantakan** - jika isi peraturan dari PDF lama tidak rapi
2. **Setelah update sistem** - untuk mendapatkan hasil ekstraksi terbaru
3. **Masalah spasi/formatting** - jika teks terpisah atau tidak sejajar
4. **Testing** - untuk membandingkan hasil ekstraksi lama vs baru

## Cara Menggunakan

### Langkah 1: Buka Form Peraturan
1. Login ke Odoo
2. Buka menu **Peraturan Hukum** → **Peraturan**
3. Pilih peraturan yang **sudah memiliki file PDF**

### Langkah 2: Klik Button "Re-extract PDF"
1. Di bagian header form, Anda akan melihat button:
   - 🔵 **Download PDF** (biru)
   - 🟠 **Re-extract PDF** (kuning/warning)
   
2. Klik button **Re-extract PDF** 🔄

### Langkah 3: Tunggu Proses
- Sistem akan mengekstrak ulang PDF dengan metode terbaru
- Notifikasi sukses akan muncul: "Isi peraturan berhasil di-ekstrak ulang dengan metode terbaru"

### Langkah 4: Cek Hasilnya
1. Scroll ke bawah form
2. Lihat field **Isi Peraturan**
3. Cek apakah formatting sudah lebih rapi:
   - ✅ Indentasi list (a, b, c) sejajar
   - ✅ Teks wrapped rapi
   - ✅ Spacing antar baris konsisten

## Perbedaan Metode Lama vs Baru

### Metode Lama (auto extraction)
- Menggunakan PyPDF2 atau pdfminer.six
- Tidak mempertahankan indentasi asli
- Hasil: teks plain tanpa layout

### Metode Baru (layout-preserving)
- Menggunakan PyMuPDF blocks
- Mendeteksi posisi horizontal teks (x0 coordinate)
- Mempertahankan indentasi berdasarkan posisi:
  - x0 < 100: Teks kiri (main content)
  - x0 < 200: Indent level 1 (list items)
  - x0 > 200: Indent level 2 (sub-items)
  - x0 ≈ 210: Teks centered (judul)

## Troubleshooting

### Button tidak muncul?
- Pastikan peraturan **memiliki file PDF** (file_pdf tidak kosong)
- Refresh browser (Ctrl+F5)
- Upgrade module: `odoo-bin -u legal_regulations`

### Error saat klik button?
- Cek log Odoo: `/c/Program Files/Odoo/server/odoo.log`
- Pastikan PyMuPDF terinstall: `pip list | grep PyMuPDF`
- File PDF mungkin corrupt/tidak valid

### Hasil masih tidak rapi?
1. Cek PDF asli - apakah text-based atau scan?
2. Untuk PDF scan, sistem menggunakan OCR (hasil mungkin kurang sempurna)
3. Pertimbangkan upload ulang dalam format DOCX untuk hasil lebih baik

## Technical Details

### Method yang Dipanggil
```python
action_reextract_pdf() 
  → _extract_text_from_pdf(pdf_data)
    → PDFExtractor.extract_text_with_layout()
      → PyMuPDF page.get_text("blocks")
```

### Log Location
File: `/c/Program Files/Odoo/server/odoo.log`
```
Search for:
- "Re-extracting PDF for regulation ID"
- "Successfully re-extracted PDF"
- "Extracting text with layout preservation"
- "Layout extraction complete"
```

## Changelog

**2025-11-03**
- ✅ Added `action_reextract_pdf()` method to legal.regulation model
- ✅ Added "Re-extract PDF" button in form view header
- ✅ Integrated with layout-preserving extraction method
- ✅ Added success notification display
- ✅ Updated CSS for better text alignment (table display)
