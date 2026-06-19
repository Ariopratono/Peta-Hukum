#!/usr/bin/env python3
"""
Advanced Structure Parser with Penjelasan Support
Parses legal document TXT with Pasal, Ayat, Huruf, and Penjelasan sections
"""
import re
from pathlib import Path

class LegalDocumentParser:
    def __init__(self):
        self.pasal_pattern = re.compile(r'^Pasal\s+(\d+)$')
        self.ayat_pattern = re.compile(r'^\((\d+)\)\s*(.*)')
        self.huruf_pattern = re.compile(r'^\s{4}([a-z])\.\s*(.*)')
        self.angka_pattern = re.compile(r'^\s{4}(\d+)\.\s*(.*)')
        self.penjelasan_pasal_pattern = re.compile(r'^Penjelasan Pasal\s+(\d+)$')
        self.penjelasan_ayat_pattern = re.compile(r'^Penjelasan Ayat\s+\((\d+)\)$')
        self.penjelasan_huruf_pattern = re.compile(r'^Huruf\s+([a-z])$')
        
    def parse(self, txt_content):
        """Parse TXT content and return structured data"""
        lines = txt_content.strip().split('\n')
        
        pasals = []
        current_pasal = None
        current_ayat = None
        current_huruf = None
        penjelasan_mode = False
        penjelasan_target = None  # {'type': 'pasal/ayat/huruf', 'pasal': n, 'ayat': n, 'huruf': x}
        penjelasan_buffer = []
        
        i = 0
        while i < len(lines):
            line = lines[i].rstrip()
            
            # Check for "Penjelasan" section start
            if line.strip() == "Penjelasan":
                penjelasan_mode = True
                # Infer context from last pasal if no "Penjelasan Pasal X" follows
                if current_pasal:
                    penjelasan_target = {'type': 'pasal', 'pasal': current_pasal['nomor']}
                i += 1
                continue
            
            # If in penjelasan mode, parse penjelasan structure
            if penjelasan_mode:
                penjelasan_pasal_match = self.penjelasan_pasal_pattern.match(line.strip())
                penjelasan_ayat_match = self.penjelasan_ayat_pattern.match(line.strip())
                penjelasan_huruf_match = self.penjelasan_huruf_pattern.match(line.strip())
                
                if penjelasan_pasal_match:
                    # Save previous penjelasan
                    self._save_penjelasan(pasals, penjelasan_target, penjelasan_buffer)
                    penjelasan_buffer = []
                    pasal_num = penjelasan_pasal_match.group(1)
                    penjelasan_target = {'type': 'pasal', 'pasal': pasal_num}
                    i += 1
                    continue
                    
                elif penjelasan_ayat_match:
                    # Save previous penjelasan
                    self._save_penjelasan(pasals, penjelasan_target, penjelasan_buffer)
                    penjelasan_buffer = []
                    ayat_num = penjelasan_ayat_match.group(1)
                    # Use current pasal context
                    if penjelasan_target:
                        penjelasan_target = {
                            'type': 'ayat',
                            'pasal': penjelasan_target.get('pasal', current_pasal['nomor'] if current_pasal else None),
                            'ayat': ayat_num
                        }
                    i += 1
                    continue
                    
                elif penjelasan_huruf_match:
                    # Save previous penjelasan
                    self._save_penjelasan(pasals, penjelasan_target, penjelasan_buffer)
                    penjelasan_buffer = []
                    huruf = penjelasan_huruf_match.group(1)
                    if penjelasan_target and penjelasan_target['type'] == 'ayat':
                        penjelasan_target = {
                            'type': 'huruf',
                            'pasal': penjelasan_target['pasal'],
                            'ayat': penjelasan_target['ayat'],
                            'huruf': huruf
                        }
                    i += 1
                    continue
                
                # Check if new Pasal starts (exit penjelasan mode) or new BAB
                elif self.pasal_pattern.match(line) or line.startswith('BAB '):
                    # Save last penjelasan
                    self._save_penjelasan(pasals, penjelasan_target, penjelasan_buffer)
                    penjelasan_mode = False
                    penjelasan_target = None
                    penjelasan_buffer = []
                    # Continue to process this Pasal/BAB line below
                
                else:
                    # Accumulate penjelasan content
                    stripped = line.strip()
                    if stripped and stripped != "Penjelasan":
                        penjelasan_buffer.append(stripped)
                    i += 1
                    continue
            
            # Parse Pasal
            pasal_match = self.pasal_pattern.match(line)
            if pasal_match:
                # Save previous pasal
                if current_pasal:
                    pasals.append(current_pasal)
                
                pasal_num = pasal_match.group(1)
                current_pasal = {
                    'nomor': pasal_num,
                    'ayats': [],
                    'penjelasan': None
                }
                current_ayat = None
                current_huruf = None
                i += 1
                continue
            
            # Parse Ayat
            ayat_match = self.ayat_pattern.match(line)
            if ayat_match and current_pasal:
                ayat_num = ayat_match.group(1)
                ayat_content = ayat_match.group(2).strip()
                current_ayat = {
                    'nomor': ayat_num,
                    'isi': [ayat_content] if ayat_content else [],
                    'hurufs': [],
                    'penjelasan': None
                }
                current_pasal['ayats'].append(current_ayat)
                current_huruf = None
                i += 1
                continue
            
            # Parse Huruf (sub-item)
            huruf_match = self.huruf_pattern.match(line)
            if huruf_match and current_ayat:
                huruf = huruf_match.group(1)
                huruf_content = huruf_match.group(2).strip()
                current_huruf = {
                    'huruf': huruf,
                    'isi': huruf_content,
                    'penjelasan': None
                }
                current_ayat['hurufs'].append(current_huruf)
                i += 1
                continue
            
            # Parse Angka (numeric sub-item in Pasal 1)
            angka_match = self.angka_pattern.match(line)
            if angka_match and current_ayat:
                angka = angka_match.group(1)
                angka_content = angka_match.group(2).strip()
                # Treat as huruf but with number
                current_huruf = {
                    'huruf': angka,
                    'isi': angka_content,
                    'penjelasan': None
                }
                current_ayat['hurufs'].append(current_huruf)
                i += 1
                continue
            
            # Accumulate content to current ayat
            if line.strip() and current_ayat and not penjelasan_mode:
                current_ayat['isi'].append(line.strip())
            
            i += 1
        
        # Save last pasal
        if current_pasal:
            pasals.append(current_pasal)
        
        # Save last penjelasan
        if penjelasan_mode and penjelasan_target:
            self._save_penjelasan(pasals, penjelasan_target, penjelasan_buffer)
        
        return pasals
    
    def _save_penjelasan(self, pasals, target, buffer):
        """Save penjelasan to the appropriate pasal/ayat/huruf"""
        print(f"DEBUG _save_penjelasan called: target={target}, buffer_len={len(buffer) if buffer else 0}")
        if not target or not buffer:
            print(f"DEBUG: Skipping save - target or buffer is empty")
            return
        
        penjelasan_text = ' '.join(buffer)
        print(f"DEBUG: Penjelasan text length: {len(penjelasan_text)}")
        
        # Find target pasal
        for pasal in pasals:
            if pasal['nomor'] == target['pasal']:
                if target['type'] == 'pasal':
                    pasal['penjelasan'] = penjelasan_text
                    print(f"DEBUG: Saved penjelasan to Pasal {target['pasal']}")
                    return
                
                elif target['type'] == 'ayat':
                    for ayat in pasal['ayats']:
                        if ayat['nomor'] == target['ayat']:
                            ayat['penjelasan'] = penjelasan_text
                            print(f"DEBUG: Saved penjelasan to Pasal {target['pasal']} Ayat ({target['ayat']})")
                            return
                
                elif target['type'] == 'huruf':
                    for ayat in pasal['ayats']:
                        if ayat['nomor'] == target['ayat']:
                            for huruf in ayat['hurufs']:
                                if huruf['huruf'] == target['huruf']:
                                    huruf['penjelasan'] = penjelasan_text
                                    print(f"DEBUG: Saved penjelasan to Pasal {target['pasal']} Ayat ({target['ayat']}) Huruf {target['huruf']}")
                                    return
    
    def generate_toc(self, pasals):
        """Generate Table of Contents HTML"""
        toc_html = ['<div class="toc-container" style="position: sticky; top: 20px;">']
        toc_html.append('<h5 class="mb-3"><i class="fa fa-list"></i> Daftar Isi</h5>')
        toc_html.append('<ul class="list-unstyled">')
        
        for pasal in pasals:
            toc_html.append(f'<li class="mb-2">')
            toc_html.append(f'<a href="#pasal{pasal["nomor"]}" class="text-decoration-none">')
            toc_html.append(f'<i class="fa fa-angle-right"></i> Pasal {pasal["nomor"]}')
            toc_html.append('</a>')
            
            if pasal['ayats']:
                toc_html.append('<ul class="list-unstyled ml-3 mt-1">')
                for ayat in pasal['ayats']:
                    toc_html.append(f'<li><a href="#pasal{pasal["nomor"]}-ayat{ayat["nomor"]}" class="text-muted text-decoration-none small">Ayat ({ayat["nomor"]})</a></li>')
                toc_html.append('</ul>')
            
            toc_html.append('</li>')
        
        toc_html.append('</ul>')
        toc_html.append('</div>')
        
        return '\n'.join(toc_html)
    
    def generate_accordion_html(self, pasals):
        """Generate accordion HTML with penjelasan integrated"""
        html = ['<div class="accordion" id="accordionPasal">']
        
        for idx, pasal in enumerate(pasals):
            pasal_id = f'pasal{pasal["nomor"]}'
            collapse_show = 'show' if idx == 0 else ''
            
            html.append(f'<div class="card mb-2" id="{pasal_id}">')
            html.append(f'<div class="card-header bg-primary text-white" id="heading{pasal_id}">')
            html.append(f'<h5 class="mb-0">')
            html.append(f'<button class="btn btn-link text-white text-decoration-none" type="button" data-toggle="collapse" data-target="#collapse{pasal_id}" aria-expanded="true" aria-controls="collapse{pasal_id}">')
            html.append(f'<i class="fa fa-chevron-down"></i> Pasal {pasal["nomor"]}')
            html.append('</button>')
            html.append('</h5>')
            html.append('</div>')
            
            html.append(f'<div id="collapse{pasal_id}" class="collapse {collapse_show}" aria-labelledby="heading{pasal_id}" data-parent="#accordionPasal">')
            html.append('<div class="card-body">')
            
            # Pasal penjelasan (if any)
            if pasal.get('penjelasan'):
                html.append('<div class="alert alert-info mb-3">')
                html.append('<strong><i class="fa fa-info-circle"></i> Penjelasan Pasal:</strong><br>')
                html.append(f'<em>{pasal["penjelasan"]}</em>')
                html.append('</div>')
            
            # Ayats
            for ayat in pasal['ayats']:
                ayat_id = f'pasal{pasal["nomor"]}-ayat{ayat["nomor"]}'
                html.append(f'<div class="ayat mb-3" id="{ayat_id}">')
                html.append(f'<strong class="text-primary">({ayat["nomor"]})</strong> ')
                html.append(' '.join(ayat['isi']))
                
                # Huruf/sub-items
                if ayat['hurufs']:
                    html.append('<ul class="mt-2">')
                    for huruf in ayat['hurufs']:
                        html.append(f'<li><strong>{huruf["huruf"]}.</strong> {huruf["isi"]}')
                        
                        # Huruf penjelasan
                        if huruf.get('penjelasan'):
                            html.append('<div class="alert alert-warning mt-2 small">')
                            html.append('<strong><i class="fa fa-lightbulb-o"></i> Penjelasan:</strong><br>')
                            html.append(f'<em>{huruf["penjelasan"]}</em>')
                            html.append('</div>')
                        
                        html.append('</li>')
                    html.append('</ul>')
                
                # Ayat penjelasan
                if ayat.get('penjelasan'):
                    html.append('<div class="alert alert-warning mt-2">')
                    html.append('<strong><i class="fa fa-lightbulb-o"></i> Penjelasan:</strong><br>')
                    html.append(f'<em>{ayat["penjelasan"]}</em>')
                    html.append('</div>')
                
                html.append('</div>')
            
            html.append('</div>')
            html.append('</div>')
            html.append('</div>')
        
        html.append('</div>')
        
        return '\n'.join(html)
    
    def generate_complete_html(self, pasals):
        """Generate complete HTML with TOC + Accordion"""
        html = ['<div class="container-fluid">']
        html.append('<div class="row">')
        
        # TOC Column (3 columns)
        html.append('<div class="col-md-3">')
        html.append(self.generate_toc(pasals))
        html.append('</div>')
        
        # Content Column (9 columns)
        html.append('<div class="col-md-9">')
        html.append(self.generate_accordion_html(pasals))
        html.append('</div>')
        
        html.append('</div>')
        html.append('</div>')
        
        return '\n'.join(html)


def main():
    # Read sample TXT file
    txt_path = Path(__file__).parent / 'contoh_uu_ite.txt'
    txt_content = txt_path.read_text(encoding='utf-8')
    
    # Parse structure
    parser = LegalDocumentParser()
    pasals = parser.parse(txt_content)
    
    # Generate HTML
    html_output = parser.generate_complete_html(pasals)
    
    # Save to file
    output_path = Path(__file__).parent / 'output_structured.html'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('<!DOCTYPE html>\n')
        f.write('<html>\n<head>\n')
        f.write('<meta charset="utf-8">\n')
        f.write('<title>Struktur Peraturan dengan Penjelasan</title>\n')
        f.write('<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">\n')
        f.write('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">\n')
        f.write('<style>\n')
        f.write('.toc-container { background: #f8f9fa; padding: 20px; border-radius: 8px; }\n')
        f.write('.ayat { line-height: 1.8; }\n')
        f.write('</style>\n')
        f.write('</head>\n<body>\n')
        f.write('<div class="container-fluid mt-4">\n')
        f.write('<h2 class="mb-4">UU ITE - Struktur dengan Penjelasan</h2>\n')
        f.write(html_output)
        f.write('</div>\n')
        f.write('<script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>\n')
        f.write('<script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.bundle.min.js"></script>\n')
        f.write('</body>\n</html>')
    
    print(f"✅ HTML generated successfully!")
    print(f"📄 Output file: {output_path}")
    print(f"📊 Total Pasal parsed: {len(pasals)}")
    
    # Print summary
    for pasal in pasals:
        penjelasan_count = 0
        if pasal.get('penjelasan'):
            penjelasan_count += 1
        for ayat in pasal['ayats']:
            if ayat.get('penjelasan'):
                penjelasan_count += 1
            for huruf in ayat['hurufs']:
                if huruf.get('penjelasan'):
                    penjelasan_count += 1
        
        print(f"  - Pasal {pasal['nomor']}: {len(pasal['ayats'])} ayat, {penjelasan_count} penjelasan")


if __name__ == '__main__':
    main()
