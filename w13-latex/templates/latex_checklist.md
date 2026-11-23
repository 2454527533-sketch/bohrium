# LaTeX 稿件结构与编译检查清单（供 Agent 填写，非正式案例）

## 1. 结构

- 主文件：`main.tex`
- 子文件（若分文件）：`sections/`、`figures/`、`references.bib`
- 导言区：`\documentclass`、宏包、`\title/\author`、正文起始

## 2. 宏包清单与加载顺序

| 宏包 | 用途 | 加载顺序注意 |
|-|-|-|
| amsmath/amssymb | 数学 | 基础宏包 |
| booktabs | 三线表 | |
| graphicx | 插图 | |
| hyperref | 超链接/书签 | 最后加载 |

## 3. 公式/表格/引用检查

- 多行公式：`align`/`gather` + `\label`+`\eqref`
- 单位正体（`\mathrm`）、变量斜体
- 三线表：`booktabs`；宽表：`tabularx`/`longtable`；不靠 `\resizebox` 缩放
- `\cite`/`\ref` 与 `.bib`/`\label` 一一对应

## 4. 模板必填项

- 标题 / 作者 / 摘要 / 关键词 / 章节结构 / 页脚（按模板要求）

## 5. 编译与依赖（可重复构建）

- 发行版 / 宏包 / 字体：
- 编译命令：`latexmk -pdf main.tex`（或 pdflatex/xelatex）
- 运行：`python3 scripts/compile_check.py main.tex --passes 3`
- 要求：`errors=[]`、`undefined_refs=[]`、`pdf_created=true`
