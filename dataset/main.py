from datasets import Dataset

# Load JSONL directly into a Dataset object
dataset_path = "/data/data/com.termux/files/home/project/agents/dataset/final.jsonl"
ds = Dataset.from_json(dataset_path)
