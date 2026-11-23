#!/usr/bin/env python3
"""从结构化 slide_plan 生成可编辑学术 PPTX（保留模板 master/layout）。

用法:
    python3 build_pptx.py outline.json 输出.pptx [--template 模板.pptx]

outline.json 结构见 templates/outline_schema.json 与 examples/example_outline.json。
- 有 --template 时用模板的母版/版式与主题，不覆盖模板配色页脚；
- 无 --template 时用 python-pptx 默认 16:9 母版。

依赖: python-pptx。缺库时给出明确安装提示，不静默失败。
"""
import json
import sys
from pathlib import Path

try:
    from pptx import Presentation
    from pptx.util import Inches, Pt
    from pptx.dml.color import RGBColor
except ImportError as e:  # pragma: no cover
    print("ERROR: python-pptx 未安装。请先 `python3 -m pip install python-pptx`。", file=sys.stderr)
    print(f"detail: {e}", file=sys.stderr)
    sys.exit(2)


# 版式选择：按名称关键词/占位符结构匹配，失败回退到常见索引。
LAYOUT_DEFAULTS = {"title": 0, "content": 1, "section": 2, "blank": 6}
NAME_HINTS = {
    "title": ("title slide", "标题幻灯片", "title"),
    "section": ("section header", "节标题", "section"),
    "content": ("title and content", "标题和内容", "content"),
    "blank": ("blank", "空白"),
}


def _layout_score(layout, kind):
    name = (layout.name or "").lower()
    score = 0
    for hint in NAME_HINTS.get(kind, ()):
        if hint in name:
            score += 10
    # 占位符结构加分
    ph_types = [ph.placeholder_format.type for ph in layout.placeholders]
    has_title = any(t is not None and "TITLE" in str(t) for t in ph_types)
    has_body = any(t is not None and ("BODY" in str(t) or "OBJECT" in str(t) or "CONTENT" in str(t)) for t in ph_types)
    if kind == "title" and has_title and not has_body:
        score += 5
    if kind == "content" and has_title and has_body:
        score += 5
    if kind == "section" and has_title and not has_body:
        score += 3
    return score


def pick_layout(prs, kind):
    layouts = prs.slide_layouts
    best = max(layouts, key=lambda l: _layout_score(l, kind))
    if _layout_score(best, kind) > 0:
        return best
    idx = LAYOUT_DEFAULTS.get(kind, 1)
    return layouts[min(idx, len(layouts) - 1)]


def _set_text(tf, text):
    tf.text = text


def _fill_bullets(tf, bullets):
    """把 bullets(含 level) 写入正文占位符，保留层级。"""
    for i, b in enumerate(bullets or []):
        text = b.get("text", "") if isinstance(b, dict) else str(b)
        level = int(b.get("level", 0)) if isinstance(b, dict) else 0
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.text = text
        p.level = min(level, 8)


def _find_placeholder(slide, kind_hint):
    for ph in slide.placeholders:
        t = str(ph.placeholder_format.type or "")
        if kind_hint == "title" and "TITLE" in t:
            return ph
        if kind_hint == "body" and ("BODY" in t or "OBJECT" in t or "CONTENT" in t or "SUBTITLE" in t):
            return ph
        if kind_hint == "picture" and ("PICTURE" in t or "OBJECT" in t or "CONTENT" in t):
            return ph
    return None


def build(outline, template_path, out_path):
    prs = Presentation(template_path) if template_path else Presentation()
    # 默认 16:9（无模板时）
    if not template_path:
        prs.slide_width = Inches(13.333)
        prs.slide_height = Inches(7.5)

    for spec in outline.get("slides", []):
        kind = spec.get("layout", "content")
        layout = pick_layout(prs, kind)
        slide = prs.slides.add_slide(layout)

        title = spec.get("title") or spec.get("claim") or ""
        tph = _find_placeholder(slide, "title")
        if tph is not None and title:
            tph.text = title

        # 正文要点
        bullets = spec.get("bullets") or []
        body = _find_placeholder(slide, "body")
        if body is not None and bullets:
            _fill_bullets(body.text_frame, bullets)
        elif bullets and title and "content" in kind:
            # 无正文占位符时的兜底文本框
            box = slide.shapes.add_textbox(Inches(0.8), Inches(1.7), Inches(11.7), Inches(5.2))
            _fill_bullets(box.text_frame, bullets)

        # 图（有图片占位符则填占位符，否则按坐标插入）
        for fi, fig in enumerate(spec.get("figures") or []):
            fpath = fig.get("path")
            if not fpath or not Path(fpath).exists():
                continue
            pic = _find_placeholder(slide, "picture") if fi == 0 else None
            w = Inches(float(fig.get("width_in", 5.5)))
            if pic is not None:
                pic.insert_picture(str(fpath))
            else:
                left = Inches(0.8 + (fi % 2) * 6.2)
                top = Inches(3.2 if bullets else 1.9)
                slide.shapes.add_picture(str(fpath), left, top, width=w)
            if fig.get("caption"):
                cap = slide.shapes.add_textbox(Inches(0.8), Inches(6.4), Inches(11.7), Inches(0.7))
                cap.text_frame.text = fig["caption"]

        # 讲稿备注（notes_slide 属性会在不存在时自动创建）
        notes = spec.get("notes")
        if notes:
            slide.notes_slide.notes_text_frame.text = notes

    prs.save(out_path)
    return out_path


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--template=")]
    template = None
    for a in sys.argv[1:]:
        if a.startswith("--template="):
            template = a.split("=", 1)[1]
    if len(args) < 2:
        print("usage: build_pptx.py outline.json out.pptx [--template=模板.pptx]", file=sys.stderr)
        sys.exit(2)
    outline = json.load(open(args[0], encoding="utf-8"))
    out = build(outline, template, args[1])
    print(json.dumps({"ok": True, "out": out, "slides": len(outline.get("slides", []))}, ensure_ascii=False))


if __name__ == "__main__":
    main()
