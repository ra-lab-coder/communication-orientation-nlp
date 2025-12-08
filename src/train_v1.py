import os
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
import joblib

DATA_DIR = "data"
MODEL_DIR = "model"
TRAIN_PATH = os.path.join(DATA_DIR, "train.csv")
VAL_PATH = os.path.join(DATA_DIR, "val.csv")
MODEL_PATH = os.path.join(MODEL_DIR, "deepsea_model_v1.pkl")

def load_train_val():
    train_df = pd.read_csv(TRAIN_PATH)
    val_df = pd.read_csv(VAL_PATH)
    return train_df, val_df

def build_pipeline():
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 2),
            min_df=2,
            max_features=5000,
            sublinear_tf=True
        )),
        ("clf", LogisticRegression(
            max_iter=1000,
            class_weight="balanced"
        ))
    ])
    return pipeline

def main():
    train_df, val_df = load_train_val()

    X_train = train_df["text"].astype(str)
    y_train = train_df["label"].astype(int)

    X_val = val_df["text"].astype(str)
    y_val = val_df["label"].astype(int)

    model = build_pipeline()
    model.fit(X_train, y_train)

    print("\nValidation performance:")
    y_val_pred = model.predict(X_val)
    print(classification_report(y_val, y_val_pred, digits=3))

    joblib.dump(model, MODEL_PATH)
    print(f"\nModel saved → {MODEL_PATH}")

if __name__ == "__main__":
    main()
