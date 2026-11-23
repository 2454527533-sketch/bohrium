# slide_plan / evidence_map 模板说明

本 Skill 的核心产物是两份结构化 JSON：`slide_plan`（页级大纲，喂给 `scripts/build_pptx.py` 生成 PPTX）与 `evidence_map`（页级证据映射，供复核）。下面是字段约定与最小示例。所有正式案例由平台提供，本模板不包含任何正式案例答案。

## 1. slide_plan（outline.json）

```json
{
  "title": "论文标题（或汇报标题）",
  "subtitle": "作者 / 期刊 / 场合（可选）",
  "slides": [
    {
      "page": 1,
      "layout": "title | content | section | blank",
      "title": "本页标题（页级主张，一句话）",
      "claim": "本页唯一主张句",
      "bullets": [
        {"text": "支撑要点 1", "level": 0},
        {"text": "支撑要点 2", "level": 1}
      ],
      "figures": [
        {"path": "work/fig3.png", "caption": "Fig 3: ...", "width_in": 5.5}
      ],
      "notes": "讲稿备注：过渡、强调点、被提问时的补充证据",
      "evidence": [
        {"paper_page": 6, "kind": "figure", "ref": "Fig 4", "quote": "原文片段"}
      ]
    }
  ]
}
```

字段规则：
- `claim` 是单句主张；`bullets` 是短语化要点，不是段落粘贴。
- `figures[].path` 必须指向实际存在的图片文件（从 PDF 用 pdf-render-tool 按页/区块导出）。
- `layout` 对应模板版式：`title` 标题页、`section` 章节页、`content` 内容页、`blank` 空白页。
- `notes` 与页面互补，不重复页面文字。

## 2. evidence_map（evidence_map.json）

```json
{
  "paper_id": "...",
  "mapping": [
    {"slide": 3, "paper_page": 6, "section": "Results", "kind": "figure",
     "ref": "Fig 4", "claim": "本页主张", "quote": "原文证据片段", "status": "confirmed | inferred"}
  ]
}
```

字段规则：
- `status=confirmed` 表示能直接回到原文定位；`status=inferred` 表示是推断，必须同时在 `result.json` 的 `uncertainty` 说明。
- 图表编号、单位、数字必须与原文一致；引用他人结果要标明来源。

## 3. result.json 骨架

见 `SKILL.md` 的「输入与输出契约」。核心：`case_id`、`status`、`result`（含 `deck_file`、`preview_files`、`evidence_map_file`）、`evidence`、`uncertainty`、`change_log`。
