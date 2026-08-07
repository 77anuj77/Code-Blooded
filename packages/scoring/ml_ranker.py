"""XGBoost-based disease ranker.

Trains a multi-class classifier on phenotype-disease associations from orpha.sqlite.
Each disease is a class; features are HPO term frequency weights.
Saves model to packages/scoring/xgb_model.pkl for use as an alternative
or complement to the rule-based ScoringIndex.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

import joblib
import numpy as np
from scipy import sparse
from sqlmodel import Session, select
from xgboost import XGBClassifier

from ingest.db import get_engine
from ingest.models import DiseasePhenotype, HPOTerm

logger = logging.getLogger(__name__)

_MODEL_PATH = Path(__file__).parent / "xgb_model.pkl"
_HPO_VOCAB_PATH = Path(__file__).parent / "_xgb_hpo_vocab.json"
_LABEL_MAP_PATH = Path(__file__).parent / "_xgb_label_map.json"


class XGBoostRanker:
    """Train and persist an XGBoost multi-class disease classifier."""

    def __init__(self) -> None:
        self._model: XGBClassifier | None = None
        self._hpo_ids: list[str] = []
        self._label_to_orpha: dict[int, int] = {}
        self._orpha_to_label: dict[int, int] = {}

    def train(self, engine, n_augment: int = 50, n_estimators: int = 200) -> None:
        """Build training data from DB, train XGBoost multi-class, save to disk.

        Args:
            engine: SQLAlchemy engine
            n_augment: Number of augmented samples per disease (subsampling HPOs)
        """
        with Session(engine) as session:
            all_hpo = sorted(
                {
                    dp.hpo_id
                    for dp in session.exec(select(DiseasePhenotype))
                    if dp.frequency_weight > 0
                }
            )
            hpo_index = {h: i for i, h in enumerate(all_hpo)}

            disease_pheno: dict[int, dict[str, float]] = {}
            for dp in session.exec(select(DiseasePhenotype)):
                if dp.frequency_weight <= 0:
                    continue
                disease_pheno.setdefault(dp.orpha_code, {})[dp.hpo_id] = dp.frequency_weight

        if not disease_pheno:
            logger.warning("No disease-phenotype data found; skipping training.")
            return

        n_hpo = len(all_hpo)
        orpha_codes = sorted(disease_pheno.keys())
        n_diseases = len(orpha_codes)

        self._orpha_to_label = {oc: i for i, oc in enumerate(orpha_codes)}
        self._label_to_orpha = {i: oc for i, oc in enumerate(orpha_codes)}

        logger.info(
            "Building training matrix: %d diseases x %d HPO features, %d augmentations per disease",
            n_diseases, n_hpo, n_augment
        )

        rng = np.random.default_rng(42)

        # Built as CSR rather than dense: each disease carries ~27 of the 8,728
        # features, so the dense matrix is ~0.3% non-zero. Materialising it cost
        # ~15 GB as float32 — and far more via .tolist(), whose Python floats
        # are what actually exhausted memory.
        data: list[float] = []
        indices: list[int] = []
        indptr: list[int] = [0]
        y_labels: list[int] = []

        for orpha_code, pheno_map in disease_pheno.items():
            label = self._orpha_to_label[orpha_code]
            cols = np.fromiter(
                (hpo_index[h] for h in pheno_map), dtype=np.int32, count=len(pheno_map)
            )
            vals = np.fromiter(pheno_map.values(), dtype=np.float32, count=len(pheno_map))
            n_phenos = cols.size

            # Add the canonical profile
            indices.extend(cols.tolist())
            data.extend(vals.tolist())
            indptr.append(len(indices))
            y_labels.append(label)

            # Add augmented samples by subsampling HPOs
            for _ in range(n_augment - 1):
                # Randomly keep each HPO with probability 0.7
                keep_mask = rng.random(n_phenos) < 0.7
                if not keep_mask.any():
                    keep_mask[rng.integers(n_phenos)] = True

                indices.extend(cols[keep_mask].tolist())
                data.extend(vals[keep_mask].tolist())
                indptr.append(len(indices))
                y_labels.append(label)

        y = np.array(y_labels, dtype=np.int32)
        X = sparse.csr_matrix(
            (
                np.asarray(data, dtype=np.float32),
                np.asarray(indices, dtype=np.int32),
                np.asarray(indptr, dtype=np.int64),
            ),
            shape=(y.size, n_hpo),
        )

        logger.info(
            "Training XGBoost multi-class on %d samples, %d classes",
            len(y), n_diseases
        )

        self._model = XGBClassifier(
            n_estimators=n_estimators,
            max_depth=8,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            objective="multi:softprob",
            eval_metric="mlogloss",
            random_state=42,
            n_jobs=-1,
            num_class=n_diseases,
        )
        self._model.fit(X, y)

        self._hpo_ids = all_hpo
        joblib.dump(
            {
                "model": self._model,
                "hpo_ids": all_hpo,
                "label_to_orpha": self._label_to_orpha,
            },
            _MODEL_PATH,
        )
        _HPO_VOCAB_PATH.write_text(json.dumps(all_hpo))
        _LABEL_MAP_PATH.write_text(json.dumps(self._label_to_orpha))
        logger.info("Model saved to %s", _MODEL_PATH)

    @classmethod
    def load(cls) -> XGBoostRanker:
        """Load a previously trained model from disk."""
        ranker = cls()
        if not _MODEL_PATH.exists():
            logger.info("No trained XGBoost model at %s", _MODEL_PATH)
            return ranker
        data = joblib.load(_MODEL_PATH)
        ranker._model = data["model"]
        ranker._hpo_ids = data["hpo_ids"]
        ranker._label_to_orpha = data["label_to_orpha"]
        ranker._orpha_to_label = {v: k for k, v in ranker._label_to_orpha.items()}
        return ranker

    @property
    def is_ready(self) -> bool:
        return self._model is not None

    def predict_scores(self, hpo_ids: list[str], top_k: int = 10) -> list[tuple[int, float]]:
        """Given a set of HPO term IDs, return top-k (orpha_code, score) pairs."""
        if not self.is_ready:
            return []
        vec = np.zeros(len(self._hpo_ids), dtype=np.float32)
        hpo_set = {h for h in hpo_ids if h in set(self._hpo_ids)}
        if not hpo_set:
            return []
        for h in hpo_set:
            vec[self._hpo_ids.index(h)] = 1.0
        proba = self._model.predict_proba(vec.reshape(1, -1))[0]
        scores = [
            (self._label_to_orpha[i], float(p))
            for i, p in enumerate(proba)
            if i in self._label_to_orpha
        ]
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]