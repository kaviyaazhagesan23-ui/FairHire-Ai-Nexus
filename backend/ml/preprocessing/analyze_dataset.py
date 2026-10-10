import pandas as pd
import re
from pathlib import Path


# ============================================================
# FAIRHIRE AI - DATASET DEEP ANALYSIS
# ============================================================

print("=" * 70)
print("FAIRHIRE AI - DATASET DEEP ANALYSIS")
print("=" * 70)


# ------------------------------------------------------------
# 1. LOAD CLEANED DATASET
# ------------------------------------------------------------

DATA_PATH = Path("../dataset/processed/fairhire_cleaned_dataset.csv")

print("\n[1/9] Loading cleaned dataset...")

df = pd.read_csv(DATA_PATH)

print(f"Rows: {len(df)}")
print(f"Columns: {len(df.columns)}")

print("Dataset loaded successfully.")


# ------------------------------------------------------------
# 2. CHECK LABEL DISTRIBUTION
# ------------------------------------------------------------

print("\n[2/9] Checking label distribution...")

label_counts = df["label"].value_counts()

print("\nLabel distribution:")
print(label_counts)

print("\nLabel percentage:")
print((df["label"].value_counts(normalize=True) * 100).round(2))


# ------------------------------------------------------------
# 3. INVESTIGATE 'PREDICTION' KEYWORD
# ------------------------------------------------------------

print("\n[3/9] Investigating possible 'prediction' leakage...")

text_columns = [
    "skills",
    "certifications",
    "projects",
    "previous_role",
    "industry",
    "resume_text",
    "job_description"
]

prediction_mask = pd.Series(False, index=df.index)

for column in text_columns:
    mask = df[column].fillna("").astype(str).str.contains(
        r"\bprediction\b",
        case=False,
        regex=True
    )

    count = mask.sum()

    if count > 0:
        print(f"\nColumn: {column}")
        print(f"Occurrences: {count}")

        prediction_mask = prediction_mask | mask

total_prediction_rows = prediction_mask.sum()

print(f"\nTotal rows containing 'prediction': {total_prediction_rows}")

if total_prediction_rows > 0:

    print("\nSample rows containing 'prediction':")

    sample = df.loc[
        prediction_mask,
        [
            "resume_id",
            "job_role",
            "experience_years",
            "label"
        ]
    ].head(10)

    print(sample.to_string(index=False))

    print("\nLabels among rows containing 'prediction':")

    print(
        df.loc[
            prediction_mask,
            "label"
        ].value_counts()
    )

else:
    print("PASS: No prediction keyword found.")


# ------------------------------------------------------------
# 4. CHECK FOR DIRECT LABEL LEAKAGE
# ------------------------------------------------------------

print("\n[4/9] Checking for direct label leakage...")

leakage_patterns = [
    r"\bstrong\s+match\b",
    r"\bweak\s+match\b",
    r"\bmatch\s+score\b",
    r"\bcandidate\s+score\b",
    r"\bsuitability\s+score\b",
    r"\bclassification\b",
    r"\bpredicted\s+label\b",
    r"\bprediction\b"
]

combined_text = (
    df["resume_text"].fillna("").astype(str)
    + " "
    + df["job_description"].fillna("").astype(str)
).str.lower()

found_patterns = {}

for pattern in leakage_patterns:

    mask = combined_text.str.contains(
        pattern,
        regex=True,
        case=False
    )

    count = mask.sum()

    if count > 0:
        found_patterns[pattern] = count

if found_patterns:

    print("\nPotentially relevant terms found:")

    for pattern, count in found_patterns.items():
        print(f"  {pattern}: {count}")

else:

    print("PASS: No obvious label leakage phrases found.")


# ------------------------------------------------------------
# 5. LABEL DISTRIBUTION BY EXPERIENCE
# ------------------------------------------------------------

print("\n[5/9] Checking label distribution by experience...")

df["experience_bin"] = pd.cut(
    df["experience_years"],
    bins=[-1, 0, 2, 5, 8, 12],
    labels=[
        "0 years",
        "1-2 years",
        "3-5 years",
        "6-8 years",
        "9-12 years"
    ]
)

experience_distribution = pd.crosstab(
    df["experience_bin"],
    df["label"],
    normalize="index"
) * 100

print("\nLabel percentage by experience group:")

print(experience_distribution.round(2))


# ------------------------------------------------------------
# 6. LABEL DISTRIBUTION BY JOB ROLE
# ------------------------------------------------------------

print("\n[6/9] Checking label distribution by job role...")

role_distribution = pd.crosstab(
    df["job_role"],
    df["label"],
    normalize="index"
) * 100

print("\nLabel percentage by job role:")

print(role_distribution.round(2))


# ------------------------------------------------------------
# 7. LABEL DISTRIBUTION BY EDUCATION AND INDUSTRY
# ------------------------------------------------------------

print("\n[7/9] Checking label distribution by education and industry...")

education_distribution = pd.crosstab(
    df["education"],
    df["label"],
    normalize="index"
) * 100

print("\nLabel percentage by education:")

print(education_distribution.round(2))


industry_distribution = pd.crosstab(
    df["industry"],
    df["label"],
    normalize="index"
) * 100

print("\nLabel percentage by industry:")

print(industry_distribution.round(2))


# ------------------------------------------------------------
# 8. TEXT LENGTH ANALYSIS
# ------------------------------------------------------------

print("\n[8/9] Checking text-length shortcuts...")

df["resume_text_length"] = (
    df["resume_text"]
    .fillna("")
    .astype(str)
    .str.len()
)

df["job_description_length"] = (
    df["job_description"]
    .fillna("")
    .astype(str)
    .str.len()
)

text_stats = df.groupby("label")[
    [
        "resume_text_length",
        "job_description_length"
    ]
].agg(
    ["mean", "median", "min", "max"]
)

print("\nText statistics by label:")

print(text_stats.round(2))


# ------------------------------------------------------------
# 9. FINAL DATASET QUALITY SUMMARY
# ------------------------------------------------------------

print("\n[9/9] Final quality summary...")

print("\nDataset shape:")
print(f"Rows: {len(df)}")
print(f"Columns: {len(df.columns) - 3}")
print("(Temporary analysis columns are excluded.)")

print("\nUnique roles:")
print(df["job_role"].nunique())

print("\nUnique industries:")
print(df["industry"].nunique())

print("\nUnique education levels:")
print(df["education"].nunique())

print("\nExperience range:")
print(
    f"{df['experience_years'].min()} - "
    f"{df['experience_years'].max()} years"
)


# ------------------------------------------------------------
# AUTOMATIC WARNINGS
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("DATASET QUALITY CHECK")
print("=" * 70)

warnings = []

if total_prediction_rows > 0:
    warnings.append(
        f"{total_prediction_rows} rows contain the word 'prediction'. "
        "These rows should be manually reviewed."
    )

if (
    "Strong Match" in label_counts.index
    and "Weak Match" in label_counts.index
):

    strong_pct = label_counts["Strong Match"] / len(df)
    weak_pct = label_counts["Weak Match"] / len(df)

    if strong_pct < 0.4 or strong_pct > 0.6:
        warnings.append(
            "Label distribution is noticeably imbalanced."
        )

if not warnings:

    print("\nPASS: No major dataset quality problems detected.")

else:

    print("\nWARNINGS:")

    for warning in warnings:
        print(f"- {warning}")


print("\n" + "=" * 70)
print("DEEP DATASET ANALYSIS COMPLETE")
print("=" * 70)