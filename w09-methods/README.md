# 方法与实验章节写作 Skill（写作09）

## 用途
把零散实验记录写成方法与实验章节：有序可执行步骤、训练/验证/测试设置、参数表、数据集表、基线对照、复现清单与限制。

## 组成
- `SKILL.md`：Skill 本体（六条判对标准、工作流、六方向规则、自检清单）
- `templates/methods_outline.md`：方法章节结构化模板
- `scripts/check_methods.py`：完整性检查（步骤/参数/数据集/基线的必填字段 + 复现项覆盖）
- `README.md`：本文档

## 脚本用法
```bash
python3 scripts/check_methods.py methods.json [report.json]
```

## 依赖
纯标准库，无第三方依赖。

## 限制与失败处理
来源缺失、版本含混、无法复现的步骤，在 `result.json` 的 `uncertainty` 如实标注，不新增材料外参数。
