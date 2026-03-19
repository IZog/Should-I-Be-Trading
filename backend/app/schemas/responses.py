from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class TickerData(BaseModel):
    price: Optional[float] = None
    change_pct: float = 0.0
    prev_close: Optional[float] = None


class SectorData(BaseModel):
    price: Optional[float] = None
    change_pct: float = 0.0
    name: str = ""
    change_5d: float = 0.0


class SubScore(BaseModel):
    score: float
    weight: float
    contribution: float
    direction: str
    interpretation: str
    details: List[Dict[str, Any]] = []


class FOMCData(BaseModel):
    next_date: str
    days_until: int
    is_within_warning: bool


class MarketDataResponse(BaseModel):
    tickers: Dict[str, TickerData] = {}
    sectors: Dict[str, SectorData] = {}
    indicators: Dict[str, Any] = {}
    fomc: Optional[FOMCData] = None
    timestamp: str = ""


class ScoresResponse(BaseModel):
    market_quality_score: float
    execution_window_score: int
    decision: str
    decision_detail: str
    mode: str
    subscores: Dict[str, SubScore] = {}
    summary: str = ""
    tickers: Dict[str, TickerData] = {}
    sectors: Dict[str, SectorData] = {}
    indicators: Dict[str, Any] = {}
    fomc: Optional[FOMCData] = None
    timestamp: str = ""
