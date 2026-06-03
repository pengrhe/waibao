"""一次性修复：Python 3.8 不支持运行时 list[X]/dict[K,V] 表达式。

策略：
- 在指定目录下扫描 .py 文件
- 把 `list[` → `List[`，`dict[` → `Dict[`，`tuple[` → `Tuple[`，`set[` → `Set[`
- 同时确保 from typing 已 import 对应的大写名
- 写回时保留 UTF-8 编码

幂等：跑多次结果一致。
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "app"

REPLS = {
    "List": re.compile(r"\blist\["),
    "Dict": re.compile(r"\bdict\["),
    "Tuple": re.compile(r"\btuple\["),
    "Set": re.compile(r"\bset\["),
}


def fix_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    original = text
    used: set[str] = set()
    for name, pat in REPLS.items():
        if pat.search(text):
            text = pat.sub(f"{name}[", text)
            used.add(name)

    if not used:
        return False

    # 确保 from typing import ... 包含 used names
    lines = text.splitlines(keepends=True)
    typing_idx = None
    for i, ln in enumerate(lines):
        if re.match(r"^from typing import .*", ln):
            typing_idx = i
            break

    if typing_idx is not None:
        line = lines[typing_idx].rstrip("\n").rstrip("\r")
        m = re.match(r"^from typing import (.+)$", line)
        if m:
            existing = {p.strip() for p in m.group(1).split(",") if p.strip()}
            merged = sorted(existing | used)
            new_line = "from typing import " + ", ".join(merged) + "\n"
            lines[typing_idx] = new_line
    else:
        # 在 from __future__ 之后插入
        insert_at = 0
        for i, ln in enumerate(lines):
            if ln.startswith("from __future__"):
                insert_at = i + 1
                break
        lines.insert(insert_at, "from typing import " + ", ".join(sorted(used)) + "\n")

    new_text = "".join(lines)
    if new_text == original:
        return False
    path.write_bytes(new_text.encode("utf-8"))
    return True


def main() -> None:
    changed: list[str] = []
    for p in ROOT.rglob("*.py"):
        if fix_file(p):
            changed.append(str(p.relative_to(ROOT.parent)))
    if changed:
        print("fixed:")
        for c in changed:
            print(" -", c)
    else:
        print("nothing to fix")


if __name__ == "__main__":
    main()
