# -*- coding: utf-8 -*-
"""清理恢复的隐患模板中字段错位的记录"""
import sqlite3

conn = sqlite3.connect("d:/wp/waibao/gongcheng/backend/safety_check.db")
c = conn.cursor()

VALID_CATEGORIES = ["消防类", "电气类", "体育场所", "档案类", "建筑消防设施专项检查"]

c.execute("SELECT COUNT(*) FROM hazard_templates")
total_before = c.fetchone()[0]

c.execute("SELECT category, COUNT(*) FROM hazard_templates GROUP BY category")
cats = c.fetchall()
print("Categories before cleanup:")
for cat, cnt in cats:
    valid = cat in VALID_CATEGORIES
    print(f"  {'[OK]' if valid else '[BAD]'} {cat}: {cnt}")

# Delete records with invalid categories
c.execute("DELETE FROM hazard_templates WHERE category NOT IN (?,?,?,?,?)", VALID_CATEGORIES)
deleted = c.rowcount

# Remove duplicates (keep lowest id for each unique description+category)
c.execute("""DELETE FROM hazard_templates WHERE id NOT IN (
    SELECT MIN(id) FROM hazard_templates GROUP BY category, description
)""")
deduped = c.rowcount

conn.commit()

c.execute("SELECT COUNT(*) FROM hazard_templates")
total_after = c.fetchone()[0]

print(f"\nDeleted {deleted} invalid records, {deduped} duplicates")
print(f"Templates: {total_before} -> {total_after}")

print("\nCategories after cleanup:")
c.execute("SELECT category, COUNT(*) FROM hazard_templates GROUP BY category")
for cat, cnt in c.fetchall():
    print(f"  {cat}: {cnt}")

conn.close()
