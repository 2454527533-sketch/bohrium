# 最小调用示例

> 输入与输出均为**示意示例**，只说明接口与完整流程，不冒充正式案例结果。

## 调用

```bash
python3 scripts/nanopub_builder.py validate nanopubs.json report.json
python3 scripts/nanopub_builder.py quality  nanopubs.json report.json
```

## 示意输入 `nanopubs.json`（节选）

```json
{
  "nanopublications": [
    {
      "id": "np1",
      "assertion": {"subject": "Method A", "predicate": "outperforms", "object": "Method B", "conditions": "on dataset D"},
      "evidence": {"quote": "A achieves 90.2%", "location": "p3 §2.1", "type": "direct"},
      "provenance": {"paper": "Paper P", "authors": ["X"], "year": "2020", "doi": "10.1/x"}
    }
  ]
}
```

## 示意输出 `validate`

```json
{"ok": true, "issues": {"assertion_missing_fields": [], "evidence_missing_fields": [],
  "provenance_missing_fields": [], "duplicate_ids": [], "ok": true}}
```

存在断言过宽、证据缺失、主体混淆（subject==object）、来源缺失时 `ok:false`，应回填 `uncertainty` 并修正。
