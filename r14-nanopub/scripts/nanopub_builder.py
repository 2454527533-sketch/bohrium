#!/usr/bin/env python3
"""Nanopublication 构建与校验。

用法:
    python3 nanopub_builder.py validate nanopubs.json [report.json]   # 结构完整性
    python3 nanopub_builder.py quality  nanopubs.json [report.json]   # 质量检查

纯标准库。检查为提示，供复核，不强制判定。
"""
import json
import re
import sys
from pathlib import Path

ASSERTION_REQ = ["subject", "predicate", "object"]
EVIDENCE_REQ = ["quote", "location"]
PROVENANCE_REQ = ["paper"]


def _nps(data):
    return data.get("nanopublications", data.get("nanopubs", []))


def validate(data):
    issues = {"assertion_missing_fields": [], "evidence_missing_fields": [],
              "provenance_missing_fields": [], "duplicate_ids": []}
    nps = _nps(data)
    seen = {}
    for i, np in enumerate(nps):
        a = np.get("assertion", {})
        for k in ASSERTION_REQ:
            if not str(a.get(k, "") or "").strip():
                issues["assertion_missing_fields"].append({"row": i + 1, "field": k})
        e = np.get("evidence", {})
        for k in EVIDENCE_REQ:
            if not str(e.get(k, "") or "").strip():
                issues["evidence_missing_fields"].append({"row": i + 1, "field": k})
        p = np.get("provenance", {})
        # paper 或 doi 至少一个
        if not str(p.get("paper", "") or "").strip() and not str(p.get("doi", "") or "").strip():
            issues["provenance_missing_fields"].append({"row": i + 1, "field": "paper|doi"})
        nid = np.get("id", "")
        if nid in seen:
            issues["duplicate_ids"].append({"id": nid, "rows": [seen[nid], i + 1]})
        elif nid:
            seen[nid] = i + 1
    issues["ok"] = not any(issues.values())
    return issues


def quality(data):
    issues = {"overbroad_assertions": [], "missing_conditions": [], "subject_equals_object": [],
              "indirect_without_note": [], "missing_source_metadata": []}
    nps = _nps(data)
    for i, np in enumerate(nps):
        a = np.get("assertion", {})
        subj, obj = a.get("subject", "").strip(), a.get("object", "").strip()
        cond = a.get("conditions", "").strip()
        pred = a.get("predicate", "").strip()
        # 断言过宽：含"所有/总是/完全/没有任何"且无 conditions
        if re.search(r"(所有|全部|总是|永远|完全|没有任何|all|always|never|entirely)", pred + " " + cond, re.I) and not cond:
            issues["overbroad_assertions"].append(i + 1)
        if not cond:
            issues["missing_conditions"].append(i + 1)
        if subj and obj and subj.lower() == obj.lower():
            issues["subject_equals_object"].append(i + 1)
        e = np.get("evidence", {})
        if e.get("type") == "indirect" and not e.get("note", "").strip():
            issues["indirect_without_note"].append(i + 1)
        p = np.get("provenance", {})
        if not str(p.get("year", "") or "").strip() and not str(p.get("authors", "") or "").strip():
            issues["missing_source_metadata"].append(i + 1)
    issues["ok"] = not any(issues.values())
    return issues


def main():
    if len(sys.argv) < 3:
        print("usage: nanopub_builder.py validate|quality nanopubs.json [report.json]", file=sys.stderr)
        sys.exit(2)
    cmd, src = sys.argv[1], sys.argv[2]
    out = sys.argv[3] if len(sys.argv) > 3 else None
    data = json.load(open(src, encoding="utf-8"))
    res = {"ok": False, "issues": (validate(data) if cmd == "validate" else quality(data))}
    res["ok"] = res["issues"]["ok"]
    print(json.dumps(res, ensure_ascii=False, indent=2))
    if out:
        Path(out).write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
