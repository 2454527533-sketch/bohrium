# 玻尔高校挑战赛·地大分站赛 作品集

本仓库存放我在玻尔高校挑战赛（中国地质大学·北京分站赛）提交的 Skill 作品。每个子目录对应一道赛题，包含 `SKILL.md`（Skill 本体）、`scripts/`（可运行脚本）、`README.md`（使用说明）与示例/模板。

## 目录与赛题对照

| 子目录 | 赛题 | challenge_id |
|-|-|-|
| `r01-doc-parse` | 阅读01 文献文档解析 | product-arena-08-3027d350 |
| `r03-translate` | 阅读03 文献翻译 | product-arena-01-5a9928c1 |
| `r10-summary` | 阅读10 文献总结与结构化笔记 | product-arena-06-6d8cf72b |
| `r14-nanopub` | 阅读14 Nanopublication | product-arena-09-0e8befd4 |
| `r15-kg` | 阅读15 文献知识图谱构建 | product-arena-10-760d1a0b |
| `w02-polish` | 写作02 学术语言润色 | product-arena-02-7051d92d |
| `w04-refs` | 写作04 参考文献与引用管理 | product-arena-03-429cc14d |
| `w08-intro` | 写作08 引言与相关工作写作 | product-arena-04-4b82ad21 |
| `w09-methods` | 写作09 方法与实验章节写作 | product-arena-05-64faa4a2 |
| `w13-latex` | 写作13 LaTeX 写作与编译 | product-arena-07-865de7e4 |
| `ppt-paper2slides` | 论文转学术 PPT | ppt-c7b80f0d |

## 每个子目录的结构

```
<子目录>/
├── SKILL.md        # Skill 本体（YAML frontmatter: name/description）
├── README.md       # 调用步骤、输入输出、关键方法、限制与自查
├── scripts/        # 可运行脚本（纯标准库，无需第三方依赖）
├── examples/       # 最小调用示例（示意输出已标注）
└── templates/      # 结构化模板（部分题目）
```

## 说明

- 全部脚本使用 Python 标准库，仅少数依赖 `pdftotext`/`pdftoppm`/`tesseract` 等系统工具（见各 README）。
- 示例文件均标注为示意，不含正式案例答案。
- 每个 Skill 的输出契约遵循平台要求：`result.json` 含 `case_id`、主结果、证据/来源定位、运行状态与 `uncertainty`。
