# CADQuery_test/train.py
from unsloth import FastLanguageModel
from datasets import load_dataset
from trl import SFTTrainer, SFTConfig
from peft import LoraConfig

# !!! Set this to the exact HF checkpoint for Qwen3 4B Instruct on your system
# examples you might see on HF (names vary):
# BASE = "Qwen/Qwen3-4B-Instruct"
# If you truly cannot get Qwen3 4B Instruct, pick the closest Qwen3 4B instruct model available.
BASE = "Qwen/Qwen3-4B"

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = BASE,
    load_in_4bit = True,          # QLoRA (saves VRAM)
    max_seq_length = 3072,        # 4B: keep a bit shorter for stability/VRAM
)
tokenizer.pad_token = tokenizer.eos_token

# LoRA config – lighter for 4B; bump r to 32 if you have headroom
peft_config = LoraConfig(
    r=16, lora_alpha=16, lora_dropout=0.05, bias="none",
    task_type="CAUSAL_LM",
    target_modules=[
        "q_proj","k_proj","v_proj","o_proj",
        "gate_proj","up_proj","down_proj"
    ],
)

train = load_dataset("json", data_files={"train":"data/cadquery_train.jsonl"})["train"]
# (optional) add a val split for TRL SFTTrainer if you want metrics during training

trainer = SFTTrainer(
    model=model, tokenizer=tokenizer, peft_config=peft_config,
    train_dataset=train,
    args=SFTConfig(
        output_dir="ckpt",
        learning_rate=2e-5,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=16,
        num_train_epochs=2,
        bf16=True,                  # set to False if your GPU doesn't support bf16
        lr_scheduler_type="cosine",
        logging_steps=20,
        save_steps=500,
    ),
    max_seq_length=3072,
)
trainer.train()
trainer.model.save_pretrained("lora_cadquery")
tokenizer.save_pretrained("lora_cadquery")
print("Saved LoRA to ./lora_cadquery")
