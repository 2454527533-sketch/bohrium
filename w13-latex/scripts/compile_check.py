#!/usr/bin/env python3
r"""LaTeX 编译与日志检查：自动选引擎编译，抓取错误、未定义引用与 overfull。

用法:
    python3 compile_check.py main.tex [--passes 3] [--engine latexmk|pdflatex|xelatex]

流程:
  1. 选引擎（默认 latexmk → pdflatex → xelatex，取第一个可用的）
  2. 编译指定轮数（默认 3，让引用/交叉引用收敛）
  3. 解析 .log：
     - 错误行（! ...）
     - LaTeX Warning: Reference/Citation ... undefined（未定义引用）
     - Overfull \hbox/\vbox（溢出）
     - 缺失文件 / 未知宏包
输出 JSON 报告；无 LaTeX 引擎时返回可用引擎列表提示。
"""
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path


def find_engine(preferred):
    if preferred and preferred != "auto":
        return preferred if shutil.which(preferred) else None
    for e in ("latexmk", "pdflatex", "xelatex", "lualatex"):
        if shutil.which(e):
            return e
    return None


def parse_log(log):
    errors = []
    undefined = []
    overfull = []
    missing = []
    for ln in log.splitlines():
        if ln.startswith("!"):
            errors.append(ln)
        m = re.search(r"LaTeX Warning: (Reference|Citation) [`\"]([^'\"`]+)", ln)
        if m:
            undefined.append(f"{m.group(1)} {m.group(2)}")
        if "Overfull" in ln and ("\\hbox" in ln or "\\vbox" in ln):
            overfull.append(ln.strip())
        mm = re.search(r"(No file |File `[^']+' not found|LaTeX Error: File `)", ln)
        if mm:
            missing.append(ln.strip())
    return {
        "errors": errors,
        "undefined_refs": sorted(set(undefined)),
        "overfull": overfull,
        "missing": missing,
    }


def main():
    args = sys.argv[1:]
    if not args:
        print("usage: compile_check.py main.tex [--passes N] [--engine E]", file=sys.stderr)
        sys.exit(2)
    main_tex = Path(args[0]).resolve()
    passes = 3
    engine = "auto"
    if "--passes" in args:
        passes = int(args[args.index("--passes") + 1])
    if "--engine" in args:
        engine = args[args.index("--engine") + 1]
    eng = find_engine(engine)
    if not eng:
        print(json.dumps({"ok": False, "reason": "no latex engine found",
                          "available": [e for e in ("latexmk", "pdflatex", "xelatex", "lualatex") if shutil.which(e)],
                          "hint": "install texlive (latexmk/pdflatex/xelatex)"}, ensure_ascii=False, indent=2))
        sys.exit(1)
    workdir = main_tex.parent
    cmds = {
        "latexmk": ["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error", main_tex.name],
        "pdflatex": ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", main_tex.name],
        "xelatex": ["xelatex", "-interaction=nonstopmode", "-halt-on-error", main_tex.name],
        "lualatex": ["lualatex", "-interaction=nonstopmode", "-halt-on-error", main_tex.name],
    }
    last_log = ""
    for i in range(passes):
        try:
            r = subprocess.run(cmds[eng], cwd=workdir, capture_output=True, text=True, timeout=300)
        except Exception as e:
            print(json.dumps({"ok": False, "engine": eng, "reason": str(e)}, ensure_ascii=False, indent=2))
            sys.exit(1)
    log_path = main_tex.with_suffix(".log")
    if log_path.exists():
        last_log = log_path.read_text(encoding="utf-8", errors="replace")
    report = parse_log(last_log)
    pdf_ok = main_tex.with_suffix(".pdf").exists()
    report.update({
        "ok": pdf_ok and not report["errors"] and not report["undefined_refs"] and not report["missing"],
        "engine": eng,
        "passes": passes,
        "pdf_created": pdf_ok,
        "log_path": str(log_path),
    })
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
