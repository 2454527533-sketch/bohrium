# 阅读01｜文献文档解析 Skill（pdf-structured-parser）

把科研论文 PDF 解析为可复核、带原文定位的结构化结果。重点修正：多栏阅读顺序、复杂表格行列归属、公式上下标与希腊字母、扫描版 OCR。

## 组成

- `SKILL.md`：Skill 本体（四条硬性要求、标准工作流、多栏/表格/公式/OCR 规则、诚实规则、自检清单）
- `scripts/pdf_extract.py`：核心解析脚本（自包含，无 Python PDF 库依赖）
- `examples/example_usage.md`：最小调用示例（示意输出已标注为示例）
- `README.md`：本文档

## 脚本用法

```bash
# 输出结构化 JSON（含每块 page/x0/y0/x1/y1 定位）
python3 scripts/pdf_extract.py paper.pdf result.json

# 额外输出 Markdown 重构稿（带页面/坐标注释）
python3 scripts/pdf_extract.py paper.pdf result.json --markdown

# 逐块打印正文/标题/题注/参考文献（便于逐块核对）
python3 scripts/pdf_extract.py paper.pdf --dump-text

# 强制 OCR（扫描版/无文本层）
python3 scripts/pdf_extract.py scanned.pdf result.json --ocr
```

## 关键方法

1. `pdftotext -bbox` 取逐词坐标 → 聚词成行（含上下标启发式）→ 行分类。
2. 只用正文/参考文献行做栏检测（x 中心聚类），标题/作者归为 title，页眉页脚单独标出。
3. 阅读顺序 = 标题 → 通栏 → 左栏 → 右栏 → 页脚，各栏内按 y 坐标。
4. 表格候选：≥3 连续正文行、≥2 个列位置在 ≥80% 行一致出现。
5. 无文本层时自动走 `pdftoppm + tesseract` OCR，并提示与渲染图抽查比对。

## 依赖

- `pdftotext`、`pdftoppm`（poppler-utils）；OCR 可选需 `tesseract`。
- Python 标准库即可，不依赖 pdfplumber/pymupdf。

## 适用场景与限制

- 适用：有文本层的单栏/双栏/多栏科研 PDF，含表格、公式、参考文献。
- 限制：数学符号（如 ∑、∫）在文本层可能被映射错（如 ∑→P），公式以渲染图为准核对；跨页续表、复杂合并单元格需结合渲染图人工确认；扫描件 OCR 数字/单位/上下标/希腊字母为高频错点。

## 失败处理

加密 PDF、无文本层且无 OCR、乱码字体、页码错乱：在 `result.json` 的 `uncertainty` 如实标注，写明原因与可人工接管位置，不补造内容。

## 自查方法

见 `SKILL.md`「输出自检清单」；落盘前逐块比对渲染图（`pdftoppm -png`）确认栏序、段落边界与表格结构。
