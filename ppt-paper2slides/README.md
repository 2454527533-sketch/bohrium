# 论文转学术 PPT Skill（论文转学术PPT 赛题）

## 用途

把一篇科研论文组织成**可编辑、可讲解、证据可回溯**的学术 PPT：从论文提取主线 → 设计页级主张 → 在给定模板中生成可编辑演示文件与讲稿备注 → 保留页级证据映射与真实渲染预览。不负责科研绘图美化或学术写作润色本身。

## 组成

| 文件 | 说明 |
|-|-|
| `SKILL.md` | Skill 本体：三条判对标准、六步工作流、模板约束、备注/证据/诚实规则、自检清单 |
| `scripts/build_pptx.py` | 从 `slide_plan` JSON 生成可编辑 PPTX，复用模板 master/layout，写入讲稿备注 |
| `templates/outline_schema.md` | `slide_plan` / `evidence_map` / `result.json` 的字段约定 |
| `examples/example_outline.json` | 最小调用示例（**示意，非正式案例答案**） |
| `README.md` | 本文档 |

## 依赖

- `python-pptx`（生成可编辑 PPTX）；缺库时报错并提示安装。
- 模板（题面/`case.json` 提供）复用其母版与版式；无模板时用 python-pptx 默认 16:9。
- PDF/PNG 导出用平台 `office-renderer`（LibreOffice headless）；字体缺失用 `font-discovery` 找替代。

## 调用方式（示意）

```bash
# 1) 从论文提取主线、图，产出 slide_plan 与 evidence_map（Agent 完成，图用 pdf-render-tool 导出）
# 2) 生成可编辑 PPTX（--template 指向题面提供的模板）
python3 scripts/build_pptx.py outline.json outputs/slides.pptx --template=模板.pptx
# 3) 导出渲染预览
libreoffice --headless --convert-to pdf --outdir outputs outputs/slides.pptx   # 或平台 office-renderer
```

`outline.json` 与 `evidence_map.json` 的字段见 `templates/outline_schema.md`；最小示例见 `examples/example_outline.json`（示意输出，不冒充正式案例结果）。

## 限制与失败处理

- 模板占位符不足、长标题、多图并列、大表格：按 `SKILL.md`「模板约束与版面适配」处置，必要时拆分页，不靠缩小字号硬塞。
- 图无法提取、公式为图片、PDF 加密、字体缺失、页数超限：如实标注到 `result.json` 的 `uncertainty`，说明可人工接管位置，不补造。
- `status` 用 `partial/unknown/refused` 时要说明原因；`evidence` 里 `inferred` 项必须同时出现在 `uncertainty`。

## 自查方法（提交前）

1. 主线是否与论文贡献一致，页序是否可讲。
2. 每页主张能否回到论文页码/章节/图表（`evidence_map.json` 齐全）。
3. `slides.pptx` 可打开、可逐页编辑；PDF/PNG 预览无溢出、字体不崩坏、编号不串位。
4. 备注与页面互补不重复；版本记录（模板、字体、软件版本、复跑命令）齐全。
