from datasets import load_dataset

# SD-198 Dataset on HF Hub
dataset = load_dataset("resyhgerwshshgdfghsdfgh/SD-198", split="train")

# Save locally
dataset.save_to_disk("sd-198")

print(""✅ SD‑198 successfully downloaded and saved in 'sd-198' folder")
