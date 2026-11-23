# 最小调用示例

> 输入与输出均为**示意示例**，只说明接口与完整流程，不冒充正式案例结果。

## 调用

```bash
python3 scripts/notes_builder.py outline source.md outline.json
python3 scripts/notes_builder.py check   notes.json report.json
```

## 示意输入 `notes.json`（节选）

```json
{
  "paper_card": {
    "research_question": "如何提升 X 的准确率？",
    "data": "数据集 D（N=1000）",
    "method_conditions": "学习率 0.01，训练 100 轮",
    "main_findings": [{"finding": "准确率提升 3.2%", "condition": "在 D 上"}],
    "limitations": ["仅测试单一数据集"]
  },
  "knowledge_points": [
    {"term": "Transformer", "definition": "基于注意力的序列模型", "source_loc": "p3 §2.1", "quote": "..."}
  ]
}
```

## 示意输出 `check`

```json
{
  "ok": true,
  "issues": {
    "card_missing_fields": [],
    "kps_missing_fields": [],
    "kps_missing_anchor": [],
    "kps_duplicates": [],
    "kps_conflicts": [],
    "ok": true
  }
}
```

存在缺失来源、重复或矛盾条目时 `ok:false`，应回填 `result.json` 的 `uncertainty` 并修正。
