CADQuery_test

End-to-end workflow to fine-tune Qwen3:4b for generating CadQuery code from given dimensions and run it locally via Ollama.

🚀 Overview

Goal:
Feed in simple part specs like height/width/thickness → get back executable CadQuery Python code that builds a 3D solid.

The project fine-tunes Qwen3-4B with a LoRA adapter, validates its output by executing the generated code, and packages the result for local inference using Ollama.

🧱 Folder layout
CADQuery_test/
├─ train.py                    # GPU training (Unsloth QLoRA)
├─ train_cpu.py                # CPU-only fallback training
├─ requirements.txt
├─ Modelfile                   # no extension; used by Ollama
├─ README.md
├─ .gitignore
│
├─ data/
│  ├─ cadquery_train.jsonl     # training data
│  └─ cadquery_val.jsonl       # validation data
│
├─ eval/
│  ├─ validator.py
│  └─ generate_and_eval.py
│
├─ tools/
│  ├─ make_dataset.py          # seed/train/val generator
│  └─ merge_lora.py            # merge LoRA → full model
│
├─ ckpt/                       # auto: checkpoints
├─ lora_cadquery/              # auto: LoRA adapter
└─ qwen3_cadquery_merged/      # auto: merged model

⚙️ Setup (PowerShell on Windows)
# 1) Go to your project
cd C:\Users\yash1\Downloads\CADQuery_test

# 2) Activate your venv
.\.venv\Scripts\Activate.ps1

# 3) Install requirements
pip install -r .\requirements.txt

📚 Dataset

To grow your dataset from a few examples to ~200 training / 30 validation:

python .\tools\make_dataset.py


Outputs:

data\cadquery_train.jsonl
data\cadquery_val.jsonl

🧠 Training
Option A — GPU (fastest, if you have NVIDIA GPU + CUDA)
python .\train.py


Output → .\lora_cadquery\ (your trained LoRA adapter)

Option B — CPU fallback (no GPU required, slower)
python .\train_cpu.py


Also produces .\lora_cadquery\.

⚠️ CPU training on a 4B model can take hours — consider doing it on RunPod/Vast/Colab, then copy the resulting lora_cadquery\ folder back here.

🔄 Convert LoRA → Ollama Adapter

Once training is done, convert your PEFT LoRA folder (lora_cadquery\) into an Ollama adapter file (cadquery_qwen3_4b.lora.bin).
If you’re on Windows and using peft + transformers, the adapter file is tiny (~50-150 MB).

Example Python snippet (save as tools\export_adapter.py):

from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

BASE = "Qwen/Qwen3-4B-Instruct"
ADAPTER_DIR = "lora_cadquery"
OUT_PATH = "cadquery_qwen3_4b.lora.bin"

model = AutoModelForCausalLM.from_pretrained(BASE)
model = PeftModel.from_pretrained(model, ADAPTER_DIR)
model.save_pretrained(".", safe_serialization=True, adapter_name="cadquery_qwen3_4b")
print("Adapter exported to:", OUT_PATH)


Then reference that file in your Modelfile (see below).

🧩 Modelfile (no extension)

File: CADQuery_test\Modelfile

FROM qwen3:4b

# If you don't have the adapter yet, comment out this line
ADAPTER ./cadquery_qwen3_4b.lora.bin

PARAMETER temperature 0.1
PARAMETER top_p 0.9

SYSTEM You output ONLY valid CadQuery Python. Use `import cadquery as cq`. Define `make_part(...)`. End by assigning the solid to variable `result`.

TEMPLATE {{ .Prompt }}

Build and run in Ollama
ollama pull qwen3:4b
ollama create cadquery-qwen3-4b -f Modelfile


Quick smoke test:

ollama run cadquery-qwen3-4b -p "Write CadQuery code for a 100×120×6 plate with a centered thru-hole of 0.2*min(w,h)."

🧪 Evaluate

Use the provided eval harness to check model output → run code → confirm solid exists.

python .\eval\generate_and_eval.py


You’ll get:

eval\outputs\candidate.py → model’s generated code

eval\outputs\result.json → pass/fail + diagnostics

🧰 Utility Scripts
Script	Purpose
tools/make_dataset.py	Generates train/val JSONL examples.
tools/merge_lora.py	Merges LoRA → full model (qwen3_cadquery_merged/).
tools/export_adapter.py	Converts LoRA → Ollama adapter (.lora.bin).
🪶 Low-disk tips

Move cache to another drive (USB/external):

setx HF_HOME "D:\hf-home"
setx TRANSFORMERS_CACHE "D:\hf-cache"


Add this to train.py:

cache_dir="D:/hf-cache"


Disable checkpoint saves in SFTConfig (only final LoRA):

save_strategy="no"


Delete after training:

Remove-Item -Recurse -Force .\ckpt


LoRA adapter is small (20–150 MB). You can train in the cloud, copy just that back.

🧩 Common issues

❌ “Modelfile doesn’t exist”
→ Must be named exactly Modelfile (capital M, no extension).
Run:

ollama create cadquery-qwen3-4b -f C:\Users\yash1\Downloads\CADQuery_test\Modelfile


❌ “Unsloth cannot find any torch accelerator”
→ You don’t have a GPU. Use train_cpu.py instead.

❌ “Model chats instead of giving code”
→ Keep the strict SYSTEM prompt and run the validator. It enforces “code-only” responses.

✅ When you’ve succeeded

lora_cadquery\ exists and contains adapter weights.

ollama create builds successfully from your Modelfile.

python .\eval\generate_and_eval.py prints:

PASS {'has_import': True, 'has_result': True, 'is_workplane': True}


eval\outputs\candidate.py contains valid CadQuery code.
