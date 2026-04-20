# -*- coding: utf-8 -*-
"""对比恢复前后的龙华项目，找出缺失的15个"""
import sqlite3

# 从备份文件中提取原始删除前的龙华项目ID列表
# 备份是在删除后做的，但 freelist 页面中扫描到的是恢复的107个
# 我们需要看恢复的107个项目的ID范围来推断缺失的

conn = sqlite3.connect("d:/wp/waibao/gongcheng/backend/safety_check.db")
c = conn.cursor()

c.execute("SELECT id, name, created_at FROM projects WHERE project_type='longhua' ORDER BY id")
recovered = c.fetchall()

print(f"Recovered longhua projects: {len(recovered)}")
print(f"ID range: {recovered[0][0]} ~ {recovered[-1][0]}")

# 找出ID范围内缺失的ID
all_ids = set(r[0] for r in recovered)
min_id, max_id = min(all_ids), max(all_ids)

# 但项目ID不一定是连续的（中间有wenti项目）
# 让我们按时间排序看看
print("\nFirst 5 (earliest recovered):")
c.execute("SELECT id, name, created_at FROM projects WHERE project_type='longhua' ORDER BY id ASC LIMIT 5")
for r in c.fetchall():
    print(f"  ID={r[0]}, created={r[2]}, name={r[1]}")

print("\nLast 5 (latest recovered):")
c.execute("SELECT id, name, created_at FROM projects WHERE project_type='longhua' ORDER BY id DESC LIMIT 5")
for r in c.fetchall():
    print(f"  ID={r[0]}, created={r[2]}, name={r[1]}")

# 看看122个的完整ID列表应该是什么
# 从recovered_fragments.txt中也许能找到线索
# 但更好的方式是看ID分布
print(f"\nAll recovered IDs (sorted):")
sorted_ids = sorted(all_ids)
print(sorted_ids)

# 找出连续ID中的间隔
gaps = []
for i in range(len(sorted_ids) - 1):
    diff = sorted_ids[i+1] - sorted_ids[i]
    if diff > 1:
        for missing_id in range(sorted_ids[i] + 1, sorted_ids[i+1]):
            gaps.append(missing_id)

print(f"\nMissing IDs in range (gaps between recovered): {gaps}")
print(f"Total gaps: {len(gaps)}")

conn.close()
