# -*- coding: utf-8 -*-
import sqlite3

conn = sqlite3.connect("d:/wp/waibao/gongcheng/backend/safety_check.db")
c = conn.cursor()

print("=== Longhua Projects (first 10) ===")
c.execute("SELECT id, name, street, address, contact, project_type FROM projects WHERE project_type='longhua' LIMIT 10")
for r in c.fetchall():
    print(r)

print(f"\n=== Longhua project count ===")
c.execute("SELECT COUNT(*) FROM projects WHERE project_type='longhua'")
print(c.fetchone()[0])

print(f"\n=== Hazards for longhua ===")
c.execute("SELECT COUNT(*) FROM hazards WHERE project_id IN (SELECT id FROM projects WHERE project_type='longhua')")
print(c.fetchone()[0])

print(f"\n=== Hazard Templates (first 10) ===")
c.execute("SELECT id, category, sub_category, seq, description, suggestion FROM hazard_templates LIMIT 10")
for r in c.fetchall():
    print(r)

print(f"\n=== Template categories ===")
c.execute("SELECT category, COUNT(*) FROM hazard_templates GROUP BY category ORDER BY COUNT(*) DESC LIMIT 10")
for r in c.fetchall():
    print(r)

conn.close()
