"""一次性测试脚本：用更新后的格式生成微信简报并发送。"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import OUTPUT_DIR, PUBLIC_BASE_URL
from brief_formatter import build_wechat_brief_text

brief_path = OUTPUT_DIR / "brief_2026-04-18.json"
data = json.loads(brief_path.read_text(encoding="utf-8"))

report_date = data["report_date"]
html_url = data.get("html_url", "")
key_summary = data.get("key_summary", "")
articles = data.get("articles", [])

text = build_wechat_brief_text(
    articles,
    report_date,
    html_url,
    PUBLIC_BASE_URL,
    key_summary_body=key_summary,
)

print("=" * 50)
print("将发送的微信消息内容：")
print("=" * 50)
print(text)
print("=" * 50)
print(f"字符数：{len(text)}")
print()

confirm = input("确认发送？(y/n): ").strip().lower()
if confirm == "y":
    from shanxiang_wechat import WeChat
    from config import WECHAT_SEND_TO
    wechat = WeChat()
    wechat.send(WECHAT_SEND_TO, text)
    print(f"已发送到 '{WECHAT_SEND_TO}'")
else:
    print("已取消发送")
