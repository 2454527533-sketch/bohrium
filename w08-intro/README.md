# 引言与相关工作写作 Skill（写作08）

## 用途
撰写论文引言与相关工作：具体背景、相关工作分组对比、空白推导、可核对贡献、引用覆盖检查。

## 组成
- `SKILL.md`：Skill 本体（五条判对标准、工作流、同维比较/空白推导/贡献-证据/引用覆盖规则、自检清单）
- `templates/intro_outline.md`：结构化引言模板（背景/对比表/空白/贡献/引用覆盖）
- `scripts/check_intro.py`：一致性检查（孤引用、未引用文献、贡献缺证据定位）
- `README.md`：本文档

## 脚本用法
```bash
python3 scripts/check_intro.py intro.md [report.json]
```

## 依赖
纯标准库，无第三方依赖。

## 限制与失败处理
论断与引用不对应、证据不足、无法确认是否首做，在 `result.json` 的 `uncertainty` 如实标注，不夸大贡献。
