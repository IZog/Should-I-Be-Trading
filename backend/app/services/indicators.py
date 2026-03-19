from __future__ import annotations

import logging
from typing import Any

import numpy as np

from app.services.data_fetcher import SECTOR_TICKERS

logger = logging.getLogger(__name__)


def calc_moving_average(prices: list[float], period: int) -> float | None:
    if not prices or len(prices) < period:
        return None
    return float(np.mean(prices[-period:]))


def calc_rsi(prices: list[float], period: int = 14) -> float | None:
    if not prices or len(prices) < period + 1:
        return None
    arr = np.array(prices[-(period + 1):], dtype=float)
    deltas = np.diff(arr)
    gains = np.where(deltas > 0, deltas, 0.0)
    losses = np.where(deltas < 0, -deltas, 0.0)
    avg_gain = float(np.mean(gains))
    avg_loss = float(np.mean(losses))
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return float(100.0 - (100.0 / (1.0 + rs)))


def calc_percent_change(current: float | None, previous: float | None) -> float:
    if current is None or previous is None or previous == 0:
        return 0.0
    return ((current - previous) / previous) * 100.0


def calc_percentile(value: float | None, history: list[float]) -> float:
    if value is None or not history:
        return 50.0
    arr = np.array(history, dtype=float)
    arr = arr[~np.isnan(arr)]
    if len(arr) == 0:
        return 50.0
    return float(np.sum(arr < value) / len(arr) * 100.0)


def calc_all_indicators(raw_data: dict[str, Any]) -> dict[str, Any]:
    indicators: dict[str, Any] = {}

    # SPY moving averages
    spy_hist = raw_data.get("SPY", {}).get("history", [])
    spy_price = raw_data.get("SPY", {}).get("current_price")
    indicators["spy_price"] = spy_price
    indicators["spy_ma20"] = calc_moving_average(spy_hist, 20)
    indicators["spy_ma50"] = calc_moving_average(spy_hist, 50)
    indicators["spy_ma200"] = calc_moving_average(spy_hist, 200)

    # QQQ
    qqq_hist = raw_data.get("QQQ", {}).get("history", [])
    qqq_price = raw_data.get("QQQ", {}).get("current_price")
    indicators["qqq_price"] = qqq_price
    indicators["qqq_ma50"] = calc_moving_average(qqq_hist, 50)

    # SPY RSI
    indicators["spy_rsi14"] = calc_rsi(spy_hist, 14)

    # VIX
    vix_data = raw_data.get("^VIX", {})
    vix_price = vix_data.get("current_price")
    vix_hist = vix_data.get("history", [])
    indicators["vix_level"] = vix_price
    indicators["vix_5d_trend"] = vix_data.get("change_5d_pct", 0.0)
    indicators["vix_1yr_percentile"] = calc_percentile(vix_price, vix_hist)

    # VVIX / Put-call proxy
    vvix_data = raw_data.get("^VVIX", {})
    vvix_price = vvix_data.get("current_price")
    indicators["vvix_level"] = vvix_price
    if vvix_price is not None and vix_price is not None and vix_price > 0:
        indicators["put_call_estimate"] = vvix_price / vix_price / 100.0
    else:
        indicators["put_call_estimate"] = None

    # Breadth: % of sector ETFs above their own MAs
    above_ma20 = 0
    above_ma50 = 0
    above_ma200 = 0
    valid_sectors = 0

    for ticker in SECTOR_TICKERS:
        td = raw_data.get(ticker, {})
        hist = td.get("history", [])
        price = td.get("current_price")
        if price is None or not hist:
            continue
        valid_sectors += 1
        ma20 = calc_moving_average(hist, 20)
        ma50 = calc_moving_average(hist, 50)
        ma200 = calc_moving_average(hist, 200)
        if ma20 is not None and price > ma20:
            above_ma20 += 1
        if ma50 is not None and price > ma50:
            above_ma50 += 1
        if ma200 is not None and price > ma200:
            above_ma200 += 1

    total = valid_sectors if valid_sectors > 0 else 1
    indicators["pct_above_ma20"] = (above_ma20 / total) * 100.0
    indicators["pct_above_ma50"] = (above_ma50 / total) * 100.0
    indicators["pct_above_ma200"] = (above_ma200 / total) * 100.0

    # Advance/Decline ratio
    sectors_positive = 0
    sectors_negative = 0
    for ticker in SECTOR_TICKERS:
        td = raw_data.get(ticker, {})
        change = td.get("change_pct", 0.0)
        if change > 0:
            sectors_positive += 1
        elif change < 0:
            sectors_negative += 1

    indicators["advance_decline_ratio"] = (
        sectors_positive / sectors_negative if sectors_negative > 0 else
        (float(sectors_positive) if sectors_positive > 0 else 1.0)
    )

    # TNX (10-year yield)
    tnx_data = raw_data.get("^TNX", {})
    tnx_price = tnx_data.get("current_price")
    indicators["tnx_level"] = tnx_price
    # TNX 5d trend is absolute change in yield
    tnx_5d_ago = tnx_data.get("price_5d_ago")
    if tnx_price is not None and tnx_5d_ago is not None:
        indicators["tnx_5d_trend"] = tnx_price - tnx_5d_ago
    else:
        indicators["tnx_5d_trend"] = 0.0

    # DXY
    dxy_data = raw_data.get("DX-Y.NYB", {})
    indicators["dxy_level"] = dxy_data.get("current_price")
    indicators["dxy_5d_trend"] = dxy_data.get("change_5d_pct", 0.0)

    # Sector daily changes
    sector_daily_changes: dict[str, float] = {}
    sector_5d_returns: dict[str, float] = {}
    sector_52w_high: dict[str, float | None] = {}
    sector_52w_low: dict[str, float | None] = {}

    for ticker in SECTOR_TICKERS:
        td = raw_data.get(ticker, {})
        sector_daily_changes[ticker] = td.get("change_pct", 0.0)
        sector_5d_returns[ticker] = td.get("change_5d_pct", 0.0)
        sector_52w_high[ticker] = td.get("high_52w")
        sector_52w_low[ticker] = td.get("low_52w")

    indicators["sector_daily_changes"] = sector_daily_changes
    indicators["sector_5d_returns"] = sector_5d_returns
    indicators["sector_52w_high"] = sector_52w_high
    indicators["sector_52w_low"] = sector_52w_low

    # Regime detection
    indicators["regime"] = _detect_regime(indicators)

    return indicators


def _detect_regime(indicators: dict[str, Any]) -> str:
    spy_price = indicators.get("spy_price")
    ma50 = indicators.get("spy_ma50")
    ma200 = indicators.get("spy_ma200")
    rsi = indicators.get("spy_rsi14")

    if spy_price is None or ma50 is None or ma200 is None:
        return "UPTREND"

    above_50 = spy_price > ma50
    above_200 = spy_price > ma200
    ma50_above_200 = ma50 > ma200

    if above_50 and above_200 and ma50_above_200:
        return "UPTREND"
    elif not above_50 and above_200:
        return "PULLBACK_IN_UPTREND"
    elif above_50 and not above_200:
        return "BEAR_RALLY"
    else:
        return "DOWNTREND"
