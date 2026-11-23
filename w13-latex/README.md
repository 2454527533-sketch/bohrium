# LaTeX 写作与编译 Skill（写作13）

## 用途
撰写并编译 LaTeX 学术稿件：源码结构与宏包、数学公式、表格与浮动体、引用与参考文献、模板适配、可重复构建。

## 组成
- `SKILL.md`：Skill 本体（六条判对标准、工作流、公式/表格/引用/模板/编译规则、自检清单）
- `templates/latex_checklist.md`：结构与编译检查清单
- `scripts/compile_check.py`：编译 + 日志检查（自动选 latexmk/pdflatex/xelatex，抓错误、未定义引用、overfull、缺失文件）
- `README.md`：本文档

## 脚本用法
```bash
python3 scripts/compile_check.py main.tex --passes 3          # 默认 latexmk→pdflatex→xelatex
python3 scripts/compile_check.py main.tex --engine xelatex    # 指定引擎
```

## 依赖
需要 TeX 发行版（latexmk/pdflatex/xelatex 至少其一）。脚本本身纯标准库。

## 限制与失败处理
无法消除的警告、字体缺失、宏包冲突，在 `result.json` 的 `uncertainty` 如实标注，不删改数据。
