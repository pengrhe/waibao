# -*- coding: utf-8 -*-
import sqlite3
conn = sqlite3.connect("d:/wp/waibao/gongcheng/backend/safety_check.db")
c = conn.cursor()
c.execute("SELECT id, name, report_code FROM projects WHERE project_type='wenti' LIMIT 10")
for r in c.fetchall():
    print(f"ID={r[0]}, name={r[1][:30]}, report_code='{r[2]}'")
conn.close()
