# 阅读03｜文献翻译 Skill（paper-translator）

把科研原文译成术语统一、段落齐全、关系准确、可核验的目标语言文本；每段译文可回查原文并说明译法依据。

## 组成

- `SKILL.md`：Skill 本体（四条判对标准、工作流、术语/段落/关系/核验规则、自检清单）
- `scripts/translate_assist.py`：辅助脚本（分段、术语候选、译文核验）
- `examples/example_usage.md`：最小调用示例（示意输出已标注）
- `README.md`：本文档

## 脚本用法

```bash
python3 scripts/translate_assist.py segments source.md seg.json    # 段落切分（段号 P1.. / 页码）
python3 scripts/translate_assist.py terms    source.md terms.json  # 术语候选（缩写/重复短语）
python3 scripts/translate_assist.py verify   source.md target.md    # 核验数字/单位/引用编号/否定
```

`verify` 输出：
- `data_numbers_missing_in_target`：正文数据数字丢失列表
- `citation_numbers_missing_in_target`：文献/图表编号丢失列表
- `units_missing_in_target`：单位丢失列表
- `negation_count_source/target`、`negation_dropped`：否定是否被削弱/丢失
- `ok`：全部通过为 true

## 关键方法

1. 先分段编号，锁定术语表，再逐段翻译；标题/摘要/正文/图注/结论同一译名。
2. 译文核验分离「正文数字」「引用编号」「单位」「否定」四类，避免 Fig.→图 这类正常改写被误判。
3. 输出段级双语对照（原文/译文/段号/页码）。

## 依赖

Python 标准库，无第三方依赖。

## 适用场景与限制

- 适用：有文本层的科研 PDF/文本的英中、中英翻译；需要术语一致与双语对照。
- 限制：脚本只做结构化核验（数字/编号/单位/否定），语义正确性需人工判断；中文否定为字符级统计，可能因「无论」等词轻微多计，最终以人工复核为准。

## 失败处理

原文歧义、术语无共识译名、材料缺失：在 `result.json` 的 `uncertainty` 如实标注，不臆造。
