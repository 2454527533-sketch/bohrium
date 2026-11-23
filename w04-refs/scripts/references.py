#!/usr/bin/env python3
"""参考文献辅助脚本：去重、按首现顺序重排编号、格式转换（GB/T 7714-2015 / APA）。

用法:
    python3 references.py dedup refs.bib [out.bib]        # 按 DOI/题名去重
    python3 references.py renumber manuscript.md [out.md] # 正文[n]按首现顺序重排，同步文末列表
    python3 references.py convert refs.bib --style gbt7714|apa [out.txt]

纯标准库实现。BibTeX 解析为启发式，覆盖 @article/@inproceedings/@book/@misc 常见字段；
复杂嵌套（如字段内多层花括号）需人工复核。
"""
import re
import sys
from pathlib import Path

ENTRY_RE = re.compile(r"@(\w+)\s*\{\s*([^,]+),\s*(.*?)\s*\}\s*(?=@|\Z)", re.S)
FIELD_RE = re.compile(r"(\w+)\s*=\s*(\{.*?\}|\"[^\"]*\")", re.S)


def _strip_value(v):
    v = v.strip()
    if v.startswith("{") and v.endswith("}"):
        v = v[1:-1]
    elif v.startswith('"') and v.endswith('"'):
        v = v[1:-1]
    return re.sub(r"\s+", " ", v).strip()


def parse_bibtex(text):
    entries = []
    for m in ENTRY_RE.finditer(text):
        typ, key, body = m.group(1).lower(), m.group(2).strip(), m.group(3)
        fields = {}
        for fm in FIELD_RE.finditer(body):
            fields[fm.group(1).lower()] = _strip_value(fm.group(2))
        entries.append({"type": typ, "key": key, "fields": fields})
    return entries


def norm_doi(s):
    s = (s or "").strip().lower()
    s = re.sub(r"^https?://(dx\.)?doi\.org/", "", s)
    return s.rstrip(".,; ")


def norm_title(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def dedup(entries):
    seen = {}
    out = []
    merges = []
    for e in entries:
        f = e["fields"]
        dkey = "doi:" + norm_doi(f.get("doi", ""))
        tkey = "title:" + norm_title(f.get("title", ""))
        key = dkey if norm_doi(f.get("doi", "")) else tkey
        if key in seen:
            merges.append({"kept": seen[key]["key"], "merged": e["key"], "by": dkey if key.startswith("doi") else tkey})
            continue
        seen[key] = e
        out.append(e)
    return out, merges


def _authors(fields):
    a = (fields.get("author") or fields.get("editor") or "").strip()
    if not a:
        return ""
    parts = [p.strip() for p in re.split(r"\s+and\s+", a, flags=re.I)]
    names = []
    for p in parts:
        p = p.strip().rstrip(",").strip()
        if "," in p:  # "Smith, John"
            surname, given = [x.strip() for x in p.split(",", 1)]
        else:  # "John Smith"
            toks = p.split()
            surname, given = toks[-1], " ".join(toks[:-1])
        initials = "".join(w[0].upper() for w in given.split() if w)
        names.append(f"{surname} {initials}".strip())
    if len(names) > 3:
        return ", ".join(names[:3]) + ", et al"
    return ", ".join(names)


def fmt_gbt7714(e):
    f = e["fields"]
    au = _authors(f)
    title = f.get("title", "")
    year = f.get("year", "")
    typ = e["type"]
    if typ == "article":
        j = f.get("journal", "")
        vol = f.get("volume", "")
        num = f.get("number", "")
        pages = f.get("pages", "").replace("--", "-")
        vn = vol + (f"({num})" if num else "")
        page = f": {pages}" if pages else ""
        return f"{au}. {title}[J]. {j}, {year}, {vn}{page}."
    if typ == "inproceedings":
        book = f.get("booktitle", "")
        addr = f.get("address", "")
        pub = f.get("publisher", "")
        pages = f.get("pages", "").replace("--", "-")
        page = f": {pages}" if pages else ""
        loc = f"{addr}: {pub}" if addr and pub else (addr or pub)
        loc = f". {loc}" if loc else ""
        return f"{au}. {title}[C]//{book}{loc}, {year}{page}."
    if typ == "book":
        addr = f.get("address", "")
        pub = f.get("publisher", "")
        loc = f"{addr}: {pub}" if addr and pub else (addr or pub)
        loc = f". {loc}" if loc else ""
        return f"{au}. {title}[M]{loc}, {year}."
    url = f.get("url", "")
    doi = f.get("doi", "")
    link = url or (f"https://doi.org/{doi}" if doi else "")
    return f"{au}. {title}[EB/OL]. ({year})[引用日期]. {link}."


def fmt_apa(e):
    f = e["fields"]
    au = _authors(f)
    year = f.get("year", "")
    title = f.get("title", "")
    doi = norm_doi(f.get("doi", ""))
    link = f" https://doi.org/{doi}" if doi else ""
    if e["type"] == "article":
        j = f.get("journal", "")
        vol = f.get("volume", "")
        num = f.get("number", "")
        pages = f.get("pages", "").replace("--", "-")
        vn = f", {vol}" + (f"({num})" if num else "")
        pg = f", {pages}" if pages else ""
        return f"{au} ({year}). {title}. {j}{vn}{pg}.{link}"
    return f"{au} ({year}). {title}.{link}"


def renumber_manuscript(text):
    head, sep, refs = text.partition(re.search(r"\n\s*#+\s*(参考文献|References)", text).group(0) if re.search(r"\n\s*#+\s*(参考文献|References)", text) else "")
    if not sep:
        return text, []
    # 正文中的引用编号
    cit_re = re.compile(r"\[(\d+(?:\s*[,，\-–]\s*\d+)*)\]")
    order = []
    for m in cit_re.finditer(head):
        for n in re.findall(r"\d+", m.group(1)):
            n = int(n)
            if n not in order:
                order.append(n)
    mapping = {old: i + 1 for i, old in enumerate(order)}
    def repl(m):
        # 单趟替换：每个数字只映射一次，避免 2→1→2 的链式重映射
        inner = m.group(1)
        inner = re.sub(r"\d+", lambda n: str(mapping.get(int(n.group()), int(n.group()))), inner)
        return f"[{inner}]"
    new_head = cit_re.sub(repl, head)
    # 文末列表重排：假设每行以 [n] 开头
    ref_lines = refs.strip().splitlines()
    parsed = {}
    for ln in ref_lines:
        m = re.match(r"\[(\d+)\]\s*(.*)", ln.strip())
        if m:
            parsed[int(m.group(1))] = m.group(2)
    new_refs = "\n".join(f"[{mapping[k]}] {parsed[k]}" for k in order if k in parsed)
    return new_head + sep + "\n" + new_refs, mapping


def main():
    args = sys.argv[1:]
    if not args:
        print("usage: references.py dedup|renumber|convert ...", file=sys.stderr)
        sys.exit(2)
    cmd = args[0]
    if cmd == "dedup":
        src = args[1] if len(args) > 1 else ""
        out = args[2] if len(args) > 2 else (str(Path(src).with_suffix("")) + ".dedup.bib")
        text = Path(src).read_text(encoding="utf-8")
        entries = parse_bibtex(text)
        kept, merges = dedup(entries)
        res = "\n\n".join(f"@{e['type']}{{{e['key']},\n" + ",\n".join(f"  {k} = {{{v}}}" for k, v in e["fields"].items()) + "\n}" for e in kept)
        Path(out).write_text(res + "\n", encoding="utf-8")
        print(json_dumps({"ok": True, "kept": len(kept), "merged": len(merges), "out": out, "merges": merges}))
    elif cmd == "renumber":
        src = args[1] if len(args) > 1 else ""
        out = args[2] if len(args) > 2 else (str(Path(src).with_suffix("")) + ".renumbered.md")
        text = Path(src).read_text(encoding="utf-8")
        new_text, mapping = renumber_manuscript(text)
        Path(out).write_text(new_text, encoding="utf-8")
        print(json_dumps({"ok": True, "mapping": mapping, "out": out}))
    elif cmd == "convert":
        src = args[1] if len(args) > 1 else ""
        style = "gbt7714"
        if "--style" in args:
            style = args[args.index("--style") + 1]
        out = args[-1] if args[-1].endswith((".txt", ".md")) else (str(Path(src).with_suffix("")) + f".{style}.txt")
        text = Path(src).read_text(encoding="utf-8")
        entries = parse_bibtex(text)
        fn = fmt_gbt7714 if style == "gbt7714" else fmt_apa
        lines = [f"[{i+1}] {fn(e)}" for i, e in enumerate(entries)]
        Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(json_dumps({"ok": True, "style": style, "count": len(entries), "out": out}))


def json_dumps(o):
    import json
    return json.dumps(o, ensure_ascii=False)


if __name__ == "__main__":
    main()
