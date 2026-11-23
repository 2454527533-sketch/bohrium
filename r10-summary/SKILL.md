---
name: paper-structured-notes
description: >
  文献总结与结构化笔记：按论文原章节提炼目的/方法/结果/结论，用统一字段生成可并排比较的论文卡片，
  把概念/变量/方法/结论拆成可检索条目并去重去冲突，每条笔记回指原文位置。当任务要求
  "总结论文/结构化笔记/论文卡片/知识提取"时调用。
---

# 文献总结与结构化笔记（回答问题，也给出依据）

## 目标与四条判对标准

产出**与原文结构一致、关键信息齐全、每条可回查、可继续加工**的笔记。判对看四件事：

1. **对得上**：摘要与笔记骨架与论文自身章节和论证顺序一致，不套用通用摘要模板。
2. **留得住**：研究问题、数据、方法条件、主要发现、局限都被记录，尤其是让结论成立的前提条件。
3. **找得回**：每条关键笔记指回原文具体章节、段落、页码或图表，不是笼统出处。
4. **用得上**：笔记可检索、可比较、可继续加工，能被下一次阅读或写作直接使用。

## 输入与输出契约

- 输入 `/input/case.json` 与 `task.md`；确认要产出章节总结、论文卡片、还是知识点条目。
- 输出 `/app/output/result.json` 与笔记：

```json
{
  "case_id": "",
  "status": "success | partial | unknown | refused",
  "result": {
    "notes_file": "outputs/notes.md",
    "section_summaries": [{"section": "章节", "purpose": "", "method": "", "result": "", "conclusion": ""}],
    "paper_card": {
      "research_question": "", "data": "", "method_conditions": "",
      "main_findings": [{"finding": "", "condition": ""}], "limitations": [], "source_ref": ""
    },
    "knowledge_points": [{"term": "", "definition": "", "source_loc": "p3 §2.1", "related": []}]
  },
  "evidence": [{"note": "笔记内容", "section": "§2.1", "page": 3, "quote": "原文片段"}],
  "uncertainty": ["缺失字段/矛盾条目/证据不足项"],
  "change_log": []
}
```

## 工作流（配合 scripts/notes_builder.py）

1. **边界**：读材料与任务，确认要章节总结/论文卡片/知识点中的哪些。
2. **结构骨架**：跑 `python3 scripts/notes_builder.py outline source.md` 提取章节层级，按原章节顺序组织，保留章节承接关系。
3. **章节总结**：每节提炼目的、方法、结果、结论（不脱离结构的通篇摘要）。
4. **论文卡片**：填研究问题、数据、方法条件、主要发现、局限，字段统一，使多篇可并排比较。
5. **知识点提取**：把概念、变量、方法、结论拆成可检索条目；跑 `python3 scripts/notes_builder.py check notes.json` 校验每条有来源定位、去重、标出矛盾。
6. **来源保留**：每条笔记写 `source_loc`（章节/页码/图表）与 `quote`，锚点粒度与可核验性匹配。
7. **落盘**：写笔记、论文卡片、知识点与 `result.json`。

## 关键规则

- **骨架对得上**：章节顺序与原文一致，摘要不套模板。
- **留得住条件**：结论的前提条件、方法条件、数据范围一并记录，不只记结论。
- **找得回**：每条笔记有章节/页码/图表定位与原文片段；机器可判定字段与需人工确认字段分开标注。
- **用得上**：条目可检索、去重、不互相矛盾；同一术语统一表述。

## 诚实与边界

- 缺失字段、矛盾条目、证据不足：写入 `uncertainty`，不补造。
- 无法从原文确认的推断标 `[推断]`，不得写成事实。

## 输出自检清单

- [ ] 笔记骨架与原文章节/论证顺序一致。
- [ ] 研究问题/数据/方法条件/主要发现/局限齐全。
- [ ] 每条笔记有 source_loc + quote，可回查。
- [ ] `notes_builder.py check` 无缺失来源、无重复/矛盾未标注。
- [ ] `uncertainty` 覆盖缺失与矛盾项。
