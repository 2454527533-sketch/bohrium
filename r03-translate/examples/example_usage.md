# 最小调用示例

> 输入与输出均为**示意示例**，只说明接口与完整流程，不冒充正式案例结果。

## 输入

原文 `source.md`（含 `第 N 页` 分页标记）与机器初译 `target.md`。

## 调用

```bash
python3 scripts/translate_assist.py segments source.md seg.json
python3 scripts/translate_assist.py terms    source.md terms.json
python3 scripts/translate_assist.py verify   source.md target.md
```

## 示意输出（`verify`，正常译文）

```json
{
  "ok": true,
  "checks": {
    "data_numbers_missing_in_target": [],
    "citation_numbers_missing_in_target": [],
    "units_missing_in_target": [],
    "negation_count_source": 2,
    "negation_count_target": 2,
    "negation_dropped": false,
    "ok": true
  }
}
```

## 示意输出（`verify`，漏译 0.01）

```json
{
  "ok": false,
  "checks": {
    "data_numbers_missing_in_target": ["0.01"],
    "citation_numbers_missing_in_target": [],
    "units_missing_in_target": [],
    "negation_count_source": 2,
    "negation_count_target": 2,
    "negation_dropped": false,
    "ok": false
  }
}
```

漏译项应回填到 `result.json` 的 `uncertainty`，并逐段修正译文。
