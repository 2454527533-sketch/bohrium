# 阅读14｜Nanopublication Skill（nanopub-builder）

把论文结论拆成单一可验证断言，逐条绑定最小证据与原文位置，记录来源元数据，做质量检查并导出可机读结构。

## 组成

- `SKILL.md`：Skill 本体（四条判对标准、工作流、断言/证据/来源/质量规则、自检清单）
- `scripts/nanopub_builder.py`：校验脚本（validate 结构完整性 / quality 质量检查）
- `examples/example_usage.md`：最小调用示例（示意输出已标注）
- `README.md`：本文档

## 脚本用法

```bash
python3 scripts/nanopub_builder.py validate nanopubs.json report.json  # 结构完整性
python3 scripts/nanopub_builder.py quality  nanopubs.json report.json  # 质量检查
```

`validate` 检查：断言三要素（subject/predicate/object）、证据（quote/location）、来源（paper|doi）、id 唯一。
`quality` 检查：断言过宽、缺 conditions、subject==object（主体混淆）、indirect 缺说明、来源元数据缺失。

## 关键方法

1. 复合句拆成单一断言，条件/限定写入 `conditions`。
2. 每条断言绑定最小证据片段 + 原文位置，direct/indirect 区分。
3. 来源元数据（论文/作者/年份/版本/DOI）完整，支撑回溯与去重。

## 依赖

Python 标准库，无第三方依赖。

## 限制与失败处理

证据不足、主体混淆、来源缺失、断言过宽：写入 `result.json` 的 `uncertainty`，不补造证据。
