from datetime import datetime, timezone

from fastapi import APIRouter, Query

from app.cache import market_cache
from app.routers.market import _fetch_market_data
from app.schemas.responses import (
    FOMCData,
    ScoresResponse,
    SubScore,
)
from app.services.market_summary import generate_summary
from app.services.scoring_engine import calc_market_quality

router = APIRouter()


@router.get("/scores", response_model=ScoresResponse)
async def get_scores(mode: str = Query("swing", regex="^(swing|day)$")):
    data = await market_cache.get_or_fetch("market", _fetch_market_data)
    indicators = data["indicators"]
    fomc = data["fomc"]

    scores = calc_market_quality(indicators, fomc, mode=mode)
    summary = generate_summary(scores, indicators)

    subscores = {}
    for key, sub in scores["subscores"].items():
        subscores[key] = SubScore(
            score=sub["score"],
            weight=sub["weight"],
            contribution=sub["contribution"],
            direction=sub["direction"],
            interpretation=sub["interpretation"],
            details=sub.get("details", []),
        )

    # Filter out non-serializable fields from indicators
    safe_indicators = {
        k: v for k, v in indicators.items()
        if k not in ("closes",)
    }

    return ScoresResponse(
        market_quality_score=scores["market_quality_score"],
        execution_window_score=scores["execution_window_score"],
        decision=scores["decision"],
        decision_detail=scores["decision_detail"],
        mode=scores["mode"],
        subscores=subscores,
        summary=summary,
        tickers=data["tickers"],
        sectors=data["sectors"],
        indicators=safe_indicators,
        fomc=FOMCData(**fomc),
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
