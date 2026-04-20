# -*- coding: utf-8 -*-
"""
数据库迁移脚本：为文体项目扩展添加新字段和新表
"""
import sys
import os
import sqlite3

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import BASE_DIR

DB_PATH = BASE_DIR / "safety_check.db"


def get_existing_columns(cursor, table_name):
    cursor.execute(f"PRAGMA table_info({table_name})")
    return {row[1] for row in cursor.fetchall()}


def get_existing_tables(cursor):
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    return {row[0] for row in cursor.fetchall()}


def migrate():
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    tables = get_existing_tables(cursor)

    if "projects" in tables:
        cols = get_existing_columns(cursor, "projects")
        new_cols = {
            "project_type": "VARCHAR(20) DEFAULT 'longhua'",
            "report_code": "VARCHAR(100)",
            "area": "VARCHAR(50)",
            "floor_info": "VARCHAR(50)",
            "inspectors": "VARCHAR(200)",
        }
        for col_name, col_def in new_cols.items():
            if col_name not in cols:
                cursor.execute(f"ALTER TABLE projects ADD COLUMN {col_name} {col_def}")
                print(f"  [projects] 新增列: {col_name}")

    if "hazards" in tables:
        cols = get_existing_columns(cursor, "hazards")
        if "suggestion" not in cols:
            cursor.execute("ALTER TABLE hazards ADD COLUMN suggestion TEXT")
            print("  [hazards] 新增列: suggestion")

    if "hazard_templates" not in tables:
        cursor.execute("""
            CREATE TABLE hazard_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category VARCHAR(50) NOT NULL,
                sub_category VARCHAR(100),
                seq INTEGER,
                description TEXT NOT NULL,
                suggestion TEXT,
                reference_standard TEXT,
                standard_clause TEXT
            )
        """)
        print("  [hazard_templates] 新建表")

    if "detection_records" not in tables:
        cursor.execute("""
            CREATE TABLE detection_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL REFERENCES projects(id),
                detection_type VARCHAR(30) NOT NULL,
                seq INTEGER DEFAULT 1,
                location VARCHAR(200),
                photo_path VARCHAR(500),
                code VARCHAR(50),
                temperature VARCHAR(20),
                resistance_value VARCHAR(20),
                result VARCHAR(50),
                remark TEXT
            )
        """)
        print("  [detection_records] 新建表")

    if "checklist_results" not in tables:
        cursor.execute("""
            CREATE TABLE checklist_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL REFERENCES projects(id),
                table_index INTEGER NOT NULL,
                item_seq INTEGER NOT NULL,
                result VARCHAR(50)
            )
        """)
        print("  [checklist_results] 新建表")

    if "inspectors" not in tables:
        cursor.execute("""
            CREATE TABLE inspectors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(50) NOT NULL,
                street_group VARCHAR(10) NOT NULL
            )
        """)
        print("  [inspectors] 新建表")

    cursor.execute("SELECT COUNT(*) FROM inspectors")
    if cursor.fetchone()[0] == 0:
        seed = [
            ("方兵", "A"),
            ("苏势喆", "A"),
            ("王宗跃", "B"),
            ("王金洋", "B"),
        ]
        cursor.executemany(
            "INSERT INTO inspectors (name, street_group) VALUES (?, ?)", seed
        )
        print("  [inspectors] 预置 4 条种子数据")

    conn.commit()
    conn.close()
    print("迁移完成!")


if __name__ == "__main__":
    print(f"数据库路径: {DB_PATH}")
    migrate()
