from datasets import load_dataset

# Dataset SD-198 di HF Hub
dataset = load_dataset("resyhgerwshshgdfghsdfgh/SD-198", split="train")

# Simpan secara lokal
dataset.save_to_disk("sd-198")

print("✅ SD‑198 berhasil didownload dan disimpan di folder 'sd-198'")
