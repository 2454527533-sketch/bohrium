# 最小调用示例

> 输入与输出均为**示意示例**，只说明接口与完整流程，不冒充正式案例结果。

## 调用

```bash
python3 scripts/kg_builder.py validate graph.json report.json
python3 scripts/kg_builder.py align    graph.json align.json
python3 scripts/kg_builder.py query    graph.json query.json
python3 scripts/kg_builder.py export   graph.json out_dir
```

## 示意输入 `graph.json`（节选）

```json
{
  "entities": [
    {"id": "e1", "name": "GPT-4", "type": "model", "aliases": ["GPT4"], "source_loc": "p1 §1", "quote": "..."},
    {"id": "e2", "name": "BLEU", "type": "metric", "source_loc": "p3 §2", "quote": "..."}
  ],
  "relations": [
    {"id": "r1", "source": "e1", "target": "e2", "type": "uses", "source_loc": "p3", "quote": "..."}
  ]
}
```

## 示意输出

`validate`：孤立边/缺证据为空时 `ok:true`。
`align`：`{"merge_suggestions": [{"canonical_name": "GPT-4", "names": ["GPT-4", "gpt-4"], "note": "别名/大小写差异…"}]}`
`query`：生成「与 e1 直接关联的实体 → [e2]」等查询，附证据。
`export`：`graph.graphml` + `graph.json`，节点/边数与输入一致。
