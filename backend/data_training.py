from transformers import T5Tokenizer, T5ForConditionalGeneration, Trainer, TrainingArguments
import pandas as pd

# Load Data
df = pd.read_csv("user_data.csv")

# Prepare Data for Training
train_texts = df["input_text"].tolist()
train_labels = df["output_text"].tolist()

tokenizer = T5Tokenizer.from_pretrained("google/mt5-small")
train_encodings = tokenizer(train_texts, truncation=True, padding=True, max_length=128)
train_labels_encodings = tokenizer(train_labels, truncation=True, padding=True, max_length=128)

# Train Model
model = T5ForConditionalGeneration.from_pretrained("google/mt5-small")
training_args = TrainingArguments(output_dir="./results", num_train_epochs=3, per_device_train_batch_size=8)
trainer = Trainer(model=model, args=training_args, train_dataset=train_encodings)

trainer.train()
