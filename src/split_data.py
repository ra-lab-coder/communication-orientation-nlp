import os
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit

DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "deepsea_conversations_llm_v1.csv")
TRAIN_PATH = os.path.join(DATA_DIR, "train_llm_v1.csv") 
VAL_PATH = os.path.join(DATA_DIR, "val_llm_v1.csv") 
TEST_PATH = os.path.join(DATA_DIR, "test_llm_v1.csv")

def main():
    df = pd.read_csv(DATA_PATH)

    assert "text" in df.columns and "label" in df.columns
    
    # Support both scenario_id (LLM dataset) and template_id (template dataset)
    if "scenario_id" in df.columns:
        group_column = "scenario_id"
    elif "template_id" in df.columns:
        group_column = "template_id"
    else:
        raise ValueError("Either 'scenario_id' or 'template_id' column is required for group-based splitting")
    
    print(f"Using '{group_column}' for grouped splitting")

    # First split: train vs temp (val+test)
    gss1 = GroupShuffleSplit(n_splits=1, test_size=0.3, random_state=42)
    train_idx, temp_idx = next(gss1.split(df, groups=df[group_column]))
    train_df = df.iloc[train_idx].copy()
    temp_df = df.iloc[temp_idx].copy()

    # Second split: val vs test from temp
    gss2 = GroupShuffleSplit(n_splits=1, test_size=0.5, random_state=42)
    val_idx, test_idx = next(gss2.split(temp_df, groups=temp_df[group_column]))
    val_df = temp_df.iloc[val_idx].copy()
    test_df = temp_df.iloc[test_idx].copy()
    
    # Additional check: Ensure class balance is similar
    val_class_balance = val_df['label'].value_counts(normalize=True)
    test_class_balance = test_df['label'].value_counts(normalize=True)
    
    # If class balance differs significantly, warn
    if abs(val_class_balance.get(0, 0) - test_class_balance.get(0, 0)) > 0.15:
        print(f"  Warning: Class balance differs between val and test:")
        print(f"   Val: Class 0 = {val_class_balance.get(0, 0)*100:.1f}%, Class 1 = {val_class_balance.get(1, 0)*100:.1f}%")
        print(f"   Test: Class 0 = {test_class_balance.get(0, 0)*100:.1f}%, Class 1 = {test_class_balance.get(1, 0)*100:.1f}%")

    train_df.to_csv(TRAIN_PATH, index=False)
    val_df.to_csv(VAL_PATH, index=False)
    test_df.to_csv(TEST_PATH, index=False)

    # Get unique group IDs for each split
    train_group_ids = set(train_df[group_column].unique())
    val_group_ids = set(val_df[group_column].unique())
    test_group_ids = set(test_df[group_column].unique())

    # Print counts
    print(f"Train samples: {len(train_df)} → {TRAIN_PATH}")
    print(f"  Unique {group_column}s: {len(train_group_ids)}")
    print(f"Validation samples: {len(val_df)} → {VAL_PATH}")
    print(f"  Unique {group_column}s: {len(val_group_ids)}")
    print(f"Test samples: {len(test_df)} → {TEST_PATH}")
    print(f"  Unique {group_column}s: {len(test_group_ids)}")

    # Verify no overlap in group IDs
    assert train_group_ids.isdisjoint(val_group_ids), f"Train and Val have overlapping {group_column}s!"
    assert train_group_ids.isdisjoint(test_group_ids), f"Train and Test have overlapping {group_column}s!"
    assert val_group_ids.isdisjoint(test_group_ids), f"Val and Test have overlapping {group_column}s!"
    print(f"\n✓ Verified: No {group_column} overlap across splits")

if __name__ == "__main__":
    main()
