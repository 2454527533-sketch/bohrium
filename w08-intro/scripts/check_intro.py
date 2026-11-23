#!/usr/bin/env python3
"""引言一致性检查：孤引用、未引用文献、贡献条目缺少证据定位。

用法:
    python3 check_intro.py intro.md [result.json]

检查项（对 Markdown 引言稿）:
  1. 正文中的 [n] 是否都有对应的参考文献条目（孤引用）
  2. 参考文献条目是否都被正文引用（未引用条目）
  3. 「贡献」小节中每条贡献是否带证据定位（见 §/图/表/结果 或 [n]）

纯标准库。输出 JSON 报告；发现的问题供 Agent 复核，不强制判定。
"""
import json
import re
import sys
from pathlib import Path


def extract_citations(text):
    nums = set()
    for m in re.finditer(r"\[(\d+(?:\s*[,，\-–]\s*\d+)*)\]", text):
        for n in re.findall(r"\d+", m.group(1)):
            nums.add(int(n))
    return nums


def extract_refs(text):
    # 参考文献段落在含"参考文献/References"的标题之后
    m = re.search(r"\n\s*#+\s*(参考文献|References).*", text)
    if not m:
        return {}
    body = text[m.start():]
    refs = {}
    for ln in body.splitlines():
        mm = re.match(r"\s*\[(\d+)\]\s*(.+)", ln)
        if mm:
            refs[int(mm.group(1))] = mm.group(2).strip()
    return refs


def check_contributions(text):
    # 找含"贡献"的小节，逐条判断是否有证据定位
    sec = None
    lines = text.splitlines()
    for i, ln in enumerate(lines):
        if re.search(r"#+\s*(贡献|Contributions?)", ln):
            sec = i
            break
    if sec is None:
        return []
    missing = []
    for ln in lines[sec:]:
        if re.match(r"\s*#", ln) and not re.search(r"贡献", ln):
            break
        s = ln.strip()
        if s.startswith("- ") or s.startswith("* ") or re.match(r"^\d+\.\s", s):
            has_ev = bool(re.search(r"(\[[0-9,\-]+\]|见\s*[§章节图表格结果]\s*\S+|Fig\.|Table|§)", s))
            if not has_ev:
                missing.append(s)
    return missing


def main():
    if len(sys.argv) < 2:
        print("usage: check_intro.py intro.md [result.json]", file=sys.stderr)
        sys.exit(2)
    text = Path(sys.argv[1]).read_text(encoding="utf-8")
    cited = extract_citations(text)
    refs = extract_refs(text)
    orphans = sorted(c for c in cited if c not in refs)
    uncited = sorted(r for r in refs if r not in cited)
    missing_ev = check_contributions(text)
    report = {
        "ok": not orphans and not uncited and not missing_ev,
        "citations_used": sorted(cited),
        "references_present": sorted(refs),
        "orphan_citations": orphans,
        "uncited_references": uncited,
        "contributions_missing_evidence": missing_ev,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if len(sys.argv) > 2:
        Path(sys.argv[2]).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
