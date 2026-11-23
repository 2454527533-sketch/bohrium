# 阅读10｜文献总结与结构化笔记 Skill（paper-structured-notes）

按原文结构做章节总结、统一字段论文卡片、可检索知识点，每条笔记回指原文位置。

## 组成

- `SKILL.md`：Skill 本体（四条判对标准、工作流、骨架/卡片/知识点/来源规则、自检清单）
- `scripts/notes_builder.py`：辅助脚本（章节骨架提取、笔记校验）
- `examples/example_usage.md`：最小调用示例（示意输出已标注）
- `README.md`：本文档

## 脚本用法

```bash
python3 scripts/notes_builder.py outline source.md outline.json   # 提取章节层级骨架
python3 scripts/notes_builder.py check   notes.json report.json   # 校验卡片字段/来源锚点/去重冲突
```

`check` 输出 `issues`：
- `card_missing_fields`：论文卡片缺字段
- `kps_missing_fields` / `kps_missing_anchor`：知识点缺字段或缺来源定位
- `kps_duplicates` / `kps_conflicts`：重复条目 / 同术语不同定义（需人工确认）

## 关键方法

1. 先按原文章节建骨架，再做章节总结（目的/方法/结果/结论），不套通用摘要模板。
2. 论文卡片统一字段，使多篇论文可并排比较。
3. 知识点拆成可检索条目，脚本检查来源锚点、去重、矛盾。

## 依赖

Python 标准库，无第三方依赖。

## 限制与失败处理

机器可判定字段与需人工确认字段分开标注；缺失字段、矛盾条目、证据不足写入 `result.json` 的 `uncertainty`，不补造。
