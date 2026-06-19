#!/usr/bin/env python3
"""
Parser untuk struktur Pasal-Ayat-Huruf dengan Penjelasan
Mendukung parsing penjelasan umum pasal dan penjelasan per ayat/huruf
"""

import re
from pathlib import Path

def parse_txt_with_penjelasan(txt):
    """
    Parse TXT menjadi struktur Pasal + Ayat + Huruf + Penjelasan
    
    Returns:
        pasal_blocks: List of dicts dengan struktur pasal, ayat, huruf, dan penjelasan
        toc: Table of contents untuk navigasi
    """
    lines = txt.splitlines()
    pasal_blocks = []
    toc = []
    
    current_pasal = None
    current_pasal_data = None
    current_ayat = None
    in_penjelasan_section = False
    penjelasan_pasal_umum = []
    penjelasan_ayat_map = {}  # Map untuk menyimpan penjelasan per ayat
    
    # Regex patterns
    pasal_pat = re.compile(r'^Pasal\s+(\d+)')
    ayat_pat = re.compile(r'^\((\d+)\)\s*(.*)')
    huruf_pat = re.compile(r'^\s{4}([a-z])\.\s*(.*)')
    penjelasan_section_pat = re.compile(r'^Penjelasan\s*$')
    penjelasan_pasal_pat = re.compile(r'^Pasal\s+(\d+)\s*$')
    penjelasan_ayat_pat = re.compile(r'^Penjelasan\s+\((\d+)\):\s*(.*)')
    penjelasan_huruf_pat = re.compile(r'^Penjelasan\s+\((\d+)\)([a-z]):\s*(.*)')
    bab_pat = re.compile(r'^BAB\s+[IVX]+')
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines
        if not line:
            i += 1
            continue
        
        # Deteksi BAB (skip, bisa ditambahkan ke struktur jika perlu)
        if bab_pat.match(line):
            i += 1
            continue
        
        # Deteksi bagian "Penjelasan"
        if penjelasan_section_pat.match(line):
            in_penjelasan_section = True
            i += 1
            continue
        
        # Jika sedang di bagian Penjelasan
        if in_penjelasan_section:
            # Deteksi "Pasal X" di bagian penjelasan
            pasal_penjelasan_match = penjelasan_pasal_pat.match(line)
            if pasal_penjelasan_match:
                current_pasal_penjelasan = pasal_penjelasan_match.group(1)
                # Kumpulkan penjelasan umum pasal sampai ketemu Penjelasan (n): atau Pasal berikutnya
                i += 1
                temp_penjelasan = []
                while i < len(lines):
                    next_line = lines[i].strip()
                    if not next_line:
                        i += 1
                        continue
                    # Cek apakah ini Penjelasan ayat atau Pasal baru
                    if penjelasan_ayat_pat.match(next_line) or penjelasan_pasal_pat.match(next_line) or pasal_pat.match(next_line):
                        break
                    temp_penjelasan.append(next_line)
                    i += 1
                
                # Simpan penjelasan umum pasal
                if temp_penjelasan:
                    penjelasan_text = ' '.join(temp_penjelasan)
                    if current_pasal_penjelasan not in penjelasan_ayat_map:
                        penjelasan_ayat_map[current_pasal_penjelasan] = {'umum': penjelasan_text, 'ayat': {}}
                    else:
                        penjelasan_ayat_map[current_pasal_penjelasan]['umum'] = penjelasan_text
                continue
            
            # Deteksi penjelasan per ayat: "Penjelasan (3): text"
            penjelasan_ayat_match = penjelasan_ayat_pat.match(line)
            if penjelasan_ayat_match and current_pasal:
                ayat_num = penjelasan_ayat_match.group(1)
                penjelasan_text = penjelasan_ayat_match.group(2).strip()
                
                if current_pasal not in penjelasan_ayat_map:
                    penjelasan_ayat_map[current_pasal] = {'umum': '', 'ayat': {}}
                penjelasan_ayat_map[current_pasal]['ayat'][ayat_num] = penjelasan_text
                i += 1
                continue
            
            # Deteksi penjelasan per huruf: "Penjelasan (3)a: text"
            penjelasan_huruf_match = penjelasan_huruf_pat.match(line)
            if penjelasan_huruf_match and current_pasal:
                ayat_num = penjelasan_huruf_match.group(1)
                huruf = penjelasan_huruf_match.group(2)
                penjelasan_text = penjelasan_huruf_match.group(3).strip()
                
                if current_pasal not in penjelasan_ayat_map:
                    penjelasan_ayat_map[current_pasal] = {'umum': '', 'ayat': {}}
                if ayat_num not in penjelasan_ayat_map[current_pasal]['ayat']:
                    penjelasan_ayat_map[current_pasal]['ayat'][ayat_num] = {}
                if not isinstance(penjelasan_ayat_map[current_pasal]['ayat'][ayat_num], dict):
                    penjelasan_ayat_map[current_pasal]['ayat'][ayat_num] = {'_text': penjelasan_ayat_map[current_pasal]['ayat'][ayat_num]}
                
                penjelasan_ayat_map[current_pasal]['ayat'][ayat_num][huruf] = penjelasan_text
                i += 1
                continue
        
        # Deteksi Pasal baru (di bagian isi peraturan)
        pasal_match = pasal_pat.match(line)
        if pasal_match and not in_penjelasan_section:
            # Simpan pasal sebelumnya
            if current_pasal_data:
                pasal_blocks.append(current_pasal_data)
                toc.append({
                    'pasal': current_pasal,
                    'ayats': [a['nomor'] for a in current_pasal_data['ayats']]
                })
            
            # Mulai pasal baru
            current_pasal = pasal_match.group(1)
            current_pasal_data = {
                'nomor': current_pasal,
                'ayats': [],
                'penjelasan_umum': ''
            }
            current_ayat = None
            i += 1
            continue
        
        # Deteksi ayat
        ayat_match = ayat_pat.match(line)
        if ayat_match and current_pasal_data and not in_penjelasan_section:
            ayat_num = ayat_match.group(1)
            ayat_text = ayat_match.group(2).strip()
            
            current_ayat = {
                'nomor': ayat_num,
                'isi': [ayat_text] if ayat_text else [],
                'hurufs': [],
                'penjelasan': ''
            }
            current_pasal_data['ayats'].append(current_ayat)
            i += 1
            continue
        
        # Deteksi huruf (a, b, c)
        huruf_match = huruf_pat.match(line)
        if huruf_match and current_ayat and not in_penjelasan_section:
            huruf = huruf_match.group(1)
            huruf_text = huruf_match.group(2).strip()
            current_ayat['hurufs'].append({
                'huruf': huruf,
                'isi': huruf_text,
                'penjelasan': ''
            })
            i += 1
            continue
        
        # Jika tidak cocok pattern apa pun, tambahkan ke isi ayat terakhir (continuation)
        if current_ayat and not in_penjelasan_section and line:
            current_ayat['isi'].append(line)
        
        i += 1
    
    # Simpan pasal terakhir
    if current_pasal_data:
        pasal_blocks.append(current_pasal_data)
        toc.append({
            'pasal': current_pasal,
            'ayats': [a['nomor'] for a in current_pasal_data['ayats']]
        })
    
    # Gabungkan penjelasan ke pasal blocks
    for pasal in pasal_blocks:
        pasal_num = pasal['nomor']
        if pasal_num in penjelasan_ayat_map:
            # Penjelasan umum pasal
            pasal['penjelasan_umum'] = penjelasan_ayat_map[pasal_num].get('umum', '')
            
            # Penjelasan per ayat
            for ayat in pasal['ayats']:
                ayat_num = ayat['nomor']
                if ayat_num in penjelasan_ayat_map[pasal_num].get('ayat', {}):
                    penjelasan_data = penjelasan_ayat_map[pasal_num]['ayat'][ayat_num]
                    
                    # Jika penjelasan_data adalah string (penjelasan ayat)
                    if isinstance(penjelasan_data, str):
                        ayat['penjelasan'] = penjelasan_data
                    # Jika penjelasan_data adalah dict (ada penjelasan huruf)
                    elif isinstance(penjelasan_data, dict):
                        ayat['penjelasan'] = penjelasan_data.get('_text', '')
                        
                        # Penjelasan per huruf
                        for huruf_item in ayat['hurufs']:
                            huruf = huruf_item['huruf']
                            if huruf in penjelasan_data:
                                huruf_item['penjelasan'] = penjelasan_data[huruf]
    
    return pasal_blocks, toc


def generate_html_with_penjelasan(pasal_blocks, toc):
    """
    Generate HTML dengan accordion + TOC + Penjelasan terintegrasi
    """
    html_parts = []
    
    # CSS untuk styling
    css = """
    <style>
        .toc {
            position: sticky;
            top: 20px;
            max-height: 80vh;
            overflow-y: auto;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
            border: 1px solid #dee2e6;
        }
        .toc h5 {
            margin-bottom: 15px;
            color: #495057;
            font-weight: 600;
        }
        .toc ul {
            list-style: none;
            padding-left: 0;
        }
        .toc ul ul {
            padding-left: 20px;
            margin-top: 5px;
        }
        .toc a {
            color: #007bff;
            text-decoration: none;
            display: block;
            padding: 5px 0;
        }
        .toc a:hover {
            color: #0056b3;
            text-decoration: underline;
        }
        .pasal-card {
            margin-bottom: 20px;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            overflow: hidden;
        }
        .pasal-header {
            background: #007bff;
            color: white;
            padding: 15px;
            cursor: pointer;
            font-weight: 600;
            font-size: 1.1em;
        }
        .pasal-header:hover {
            background: #0056b3;
        }
        .pasal-content {
            padding: 20px;
            background: white;
        }
        .ayat {
            margin-bottom: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-left: 4px solid #007bff;
            border-radius: 4px;
        }
        .ayat strong {
            color: #007bff;
            font-size: 1.1em;
        }
        .ayat ul {
            margin-top: 10px;
            padding-left: 20px;
        }
        .ayat li {
            margin-bottom: 10px;
        }
        .penjelasan {
            margin-top: 10px;
            padding: 10px;
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            border-radius: 4px;
            font-style: italic;
        }
        .penjelasan strong {
            color: #856404;
            font-style: normal;
        }
        .penjelasan-umum {
            margin-bottom: 20px;
            padding: 15px;
            background: #d1ecf1;
            border-left: 4px solid #17a2b8;
            border-radius: 4px;
        }
        .penjelasan-umum strong {
            color: #0c5460;
        }
    </style>
    """
    
    html_parts.append(css)
    
    # Container dengan grid layout
    html_parts.append('<div class="container-fluid"><div class="row">')
    
    # Table of Contents (Sidebar)
    html_parts.append('<div class="col-md-3">')
    html_parts.append('<nav class="toc"><h5>📋 Daftar Isi</h5><ul>')
    for entry in toc:
        html_parts.append(f'<li><a href="#pasal{entry["pasal"]}">Pasal {entry["pasal"]}</a>')
        if entry['ayats']:
            html_parts.append('<ul>')
            for ayat in entry['ayats']:
                html_parts.append(f'<li><a href="#pasal{entry["pasal"]}-ayat{ayat}">Ayat ({ayat})</a></li>')
            html_parts.append('</ul>')
        html_parts.append('</li>')
    html_parts.append('</ul></nav>')
    html_parts.append('</div>')
    
    # Content Area
    html_parts.append('<div class="col-md-9">')
    
    # Accordion untuk setiap Pasal
    for pasal in pasal_blocks:
        pasal_id = f'pasal{pasal["nomor"]}'
        
        html_parts.append(f'<div class="pasal-card" id="{pasal_id}">')
        html_parts.append(f'<div class="pasal-header" onclick="togglePasal(\'{pasal_id}-content\')">')
        html_parts.append(f'📜 Pasal {pasal["nomor"]}')
        html_parts.append('</div>')
        
        html_parts.append(f'<div class="pasal-content" id="{pasal_id}-content" style="display:block;">')
        
        # Penjelasan Umum Pasal (jika ada)
        if pasal.get('penjelasan_umum'):
            html_parts.append('<div class="penjelasan-umum">')
            html_parts.append('<strong>💡 Penjelasan Pasal:</strong><br>')
            html_parts.append(pasal['penjelasan_umum'])
            html_parts.append('</div>')
        
        # Ayat-ayat
        for ayat in pasal['ayats']:
            ayat_id = f'{pasal_id}-ayat{ayat["nomor"]}'
            ayat_text = ' '.join(ayat['isi']).strip()
            
            html_parts.append(f'<div class="ayat" id="{ayat_id}">')
            html_parts.append(f'<strong>({ayat["nomor"]})</strong> {ayat_text}')
            
            # Sub-huruf (jika ada)
            if ayat['hurufs']:
                html_parts.append('<ul>')
                for huruf in ayat['hurufs']:
                    html_parts.append(f'<li><strong>{huruf["huruf"]}.</strong> {huruf["isi"]}')
                    
                    # Penjelasan huruf (jika ada)
                    if huruf.get('penjelasan'):
                        html_parts.append('<div class="penjelasan">')
                        html_parts.append(f'<strong>💡 Penjelasan huruf {huruf["huruf"]}:</strong> {huruf["penjelasan"]}')
                        html_parts.append('</div>')
                    
                    html_parts.append('</li>')
                html_parts.append('</ul>')
            
            # Penjelasan Ayat (jika ada)
            if ayat.get('penjelasan'):
                html_parts.append('<div class="penjelasan">')
                html_parts.append(f'<strong>💡 Penjelasan ayat ({ayat["nomor"]}):</strong> {ayat["penjelasan"]}')
                html_parts.append('</div>')
            
            html_parts.append('</div>')
        
        html_parts.append('</div>')
        html_parts.append('</div>')
    
    html_parts.append('</div>')
    html_parts.append('</div></div>')
    
    # JavaScript untuk toggle accordion
    js = """
    <script>
    function togglePasal(id) {
        var content = document.getElementById(id);
        if (content.style.display === 'none' || content.style.display === '') {
            content.style.display = 'block';
        } else {
            content.style.display = 'none';
        }
    }
    </script>
    """
    
    html_parts.append(js)
    
    return '\n'.join(html_parts)


if __name__ == '__main__':
    # Test dengan file contoh
    txt_path = Path(__file__).parent / 'contoh_dengan_penjelasan.txt'
    
    if not txt_path.exists():
        print(f"❌ File tidak ditemukan: {txt_path}")
        exit(1)
    
    print("📖 Membaca file TXT...")
    txt = txt_path.read_text(encoding='utf-8')
    
    print("🔍 Parsing struktur Pasal-Ayat-Huruf dengan Penjelasan...")
    pasal_blocks, toc = parse_txt_with_penjelasan(txt)
    
    print(f"✅ Berhasil parsing {len(pasal_blocks)} pasal\n")
    
    # Debug output
    for pasal in pasal_blocks:
        print(f"Pasal {pasal['nomor']}:")
        if pasal['penjelasan_umum']:
            print(f"  └─ Penjelasan Umum: {pasal['penjelasan_umum'][:50]}...")
        for ayat in pasal['ayats']:
            print(f"  └─ Ayat ({ayat['nomor']}): {' '.join(ayat['isi'])[:50]}...")
            if ayat['penjelasan']:
                print(f"     └─ Penjelasan: {ayat['penjelasan'][:50]}...")
            for huruf in ayat['hurufs']:
                print(f"     └─ {huruf['huruf']}. {huruf['isi'][:40]}...")
                if huruf['penjelasan']:
                    print(f"        └─ Penjelasan: {huruf['penjelasan'][:40]}...")
        print()
    
    print("🎨 Generating HTML dengan accordion dan TOC...")
    html = generate_html_with_penjelasan(pasal_blocks, toc)
    
    # Simpan ke file HTML untuk preview
    output_path = Path(__file__).parent / 'output_with_penjelasan.html'
    output_path.write_text(html, encoding='utf-8')
    
    print(f"✅ HTML berhasil di-generate!")
    print(f"📄 Output: {output_path}")
    print(f"🌐 Buka file HTML di browser untuk melihat hasilnya")
