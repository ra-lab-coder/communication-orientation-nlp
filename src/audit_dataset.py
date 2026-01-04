"""
Dataset audit script for DeepSea Communication Orientation Auditor.

Analyzes the LLM-generated dataset to check:
- Class balance
- Difficulty balance
- Top TF-IDF tokens per class (to detect shortcut words)
"""

import os
import sys
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import argparse

DATA_DIR = "data"
DEFAULT_INPUT = os.path.join(DATA_DIR, "deepsea_conversations_llm_v1.csv")


def audit_dataset(csv_path: str):
    """
    Audit the dataset and print statistics.
    
    Args:
        csv_path: Path to the CSV file
    """
    if not os.path.exists(csv_path):
        print(f"❌ Error: File not found: {csv_path}")
        return 1
    
    print(f"Loading dataset from: {csv_path}\n")
    df = pd.read_csv(csv_path)
    
    print("=" * 60)
    print("DATASET OVERVIEW")
    print("=" * 60)
    print(f"Total samples: {len(df)}")
    print(f"Unique scenarios: {df['scenario_id'].nunique()}")
    print(f"Columns: {', '.join(df.columns.tolist())}\n")
    
    # Class balance
    print("=" * 60)
    print("CLASS BALANCE")
    print("=" * 60)
    class_counts = df['label'].value_counts().sort_index()
    class_props = df['label'].value_counts(normalize=True).sort_index()
    
    for label in sorted(df['label'].unique()):
        label_name = df[df['label'] == label]['label_name'].iloc[0] if 'label_name' in df.columns else f"label_{label}"
        count = class_counts[label]
        prop = class_props[label] * 100
        print(f"Label {label} ({label_name}): {count} samples ({prop:.1f}%)")
    
    # Check if balanced
    if len(class_props) == 2:
        imbalance = abs(class_props.iloc[0] - class_props.iloc[1])
        if imbalance < 0.05:
            print("✓ Classes are well balanced")
        else:
            print(f"⚠️  Class imbalance: {imbalance*100:.1f}% difference")
    print()
    
    # Difficulty balance
    if 'difficulty' in df.columns:
        print("=" * 60)
        print("DIFFICULTY DISTRIBUTION")
        print("=" * 60)
        difficulty_counts = df['difficulty'].value_counts()
        difficulty_props = df['difficulty'].value_counts(normalize=True)
        
        for diff in ['easy', 'medium', 'hard']:
            if diff in difficulty_counts.index:
                count = difficulty_counts[diff]
                prop = difficulty_props[diff] * 100
                print(f"{diff.capitalize()}: {count} samples ({prop:.1f}%)")
        print()
        
        # Difficulty by class
        print("=" * 60)
        print("DIFFICULTY BY CLASS")
        print("=" * 60)
        difficulty_by_class = pd.crosstab(df['label'], df['difficulty'], normalize='index') * 100
        print(difficulty_by_class.round(1))
        print()
    
    # Setting distribution
    if 'setting' in df.columns:
        print("=" * 60)
        print("SETTING DISTRIBUTION")
        print("=" * 60)
        setting_counts = df['setting'].value_counts()
        for setting, count in setting_counts.items():
            prop = (count / len(df)) * 100
            print(f"{setting}: {count} samples ({prop:.1f}%)")
        print()
    
    # TF-IDF analysis per class
    print("=" * 60)
    print("TOP 20 TF-IDF TOKENS BY CLASS")
    print("=" * 60)
    print("(Higher TF-IDF = more distinctive to that class)\n")
    
    for label in sorted(df['label'].unique()):
        label_name = df[df['label'] == label]['label_name'].iloc[0] if 'label_name' in df.columns else f"label_{label}"
        label_texts = df[df['label'] == label]['text'].tolist()
        other_texts = df[df['label'] != label]['text'].tolist()
        
        # Fit TF-IDF on all texts
        vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            lowercase=True,
            ngram_range=(1, 2),  # Include unigrams and bigrams
            min_df=2  # Word must appear in at least 2 documents
        )
        
        all_texts = label_texts + other_texts
        vectorizer.fit(all_texts)
        
        # Transform label texts
        label_vectors = vectorizer.transform(label_texts)
        
        # Calculate mean TF-IDF scores for this class
        mean_scores = label_vectors.mean(axis=0).A1
        
        # Get feature names
        feature_names = vectorizer.get_feature_names_out()
        
        # Get top tokens
        top_indices = mean_scores.argsort()[-20:][::-1]
        
        print(f"Label {label} ({label_name}):")
        print("-" * 40)
        for idx in top_indices:
            token = feature_names[idx]
            score = mean_scores[idx]
            print(f"  {token:30s} {score:.4f}")
        print()
    
    # Check for potential shortcut words (words that appear in one class but not the other)
    print("=" * 60)
    print("POTENTIAL SHORTCUT WORDS DETECTION")
    print("=" * 60)
    
    if len(df['label'].unique()) == 2:
        label_0 = df[df['label'] == 0]['text'].str.lower().str.cat(sep=' ')
        label_1 = df[df['label'] == 1]['text'].str.lower().str.cat(sep=' ')
        
        # Simple word frequency check
        words_0 = set(label_0.split())
        words_1 = set(label_1.split())
        
        # Words only in label 0
        only_0 = words_0 - words_1
        # Words only in label 1
        only_1 = words_1 - words_0
        
        # Filter out very short words and common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can'}
        
        only_0_filtered = [w for w in only_0 if len(w) > 3 and w not in stop_words]
        only_1_filtered = [w for w in only_1 if len(w) > 3 and w not in stop_words]
        
        if only_0_filtered:
            print(f"Words only in label 0 (top 10): {', '.join(sorted(only_0_filtered)[:10])}")
        if only_1_filtered:
            print(f"Words only in label 1 (top 10): {', '.join(sorted(only_1_filtered)[:10])}")
        
        if not only_0_filtered and not only_1_filtered:
            print("✓ No obvious shortcut words detected (good!)")
        print()
    
    print("=" * 60)
    print("AUDIT COMPLETE")
    print("=" * 60)
    
    return 0


def main():
    parser = argparse.ArgumentParser(description="Audit the LLM-generated dataset")
    parser.add_argument("--input", type=str, default=DEFAULT_INPUT,
                       help=f"Input CSV path (default: {DEFAULT_INPUT})")
    
    args = parser.parse_args()
    
    return audit_dataset(args.input)


if __name__ == "__main__":
    sys.exit(main())



