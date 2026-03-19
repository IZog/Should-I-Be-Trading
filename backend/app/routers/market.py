from datetime import datetime, timezone

from fastapi import APIRouter

from app.cache import market_cache
from app.services.data_fetcher import fetch_all_data, SECTOR_NAMES, SECTOR_TICKERS
from app.services.fomc_calendar import get_next_fomc
from app.services.indicators import calc_all_indicators
from app.schemas.responses import (
    FOMCData,
    MarketDataResponse,
    SectorData,
    TickerData,
)

router = APIRouter()

INDEX_TICKERS = ["SPY", "QQQ", "^VIX", "^VVIX", "DX-Y.NYB", "^TNX"]


async def _fetch_market_data() -> dict:
    raw = await fetch_all_data()
    indicators = calc_all_indicators(raw)
    fomc = get_next_fomc()

    tickers = {}
    for t in INDEX_TICKERS:
        td = raw.get(t, {})
        tickers[t] = TickerData(
            price=td.get("current_price"),
            change_pct=td.get("change_pct", 0.0),
            prev_close=td.get("prev_close"),
        )

    sectors = {}
    for t in SECTOR_TICKERS:
        td = raw.get(t, {})
        sectors[t] = SectorData(
            price=td.get("current_price"),
            change_pct=td.get("change_pct", 0.0),
            name=SECTOR_NAMES.get(t, t),
            change_5d=td.get("change_5d_pct", 0.0),
        )

    return {
        "raw": raw,
        "indicators": indicators,
        "fomc": fomc,
        "tickers": tickers,
        "sectors": sectors,
    }


@router.get("/market-data", response_model=MarketDataResponse)
async def get_market_data():
    data = await market_cache.get_or_fetch("market", _fetch_market_data)

    # Filter out non-serializable fields from indicators
    safe_indicators = {
        k: v for k, v in data["indicators"].items()
        if k not in ("closes",)
    }

    return MarketDataResponse(
        tickers=data["tickers"],
        sectors=data["sectors"],
        indicators=safe_indicators,
        fomc=FOMCData(**data["fomc"]),
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "market-data"}
