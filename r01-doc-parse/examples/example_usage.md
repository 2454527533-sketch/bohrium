# 最小调用示例

> 以下输入与输出均为**示意示例**，用于说明接口与完整使用流程，不冒充正式案例结果。

## 输入

一份科研 PDF 文件，例如 `paper.pdf`（双栏、含一张表格与公式）。

## 调用

```bash
python3 scripts/pdf_extract.py paper.pdf result.json --markdown
```

## 示意输出（`result.json` 片段，节选）

```json
{
  "ok": true,
  "engine": "pdftotext_bbox",
  "meta": {"pages": 3, "words": 2841, "has_text_layer": true},
  "pages": [
    {
      "page": 1, "width": 595.3, "height": 841.9,
      "columns": [{"x0": 72.0, "x1": 260.0}, {"x0": 318.0, "x1": 523.0}],
      "blocks": [
        {"page": 1, "x0": 72.0, "y0": 246.2, "x1": 523.0, "y1": 305.0,
         "kind": "body", "text": "Abstract 正文首段……"}
      ]
    }
  ],
  "tables": [
    {"page": 2, "y0": 511.0, "y1": 560.7,
     "rows": [["Name", "Value", "Unit"], ["lr", "0.01", "-"]]}
  ]
}
```

## 示意 Markdown 片段（`--markdown` 输出）

```markdown
<!-- p1 72,246 -->

## Abstract

<!-- p1 72,271 -->
Abstract 正文，含公式 E = mc^2 与希腊字母 αβγ。
```

每个 `<!-- p页码 x,y -->` 注释即为该块的原文定位，满足「核得回」。
