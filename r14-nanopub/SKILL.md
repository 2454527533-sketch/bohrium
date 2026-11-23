---
name: nanopub-builder
description: >
  构建 Nanopublication：把段落结论拆成若干条单一、可验证的断言，为每条绑定最小证据片段与原文位置，
  记录论文/作者/年份/版本/标识符等来源元数据，并做质量检查（断言过宽、证据不足、主体混淆、来源缺失），
  导出可被下游程序直接解析的结构。当任务要求"构建 Nanopublication/断言拆解/证据绑定"时调用。
---

# Nanopublication 构建（回答问题，也给出依据）

## 目标与四条判对标准

把论文结论变成**可机读、可独立判真、证据可回查、来源链路完整**的知识单元。判对看四件事：

1. **拆得细**：一段结论拆成若干条各自可判断真假的断言，不把整段塞进一个字段；保留条件与限定范围，处理并列与因果结构。
2. **对得上**：每条断言绑定真正支撑它的最小证据片段，证据原文位置可指出；区分直接证据与间接推论。
3. **追得回**：断言、证据、论文、作者、年份、版本之间的链路完整，能回到原文。
4. **读得懂**：导出结构符合约定字段与序列化形态，下游程序可直接解析，无需人工清洗。

## 输入与输出契约

- 输入 `/input/case.json` 与 `task.md`；确认目标字段约定（如是否需 RDF/TriG，还是 JSON 序列化）。
- 输出 `/app/output/result.json`：

```json
{
  "case_id": "",
  "status": "success | partial | unknown | refused",
  "result": {
    "nanopubs_file": "outputs/nanopubs.json",
    "nanopublications": [
      {
        "id": "np1",
        "assertion": {"subject": "", "predicate": "", "object": "", "conditions": ""},
        "evidence": {"quote": "原文片段", "location": "p3 §2.1", "type": "direct|indirect"},
        "provenance": {"paper": "", "authors": [], "year": "", "doi": "", "version": ""}
      }
    ]
  },
  "evidence": [{"np_id": "np1", "location": "p3 §2.1", "quote": ""}],
  "uncertainty": ["证据不足/主体混淆/来源缺失/断言过宽项"],
  "change_log": []
}
```

## 工作流（配合 scripts/nanopub_builder.py）

1. **边界**：读材料与任务，确认断言来源段落与目标序列化形态。
2. **断言拆解**：把复合句拆成单一断言（主语-谓词-宾语），保留条件与限定；并列拆多条、因果写方向。
3. **证据绑定**：为每条断言选最小充分证据片段 + 原文位置，标 `direct`（直接证据）或 `indirect`（间接推论）。
4. **来源元数据**：填论文、作者、年份、版本、DOI/标识符，支撑回溯与去重。
5. **质量检查**：跑 `python3 scripts/nanopub_builder.py validate nanopubs.json` 与 `quality nanopubs.json`，检出断言过宽、证据不足、主体混淆、来源缺失。
6. **导出**：按约定序列化（JSON；如要求 RDF/TriG 用对应模板）导出，保证下游可直接解析。
7. **落盘**：写 nanopubs、证据、来源与 `result.json`。

## 关键规则

- **单一断言**：一条 = 一个可判真的命题；复合句拆分，条件与限定显式写进 `conditions`。
- **最小证据**：证据片段要最小充分，`location` 精确到章节/页码/图表；间接推论标 `indirect`。
- **链路完整**：断言→证据→论文→作者→年份→版本 一条链不缺。
- **可机读**：字段名、类型、序列化形态稳定，不做自由文本拼接。

## 诚实与边界

- 证据不足、主体混淆、来源缺失、断言过宽：写入 `uncertainty`，不补造证据。
- 无法判断真假的断言标 `[无法判断]`，不得写成事实。

## 输出自检清单

- [ ] 每条断言单一、可验证，条件与限定保留。
- [ ] 每条有最小证据片段 + 原文位置，direct/indirect 标注正确。
- [ ] 来源元数据（论文/作者/年份/版本/标识符）齐全。
- [ ] `validate` 通过、`quality` 无未解释问题。
- [ ] `uncertainty` 覆盖证据不足/来源缺失项。
