#!/usr/bin/env python3
# Quick script to fix indentation issue

file_path = r'c:\Program Files\Odoo\custom_addons\legal_regulations\models\legal_regulation.py'

# Read file
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find and fix the problematic section (around line 543-577)
# The section with extra indentation should be removed
new_lines = []
skip_until_line = None

for i, line in enumerate(lines, 1):
    # Skip duplicate code from line 544 to 577
    if i == 544 and line.strip().startswith('# Determine indentation level'):
        # Start skipping
        skip_until_line = 577
        print(f"Skipping from line {i}")
        continue
    
    if skip_until_line and i <= skip_until_line:
        print(f"Skipping line {i}: {line[:50].strip()}...")
        continue
    
        if skip_until_line and i == skip_until_line + 1:
                print(f"Resuming from line {i}")
                skip_until_line = None
    
    new_lines.append(line)

# Write back
with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print(f"\nFixed! Removed duplicate code. New file has {len(new_lines)} lines (was {len(lines)} lines)")
