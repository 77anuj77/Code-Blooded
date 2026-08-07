"""Train the XGBoost disease classifier and save to packages/scoring/xgb_model.pkl.

Usage:
    cd apps/api && uv run python ../../scripts/train_xgb.py
    cd apps/api && uv run python ../../scripts/train_xgb.py --n-augment 100
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure packages are importable when run via uv from apps/api
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "scoring"))
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "ingest"))

from ingest.db import get_engine
from ingest.models import DiseasePhenotype
from scoring.ml_ranker import XGBoostRanker
from sqlmodel import Session, func, select


def main() -> None:
    parser = argparse.ArgumentParser(description="Train XGBoost disease classifier")
    parser.add_argument(
        "--n-augment",
        type=int,
        default=50,
        help="Number of augmented samples per disease (default: 50)",
    )
    parser.add_argument(
        "--db-path",
        type=Path,
        default=None,
        help="Path to orpha.sqlite (default: auto-detect)",
    )
    args = parser.parse_args()

    engine = get_engine(args.db_path)

    # Quick stats for the summary line
    with Session(engine) as session:
        n_diseases: int = session.exec(
            select(func.count(func.distinct(DiseasePhenotype.orpha_code)))
            .where(DiseasePhenotype.frequency_weight > 0.0)
        ).one()
        n_hpo: int = session.exec(
            select(func.count(func.distinct(DiseasePhenotype.hpo_id)))
            .where(DiseasePhenotype.frequency_weight > 0.0)
        ).one()

    print(f"Training XGBoost on {n_diseases} diseases × {n_hpo} HPO features "
          f"with {args.n_augment} augmentations per disease …")

    ranker = XGBoostRanker()
    ranker.train(engine, n_augment=args.n_augment)

    print(f"Trained on {n_diseases} diseases, {n_hpo} HPO features. Saved to xgb_model.pkl")


if __name__ == "__main__":
    main()