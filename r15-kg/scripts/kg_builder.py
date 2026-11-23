#!/usr/bin/env python3
"""知识图谱构建与校验。

用法:
    python3 kg_builder.py validate graph.json [report.json]    # 结构完整性 + 孤立边 + 缺证据
    python3 kg_builder.py align    graph.json [report.json]    # 别名/缩写/大小写对齐建议
    python3 kg_builder.py query    graph.json [report.json]    # 3 个真实查询（邻居/按类型/路径）
    python3 kg_builder.py export   graph.json out_dir          # 导出 GraphML + JSON

纯标准库。检查为提示，供复核，不强制判定。
"""
import json
import re
import sys
from pathlib import Path
from xml.sax.saxutils import escape

ENTITY_REQ = ["id", "name", "type"]
REL_REQ = ["id", "source", "target", "type"]


def _norm_name(s):
    return re.sub(r"[^a-z0-9\u4e00-\u9fff]", "", (s or "").lower())


def validate(data):
    issues = {"entity_missing_fields": [], "relation_missing_fields": [], "dangling_edges": [],
              "missing_evidence": [], "duplicate_ids": []}
    ents = data.get("entities", [])
    rels = data.get("relations", [])
    eids = set()
    seen = set()
    for i, e in enumerate(ents):
        for k in ENTITY_REQ:
            if not str(e.get(k, "") or "").strip():
                issues["entity_missing_fields"].append({"row": i + 1, "field": k})
        if not str(e.get("source_loc", "") or "").strip() and not str(e.get("quote", "") or "").strip():
            issues["missing_evidence"].append({"element": e.get("id", f"entity#{i+1}")})
        eid = e.get("id")
        if eid in seen:
            issues["duplicate_ids"].append({"id": eid, "kind": "entity"})
        if eid:
            seen.add(eid)
            eids.add(eid)
    seen_rel = set()
    for i, r in enumerate(rels):
        for k in REL_REQ:
            if not str(r.get(k, "") or "").strip():
                issues["relation_missing_fields"].append({"row": i + 1, "field": k})
        if r.get("source") not in eids or r.get("target") not in eids:
            issues["dangling_edges"].append({"relation": r.get("id", f"rel#{i+1}"),
                                             "source": r.get("source"), "target": r.get("target")})
        if not str(r.get("source_loc", "") or "").strip() and not str(r.get("quote", "") or "").strip():
            issues["missing_evidence"].append({"element": r.get("id", f"rel#{i+1}")})
        rid = r.get("id")
        if rid in seen_rel:
            issues["duplicate_ids"].append({"id": rid, "kind": "relation"})
        if rid:
            seen_rel.add(rid)
    issues["ok"] = not any(issues.values())
    return issues


def align(data):
    ents = data.get("entities", [])
    groups = {}
    for i, e in enumerate(ents):
        key = _norm_name(e.get("name", ""))
        if key:
            groups.setdefault(key, []).append(i)
    suggestions = []
    for key, idxs in groups.items():
        if len(idxs) > 1:
            names = [ents[i].get("name") for i in idxs]
            if len(set(names)) > 1:
                suggestions.append({"canonical_name": names[0], "rows": [i + 1 for i in idxs],
                                    "names": names, "note": "别名/大小写差异，人工确认是否同一实体"})
            else:
                suggestions.append({"canonical_name": names[0], "rows": [i + 1 for i in idxs],
                                    "names": names, "note": "同名实体，人工确认是否不同对象"})
    return {"ok": True, "merge_suggestions": suggestions}


def query(data):
    ents = data.get("entities", [])
    rels = data.get("relations", [])
    by_id = {e.get("id"): e for e in ents}
    queries = []
    if rels:
        # 查询1：某实体的邻居
        src = rels[0].get("source")
        neigh = [r.get("target") for r in rels if r.get("source") == src] + \
                [r.get("source") for r in rels if r.get("target") == src]
        queries.append({"query": f"与 {src} 直接关联的实体", "results": sorted(set(neigh)),
                        "evidence": [{"relation": rels[0].get("id"), "quote": rels[0].get("quote", "")}]})
    # 查询2：按类型列出实体
    typ = ents[0].get("type") if ents else None
    if typ:
        queries.append({"query": f"类型为 {typ} 的实体", "results": [e.get("id") for e in ents if e.get("type") == typ],
                        "evidence": [{"entity": e.get("id"), "quote": e.get("quote", "")} for e in ents if e.get("type") == typ]})
    # 查询3：两实体间是否有路径（直接边或两步）
    if len(rels) >= 1 and len(ents) >= 2:
        a, b = ents[0].get("id"), ents[-1].get("id")
        path = [r.get("id") for r in rels if (r.get("source") == a and r.get("target") == b) or
                (r.get("source") == b and r.get("target") == a)]
        queries.append({"query": f"{a} 与 {b} 之间是否存在关系", "results": path,
                        "evidence": [{"relation": p, "quote": next((r.get("quote", "") for r in rels if r.get("id") == p), "")} for p in path]})
    return {"ok": True, "queries": queries}


GRAPHML = """<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns">
<key id="d_type" for="node" attr.name="type" attr.type="string"/>
<key id="d_rel" for="edge" attr.name="relation" attr.type="string"/>
<graph id="G" edgedefault="directed">
{nodes}{edges}</graph>
</graphml>"""


def export(data, out_dir):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    ents = data.get("entities", [])
    rels = data.get("relations", [])
    nodes = "".join(
        f'<node id="{escape(str(e.get("id")))}"><data key="d_type">{escape(str(e.get("type", "")))}</data></node>\n'
        for e in ents)
    edges = "".join(
        f'<edge id="{escape(str(r.get("id")))}" source="{escape(str(r.get("source")))}" target="{escape(str(r.get("target")))}">'
        f'<data key="d_rel">{escape(str(r.get("type", "")))}</data></edge>\n'
        for r in rels)
    (out / "graph.graphml").write_text(GRAPHML.format(nodes=nodes, edges=edges), encoding="utf-8")
    (out / "graph.json").write_text(json.dumps({"entities": ents, "relations": rels}, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"ok": True, "graphml": str(out / "graph.graphml"), "json": str(out / "graph.json"),
            "nodes": len(ents), "edges": len(rels)}


def main():
    if len(sys.argv) < 3:
        print("usage: kg_builder.py validate|align|query graph.json [out] | export graph.json out_dir", file=sys.stderr)
        sys.exit(2)
    cmd, src = sys.argv[1], sys.argv[2]
    data = json.load(open(src, encoding="utf-8"))
    if cmd == "export":
        res = export(data, sys.argv[3] if len(sys.argv) > 3 else "graph_out")
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return
    fn = {"validate": validate, "align": align, "query": query}[cmd]
    res = fn(data)
    res = {"ok": res.get("ok", True), "report": res}
    print(json.dumps(res, ensure_ascii=False, indent=2))
    if len(sys.argv) > 3:
        Path(sys.argv[3]).write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
