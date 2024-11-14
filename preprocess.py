import pandas as pd
from sklearn.model_selection import train_test_split
import os

df = pd.read_csv('sd-198/train.csv')
df.columns = df.columns.str.strip()

train_df = pd.DataFrame()
valid_df = pd.DataFrame()

for label in df['label'].unique():
    class_df = df[df['label'] == label]
    class_train, class_valid = train_test_split(class_df, test_size=0.2, stratify=class_df['label'])
    train_df = pd.concat([train_df, class_train])
    valid_df = pd.concat([valid_df, class_valid])

print(f"Training set size: {len(train_df)}")
print(f"Validation set size: {len(valid_df)}")

train_df.to_csv('sd-198/train_split.csv', index=False)
valid_df.to_csv('sd-198/valid_split.csv', index=False)
