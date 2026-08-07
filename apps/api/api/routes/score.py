from extractors.models import HPOTerm
from fastapi import APIRouter, Request
from pydantic import BaseModel
from scoring.ranker import GeneticEvidence, RankResult

router = APIRouter(prefix="/score", tags=["score"])

_MODALITY_CAP = {1: 40.0, 2: 55.0, 3: 65.0, 4: 80.0}


class ScoreRequest(BaseModel):
    terms: list[HPOTerm]
    top_k: int = 10
    modalities: int = 1
    genetic_evidence: list[GeneticEvidence] = []
    lang: str | None = None
    locale: str | None = None
    use_xgb: bool = False


@router.post("", response_model=list[RankResult])
async def score_case(body: ScoreRequest, request: Request) -> list[RankResult]:
    index = request.app.state.scoring_index
    results = index.rank(
        body.terms,
        top_k=body.top_k,
        genetic_evidence=body.genetic_evidence,
    )
    if body.use_xgb:
        xgb_ranker = getattr(request.app.state, "xgb_ranker", None)
        if xgb_ranker is not None and xgb_ranker.is_ready:
            hpo_ids = [t.hpo_id for t in body.terms if t.confidence > 0]
            xgb_scores = dict(xgb_ranker.predict_scores(hpo_ids, top_k=body.top_k * 3))
            for r in results:
                xgb_boost = xgb_scores.get(r.orpha_code, 0.0)
                r.score = round(min(1.0, r.score + xgb_boost * 0.3), 4)
                r.confidence = round(min(100.0, r.confidence + xgb_boost * 15.0), 1)
            results.sort(key=lambda r: r.confidence, reverse=True)
            results = results[: body.top_k]
    if not body.genetic_evidence and not any(t.review_status for t in body.terms):
        cap = _MODALITY_CAP.get(max(1, min(4, body.modalities)), 40.0)
        for r in results:
            r.confidence = round(min(cap, r.score * cap), 1)
    return results
