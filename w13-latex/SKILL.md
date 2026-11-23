---
name: latex-writer
description: >
  撰写并编译 LaTeX 学术稿件：组织源码结构与宏包、处理数学公式/表格/浮动体/引用、适配期刊会议
  模板，并跑编译检查脚本定位错误、未定义引用与 overfull，保证可重复构建。当任务要求
  "LaTeX 写作与编译/修编译错误/模板适配"时调用。
---

# LaTeX 写作与编译（完成产物，也保留来源）

## 目标与六条判对标准

产出**结构清晰、公式/表格/引用正确、模板合规、可重复编译**的 LaTeX 稿件。判对看六件事：

1. **源码结构与宏包**：主文件/子文件划分、导言区组织、宏包选择与加载顺序正确，不"加一个宏包坏另一处"。
2. **数学公式**：多行公式对齐、编号与引用、符号上下标、单位正体变量斜体、定理证明环境正确，公式含义与正文一致。
3. **表格与浮动体**：宽表跨页、列宽对齐、合并单元格、图表标题与位置约束、三线表，避免溢出裁切和靠缩放掩盖。
4. **引用与参考文献**：`\cite/\ref` 解析与编号、`.bib` 条目与正文对应、样式与排序、多遍编译收敛，无 undefined reference/citation。
5. **模板适配**：期刊/会议/学位模板的版式约束、必填项与文件结构合规。
6. **编译错误与可重复构建**：错误与关键警告被定位修复；编译轮次稳定；TeX 发行版、宏包、字体依赖写清，他人可复跑。

## 输入与输出契约

- 输入 `/input/case.json` 与 `task.md`；先确认目标模板（期刊/会议/学位）、TeX 发行版与编译命令。
- 输出 `/app/output/result.json` 与源码/PDF/日志：

```json
{
  "case_id": "",
  "status": "success | partial | unknown | refused",
  "result": {
    "main_file": "outputs/main.tex",
    "pdf_file": "outputs/main.pdf",
    "build_log": "outputs/build.log",
    "build_report": {"errors": 0, "undefined_refs": [], "overfull": 0}
  },
  "evidence": [{"formula": "编号", "ref": "正文引用位置"}],
  "uncertainty": ["未解决警告/字体缺失/宏包冲突项"],
  "change_log": []
}
```

## 工作流

1. **边界**：读模板、目标格式、TeX 发行版与编译命令；确认主文件/子文件/导言区结构。
2. **源码结构与宏包**：组织主文件与子文件、导言区、宏包加载顺序（先基础后功能，避免冲突宏包）。
3. **公式**：多行用 `align`/`gather`，编号 `\label`+`\eqref`；符号上下标、单位正体（`\mathrm`）、变量斜体；定理证明用 `amsthm`。
4. **表格与浮动体**：三线表用 `booktabs`；宽表用 `longtable`/`tabularx`；`\caption`+`\label`，位置用 `[htbp]`；不靠 `\resizebox` 缩放掩盖溢出。
5. **引用**：`\cite`/`\ref` 与 `.bib`/`\label` 对应；用 `natbib`/`biblatex` 控制样式；编译至编号收敛。
6. **模板适配**：按模板必填项（标题、作者、摘要、关键词、章节结构、页脚）迁入稿件，不覆盖模板版式。
7. **编译检查**：跑 `scripts/compile_check.py main.tex`（自动选 latexmk→pdflatex→xelatex），读 `.log` 抓错误、`undefined reference/citation`、`overfull`；逐条修复后重跑。
8. **落盘**：写源码、PDF、构建日志、`build_report` 与 `result.json`。

## 关键规则

- **宏包加载顺序**：`hyperref` 一般放最后；避免同时加载冲突宏包；每次只加必要宏包。
- **公式正确**：单位正体、变量斜体；多行对齐；编号与正文引用一致。
- **表格合规**：优先 `booktabs` 三线表；宽表/长表用对应环境；不靠缩放掩盖。
- **引用收敛**：多次编译直到 `LaTeX Warning: There were undefined references` 消失。
- **可重复构建**：写清发行版、宏包、字体、编译命令；他人可复跑出同一 PDF。
- **诚实**：无法消除的警告、字体缺失、宏包冲突写入 `uncertainty`；不删改数据。

## 输出自检清单

- [ ] 源码结构清晰，宏包无冲突、加载顺序正确。
- [ ] 公式/表格/浮动体/引用正确，编号收敛。
- [ ] 模板必填项齐全，版式合规。
- [ ] `compile_check.py` 报 errors=0、undefined_refs 为空。
- [ ] 可重复编译出 PDF；构建日志与发行版/宏包/字体依赖齐全。
- [ ] `uncertainty` 覆盖未解决警告与依赖。
