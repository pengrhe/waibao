# -*- coding: utf-8 -*-
from services.template_loader import parse_hazard_templates

path = r"d:\wp\waibao\gongcheng\文体\隐患依据(2).xlsx"
items = parse_hazard_templates(path)

cats = {}
for t in items:
    c = t["category"]
    if c not in cats:
        cats[c] = 0
    cats[c] += 1

print(f"Total templates: {len(items)}")
for c, n in cats.items():
    print(f"  {c}: {n}")
