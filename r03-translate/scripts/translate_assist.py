#!/usr/bin/env python3
"""文献翻译辅助脚本：分段、术语候选、译文核验。

用法:
    python3 translate_assist.py segments source.md [out.json]   # 段落切分（带段号/页码标记）
    python3 translate_assist.py terms    source.md [out.json]   # 术语候选（缩写/重复短语）
    python3 translate_assist.py verify   source.md target.md    # 核验数字/单位/编号/否定/段数

纯标准库。输出 JSON；核验只提示不强制，供译者复核。
"""
import json
import re
import sys
from pathlib import Path


def read_text(p):
    return Path(p).read_text(encoding="utf-8")


def segments(text):
    """按空行/页码标记切段，逐段编号。支持 '\\f'(换页) 与 '--- 第N页 ---' 标记。"""
    text = text.replace("\f", "\n--- PAGEBREAK ---\n")
    raw = re.split(r"\n\s*\n", text)
    paras, page = [], 1
    for r in raw:
        s = r.strip()
        if not s:
            continue
        m = re.search(r"第\s*(\d+)\s*页|PAGEBREAK", s)
        if "PAGEBREAK" in s:
            page += 1
            continue
        if m and re.match(r"^\s*[-\u2014]*\s*第", s):
            page = int(m.group(1))
            continue
        paras.append({"para_id": f"P{len(paras)+1}", "page": page, "text": s})
    return paras


def term_candidates(text):
    """候选术语：全大写缩写、首字母大写短语、高频名词短语。"""
    cand = {}
    # 缩写
    for m in re.finditer(r"\b[A-Z]{2,6}\b", text):
        w = m.group(0)
        if w in ("THE", "AND", "FOR", "OUR", "A", "I", "II", "III", "IV", "V"):
            continue
        cand[w] = cand.get(w, 0) + 1
    # 首字母大写 2-3 词短语
    for m in re.finditer(r"\b([A-Z][a-z]+(?:[- ][A-Z][a-z]+){1,2})\b", text):
        cand[m.group(1)] = cand.get(m.group(1), 0) + 1
    out = [{"term": t, "occurrences": c} for t, c in sorted(cand.items(), key=lambda x: -x[1])]
    return out[:80]


def _data_numbers(s):
    """正文数据数字（排除 [n] 文献引用）。"""
    s2 = re.sub(r"\[\s*\d+(?:[,\-]\d+)*\s*\]", " ", s)
    return set(re.findall(r"\d+(?:[.,]\d+)?", s2))


def _units(s):
    return set(re.findall(r"\b(?:nm|μm|mm|cm|m|kg|g|mg|s|ms|min|h|mol|M|K|°C|Hz|kHz|MHz|GHz|eV|Pa|bar|%)\b", s, re.I))


def _cite_numbers(s):
    out = set()
    for m in re.findall(r"\[\s*(\d+(?:[,\-]\d+)*)\s*\]", s):
        out.update(re.findall(r"\d+", m))
    out.update(re.findall(r"(?:Fig\.?|Figure|Table|Eq\.?|Equation|图|表|式|公式)\s*(\d+)", s, re.I))
    return out


def _negation_count(s):
    en = len(re.findall(r"\b(?:not|never|no|none|without|unable|unlike)\b", s, re.I))
    zh = len(re.findall(r"(?:不|非|未|无|没)", s))
    return en + zh


def verify(src, tgt):
    src_dn, tgt_dn = _data_numbers(src), _data_numbers(tgt)
    src_cn, tgt_cn = _cite_numbers(src), _cite_numbers(tgt)
    src_neg, tgt_neg = _negation_count(src), _negation_count(tgt)
    report = {
        "data_numbers_missing_in_target": sorted(src_dn - tgt_dn),
        "citation_numbers_missing_in_target": sorted(src_cn - tgt_cn),
        "units_missing_in_target": sorted(_units(src) - _units(tgt)),
        "negation_count_source": src_neg,
        "negation_count_target": tgt_neg,
        "negation_dropped": tgt_neg < src_neg,
    }
    report["ok"] = (not report["data_numbers_missing_in_target"]
                    and not report["citation_numbers_missing_in_target"]
                    and not report["units_missing_in_target"]
                    and not report["negation_dropped"])
    return report


def main():
    if len(sys.argv) < 3:
        print("usage: translate_assist.py segments|terms|verify ...", file=sys.stderr)
        sys.exit(2)
    cmd = sys.argv[1]
    if cmd == "verify":
        if len(sys.argv) < 4:
            print("usage: translate_assist.py verify source.md target.md [out.json]", file=sys.stderr)
            sys.exit(2)
        src, tgt = sys.argv[2], sys.argv[3]
        out = sys.argv[4] if len(sys.argv) > 4 else None
        res = {"ok": False, "checks": verify(read_text(src), read_text(tgt))}
        res["ok"] = res["checks"]["ok"]
        print(json.dumps(res, ensure_ascii=False, indent=2))
        if out:
            Path(out).write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
        return
    src = sys.argv[2]
    out = sys.argv[3] if len(sys.argv) > 3 else None
    res = {}
    if cmd == "segments":
        res = {"ok": True, "paragraphs": segments(read_text(src))}
    elif cmd == "terms":
        res = {"ok": True, "term_candidates": term_candidates(read_text(src))}
    else:
        print("unknown command", file=sys.stderr)
        sys.exit(2)
    print(json.dumps(res, ensure_ascii=False, indent=2))
    if out:
        Path(out).write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
