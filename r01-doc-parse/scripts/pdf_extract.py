#!/usr/bin/env python3
"""科研 PDF 结构化解析（自包含，优先用 pdftotext -bbox 坐标，无需 Python PDF 库）。

用法:
    python3 pdf_extract.py <pdf路径> [out.json] [--markdown] [--dump-text] [--ocr]

流程:
  1. pdftotext -bbox 取逐词坐标（引擎: pdftotext_bbox）
  2. 聚词成行 -> 行分类 -> 只用正文行做栏检测 -> 阅读顺序 -> 段落块
  3. 表格候选检测（列位置在多数行一致才判为表格）；公式上下标用字号+基线启发式保留
  4. 无文本层/字数过少时用 pdftoppm + tesseract 走 OCR（引擎: ocr），无 tesseract 则如实标注
输出 JSON：meta / pages[].{page,width,height,columns,blocks[]} / tables / markdown / warnings。
每个 block 带 page/x0/y0/x1/y1 坐标与 kind，保证"核得回"。
"""
import html as _html
import json
import re
import subprocess
import sys
from pathlib import Path


def run_pdftotext_bbox(pdf):
    try:
        r = subprocess.run(["pdftotext", "-bbox", str(pdf), "-"],
                           capture_output=True, text=True, timeout=300)
    except FileNotFoundError:
        return None
    if r.returncode != 0:
        return None
    token = re.compile(
        r'<page width="([\d.]+)" height="([\d.]+)">'
        r'|<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</word>',
        re.S)
    pages, cur = [], None
    for m in token.finditer(r.stdout):
        if m.group(1):
            cur = {"page": len(pages) + 1, "width": float(m.group(1)), "height": float(m.group(2)), "words": []}
            pages.append(cur)
        elif cur is not None:
            cur["words"].append({
                "x0": float(m.group(3)), "y0": float(m.group(4)),
                "x1": float(m.group(5)), "y1": float(m.group(6)),
                "text": _html.unescape(m.group(7)),
            })
    return pages


def group_lines(pages):
    for pg in pages:
        words = sorted(pg["words"], key=lambda w: (round(w["y0"] / 2), w["x0"]))
        lines = []
        for w in words:
            if lines and abs(w["y0"] - lines[-1]["y0"]) < 3.5:
                lines[-1]["words"].append(w)
                lines[-1]["x0"] = min(lines[-1]["x0"], w["x0"])
                lines[-1]["x1"] = max(lines[-1]["x1"], w["x1"])
                lines[-1]["y0"] = min(lines[-1]["y0"], w["y0"])
                lines[-1]["y1"] = max(lines[-1]["y1"], w["y1"])
            else:
                lines.append({"x0": w["x0"], "y0": w["y0"], "x1": w["x1"], "y1": w["y1"],
                              "words": [w]})
        out = []
        for ln in lines:
            ws = sorted(ln["words"], key=lambda w: w["x0"])
            ln["height"] = ln["y1"] - ln["y0"]
            hs = sorted(w["y1"] - w["y0"] for w in ws)
            med = hs[len(hs) // 2] if hs else 8
            ln["median_h"] = med
            text = ws[0]["text"]
            for w in ws[1:]:
                h = w["y1"] - w["y0"]
                dy = (w["y0"] + w["y1"]) / 2 - (ln["y0"] + ln["y1"]) / 2
                if h < 0.75 * med and dy < -0.12 * med:      # 上标
                    text += "^" + w["text"]
                elif h < 0.75 * med and dy > 0.12 * med:     # 下标
                    text += "_" + w["text"]
                else:
                    text += " " + w["text"]
            ln["text"] = text
            out.append(ln)
        pg["lines"] = out
    return pages


def classify(line, page_w, page_h):
    t = line["text"].strip()
    low = t.lower()
    cx = (line["x0"] + line["x1"]) / 2
    w = line["x1"] - line["x0"]
    if not t:
        return "body"
    # 页眉页脚
    if line["y0"] < 0.08 * page_h and len(t) < 200:
        return "header"
    if line["y0"] > 0.80 * page_h and len(t) < 200:
        return "footer"
    # 标题/作者：顶部居中
    if line["y0"] < 0.35 * page_h and abs(cx - page_w / 2) < 0.14 * page_w and w < 0.6 * page_w:
        return "title"
    if re.match(r"^(fig(ure)?\.?\s|table\s|图\s*\d|表\s*\d)", low) and len(t) < 200:
        return "caption"
    if re.match(r"^\[\d+\]", t) or re.match(r"^(doi|https?://)", low):
        return "reference"
    if re.match(r"^\d+(\.\d+)*\.?\s+\S", t) and len(t) < 120:
        return "heading"
    if low in ("abstract", "introduction", "methods", "results", "discussion", "conclusion",
               "references", "摘要", "引言", "方法", "结果", "讨论", "结论", "参考文献") and len(t) < 40:
        return "heading"
    return "body"


def detect_columns(body_lines, page_width):
    if len(body_lines) < 3:
        return [{"x0": 0.0, "x1": page_width, "idx": 0}]
    centers = sorted((l["x0"] + l["x1"]) / 2 for l in body_lines)
    thr = max(page_width / 8, 20.0)
    clusters = []
    for c in centers:
        if clusters and c - clusters[-1][-1] <= thr:
            clusters[-1].append(c)
        else:
            clusters.append([c])
    cols = [{"x0": min(cl), "x1": max(cl), "idx": i} for i, cl in enumerate(clusters) if len(cl) >= 2]
    if not cols:
        cols = [{"x0": min(centers), "x1": max(centers), "idx": 0}]
    return cols


def assemble_blocks(pg):
    lines = pg["lines"]
    w, h = pg["width"], pg["height"]
    for l in lines:
        l["kind"] = classify(l, w, h)
    # 栏检测只用正文/参考文献行（排除标题、题注、页眉页脚、公式孤立行等）
    flow = [l for l in lines if l["kind"] in ("body", "reference")]
    cols = detect_columns(flow, w)
    for l in lines:
        if l["kind"] in ("title",):
            l["col"] = -2
        elif l["kind"] == "footer":
            l["col"] = 999
        elif (l["x1"] - l["x0"]) > 0.6 * w:
            l["col"] = -1
        else:
            c = (l["x0"] + l["x1"]) / 2
            best = min(cols, key=lambda cc: abs(c - (cc["x0"] + cc["x1"]) / 2))
            l["col"] = best["idx"]
    order = sorted(range(len(lines)),
                   key=lambda i: (lines[i]["col"], round(lines[i]["y0"] / 10), lines[i]["y0"]))
    blocks = []
    for i in order:
        l = lines[i]
        if (blocks and l["col"] == blocks[-1]["lines"][-1]["col"]
                and l["kind"] == blocks[-1]["lines"][-1]["kind"]
                and (l["y0"] - blocks[-1]["lines"][-1]["y1"]) < 1.6 * max(l["height"], 8)):
            blocks[-1]["lines"].append(l)
            blocks[-1]["x0"] = min(blocks[-1]["x0"], l["x0"])
            blocks[-1]["x1"] = max(blocks[-1]["x1"], l["x1"])
            blocks[-1]["y1"] = max(blocks[-1]["y1"], l["y1"])
        else:
            blocks.append({"page": pg["page"], "x0": l["x0"], "y0": l["y0"],
                           "x1": l["x1"], "y1": l["y1"], "lines": [l], "kind": l["kind"]})
    for b in blocks:
        b["text"] = " ".join(l["text"] for l in b["lines"])
    pg["blocks"] = blocks
    pg["columns"] = [{"x0": c["x0"], "x1": c["x1"]} for c in cols]
    pg["reading_order"] = order
    return pg


def detect_tables(pg):
    """表格候选：≥3 连续正文行，≥2 个列位置在 ≥80% 行一致出现，且每行词数受限。"""
    tables = []
    lines = pg["lines"]
    i = 0
    while i < len(lines) - 2:
        if lines[i]["kind"] not in ("body",):
            i += 1
            continue
        grp = [lines[i]]
        j = i + 1
        while j < len(lines) and lines[j]["kind"] == "body" and \
                abs(lines[j]["y0"] - grp[-1]["y0"]) < 2.5 * max(grp[-1]["height"], 8):
            grp.append(lines[j])
            j += 1
        if len(grp) >= 3 and all(len(l["words"]) <= 12 for l in grp):
            colxs = []
            for x in sorted(round(w["x0"], 1) for l in grp for w in l["words"]):
                if not colxs or x - colxs[-1] > 4:
                    colxs.append(x)
                else:
                    colxs[-1] = (colxs[-1] + x) / 2
            hits = [0] * len(colxs)
            for l in grp:
                for k, cx in enumerate(colxs):
                    if any(abs(w["x0"] - cx) <= 4 for w in l["words"]):
                        hits[k] += 1
            n_lines = len(grp)
            valid = [cx for cx, hh in zip(colxs, hits) if hh >= 0.8 * n_lines]
            if len(valid) >= 2:
                rows = []
                for l in grp:
                    cells = []
                    for k in range(len(valid)):
                        lo = valid[k] - 3
                        hi = valid[k + 1] - 3 if k + 1 < len(valid) else 10**9
                        cells.append(" ".join(w["text"] for w in sorted(l["words"], key=lambda w: w["x0"]) if lo <= w["x0"] < hi))
                    rows.append(cells)
                tables.append({"page": pg["page"], "y0": grp[0]["y0"], "y1": grp[-1]["y1"], "rows": rows})
                i = j
                continue
        i += 1
    return tables


def to_markdown(pages):
    parts = []
    for pg in pages:
        for b in pg["blocks"]:
            kind, t = b["kind"], b["text"]
            loc = f"<!-- p{pg['page']} {b['x0']:.0f},{b['y0']:.0f} -->"
            if kind == "heading":
                parts.append(f"{loc}\n\n## {t}")
            elif kind == "title":
                parts.append(f"{loc}\n\n# {t}")
            elif kind == "reference":
                parts.append(f"{loc}\n{t}")
            elif kind in ("header", "footer"):
                parts.append(f"{loc}\n[{kind.upper()}] {t}")
            else:
                parts.append(f"{loc}\n{t}")
    return "\n\n".join(parts)


def run_ocr(pdf, pno):
    try:
        subprocess.run(["pdftoppm", "-version"], capture_output=True)
        subprocess.run(["tesseract", "--version"], capture_output=True)
    except FileNotFoundError:
        return None
    try:
        subprocess.run(["pdftoppm", "-png", "-r", "300", "-f", str(pno), "-l", str(pno),
                        str(pdf), "/tmp/_pg"], capture_output=True, check=True)
        r = subprocess.run(["tesseract", f"/tmp/_pg-{pno:02d}.png", "-", "tsv"],
                           capture_output=True, text=True, check=True)
        return r.stdout
    except Exception:
        return None


def main():
    argv = sys.argv[1:]
    want_md = "--markdown" in argv
    dump_text = "--dump-text" in argv
    force_ocr = "--ocr" in argv
    pos = [a for a in argv if not a.startswith("--")]
    if not pos:
        print("usage: pdf_extract.py <pdf> [out.json] [--markdown] [--dump-text] [--ocr]", file=sys.stderr)
        sys.exit(2)
    pdf = Path(pos[0])
    out_path = Path(pos[1]) if len(pos) > 1 else None

    OUT = {"ok": False, "engine": None, "meta": {}, "pages": [], "tables": [], "markdown": "", "warnings": []}
    if not pdf.exists():
        OUT["warnings"].append(f"pdf not found: {pdf}")
        print(json.dumps(OUT, ensure_ascii=False, indent=2))
        sys.exit(1)

    pages = run_pdftotext_bbox(pdf)
    total_words = sum(len(p["words"]) for p in (pages or []))
    if pages and total_words > 0 and not force_ocr:
        pages = group_lines(pages)
        for p in pages:
            assemble_blocks(p)
        tables = []
        for p in pages:
            tables.extend(detect_tables(p))
        OUT.update({
            "ok": True, "engine": "pdftotext_bbox",
            "meta": {"pages": len(pages), "words": total_words, "has_text_layer": total_words > 0},
            "pages": [{"page": p["page"], "width": p["width"], "height": p["height"],
                       "columns": p["columns"], "blocks": p["blocks"]} for p in pages],
            "tables": tables,
        })
    else:
        if pages is None:
            OUT["warnings"].append("pdftotext failed; trying OCR (pdftoppm+tesseract)")
        elif total_words == 0:
            OUT["warnings"].append("no text layer; trying OCR")
        ocr_done = 0
        for p in (pages or [{"page": 1}]):
            if run_ocr(pdf, p["page"]) is not None:
                ocr_done += 1
        if ocr_done:
            OUT["engine"] = "ocr"
            OUT["meta"] = {"pages": len(pages or [1]), "has_text_layer": False, "ocr_pages": ocr_done}
            OUT["warnings"].append("OCR 结果需与渲染图抽查比对；数字/单位/上下标/希腊字母为高频错点")
        else:
            OUT["engine"] = "none"
            OUT["warnings"].append("无文本层且 OCR 不可用；需要人工接管或图像型处理")

    OUT["markdown"] = to_markdown(OUT["pages"]) if OUT["pages"] else ""
    if dump_text:
        for pg in OUT["pages"]:
            for b in pg["blocks"]:
                print(f"[p{pg['page']}][{b['kind']}]({b['x0']:.0f},{b['y0']:.0f}) {b['text']}")
    if out_path:
        out_path.write_text(json.dumps(OUT, ensure_ascii=False, indent=2), encoding="utf-8")
    if want_md:
        print(OUT["markdown"])
    elif out_path is None:
        print(json.dumps(OUT, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
