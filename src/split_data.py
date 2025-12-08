import os
import pandas as pd
from sklearn.model_selection import train_test_split

DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "deepsea_conversations.csv")
TRAIN_PATH = os.path.join(DATA_DIR, "train.csv") 
VAL_PATH = os.path.join(DATA_DIR, "val.csv") 
TEST_PATH = os.path.join(DATA_DIR, "test.csv")

def main():
    df = pd.read_csv(DATA_PATH)

    assert "text" in df.columns and "label" in df.columns

    # First split: train + temp
    train_df, temp_df = train_test_split(
        df,
        test_size=0.3,          # 70% train, 30% for val+test
        random_state=42,
        stratify=df["label"]
    )

    # Second split: validation + test
    val_df, test_df = train_test_split(
        temp_df,
        test_size=0.5,          # 15% val, 15% test
        random_state=42,
        stratify=temp_df["label"]
    )

    train_df.to_csv(TRAIN_PATH, index=False)
    val_df.to_csv(VAL_PATH, index=False)
    test_df.to_csv(TEST_PATH, index=False)

    print(f"Train samples: {len(train_df)} → {TRAIN_PATH}")
    print(f"Validation samples: {len(val_df)} → {VAL_PATH}")
    print(f"Test samples: {len(test_df)} → {TEST_PATH}")

if __name__ == "__main__":
    main()
