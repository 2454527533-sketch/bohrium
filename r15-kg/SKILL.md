---
name: paper-knowledge-graph
description: >
  构建文献知识图谱：从论文抽取研究者/材料/方法/任务/指标/结论等实体，处理别名缩写与同名冲突做实体对齐，
  只建立有证据支持的关系并标注类型与方向，为每个节点和边绑定原文位置与证据强度，提供真实查询并导出
  可读图谱文件（GraphML/JSON），支持增量更新。当任务要求"构建知识图谱/实体关系抽取/图谱查询"时调用。
---

# 文献知识图谱构建（回答问题，也给出依据）

## 目标与四条判对标准

把多篇论文整合成**实体真实、关系有据、对齐正确、可查询可回溯**的知识图谱。判对看四件事：

1. **抽得准**：实体对应论文里真实出现的科研对象（研究者/材料/方法/任务/指标/结论），不是模型凭常识补全的概念。
2. **连得对**：关系类型、方向和适用条件与原文一致，不把共现、综述转述或推测当成直接证据。
3. **对得齐**：同一对象在不同论文中的别名、缩写、大小写、同名冲突被正确处理，不产生重复节点，也不错误合并不同对象。
4. **查得到、回得去**：图谱能回答真实查询，每个节点和每条边都能回到论文具体位置与原文片段。

## 输入与输出契约

- 输入 `/input/case.json` 与 `task.md`；确认目标实体/关系类型集与查询要求。
- 输出 `/app/output/result.json`：

```json
{
  "case_id": "",
  "status": "success | partial | unknown | refused",
  "result": {
    "graph_file": "outputs/graph.json",
    "entities": [{"id": "e1", "name": "", "type": "method", "aliases": [], "source_loc": "p2 §1", "quote": ""}],
    "relations": [{"id": "r1", "source": "e1", "target": "e2", "type": "uses|compares|outperforms|supports|contradicts", "conditions": "", "evidence_strength": "direct|indirect", "source_loc": "p4 §3.2", "quote": ""}],
    "queries": [{"query": "与 e1 关联的方法", "results": ["e2"], "evidence": [{"relation": "r1", "quote": ""}]}]
  },
  "evidence": [{"element": "e1|r1", "source_loc": "p2 §1", "quote": ""}],
  "uncertainty": ["证据不足/同名冲突/无法确定关系项"],
  "change_log": []
}
```

## 工作流（配合 scripts/kg_builder.py）

1. **边界**：读材料与任务，确认实体/关系类型集（方法/材料/任务/指标/结论等）与查询要求。
2. **实体识别**：抽取真实出现的科研对象，保留原文位置与表述原文，区分作者自述与他人转述。
3. **实体对齐**：跑 `python3 scripts/kg_builder.py align graph.json` 处理别名、缩写、大小写、全称简称、同名实体，输出合并依据；不产生重复节点，不误合并不同对象。
4. **关系抽取**：只建证据支持的关系，明确类型、方向、适用条件与证据强度（direct/indirect）；共现/转述/推测标 `indirect` 或列入 `uncertainty`。
5. **来源绑定**：每个节点和边保留论文标识、章节/图表位置、原文片段。
6. **校验与查询**：跑 `python3 scripts/kg_builder.py validate graph.json` 与 `query graph.json`，展示 ≥3 个真实查询、结果子图与无法确定的关系。
7. **导出**：跑 `python3 scripts/kg_builder.py export graph.json out_dir` 导出 GraphML 与 JSON；增量更新时保留既有节点编号，说明新增/合并/冲突处置。
8. **落盘**：写 graph、查询、证据与 `result.json`。

## 关键规则

- **实体真实**：只收论文里出现的对象；不凭常识补全；转述内容标注来源。
- **关系有据**：type/direction/conditions 与原文一致；共现≠关系；推测标 `indirect`。
- **对齐可解释**：合并依据写清（DOI/全称简称/别名）；同名不同对象不合并。
- **可查询可回溯**：每个节点/边有 source_loc + quote；查询结果附支撑证据。
- **增量更新**：新论文加入保留既有 id，新增/合并/冲突分别说明。

## 诚实与边界

- 证据不足、同名冲突、无法确定关系：写入 `uncertainty`，不补造边或节点。
- 无法从原文确认的关系不建；推断关系标 `indirect` 或 `[推断]`。

## 输出自检清单

- [ ] 实体真实、类型正确，来源定位齐全。
- [ ] 关系类型/方向/条件与原文一致，证据强度标注正确。
- [ ] `align` 无未解释的重复/错误合并。
- [ ] `validate` 无孤立边、无缺证据；≥3 个查询有结果与证据。
- [ ] 导出 GraphML/JSON 可读；`uncertainty` 覆盖证据不足项。
