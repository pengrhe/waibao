# -*- coding: utf-8 -*-
import sqlite3
conn = sqlite3.connect("d:/wp/waibao/gongcheng/backend/safety_check.db")
c = conn.cursor()
c.execute("SELECT id FROM projects WHERE project_type='wenti'")
ids = [r[0] for r in c.fetchall()]
print(f"Wenti projects to delete: {len(ids)}")
if ids:
    ph = ",".join("?" * len(ids))
    for t in ["checklist_results", "detection_records", "scene_photos", "hazards", "generated_docs"]:
        c.execute(f"DELETE FROM {t} WHERE project_id IN ({ph})", ids)
        print(f"  {t}: {c.rowcount}")
    c.execute(f"DELETE FROM projects WHERE id IN ({ph})", ids)
    print(f"  projects: {c.rowcount}")
    conn.commit()
print("Done")
c.execute("SELECT project_type, COUNT(*) FROM projects GROUP BY project_type")
print("Remaining:", c.fetchall())
conn.close()
