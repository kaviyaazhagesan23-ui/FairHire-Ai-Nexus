from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_score,
    recall_score,
    f1_score,
)


# ============================================================
# PATHS
# ============================================================

TRAIN_PATH = Path("../dataset/processed/splits_v2/train.csv")
VAL_PATH = Path("../dataset/processed/splits_v2/validation.csv")


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("FAIRHIRE AI - V2 BASELINE MODEL")
print("=" * 70)

print("\n[1/6] Loading datasets...")

train_df = pd.read_csv(TRAIN_PATH)
val_df = pd.read_csv(VAL_PATH)

print(f"Training rows:   {len(train_df)}")
print(f"Validation rows: {len(val_df)}")


# ============================================================
# PREPARE TEXT
# ============================================================

print("\n[2/6] Preparing resume + job description text...")

def build_text(df):
    resume = df["resume_text"].fillna("")
    job = df["job_description"].fillna("")

    return resume + " [JOB_DESCRIPTION] " + job


X_train_text = build_text(train_df)
X_val_text = build_text(val_df)

y_train = train_df["label"]
y_val = val_df["label"]


# ============================================================
# TF-IDF
# ============================================================

print("\n[3/6] Creating TF-IDF features...")

vectorizer = TfidfVectorizer(
    lowercase=True,
    stop_words="english",
    ngram_range=(1, 2),
    min_df=2,
    max_df=0.95,
    sublinear_tf=True,
)

X_train = vectorizer.fit_transform(X_train_text)
X_val = vectorizer.transform(X_val_text)

print(f"Training feature matrix:   {X_train.shape}")
print(f"Validation feature matrix: {X_val.shape}")


# ============================================================
# LOGISTIC REGRESSION
# ============================================================

print("\n[4/6] Training Logistic Regression...")

model = LogisticRegression(
    max_iter=2000,
    random_state=42,
)

model.fit(X_train, y_train)

print("Model training complete.")


# ============================================================
# VALIDATION
# ============================================================

print("\n[5/6] Evaluating on validation set...")

y_pred = model.predict(X_val)

accuracy = accuracy_score(y_val, y_pred)
precision = precision_score(
    y_val,
    y_pred,
    pos_label="Strong Match",
)
recall = recall_score(
    y_val,
    y_pred,
    pos_label="Strong Match",
)
f1 = f1_score(
    y_val,
    y_pred,
    pos_label="Strong Match",
)

print("\n" + "=" * 70)
print("VALIDATION RESULTS")
print("=" * 70)

print(f"Accuracy:  {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall:    {recall:.4f}")
print(f"F1 Score:  {f1:.4f}")

print("\nClassification Report:")
print(classification_report(y_val, y_pred))

print("Confusion Matrix:")
print(confusion_matrix(
    y_val,
    y_pred,
    labels=["Weak Match", "Strong Match"]
))


# ============================================================
# TOP FEATURES
# ============================================================

print("\n[6/6] Inspecting important TF-IDF features...")

feature_names = vectorizer.get_feature_names_out()
coefficients = model.coef_[0]

top_positive_indices = coefficients.argsort()[-20:][::-1]
top_negative_indices = coefficients.argsort()[:20]

print("\nTop features associated with Strong Match:")

for index in top_positive_indices:
    print(
        f"{feature_names[index]:40s} "
        f"{coefficients[index]:.4f}"
    )

print("\nTop features associated with Weak Match:")

for index in top_negative_indices:
    print(
        f"{feature_names[index]:40s} "
        f"{coefficients[index]:.4f}"
    )


print("\n" + "=" * 70)
print("V2 BASELINE TRAINING COMPLETE")
print("=" * 70)