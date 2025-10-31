# eval/generate_and_eval.py
import json
import subprocess
from pathlib import Path
from validator import validate_cadquery_code

MODEL = "cadquery-qwen3-4b"   # <-- the name you'll create in Ollama with your Modelfile/adapter
PROMPT = """Write a single Python file that:
- imports cadquery as cq
- defines make_part(w,h,t) in millimeters
- models a rectangular plate w×h×t with a centered thru-hole diameter = min(w,h)*0.2
- ends by assigning the solid to variable `result`
Output ONLY code.
Use: w=80, h=120, t=6.
"""

def run_ollama(model, prompt):
    # Call: ollama run <model> -p "<prompt>"
    completed = subprocess.run(
        ["ollama", "run", model],
        input=prompt.encode("utf-8"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.decode())
    return completed.stdout.decode()

def main():
    out_dir = Path("eval/outputs")
    out_dir.mkdir(parents=True, exist_ok=True)

    py_src = run_ollama(MODEL, PROMPT)
    (out_dir / "candidate.py").write_text(py_src, encoding="utf-8")

    ok, info = validate_cadquery_code(py_src)
    print("PASS" if ok else "FAIL", info)

    # Save a JSON record for later inspection
    (out_dir / "result.json").write_text(json.dumps({
        "ok": ok, "info": info, "code": py_src,
    }, indent=2), encoding="utf-8")

if __name__ == "__main__":
    main()
