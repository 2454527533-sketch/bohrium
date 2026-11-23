# 阅读15｜文献知识图谱构建 Skill（paper-knowledge-graph）

从论文抽取实体与关系，做实体对齐、来源绑定、真实查询，导出 GraphML/JSON 图谱，支持增量更新。

## 组成

- `SKILL.md`：Skill 本体（四条判对标准、工作流、实体/关系/对齐/查询/增量规则、自检清单）
- `scripts/kg_builder.py`：辅助脚本（validate / align / query / export）
- `examples/example_usage.md`：最小调用示例（示意输出已标注）
- `README.md`：本文档

## 脚本用法

```bash
python3 scripts/kg_builder.py validate graph.json report.json   # 结构/孤立边/缺证据
python3 scripts/kg_builder.py align    graph.json report.json   # 别名/缩写/同名对齐建议
python3 scripts/kg_builder.py query    graph.json report.json   # 3 个真实查询 + 证据
python3 scripts/kg_builder.py export   graph.json out_dir       # 导出 GraphML + JSON
```

`validate` 检查：实体/关系必填字段、孤立边（source/target 不存在）、缺证据、重复 id。
`align` 给出别名/大小写/同名实体的合并或区分建议（附依据）。
`query` 生成邻居查询、按类型查询、两实体路径查询，均附支撑证据。

## 关键方法

1. 只收论文中真实出现的实体，保留 source_loc + quote。
2. 关系只建证据支持者，明确类型/方向/条件/证据强度（direct/indirect）。
3. 对齐可解释：别名、大小写、全称简称、同名实体分别处理。
4. 增量更新保留既有 id，新增/合并/冲突分别说明。

## 依赖

Python 标准库，无第三方依赖。

## 限制与失败处理

证据不足、同名冲突、无法确定关系：写入 `result.json` 的 `uncertainty`，不补造节点或边。
