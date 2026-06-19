import re
from pathlib import Path

def parse_txt_structure(txt):
    lines = txt.splitlines()
    pasal_blocks = []
    toc = []
    current_pasal = None
    current_ayat = None
    ayat_list = []
    ayat_counter = 0
    pasal_counter = 0
    html_blocks = []

    # Regex patterns
    pasal_pat = re.compile(r'^Pasal\s+(\d+)')
    ayat_pat = re.compile(r'^\((\d+)\)')
    huruf_pat = re.compile(r'^\s{2,}([a-z])\.\s*(.*)')

    for idx, line in enumerate(lines):
        pasal_match = pasal_pat.match(line)
        ayat_match = ayat_pat.match(line)
        huruf_match = huruf_pat.match(line)

        if pasal_match:
            # Save previous pasal block
            if current_pasal:
                pasal_blocks.append({
                    'nomor': current_pasal,
                    'ayats': ayat_list
                })
                toc.append({'pasal': current_pasal, 'ayats': [a['nomor'] for a in ayat_list]})
            # Start new pasal
            pasal_counter += 1
            current_pasal = pasal_match.group(1)
            ayat_list = []
            ayat_counter = 0
            current_ayat = None
        elif ayat_match:
            ayat_counter += 1
            current_ayat = ayat_match.group(1)
            ayat_list.append({'nomor': current_ayat, 'isi': [], 'hurufs': []})
        elif huruf_match and ayat_list:
            ayat_list[-1]['hurufs'].append({'huruf': huruf_match.group(1), 'isi': huruf_match.group(2)})
        elif current_ayat and ayat_list:
            # Add line to current ayat
            ayat_list[-1]['isi'].append(line.strip())

    # Save last pasal
    if current_pasal:
        pasal_blocks.append({
            'nomor': current_pasal,
            'ayats': ayat_list
        })
        toc.append({'pasal': current_pasal, 'ayats': [a['nomor'] for a in ayat_list]})

    return pasal_blocks, toc

def generate_html(pasal_blocks, toc):
    # Table of Contents
    toc_html = ['<nav class="toc"><h5>Daftar Isi</h5><ul>']
    for entry in toc:
        toc_html.append(f'<li><a href="#pasal{entry["pasal"]}">Pasal {entry["pasal"]}</a>')
        if entry['ayats']:
            toc_html.append('<ul>')
            for ayat in entry['ayats']:
                toc_html.append(f'<li><a href="#pasal{entry["pasal"]}-ayat{ayat}">Ayat ({ayat})</a></li>')
            toc_html.append('</ul>')
        toc_html.append('</li>')
    toc_html.append('</ul></nav>')

    # Accordion HTML
    accordion_html = ['<div class="accordion" id="accordionPasal">']
    for pasal in pasal_blocks:
        pasal_id = f'pasal{pasal["nomor"]}'
        accordion_html.append(f'<div class="card"><div class="card-header" id="heading{pasal_id}">')
        accordion_html.append(f'<h5><a href="#" data-toggle="collapse" data-target="#{pasal_id}" aria-expanded="false" aria-controls="{pasal_id}">Pasal {pasal["nomor"]}</a></h5></div>')
        accordion_html.append(f'<div id="{pasal_id}" class="collapse" aria-labelledby="heading{pasal_id}" data-parent="#accordionPasal">')
        for ayat in pasal['ayats']:
            ayat_id = f'{pasal_id}-ayat{ayat["nomor"]}'
            ayat_isi = ' '.join(ayat['isi']).strip()
            accordion_html.append(f'<div class="ayat"><strong id="{ayat_id}">( {ayat["nomor"]} )</strong> {ayat_isi}')
            if ayat['hurufs']:
                accordion_html.append('<ul>')
                for huruf in ayat['hurufs']:
                    accordion_html.append(f'<li><strong>{huruf["huruf"]}.</strong> {huruf["isi"]}</li>')
                accordion_html.append('</ul>')
            accordion_html.append('</div>')
        accordion_html.append('</div></div>')
    accordion_html.append('</div>')

    return '\n'.join(toc_html + accordion_html)

if __name__ == '__main__':
    txt_path = Path(__file__).parent / 'contoh_peraturan.txt'
    txt = txt_path.read_text(encoding='utf-8')
    pasal_blocks, toc = parse_txt_structure(txt)
    html = generate_html(pasal_blocks, toc)
    print(html)
