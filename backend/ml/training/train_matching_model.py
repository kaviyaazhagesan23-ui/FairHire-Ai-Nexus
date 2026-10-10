import pandas as pd
import joblib

from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)


# ============================================================
# FAIRHIRE AI - TF-IDF + LOGISTIC REGRESSION
# ============================================================

print("=" * 70)
print("FAIRHIRE AI - MATCHING MODEL TRAINING")
print("=" * 70)


# ------------------------------------------------------------
# 1. PATHS
# ------------------------------------------------------------

TRAIN_PATH = Path(
    "../dataset/processed/splits/train.csv"
)

VALIDATION_PATH = Path(
    "../dataset/processed/splits/validation.csv"
)

MODEL_DIR = Path("../models")

MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ------------------------------------------------------------
# 2. LOAD DATA
# ------------------------------------------------------------

print("\n[1/8] Loading datasets...")

train_df = pd.read_csv(TRAIN_PATH)
validation_df = pd.read_csv(VALIDATION_PATH)

print(f"Training rows   : {len(train_df)}")
print(f"Validation rows : {len(validation_df)}")


# ------------------------------------------------------------
# 3. CREATE COMBINED TEXT
# ------------------------------------------------------------

print("\n[2/8] Preparing text features...")


def create_combined_text(df):

    resume_text = df["resume_text"].fillna("").astype(str)

    job_description = (
        df["job_description"]
        .fillna("")
        .astype(str)
    )

    combined_text = (
        "RESUME "
        + resume_text
        + " JOB_DESCRIPTION "
        + job_description
    )

    return combined_text


X_train_text = create_combined_text(train_df)
X_validation_text = create_combined_text(validation_df)

y_train = train_df["label"]
y_validation = validation_df["label"]


# ------------------------------------------------------------
# 4. TF-IDF
# ------------------------------------------------------------

print("\n[3/8] Creating TF-IDF features...")

vectorizer = TfidfVectorizer(
    lowercase=True,
    stop_words="english",
    ngram_range=(1, 2),
    min_df=2,
    max_df=0.95,
    sublinear_tf=True
)

X_train = vectorizer.fit_transform(
    X_train_text
)

X_validation = vectorizer.transform(
    X_validation_text
)

print(f"Training feature matrix   : {X_train.shape}")
print(f"Validation feature matrix : {X_validation.shape}")


# ------------------------------------------------------------
# 5. TRAIN LOGISTIC REGRESSION
# ------------------------------------------------------------

print("\n[4/8] Training Logistic Regression...")

model = LogisticRegression(
    max_iter=2000,
    random_state=42
)

model.fit(
    X_train,
    y_train
)

print("Model training complete.")


# ------------------------------------------------------------
# 6. VALIDATION PREDICTIONS
# ------------------------------------------------------------

print("\n[5/8] Evaluating on validation data...")

y_pred = model.predict(
    X_validation
)

y_probability = model.predict_proba(
    X_validation
)


# ------------------------------------------------------------
# 7. METRICS
# ------------------------------------------------------------

print("\n[6/8] Validation metrics...")

accuracy = accuracy_score(
    y_validation,
    y_pred
)

precision = precision_score(
    y_validation,
    y_pred,
    pos_label="Strong Match"
)

recall = recall_score(
    y_validation,
    y_pred,
    pos_label="Strong Match"
)

f1 = f1_score(
    y_validation,
    y_pred,
    pos_label="Strong Match"
)


print(f"\nAccuracy  : {accuracy:.4f}")
print(f"Precision : {precision:.4f}")
print(f"Recall    : {recall:.4f}")
print(f"F1 Score  : {f1:.4f}")


print("\nClassification Report:")
print(
    classification_report(
        y_validation,
        y_pred
    )
)


print("Confusion Matrix:")

cm = confusion_matrix(
    y_validation,
    y_pred,
    labels=[
        "Weak Match",
        "Strong Match"
    ]
)

print(cm)


# ------------------------------------------------------------
# 8. SAVE MODEL + VECTORIZER
# ------------------------------------------------------------

print("\n[7/8] Saving model artifacts...")

model_path = MODEL_DIR / "matching_model.joblib"

vectorizer_path = MODEL_DIR / "tfidf_vectorizer.joblib"

joblib.dump(
    model,
    model_path
)

joblib.dump(
    vectorizer,
    vectorizer_path
)

print(f"Model saved      : {model_path}")
print(f"Vectorizer saved : {vectorizer_path}")


# ------------------------------------------------------------
# SAMPLE PREDICTIONS
# ------------------------------------------------------------

print("\n[8/8] Sample predictions...")

sample_count = min(
    10,
    len(validation_df)
)

for i in range(sample_count):

    probabilities = y_probability[i]

    class_probabilities = dict(
        zip(
            model.classes_,
            probabilities
        )
    )

    prediction = y_pred[i]

    strong_probability = class_probabilities.get(
        "Strong Match",
        0
    )

    match_score = strong_probability * 100

    print(
        f"{i + 1:02d}. "
        f"Actual: {y_validation.iloc[i]:<12} | "
        f"Predicted: {prediction:<12} | "
        f"Match Score: {match_score:6.2f}%"
    )


print("\n" + "=" * 70)
print("MODEL TRAINING COMPLETE")
print("=" * 70)