# -*- coding: utf-8 -*-
from services.template_loader import parse_hazard_templates

path = r"d:\wp\waibao\gongcheng\文体\隐患依据(2).xlsx"
items = parse_hazard_templates(path)

# Show first 5 items from 消防 category
print("=== 消防设施安全隐患 (first 3) ===")
fire = [t for t in items if "消防" in t["category"]]
for t in fire[:3]:
    print(f"  seq: {t['seq']}")
    print(f"  description: {t['description'][:60]}")
    print(f"  suggestion: {t['suggestion'][:60]}")
    print(f"  reference_standard: {t['reference_standard'][:60]}")
    print(f"  standard_clause: {t['standard_clause'][:40]}")
    print()

# Show first 3 from 电气
print("=== 电气设备安全隐患 (first 3) ===")
elec = [t for t in items if "电气" in t["category"]]
for t in elec[:3]:
    print(f"  sub_category: {t['sub_category']}")
    print(f"  seq: {t['seq']}")
    print(f"  description: {t['description'][:60]}")
    print(f"  suggestion: {t['suggestion'][:60]}")
    print(f"  reference_standard: {t['reference_standard'][:60]}")
    print(f"  standard_clause: {t['standard_clause'][:40]}")
    print()
