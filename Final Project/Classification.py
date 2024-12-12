# -*- coding: utf-8 -*-
"""CSE_584_Final_project.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/18MIMltvdmIusqkuFmJxYcUJKt56nccTx
"""

!pip install datasets

!pip install evaluate

!pip install wandb

!wandb login

!pip install transformers

from datasets import Dataset, DatasetDict
import torch
import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer
import numpy as np
import evaluate
import matplotlib.pyplot as plt
import os
os.environ['CUDA_LAUNCH_BLOCKING'] = "1"  # Enable debugging

# Device setup
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Paths to datasets
train_path = 'train3.csv'
train_df = pd.read_csv(train_path, encoding='latin1')
val_path = 'val3.csv'
val_df = pd.read_csv(val_path, encoding='latin1')

# Sampling for debugging purposes
train_df = train_df.sample(frac=0.1, random_state=42)
val_df = val_df.sample(frac=0.1, random_state=42)

# Convert to Hugging Face dataset format
train_dataset = Dataset.from_pandas(train_df)
val_dataset = Dataset.from_pandas(val_df)

# Create a dataset dictionary
dataset_dict = DatasetDict({
    'train': train_dataset,
    'test': val_dataset
})

# Tokenizer setup
tokenizer = AutoTokenizer.from_pretrained("bert-base-cased")

def tokenize_function(examples):
    text_column_name = next(key for key in examples.keys() if 'text' in key)
    return tokenizer(examples[text_column_name], padding="max_length", truncation=True)

tokenized_datasets = dataset_dict.map(tokenize_function, batched=True)

small_train_dataset = tokenized_datasets["train"].shuffle(seed=42)
small_eval_dataset = tokenized_datasets["test"].shuffle(seed=42)

# Metric for evaluation
metric = evaluate.load("accuracy")

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    return metric.compute(predictions=predictions, references=labels)

# Model setup
model = AutoModelForSequenceClassification.from_pretrained("bert-base-cased", num_labels=15)
model.to(device)

# Freeze the encoder layers
for param in model.bert.encoder.parameters():
    param.requires_grad = False

# Print layer statuses
print("Model Layers and Trainable Status:")
for name, param in model.named_parameters():
    trainable = param.requires_grad
    print(f"{name}: {'Trainable' if trainable else 'Frozen'}")

# Training arguments
training_args = TrainingArguments(
    output_dir="test_trainer",
    evaluation_strategy="epoch",
    learning_rate=2e-3,
    logging_dir="log",
    logging_strategy="steps",
    logging_steps=1,
    per_device_train_batch_size=64,
    per_device_eval_batch_size=64,
    num_train_epochs=20,
    weight_decay=0.01,
    load_best_model_at_end=True,
    save_strategy="epoch",
    metric_for_best_model="accuracy",
)

# Trainer setup
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=small_train_dataset,
    eval_dataset=small_eval_dataset,
    compute_metrics=compute_metrics,
)

# Train the model
train_history = trainer.train()

# Evaluate model after each epoch
validation_results = trainer.evaluate()
print("Evaluation Results:", validation_results)

# Save the model and tokenizer
model_save_path = "model"
tokenizer_save_path = "tokenizer"
model.save_pretrained(model_save_path)
tokenizer.save_pretrained(tokenizer_save_path)

# Extract training and validation metrics from logs
train_losses = []
val_losses = []
accuracies = []

epoch_logs = trainer.state.log_history
for log in epoch_logs:
    if 'loss' in log:
        train_losses.append(log['loss'])
    if 'eval_loss' in log:
        val_losses.append(log['eval_loss'])
    if 'eval_accuracy' in log:
        accuracies.append(log['eval_accuracy'])

# Plot training loss
plt.figure(figsize=(10, 6))
plt.grid(True)
plt.plot(range(1, len(train_losses) + 1), train_losses, label='Training Loss', color='blue')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.title('Training Loss')
plt.legend()
plt.savefig('training_loss_plot.pdf')
plt.show()

# Plot validation loss
if val_losses:
    plt.figure(figsize=(10, 6))
    plt.grid(True)
    plt.plot(range(1, len(val_losses) + 1), val_losses, label='Validation Loss', color='red')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.title('Validation Loss')
    plt.legend()
    plt.savefig('validation_loss_plot.pdf')
    plt.show()
else:
    print("No validation loss logged.")

# Plot accuracy
if accuracies:
    plt.figure(figsize=(10, 6))
    plt.grid(True)
    plt.plot(range(1, len(accuracies) + 1), accuracies, label='Validation Accuracy', color='orange')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.title('Validation Accuracy')
    plt.legend()
    plt.savefig('accuracy_plot.pdf')
    plt.show()
else:
    print("No accuracy data logged.")

import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import numpy as np
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt
from scipy.stats import probplot

# Define the paths where the model and tokenizer are saved
model_save_path = "model"
tokenizer_save_path = "tokenizer"

# Check if GPU is available and select the device
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Load the saved model and tokenizer
model = AutoModelForSequenceClassification.from_pretrained(model_save_path)
model.to(device)  # Move model to GPU if available
tokenizer = AutoTokenizer.from_pretrained(tokenizer_save_path)

# Load the test dataset
test_df = pd.read_csv('test3.csv')

# Define a function to get predictions
def predict(sentence):
    inputs = tokenizer(sentence, return_tensors="pt", padding=True, truncation=True).to(device)  # Move inputs to GPU if available
    with torch.no_grad():
        outputs = model(**inputs)
    logits = outputs.logits
    prediction = torch.argmax(logits, dim=-1)
    return prediction.item()

# Initialize lists to store true and predicted labels
true_labels = []
predicted_labels = []

# Iterate over each row in the test dataset
for index, row in test_df.iterrows():
    sentence = row['text']
    true_label = row['label']
    # Get the predicted label
    predicted_label = predict(sentence)
    # Append the true and predicted labels to the lists
    true_labels.append(true_label)
    predicted_labels.append(predicted_label)

# Convert predicted labels to a NumPy array and save it
predicted_labels_np = np.array(predicted_labels)

# Calculate metrics
accuracy = accuracy_score(true_labels, predicted_labels)
f1 = f1_score(true_labels, predicted_labels, average='weighted')
precision = precision_score(true_labels, predicted_labels, average='weighted')
recall = recall_score(true_labels, predicted_labels, average='weighted')

print(f"Test Accuracy: {accuracy:.4f}")
print(f"Test F1 Score: {f1:.4f}")
print(f"Test Precision: {precision:.4f}")
print(f"Test Recall: {recall:.4f}")

# Define the number of classes
num_classes = 15
class_labels = [
    'Economics',
    'Physics',
    'Technology',
    'Biology',
    'Mathematics',
    'Astronomy',
    'Chemistry',
    'Psychology',
    'Medicine',
    'Ecology',
    'Environment',
    'Geology',
    'Philosophy of science',
    'Miscellaneous',
    'Engineering'
]

# Initialize a dictionary to store correct predictions and total counts per class
correct_per_class = {i: 0 for i in range(num_classes)}
total_per_class = {i: 0 for i in range(num_classes)}

# Iterate over both true and predicted labels
for true, pred in zip(true_labels, predicted_labels):
    total_per_class[true] += 1  # Count total instances for the true class
    if true == pred:
        correct_per_class[true] += 1  # Count correct predictions for the true class

# Calculate accuracy for each class (multiply by 100 to get percentage)
accuracy_per_class = {i: (correct_per_class[i] / total_per_class[i]) * 100 if total_per_class[i] > 0 else 0 for i in range(num_classes)}

# Plotting accuracy per class
accuracies = [accuracy_per_class[i] for i in range(num_classes)]

plt.figure(figsize=(15, 6))
bars = plt.bar(class_labels, accuracies, color='#1f77b4')  # Darker blue color (hex code)
plt.xlabel('Class Label')
plt.ylabel('Accuracy (%)')
plt.title('Accuracy for Each Class Label')
plt.ylim([0, 105])  # Accuracy as a percentage from 0 to 100

# Add the accuracy value on top of each bar
for bar, accuracy in zip(bars, accuracies):
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width() / 2, yval + 1, f'{accuracy:.2f}%', ha='center', va='bottom')

plt.savefig('accuracy.pdf')
plt.show()

# Q-Q plot for class accuracies
plt.figure(figsize=(8, 8))
probplot(accuracies, dist="norm", plot=plt)
plt.title("Q-Q Plot of Class Accuracies")
plt.xlabel("Theoretical Quantiles")
plt.ylabel("Sample Quantiles")
plt.grid(True)
plt.savefig('qq_plot.pdf')
plt.show()

# Confusion Matrix
cm = confusion_matrix(true_labels, predicted_labels, labels=range(num_classes))
plt.figure(figsize=(10, 10))
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=class_labels)
disp.plot(cmap=plt.cm.Blues, xticks_rotation='vertical')
plt.title('Confusion Matrix')
plt.savefig('confusion_matrix.pdf')
plt.show()