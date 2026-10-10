from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split


# ============================================================
# FairHire AI - Dataset V2 Split
# ============================================================

DATA_PATH = Path(
    "../dataset/processed/fairhire_cleaned_dataset_v2.csv"
)

OUTPUT_DIR = Path(
    "../dataset/processed/splits_v2"
)

RANDOM_STATE = 42


def main():

    print("=" * 70)
    print("FAIRHIRE AI - DATASET V2 TRAIN/VALIDATION/TEST SPLIT")
    print("=" * 70)

    # --------------------------------------------------------
    # 1. Load
    # --------------------------------------------------------

    print("\n[1/6] Loading cleaned V2 dataset...")

    df = pd.read_csv(DATA_PATH)

    print(f"Total rows: {len(df)}")

    # --------------------------------------------------------
    # 2. Create stratification key
    # --------------------------------------------------------

    print("\n[2/6] Creating stratification groups...")

    # Preserve both job-role and label distribution.
    stratify_key = (
        df["job_role"].astype(str)
        + "__"
        + df["label"].astype(str)
    )

    # --------------------------------------------------------
    # 3. Train + temporary split
    # --------------------------------------------------------

    print("\n[3/6] Creating train split...")

    train_df, temp_df = train_test_split(
        df,
        test_size=0.30,
        random_state=RANDOM_STATE,
        stratify=stratify_key,
    )

    # --------------------------------------------------------
    # 4. Validation + test
    # --------------------------------------------------------

    print("\n[4/6] Creating validation/test split...")

    temp_stratify_key = (
        temp_df["job_role"].astype(str)
        + "__"
        + temp_df["label"].astype(str)
    )

    validation_df, test_df = train_test_split(
        temp_df,
        test_size=0.50,
        random_state=RANDOM_STATE,
        stratify=temp_stratify_key,
    )

    # --------------------------------------------------------
    # 5. Shuffle
    # --------------------------------------------------------

    train_df = train_df.sample(
        frac=1,
        random_state=RANDOM_STATE,
    ).reset_index(drop=True)

    validation_df = validation_df.sample(
        frac=1,
        random_state=RANDOM_STATE,
    ).reset_index(drop=True)

    test_df = test_df.sample(
        frac=1,
        random_state=RANDOM_STATE,
    ).reset_index(drop=True)

    # --------------------------------------------------------
    # 6. Save
    # --------------------------------------------------------

    print("\n[5/6] Saving splits...")

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    train_path = OUTPUT_DIR / "train.csv"
    validation_path = OUTPUT_DIR / "validation.csv"
    test_path = OUTPUT_DIR / "test.csv"

    train_df.to_csv(train_path, index=False)
    validation_df.to_csv(validation_path, index=False)
    test_df.to_csv(test_path, index=False)

    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    print("\n[6/6] Validating split sizes...")

    print(f"\nTrain:      {len(train_df)} rows")
    print(f"Validation: {len(validation_df)} rows")
    print(f"Test:       {len(test_df)} rows")

    assert len(train_df) == 2100
    assert len(validation_df) == 450
    assert len(test_df) == 450

    # Check IDs don't overlap.
    train_ids = set(train_df["resume_id"])
    validation_ids = set(validation_df["resume_id"])
    test_ids = set(test_df["resume_id"])

    assert train_ids.isdisjoint(validation_ids)
    assert train_ids.isdisjoint(test_ids)
    assert validation_ids.isdisjoint(test_ids)

    print("\nLabel distribution:")
    print("\nTRAIN")
    print(train_df["label"].value_counts())

    print("\nVALIDATION")
    print(validation_df["label"].value_counts())

    print("\nTEST")
    print(test_df["label"].value_counts())

    print("\nFiles created:")
    print(train_path)
    print(validation_path)
    print(test_path)

    print("\n" + "=" * 70)
    print("DATASET V2 SPLIT COMPLETE")
    print("=" * 70)
    print("70% Train / 15% Validation / 15% Test")
    print("Split validation: PASS")


if __name__ == "__main__":
    main()