#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyze Penjelasan section to count real explanations
"""

import re

file_path = r'C:\Users\Ario\Downloads\UU Nomor 11 Tahun 2008.txt'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Get Penjelasan section
penjelasan_section = text[text.find('PENJELASAN ATAS'):]

lines = penjelasan_section.split('\n')

current_pasal = None
current_ayat = None
ayat_with_explanation = []
huruf_with_explanation = []

for i, line in enumerate(lines):
    stripped = line.strip()
    
    # Detect Pasal
    if re.match(r'^Pasal\s+(\d+)\s*$', stripped):
        current_pasal = re.match(r'^Pasal\s+(\d+)\s*$', stripped).group(1)
        current_ayat = None
    
    # Detect Ayat
    if re.match(r'^Ayat\s+\((\d+)\)\s*$', stripped):
        current_ayat = re.match(r'^Ayat\s+\((\d+)\)\s*$', stripped).group(1)
        # Check next line
        if i+1 < len(lines):
            next_line = lines[i+1].strip()
            if next_line and next_line != 'Cukup jelas.' and not re.match(r'^(Huruf|Ayat|Pasal)', next_line):
                ayat_with_explanation.append(f'Pasal {current_pasal} Ayat ({current_ayat})')
    
    # Detect Huruf
    if re.match(r'^Huruf\s+([a-z])\s*$', stripped) and current_ayat:
        huruf = re.match(r'^Huruf\s+([a-z])\s*$', stripped).group(1)
        # Check next line
        if i+1 < len(lines):
            next_line = lines[i+1].strip()
            if next_line and next_line != 'Cukup jelas.' and not re.match(r'^(Huruf|Ayat|Pasal)', next_line):
                huruf_with_explanation.append(f'Pasal {current_pasal} Ayat ({current_ayat}) Huruf {huruf}')

print("="*80)
print("ANALYSIS OF PENJELASAN SECTION")
print("="*80)

print(f'\nAyat with real explanation (not "Cukup jelas"): {len(ayat_with_explanation)}')
print("-"*80)
for item in ayat_with_explanation[:15]:
    print(f'  - {item}')
if len(ayat_with_explanation) > 15:
    print(f'  ... and {len(ayat_with_explanation)-15} more')

print(f'\n\nHuruf with real explanation (not "Cukup jelas"): {len(huruf_with_explanation)}')
print("-"*80)
for item in huruf_with_explanation:
    print(f'  - {item}')

print("\n" + "="*80)
print(f"TOTAL EXPECTED: {len(ayat_with_explanation)} Ayat + {len(huruf_with_explanation)} Huruf = {len(ayat_with_explanation) + len(huruf_with_explanation)}")
print("="*80)
