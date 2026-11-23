#!/usr/bin/env python3
"""方法章节完整性检查：参数表/数据集表/复现清单/步骤的必填字段与复现项覆盖。

用法:
    python3 check_methods.py methods.json [report.json]

methods.json 结构见 SKILL.md 的 result 字段（steps/param_table/dataset_table/baselines/reproducibility_checklist）。
纯标准库。检查结果为提示，供 Agent 补齐，不强制判定。
"""
import json
import sys
from pathlib import Path

PARAM_REQ = ["name", "value", "unit", "object", "source"]
DATASET_REQ = ["name", "version", "size", "preprocessing", "split", "use"]
STEP_REQ = ["step", "input", "operation", "output", "condition"]
BASELINE_REQ = ["name", "version", "budget", "metrics", "statistical_test"]
REPRO_KEYWORDS = ["代码", "环境", "命令", "种子", "数据"]


def missing_fields(items, required):
    out = []
    for i, it in enumerate(items):
        for k in required:
            v = str(it.get(k, "") or "").strip()
            if not v:
                out.append({"row": i + 1, "field": k})
    return out


def main():
    if len(sys.argv) < 2:
        print("usage: check_methods.py methods.json [report.json]", file=sys.stderr)
        sys.exit(2)
    data = json.load(open(sys.argv[1], encoding="utf-8"))
    res = data.get("result", data)
    steps = res.get("steps", [])
    params = res.get("param_table", [])
    datasets = res.get("dataset_table", [])
    baselines = res.get("baselines", [])
    repro = res.get("reproducibility_checklist", [])

    repro_text = " ".join(str(x) for x in repro)
    repro_missing = [k for k in REPRO_KEYWORDS if k not in repro_text]

    report = {
        "ok": False,
        "steps_missing_fields": missing_fields(steps, STEP_REQ),
        "params_missing_fields": missing_fields(params, PARAM_REQ),
        "datasets_missing_fields": missing_fields(datasets, DATASET_REQ),
        "baselines_missing_fields": missing_fields(baselines, BASELINE_REQ),
        "reproducibility_missing_keywords": repro_missing,
    }
    report["ok"] = not any([
        report["steps_missing_fields"], report["params_missing_fields"],
        report["datasets_missing_fields"], report["baselines_missing_fields"],
        repro_missing,
    ])
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if len(sys.argv) > 2:
        Path(sys.argv[2]).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
