# Lumina — XGBoost Model & Scoring Knowledge

## 1. Overview

Lumina is a clinical decision-support platform for rare disease triage. Its architecture consists of a Next.js frontend and a FastAPI backend, with local/database-backed clinical and disease knowledge.

The project includes an HPO-based scoring system and a trained XGBoost disease classifier.

The important distinction is between:

- **Training the XGBoost model** — performed by `scripts/train_xgb.py`
- **Loading/using the trained model** — performed by the runtime scoring code, if it is wired to load the saved model
- **HPO semantic search** — uses the pretrained `all-MiniLM-L6-v2` sentence-transformers model

---

## 2. Project Structure Relevant to the Model

```text
lumina/
├── apps/
│   └── api/
│       ├── main.py
│       └── routes/
│           ├── disease.py
│           ├── score.py
│           └── search.py
│
├── packages/
│   ├── scoring/
│   │   ├── xgb_model.pkl       # Trained XGBoost model
│   │   └── ...
│   │
│   └── ...
│
├── scripts/
│   ├── build_hpo_index.py      # Builds HPO embedding index
│   ├── eval.py                 # Evaluation utilities
│   └── train_xgb.py            # Trains XGBoost model
│
└── database/
    └── orpha.sqlite            # Disease/HPO knowledge graph
```

The PRD identifies `scripts/train_xgb.py` as the XGBoost training script and `packages/scoring/` as the scoring engine.

---

## 3. Where Is the XGBoost Model?

The trained model is saved here:

```text
packages/scoring/xgb_model.pkl
```

This is the **trained model artifact**.

It is different from:

```text
scripts/train_xgb.py
```

`train_xgb.py` is the program that **creates/trains** the model. It is not the model itself.

The flow is:

```text
database/orpha.sqlite
        ↓
Phenotype-disease associations
        ↓
scripts/train_xgb.py
        ↓
XGBoost training
        ↓
packages/scoring/xgb_model.pkl
```

---

## 4. Do You Need to Import `train_xgb.py`?

### No — not for normal prediction.

You normally do **not** import or execute `train_xgb.py` whenever the FastAPI server starts.

The training script is used when you need to create or retrain the model.

For example:

```bash
cd apps/api
uv run python ../../scripts/train_xgb.py
```

After training, the resulting model is:

```text
packages/scoring/xgb_model.pkl
```

The runtime application should load this already-trained model.

---

## 5. How the Runtime Loads the Model

If the scoring code uses the XGBoost model, it should load the pickle file.

A typical pattern is:

```python
import joblib

model = joblib.load("packages/scoring/xgb_model.pkl")
```

Then the loaded model can be used for inference:

```python
prediction = model.predict(X)
```

The exact import path and loading location should match the actual project structure.

---

## 6. Training vs Runtime

### Training

Training happens when `train_xgb.py` is executed:

```text
orpha.sqlite
     ↓
training data
     ↓
XGBoost
     ↓
xgb_model.pkl
```

### Runtime

The API should use the saved model:

```text
Clinical evidence
       ↓
HPO extraction
       ↓
HPO features
       ↓
xgb_model.pkl
       ↓
Disease prediction/ranking
```

You should not retrain the model every time the API starts.

---

## 7. HPO Embedding Model Is Different

Lumina also uses:

```text
all-MiniLM-L6-v2
```

This is a pretrained sentence-transformers model used for semantic HPO search.

The PRD describes:

```text
scripts/build_hpo_index.py
```

as the script that builds the HPO embedding index.

The API's semantic HPO search endpoint uses sentence-transformers embeddings.

This model is therefore **not the same thing as `xgb_model.pkl`**.

### Difference

| Model | Purpose | Location/Source |
|---|---|---|
| XGBoost model | Disease classification/scoring | `packages/scoring/xgb_model.pkl` |
| `all-MiniLM-L6-v2` | Semantic HPO search | Loaded through sentence-transformers |
| HPO scoring logic | HPO similarity ranking | `packages/scoring/` |

---

## 8. Lumina Scoring Architecture

Conceptually, the scoring pipeline is:

```text
                    Clinical Evidence
                           ↓
                     HPO Extraction
                           ↓
                       HPO Terms
                           ↓
              ┌────────────┴────────────┐
              ↓                         ↓
       HPO Similarity             XGBoost Model
       Jaccard / Lin              xgb_model.pkl
       Information Content              ↓
              ↓                         ↓
              └────────────┬────────────┘
                           ↓
                    Disease Ranking
                           ↓
                    Doctor Review
```

The PRD describes `packages/scoring/` as the HPO similarity ranking/scoring engine and identifies Jaccard, Lin distances, Information Content weighting, and genetic variant scoring.

---

## 9. Important Question: Is the XGBoost Model Actually Being Used?

Having:

```text
packages/scoring/xgb_model.pkl
```

does **not automatically mean** the FastAPI application is using it.

There are two possibilities.

### Case A — Model is loaded by runtime code

If `packages/scoring/` or another runtime module contains something like:

```python
joblib.load(...)
```

or:

```python
pickle.load(...)
```

and loads:

```text
xgb_model.pkl
```

then the model is part of the runtime scoring pipeline.

### Case B — Model exists but is not loaded

If no runtime scoring code loads:

```text
xgb_model.pkl
```

then the model exists as a trained artifact but is currently not being used by the API.

This distinction is important.

---

## 10. What to Check Next

Inspect:

```text
packages/scoring/
```

and especially:

```text
score.py
```

Look for:

```python
joblib.load(...)
```

```python
pickle.load(...)
```

```python
XGBClassifier(...)
```

or references to:

```text
xgb_model.pkl
```

You can search the repository with:

```bash
grep -R "xgb_model" packages/ apps/ scripts/
```

or:

```bash
grep -R "joblib.load\|pickle.load" packages/ apps/ scripts/
```

If the search finds the model being loaded by the scoring runtime, then the model is connected to the application.

---

## 11. Simple Mental Model

Remember it this way:

```text
train_xgb.py
     │
     │ trains
     ▼
xgb_model.pkl
     │
     │ loaded by
     ▼
runtime scoring code
     │
     │ predicts
     ▼
disease ranking
```

So:

> **`train_xgb.py` = trainer**

> **`xgb_model.pkl` = trained model**

> **runtime scoring code = model user**

---

## 12. Key Takeaways

1. The trained XGBoost model is saved at:

   ```text
   packages/scoring/xgb_model.pkl
   ```

2. `scripts/train_xgb.py` creates/trains that model.

3. You do **not** normally import `train_xgb.py` into the FastAPI application for prediction.

4. The runtime scoring code should load `xgb_model.pkl` if XGBoost is part of the live scoring pipeline.

5. The existence of `xgb_model.pkl` alone does not prove that the API is currently using it.

6. `all-MiniLM-L6-v2` is a separate pretrained embedding model used for semantic HPO search.

7. `packages/scoring/` contains the project's scoring engine.

8. The next file to inspect is the runtime scoring implementation, especially `packages/scoring/score.py`, to confirm whether `xgb_model.pkl` is actually loaded and used.

---

## 13. Useful Commands

### Train/retrain the XGBoost model

```bash
cd apps/api
uv run python ../../scripts/train_xgb.py
```

### Check whether the model exists

From the project root:

```bash
ls -lh packages/scoring/xgb_model.pkl
```

### Search for model usage

```bash
grep -R "xgb_model" packages/ apps/ scripts/
```

### Search for model-loading code

```bash
grep -R "joblib.load\|pickle.load" packages/ apps/ scripts/
```

---

## Source Notes

The project PRD states that:

- `scripts/train_xgb.py` is the XGBoost training script.
- `packages/scoring/` is the scoring engine.
- `scripts/build_hpo_index.py` builds the HPO embedding index using `all-MiniLM-L6-v2`.
- `routes/search.py` uses sentence-transformers embeddings for semantic HPO search.
- `routes/disease.py` handles disease lookup and differential diagnosis scoring.
- `routes/agent.py` handles agent functionality such as referral letter generation and patient summaries.

The exact runtime loading of `xgb_model.pkl` must be verified from the actual scoring source code rather than inferred solely from the PRD.
