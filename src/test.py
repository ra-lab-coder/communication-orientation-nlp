import os
import pandas as pd
from sklearn.metrics import classification_report
import joblib

DATA_DIR = "data"
MODEL_DIR = "model"
TEST_PATH = os.path.join(DATA_DIR, "test.csv")
MODEL_PATH = os.path.join(MODEL_DIR, "deepsea_model_v1.pkl")

def load_test():
    test_df = pd.read_csv(TEST_PATH)
    return test_df

def main():
    test_df = load_test()
    model = joblib.load(MODEL_PATH)

    X_test = test_df["text"].astype(str)
    y_test = test_df["label"].astype(int)

    y_pred = model.predict(X_test)

    print("\nTest performance:")
    print(classification_report(y_test, y_pred, digits=3))

if __name__ == "__main__":
    main()
