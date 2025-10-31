# CADQuery Test

WorkFlow Fine-tune Qwen3:4b for generating CadQuery code from given dimensions and run it locally via Ollama.

# Overview

Goal:
Give dimensions like height/width/thickness → get CADQuery python code, for FreeCAD 

Use Qwen3-4B using a LoRA adapter, validate output by executing the generated code, and package for local inference using Ollama.

# Folder layout \n
CADQuery_test/ \n
├─ train.py                    # GPU training (Unsloth QLoRA) \n
├─ train_cpu.py                # CPU-only fallback training \n
├─ requirements.txt \n
├─ Modelfile                   # no extension; used by Ollama \n
├─ README.md \n
├─ .gitignore \n
│ \n
├─ data/ \n
│  ├─ cadquery_train.jsonl     # training data \n
│  └─ cadquery_val.jsonl       # validation data \n
│ \n 
├─ eval/ \n 
│  ├─ validator.py \n 
│  └─ generate_and_eval.py \n
│ \n 
├─ tools/ \n 
│  ├─ make_dataset.py          # seed/train/val generator \n
│  └─ merge_lora.py            # merge LoRA → full model \n
│ \n
├─ ckpt/                       # auto: checkpoints \n
├─ lora_cadquery/              # auto: LoRA adapter \n 
└─ qwen3_cadquery_merged/      # auto: merged model \n

# Setup (PowerShell on Windows)
1) Go to your project
cd (LOCAL_LOCATION)

2) Activate your virtual environment
.\.venv\Scripts\Activate.ps1

3) Install required packages
pip install -r .\requirements.txt

4) Optional: To grow your dataset from a few examples to ~200 training / 30 validation:
python .\tools\make_dataset.py


Outputs:

data\cadquery_train.jsonl
data\cadquery_val.jsonl

# Training
Option A — GPU (fastest, if you have NVIDIA GPU + CUDA)
python .\train.py

Option B — CPU fallback (shit performance)
python .\train_cpu.py

Produces .\lora_cadquery\. (Your LoRA adapter)

# Convert LoRA → Ollama Adapter

Once training is done, convert your PEFT LoRA folder (lora_cadquery\) into an Ollama adapter file (cadquery_qwen3_4b.lora.bin).

Use export_adapter.py at tools

Then reference that file in your Modelfile (see below).

    (ADAPTER ./cadquery_qwen3_4b.lora.bin)

Build and run in Ollama
ollama pull qwen3:4b
ollama create cadquery-qwen3-4b -f Modelfile

RUN:

ollama run cadquery-qwen3-4b -p "Write CadQuery code for a 100×120×6 plate with a centered thru-hole of 0.2*min(w,h)."

#Evaluation

Use the provided eval harness to check model output → run code → confirm solid exists.

python .\eval\generate_and_eval.py

You’ll get:

eval\outputs\candidate.py → model’s generated code

eval\outputs\result.json → pass/fail + diagnostics

# Utility Scripts
Script	Purpose
tools/make_dataset.py	Generates train/val JSONL examples.
tools/merge_lora.py	Merges LoRA → full model (qwen3_cadquery_merged/).
tools/export_adapter.py	Converts LoRA → Ollama adapter (.lora.bin).



# WORK IN PROGRESS!!!!!