#!/usr/bin/env python3
"""文献笔记辅助脚本：章节骨架提取、论文卡片/知识点校验。

用法:
    python3 notes_builder.py outline source.md [out.json]      # 提取章节层级骨架
    python3 notes_builder.py check   notes.json [report.json]  # 校验笔记来源锚点/卡片字段/知识点去重冲突

纯标准库。检查为提示，供复核，不强制判定。
"""
import json
import re
import sys
from pathlib import Path

PAPER_CARD_REQ = ["research_question", "data", "method_conditions", "main_findings", "limitations"]
KP_REQ = ["term", "definition", "source_loc"]


def outline(text):
    heads = []
    for ln in text.splitlines():
        s = ln.strip()
        m = re.match(r"^(#{1,4})\s+(.*)", s)
        if m:
            heads.append({"level": len(m.group(1)), "title": m.group(2).strip()})
        elif re.match(r"^\d+(\.\d+)*\.?\s+\S", s) and len(s) < 120:
            heads.append({"level": s.count(".") + 1 if "." in s.split()[0] else 1, "title": s})
    return heads


def check(data):
    issues = {"card_missing_fields": [], "kps_missing_fields": [], "kps_missing_anchor": [],
              "kps_duplicates": [], "kps_conflicts": []}
    card = data.get("paper_card", {})
    for k in PAPER_CARD_REQ:
        v = card.get(k)
        if not v or (isinstance(v, (list, dict)) and len(v) == 0):
            issues["card_missing_fields"].append(k)
    kps = data.get("knowledge_points", [])
    seen_terms = {}
    for i, kp in enumerate(kps):
        for k in KP_REQ:
            if not str(kp.get(k, "") or "").strip():
                issues["kps_missing_fields"].append({"row": i + 1, "field": k})
        loc = kp.get("source_loc", "")
        quote = kp.get("quote", "")
        if not loc and not quote:
            issues["kps_missing_anchor"].append(i + 1)
        term = (kp.get("term") or "").strip().lower()
        if term:
            if term in seen_terms:
                issues["kps_duplicates"].append({"term": kp.get("term"), "rows": [seen_terms[term], i + 1]})
            else:
                seen_terms[term] = i + 1
    # 冲突：同 term 不同 definition 视为需人工确认
    by_term = {}
    for i, kp in enumerate(kps):
        t = (kp.get("term") or "").strip().lower()
        d = (kp.get("definition") or "").strip()
        if t and d:
            if t in by_term and by_term[t][0] != d:
                issues["kps_conflicts"].append({"term": kp.get("term"), "rows": [by_term[t][1], i + 1]})
            else:
                by_term[t] = (d, i + 1)
    issues["ok"] = not any(issues.values())
    return issues


def main():
    if len(sys.argv) < 3:
        print("usage: notes_builder.py outline source.md [out.json] | check notes.json [report.json]", file=sys.stderr)
        sys.exit(2)
    cmd, src = sys.argv[1], sys.argv[2]
    out = sys.argv[3] if len(sys.argv) > 3 else None
    if cmd == "outline":
        res = {"ok": True, "headings": outline(Path(src).read_text(encoding="utf-8"))}
    elif cmd == "check":
        data = json.load(open(src, encoding="utf-8"))
        res = {"ok": False, "issues": check(data)}
        res["ok"] = res["issues"]["ok"]
    else:
        print("unknown command", file=sys.stderr)
        sys.exit(2)
    print(json.dumps(res, ensure_ascii=False, indent=2))
    if out:
        Path(out).write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
