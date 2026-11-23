# 参考文献与引用管理 Skill（写作04）

## 用途
管理学术稿件的引用与参考文献：定位/插入引用、按首现顺序重排编号并同步交叉引用、去重归并、格式转换（BibTeX→GB/T 7714-2015/APA）、DOI/检索/原文核验。

## 组成
- `SKILL.md`：Skill 本体（五条判对标准、工作流、编号/去重/格式/核验规则、自检清单）
- `scripts/references.py`：辅助脚本（`dedup` / `renumber` / `convert`，纯标准库）
- `README.md`：本文档

## 脚本用法
```bash
python3 scripts/references.py dedup refs.bib refs.dedup.bib          # 按 DOI/题名去重
python3 scripts/references.py renumber manuscript.md manuscript.md   # 正文[n]按首现顺序重排
python3 scripts/references.py convert refs.bib --style gbt7714 refs.txt  # 或 --style apa
```

## 依赖
纯标准库（无第三方依赖）。BibTeX 解析为启发式，复杂嵌套字段需人工复核（见 SKILL.md 工作流第 7 步）。

## 限制与失败处理
编造条目、元数据错配、DOI 无法解析、证据不足的论断，在 `result.json` 的 `uncertainty` 中如实标注，不补造事实或文献。
