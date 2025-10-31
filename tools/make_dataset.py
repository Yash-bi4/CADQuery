# tools/make_dataset.py
import json
import random
from pathlib import Path
random.seed(42)

SYSTEM = "You output ONLY executable CadQuery Python. Use `import cadquery as cq`. Final object in variable `result`."
USER_TMPL = (
    "Plate: width={w} mm, height={h} mm, thickness={t} mm. "
    "Centered thru-hole dia=min(w,h)*0.2. "
    "Write make_part(w,h,t) and call it. Output ONLY code."
)
ASSISTANT_TMPL = """import cadquery as cq

def make_part(w,h,t):
    assert w>0 and h>0 and t>0
    hole = min(w,h)*0.2
    wp = (cq.Workplane('XY').rect(w, h).extrude(t)
          .faces('>Z').workplane(centerOption='CenterOfMass').hole(hole))
    return wp

result = make_part({w},{h},{t})
"""

def one_example(w,h,t):
    return {
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": USER_TMPL.format(w=w,h=h,t=t)},
            {"role": "assistant", "content": ASSISTANT_TMPL.format(w=w,h=h,t=t)},
        ]
    }

def gen_dims(n, w_range=(40, 250), h_range=(45, 180), t_range=(3, 20)):
    seen = set()
    out = []
    while len(out) < n:
        w = random.randrange(*w_range)
        h = random.randrange(*h_range)
        t = random.randrange(*t_range)
        # avoid duplicates and too tiny/degenerate combos
        if (w,h,t) in seen or min(w,h) < 40:
            continue
        seen.add((w,h,t))
        out.append((w,h,t))
    return out

def write_jsonl(path, items):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for ex in items:
            f.write(json.dumps(ex, ensure_ascii=False))
            f.write("\n")

def main():
    root = Path(".")
    data_dir = root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    # change these if you want different sizes
    n_train = 200
    n_val   = 30

    train_dims = gen_dims(n_train)
    val_dims   = gen_dims(n_val)

    train = [one_example(w,h,t) for (w,h,t) in train_dims]
    val   = [one_example(w,h,t) for (w,h,t) in val_dims]

    write_jsonl(data_dir / "cadquery_train.jsonl", train)
    write_jsonl(data_dir / "cadquery_val.jsonl", val)

    print(f"Wrote {len(train)} train and {len(val)} val examples into ./data")

if __name__ == "__main__":
    main()
