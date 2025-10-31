from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

BASE = "Qwen/Qwen3-4B-Instruct"
ADAPTER_DIR = "lora_cadquery"
OUT_PATH = "cadquery_qwen3_4b.lora.bin"

model = AutoModelForCausalLM.from_pretrained(BASE)
model = PeftModel.from_pretrained(model, ADAPTER_DIR)
model.save_pretrained(".", safe_serialization=True, adapter_name="cadquery_qwen3_4b")
print("Adapter exported to:", OUT_PATH)
