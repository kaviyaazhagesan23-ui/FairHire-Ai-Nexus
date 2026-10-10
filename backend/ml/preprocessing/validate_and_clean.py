from pathlib import Path
import pandas as pd


# ============================================================
# FairHire AI - Dataset V2 Validation & Cleaning
# ============================================================

DATA_PATH = Path("../dataset/raw/fairhire_synthetic_dataset_v2_3000.csv")

OUTPUT_PATH = Path(
    "../dataset/processed/fairhire_cleaned_dataset_v2.csv"
)

EXPECTED_COLUMNS = [
    "resume_id",
    "candidate_name",
    "job_role",
    "education",
    "experience_years",
    "skills",
    "certifications",
    "projects",
    "previous_role",
    "industry",
    "resume_text",
    "job_description",
    "label",
]

VALID_LABELS = {
    "Strong Match",
    "Weak Match",
}


def main():

    print("=" * 70)
    print("FAIRHIRE AI - DATASET V2 VALIDATION & CLEANING")
    print("=" * 70)

    # --------------------------------------------------------
    # 1. Load
    # --------------------------------------------------------

    print("\n[1/9] Loading dataset...")

    df = pd.read_csv(DATA_PATH)

    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")

    # --------------------------------------------------------
    # 2. Column validation
    # --------------------------------------------------------

    print("\n[2/9] Checking columns...")

    if list(df.columns) != EXPECTED_COLUMNS:
        raise ValueError(
            "Column structure does not match expected schema."
        )

    print("Column structure: PASS")

    # --------------------------------------------------------
    # 3. Duplicate validation
    # --------------------------------------------------------

    print("\n[3/9] Checking duplicates...")

    duplicate_rows = df.duplicated().sum()
    duplicate_ids = df["resume_id"].duplicated().sum()

    print(f"Duplicate rows: {duplicate_rows}")
    print(f"Duplicate resume IDs: {duplicate_ids}")

    if duplicate_rows > 0:
        df = df.drop_duplicates()

    if duplicate_ids > 0:
        raise ValueError("Duplicate resume IDs detected.")

    # --------------------------------------------------------
    # 4. Missing values
    # --------------------------------------------------------

    print("\n[4/9] Checking missing values...")

    for column in EXPECTED_COLUMNS:
        missing = df[column].isna().sum()

        if missing > 0:
            print(f"{column}: {missing} missing")

    # Certifications can legitimately be None.
    df["certifications"] = (
        df["certifications"]
        .fillna("None")
        .astype(str)
        .str.strip()
    )

    critical_columns = [
        "resume_id",
        "candidate_name",
        "job_role",
        "education",
        "experience_years",
        "skills",
        "projects",
        "previous_role",
        "industry",
        "resume_text",
        "job_description",
        "label",
    ]

    for column in critical_columns:

        if df[column].isna().any():
            raise ValueError(
                f"Critical missing values found in: {column}"
            )

    print("Missing-value validation: PASS")

    # --------------------------------------------------------
    # 5. Label validation
    # --------------------------------------------------------

    print("\n[5/9] Checking labels...")

    invalid_labels = set(df["label"].unique()) - VALID_LABELS

    if invalid_labels:
        raise ValueError(
            f"Invalid labels detected: {invalid_labels}"
        )

    print(df["label"].value_counts())

    # --------------------------------------------------------
    # 6. Experience validation
    # --------------------------------------------------------

    print("\n[6/9] Checking experience...")

    df["experience_years"] = pd.to_numeric(
        df["experience_years"],
        errors="raise",
    )

    if not df["experience_years"].between(0, 12).all():
        raise ValueError(
            "Experience contains values outside 0-12."
        )

    print(
        f"Min: {df['experience_years'].min()}"
    )
    print(
        f"Max: {df['experience_years'].max()}"
    )
    print(
        f"Mean: {df['experience_years'].mean():.2f}"
    )

    # --------------------------------------------------------
    # 7. Role validation
    # --------------------------------------------------------

    print("\n[7/9] Checking job roles...")

    role_counts = df["job_role"].value_counts()

    print(f"Unique roles: {df['job_role'].nunique()}")

    for role, count in role_counts.sort_index().items():
        print(f"{role}: {count}")

    if df["job_role"].nunique() != 20:
        raise ValueError(
            "Expected exactly 20 job roles."
        )

    if not (role_counts == 150).all():
        raise ValueError(
            "Every job role must contain exactly 150 rows."
        )

    # --------------------------------------------------------
    # 8. Text validation
    # --------------------------------------------------------

    print("\n[8/9] Checking text fields...")

    for column in [
        "resume_text",
        "job_description",
        "skills",
        "projects",
    ]:

        empty_count = (
            df[column]
            .fillna("")
            .astype(str)
            .str.strip()
            .eq("")
            .sum()
        )

        print(f"{column} empty: {empty_count}")

        if empty_count > 0:
            raise ValueError(
                f"Empty values found in {column}."
            )

    # --------------------------------------------------------
    # 9. Save
    # --------------------------------------------------------

    print("\n[9/9] Saving cleaned dataset...")

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df = df[EXPECTED_COLUMNS]

    df.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print(f"\nSaved to:")
    print(OUTPUT_PATH)

    print("\n" + "=" * 70)
    print("DATASET V2 CLEANING COMPLETE")
    print("=" * 70)

    print(f"Final rows: {len(df)}")
    print(f"Final columns: {len(df.columns)}")
    print("Validation: PASS")


if __name__ == "__main__":
    main()