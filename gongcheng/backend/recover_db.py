# -*- coding: utf-8 -*-
"""从 SQLite freelist 页面中恢复已删除的龙华项目数据"""
import sqlite3
import struct
import os
import re

DB_PATH = os.path.join(os.path.dirname(__file__), "safety_check.db.bak")
RECOVER_DB = os.path.join(os.path.dirname(__file__), "safety_check_recovered.db")

def scan_raw_bytes():
    with open(DB_PATH, "rb") as f:
        data = f.read()

    print(f"DB file size: {len(data)} bytes")
    print(f"'longhua' occurrences: {data.count(b'longhua')}")

    streets = ["观湖", "观澜", "福城", "民治", "大浪"]
    for s in streets:
        c = data.count(s.encode("utf-8"))
        if c:
            print(f"  Street '{s}': {c} occurrences")

def try_undrop():
    """Use .clone + manual page scan to recover deleted rows."""
    import shutil
    shutil.copy2(DB_PATH, RECOVER_DB)

    conn = sqlite3.connect(RECOVER_DB)
    c = conn.cursor()

    c.execute("PRAGMA freelist_count")
    free = c.fetchone()[0]
    print(f"\nFreelist pages: {free}")

    c.execute("SELECT COUNT(*) FROM projects")
    print(f"Current projects: {c.fetchone()[0]}")
    c.execute("SELECT COUNT(*) FROM hazards")
    print(f"Current hazards: {c.fetchone()[0]}")
    c.execute("SELECT COUNT(*) FROM hazard_templates")
    print(f"Current templates: {c.fetchone()[0]}")

    conn.close()

    # Read raw pages and try to extract text records
    with open(DB_PATH, "rb") as f:
        raw = f.read()

    page_size = 4096
    total_pages = len(raw) // page_size

    # Extract all freelist page numbers
    # Page 1 header: offset 32-35 = first freelist trunk page
    first_trunk = struct.unpack(">I", raw[32:36])[0]
    print(f"First freelist trunk page: {first_trunk}")

    freelist_pages = set()
    trunk = first_trunk
    while trunk:
        offset = (trunk - 1) * page_size
        next_trunk = struct.unpack(">I", raw[offset:offset+4])[0]
        leaf_count = struct.unpack(">I", raw[offset+4:offset+8])[0]
        for i in range(leaf_count):
            pg = struct.unpack(">I", raw[offset+8+i*4:offset+12+i*4])[0]
            freelist_pages.add(pg)
        freelist_pages.add(trunk)
        trunk = next_trunk

    print(f"Freelist pages found: {len(freelist_pages)}")

    # Scan freelist pages for project-like data
    found_projects = []
    found_hazards = []
    found_templates = []

    for pg in sorted(freelist_pages):
        offset = (pg - 1) * page_size
        page_data = raw[offset:offset+page_size]

        # Try to find text patterns in the page
        text = page_data.decode("utf-8", errors="replace")

        # Look for longhua project records
        if "longhua" in text:
            # Try to extract structured data
            # Projects have patterns like: name, street, address, contact, phone
            parts = []
            idx = 0
            while True:
                pos = text.find("longhua", idx)
                if pos < 0:
                    break
                # Extract surrounding context
                start = max(0, pos - 500)
                end = min(len(text), pos + 200)
                context = text[start:end]
                parts.append((pg, context))
                idx = pos + 7

            for pg_num, ctx in parts:
                found_projects.append((pg_num, ctx))

    print(f"\nFound {len(found_projects)} potential project fragments in freelist pages")

    # Write fragments to a text file for inspection
    output_file = os.path.join(os.path.dirname(__file__), "recovered_fragments.txt")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("=== RECOVERED PROJECT FRAGMENTS ===\n\n")
        for pg, ctx in found_projects:
            f.write(f"--- Page {pg} ---\n")
            # Clean up non-printable chars
            clean = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '|', ctx)
            f.write(clean + "\n\n")

    print(f"Fragments written to: {output_file}")

    # Also try to directly recover using SQLite's own mechanism
    # by rebuilding the btree
    print("\nAttempting direct record recovery from raw pages...")
    recover_records_from_pages(raw, page_size, freelist_pages)


def recover_records_from_pages(raw, page_size, freelist_pages):
    """Parse SQLite B-tree leaf pages to extract cell records."""
    recovered_projects = []
    recovered_hazards = []
    recovered_templates = []

    for pg in sorted(freelist_pages):
        offset = (pg - 1) * page_size
        page_data = raw[offset:offset + page_size]

        # Check page type: 0x0D = leaf table, 0x0A = leaf index
        page_type = page_data[0]
        if page_type != 0x0D:
            continue

        # Parse leaf table b-tree page
        # Offset 3-4: number of cells
        try:
            num_cells = struct.unpack(">H", page_data[3:5])[0]
        except:
            continue

        if num_cells == 0 or num_cells > 500:
            continue

        # Cell pointer array starts at offset 8
        for i in range(num_cells):
            try:
                cell_offset = struct.unpack(">H", page_data[8 + i * 2:10 + i * 2])[0]
                if cell_offset >= page_size:
                    continue

                # Parse cell: payload_length (varint), rowid (varint), payload
                pos = cell_offset
                payload_len, bytes_read = read_varint(page_data, pos)
                pos += bytes_read
                rowid, bytes_read = read_varint(page_data, pos)
                pos += bytes_read

                if payload_len <= 0 or payload_len > page_size:
                    continue

                payload = page_data[pos:pos + min(payload_len, page_size - pos)]

                # Parse record format
                fields = parse_record(payload)
                if not fields:
                    continue

                # Check if this looks like a project record (has 'longhua' in fields)
                field_strs = [str(f) for f in fields]
                joined = " ".join(field_strs)

                if "longhua" in joined:
                    recovered_projects.append((rowid, fields))
                elif any(k in joined for k in ["消防", "电气", "体育", "档案"]):
                    # Could be hazard template
                    if len(fields) >= 5:
                        recovered_templates.append((rowid, fields))

            except Exception:
                continue

    print(f"Recovered project records: {len(recovered_projects)}")
    print(f"Recovered template records: {len(recovered_templates)}")

    # Insert recovered data back
    if recovered_projects or recovered_templates:
        dest_db = os.path.join(os.path.dirname(__file__), "safety_check.db")
        conn = sqlite3.connect(dest_db)
        c = conn.cursor()

        proj_inserted = 0
        for rowid, fields in recovered_projects:
            try:
                # Project table columns:
                # id, name, street, address, contact, phone, category,
                # build_unit, construct_unit, supervise_unit, check_date,
                # status, excel_file, created_at, project_type, report_code, area, floor_info, inspectors
                if len(fields) < 15:
                    continue
                c.execute("""INSERT OR IGNORE INTO projects 
                    (id, name, street, address, contact, phone, category,
                     build_unit, construct_unit, supervise_unit, check_date,
                     status, excel_file, created_at, project_type, report_code, area, floor_info, inspectors)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    [rowid] + list(fields[1:19]) if len(fields) >= 19 else [rowid] + list(fields[1:]) + [None] * (18 - len(fields) + 1))
                proj_inserted += c.rowcount
            except Exception as e:
                pass

        tpl_inserted = 0
        for rowid, fields in recovered_templates:
            try:
                if len(fields) < 5:
                    continue
                c.execute("""INSERT OR IGNORE INTO hazard_templates
                    (id, category, sub_category, seq, description, suggestion, reference_standard, standard_clause)
                    VALUES (?,?,?,?,?,?,?,?)""",
                    [rowid] + list(fields[1:8]) if len(fields) >= 8 else [rowid] + list(fields[1:]) + [None] * (7 - len(fields) + 1))
                tpl_inserted += c.rowcount
            except Exception as e:
                pass

        conn.commit()
        print(f"\nInserted back: {proj_inserted} projects, {tpl_inserted} templates")

        c.execute("SELECT COUNT(*) FROM projects")
        print(f"Total projects now: {c.fetchone()[0]}")
        c.execute("SELECT COUNT(*) FROM hazard_templates")
        print(f"Total templates now: {c.fetchone()[0]}")
        conn.close()


def read_varint(data, offset):
    """Read a SQLite varint."""
    result = 0
    for i in range(9):
        if offset + i >= len(data):
            return result, i + 1
        byte = data[offset + i]
        if i < 8:
            result = (result << 7) | (byte & 0x7F)
            if byte < 0x80:
                return result, i + 1
        else:
            result = (result << 8) | byte
            return result, 9
    return result, 9


def parse_record(payload):
    """Parse a SQLite record format payload into field values."""
    if not payload:
        return None

    try:
        header_size, hdr_bytes = read_varint(payload, 0)
        if header_size <= 0 or header_size > len(payload):
            return None

        # Read serial types
        serial_types = []
        pos = hdr_bytes
        while pos < header_size:
            st, nb = read_varint(payload, pos)
            serial_types.append(st)
            pos += nb

        # Read values
        fields = []
        data_pos = header_size
        for st in serial_types:
            if st == 0:
                fields.append(None)
            elif st == 1:
                if data_pos + 1 <= len(payload):
                    fields.append(struct.unpack(">b", payload[data_pos:data_pos+1])[0])
                    data_pos += 1
                else:
                    fields.append(None)
            elif st == 2:
                if data_pos + 2 <= len(payload):
                    fields.append(struct.unpack(">h", payload[data_pos:data_pos+2])[0])
                    data_pos += 2
                else:
                    fields.append(None)
            elif st == 3:
                if data_pos + 3 <= len(payload):
                    val = struct.unpack(">i", b'\x00' + payload[data_pos:data_pos+3])[0]
                    fields.append(val)
                    data_pos += 3
                else:
                    fields.append(None)
            elif st == 4:
                if data_pos + 4 <= len(payload):
                    fields.append(struct.unpack(">i", payload[data_pos:data_pos+4])[0])
                    data_pos += 4
                else:
                    fields.append(None)
            elif st == 5:
                if data_pos + 6 <= len(payload):
                    val = struct.unpack(">q", b'\x00\x00' + payload[data_pos:data_pos+6])[0]
                    fields.append(val)
                    data_pos += 6
                else:
                    fields.append(None)
            elif st == 6:
                if data_pos + 8 <= len(payload):
                    fields.append(struct.unpack(">q", payload[data_pos:data_pos+8])[0])
                    data_pos += 8
                else:
                    fields.append(None)
            elif st == 7:
                if data_pos + 8 <= len(payload):
                    fields.append(struct.unpack(">d", payload[data_pos:data_pos+8])[0])
                    data_pos += 8
                else:
                    fields.append(None)
            elif st == 8:
                fields.append(0)
            elif st == 9:
                fields.append(1)
            elif st >= 12 and st % 2 == 0:
                # BLOB
                length = (st - 12) // 2
                if data_pos + length <= len(payload):
                    fields.append(payload[data_pos:data_pos+length])
                    data_pos += length
                else:
                    fields.append(None)
            elif st >= 13 and st % 2 == 1:
                # TEXT
                length = (st - 13) // 2
                if data_pos + length <= len(payload):
                    try:
                        fields.append(payload[data_pos:data_pos+length].decode("utf-8"))
                    except:
                        fields.append(payload[data_pos:data_pos+length].decode("utf-8", errors="replace"))
                    data_pos += length
                else:
                    fields.append(None)
            else:
                fields.append(None)

        return fields
    except Exception:
        return None


if __name__ == "__main__":
    scan_raw_bytes()
    try_undrop()
