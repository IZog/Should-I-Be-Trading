import logging
from typing import Any

from app.services.data_fetcher import SECTOR_TICKERS

logger = logging.getLogger(__name__)


def calc_volatility_score(indicators: dict[str, Any]) -> dict[str, Any]:
    details: list[dict[str, Any]] = []

    # VIX Level (25%)
    vix = indicators.get("vix_level")
    if vix is not None:
        if vix < 12:
            vix_score = 95
        elif vix < 16:
            vix_score = 85
        elif vix < 20:
            vix_score = 70
        elif vix < 25:
            vix_score = 45
        elif vix < 30:
            vix_score = 25
        elif vix < 40:
            vix_score = 10
        else:
            vix_score = 0
    else:
        vix_score = 50
    details.append({
        "name": "VIX Level",
        "score": vix_score,
        "weight": 0.25,
        "value": vix,
        "interpretation": f"VIX at {vix:.1f}" if vix is not None else "VIX unavailable",
    })

    # VIX 5d Trend (25%)
    vix_trend = indicators.get("vix_5d_trend", 0.0)
    if vix_trend < -10:
        trend_score = 95
    elif vix_trend < -5:
        trend_score = 80
    elif vix_trend < 0:
        trend_score = 65
    elif vix_trend < 5:
        trend_score = 45
    elif vix_trend < 10:
        trend_score = 25
    else:
        trend_score = 10
    details.append({
        "name": "VIX 5d Trend",
        "score": trend_score,
        "weight": 0.25,
        "value": vix_trend,
        "interpretation": f"VIX {'falling' if vix_trend < 0 else 'rising'} {abs(vix_trend):.1f}% over 5 days",
    })

    # VIX 1yr Percentile (25%)
    vix_pct = indicators.get("vix_1yr_percentile", 50.0)
    pct_score = max(0, 100 - vix_pct)
    details.append({
        "name": "VIX 1yr Percentile",
        "score": pct_score,
        "weight": 0.25,
        "value": vix_pct,
        "interpretation": f"VIX at {vix_pct:.0f}th percentile of 1yr range",
    })

    # Put/Call Proxy (25%)
    pc = indicators.get("put_call_estimate")
    if pc is not None:
        if pc < 0.7:
            pc_score = 60
        elif pc < 0.85:
            pc_score = 80
        elif pc < 1.0:
            pc_score = 65
        elif pc < 1.1:
            pc_score = 40
        else:
            pc_score = 20
    else:
        pc_score = 50
    details.append({
        "name": "Put/Call Proxy",
        "score": pc_score,
        "weight": 0.25,
        "value": pc,
        "interpretation": f"VVIX/VIX ratio proxy at {pc:.2f}" if pc is not None else "Put/Call proxy unavailable",
    })

    composite = (
        vix_score * 0.25 + trend_score * 0.25 + pct_score * 0.25 + pc_score * 0.25
    )

    return {
        "score": round(composite, 1),
        "details": details,
    }


def calc_momentum_score(indicators: dict[str, Any]) -> dict[str, Any]:
    details: list[dict[str, Any]] = []
    sector_changes = indicators.get("sector_daily_changes", {})
    sector_5d = indicators.get("sector_5d_returns", {})

    # Sector Spread (40%)
    changes = sorted(sector_changes.values())
    if len(changes) >= 6:
        top3_avg = sum(changes[-3:]) / 3
        bot3_avg = sum(changes[:3]) / 3
        spread = top3_avg - bot3_avg
    else:
        spread = 1.0

    if spread < 0.5:
        spread_score = 85
    elif spread < 1.0:
        spread_score = 70
    elif spread < 2.0:
        spread_score = 50
    elif spread < 3.0:
        spread_score = 30
    else:
        spread_score = 15
    details.append({
        "name": "Sector Spread",
        "score": spread_score,
        "weight": 0.40,
        "value": round(spread, 2),
        "interpretation": f"Top-bottom sector spread: {spread:.2f}%",
    })

    # Avg 5d Sector Return (30%)
    five_d_vals = list(sector_5d.values())
    avg_5d = sum(five_d_vals) / len(five_d_vals) if five_d_vals else 0.0
    avg5d_score = max(0, min(100, 50 + avg_5d * 20))
    details.append({
        "name": "Avg 5d Sector Return",
        "score": round(avg5d_score, 1),
        "weight": 0.30,
        "value": round(avg_5d, 2),
        "interpretation": f"Average 5-day sector return: {avg_5d:.2f}%",
    })

    # Sector Breadth (30%)
    sectors_positive = sum(1 for v in sector_changes.values() if v > 0)
    total_sectors = len(sector_changes) if sector_changes else 11
    breadth_score = (sectors_positive / total_sectors) * 100
    details.append({
        "name": "Sector Breadth",
        "score": round(breadth_score, 1),
        "weight": 0.30,
        "value": f"{sectors_positive}/{total_sectors}",
        "interpretation": f"{sectors_positive} of {total_sectors} sectors positive today",
    })

    composite = spread_score * 0.40 + avg5d_score * 0.30 + breadth_score * 0.30

    return {
        "score": round(composite, 1),
        "details": details,
    }


def calc_trend_score(indicators: dict[str, Any]) -> dict[str, Any]:
    details: list[dict[str, Any]] = []

    # SPY vs MAs (35%)
    spy_price = indicators.get("spy_price")
    ma20 = indicators.get("spy_ma20")
    ma50 = indicators.get("spy_ma50")
    ma200 = indicators.get("spy_ma200")

    count_above = 0
    if spy_price is not None:
        if ma20 is not None and spy_price > ma20:
            count_above += 1
        if ma50 is not None and spy_price > ma50:
            count_above += 1
        if ma200 is not None and spy_price > ma200:
            count_above += 1

    if count_above == 3:
        ma_score = 95
    elif count_above == 2:
        ma_score = 65
    elif count_above == 1:
        ma_score = 35
    else:
        ma_score = 10

    # Bonus for golden alignment: spy > ma20 > ma50 > ma200
    if (spy_price is not None and ma20 is not None and ma50 is not None and ma200 is not None
            and spy_price > ma20 > ma50 > ma200):
        ma_score = min(100, ma_score + 5)

    details.append({
        "name": "SPY vs MAs",
        "score": ma_score,
        "weight": 0.35,
        "value": count_above,
        "interpretation": f"SPY above {count_above}/3 key moving averages",
    })

    # QQQ vs 50d (20%)
    qqq_price = indicators.get("qqq_price")
    qqq_ma50 = indicators.get("qqq_ma50")
    if qqq_price is not None and qqq_ma50 is not None and qqq_ma50 > 0:
        distance_pct = ((qqq_price - qqq_ma50) / qqq_ma50) * 100
        qqq_score = max(0, min(100, 50 + distance_pct * 10))
    else:
        qqq_score = 50
        distance_pct = 0
    details.append({
        "name": "QQQ vs 50d MA",
        "score": round(qqq_score, 1),
        "weight": 0.20,
        "value": round(distance_pct, 2) if qqq_price and qqq_ma50 else None,
        "interpretation": f"QQQ {distance_pct:+.1f}% from 50d MA" if qqq_price and qqq_ma50 else "QQQ data unavailable",
    })

    # RSI (25%)
    rsi = indicators.get("spy_rsi14")
    if rsi is not None:
        if rsi > 70:
            rsi_score = 30
        elif rsi > 60:
            rsi_score = 75
        elif rsi > 40:
            rsi_score = 85
        elif rsi > 30:
            rsi_score = 50
        else:
            rsi_score = 25
    else:
        rsi_score = 50
    details.append({
        "name": "RSI(14)",
        "score": rsi_score,
        "weight": 0.25,
        "value": round(rsi, 1) if rsi is not None else None,
        "interpretation": f"SPY RSI(14) at {rsi:.1f}" if rsi is not None else "RSI unavailable",
    })

    # Regime (20%)
    regime = indicators.get("regime", "UPTREND")
    regime_scores = {
        "UPTREND": 85,
        "PULLBACK_IN_UPTREND": 60,
        "BEAR_RALLY": 40,
        "DOWNTREND": 15,
    }
    regime_score = regime_scores.get(regime, 50)
    details.append({
        "name": "Market Regime",
        "score": regime_score,
        "weight": 0.20,
        "value": regime,
        "interpretation": f"Current regime: {regime.replace('_', ' ').title()}",
    })

    composite = ma_score * 0.35 + qqq_score * 0.20 + rsi_score * 0.25 + regime_score * 0.20

    return {
        "score": round(composite, 1),
        "details": details,
    }


def calc_breadth_score(indicators: dict[str, Any]) -> dict[str, Any]:
    details: list[dict[str, Any]] = []

    # % Above MAs (50%)
    pct_20 = indicators.get("pct_above_ma20", 50)
    pct_50 = indicators.get("pct_above_ma50", 50)
    pct_200 = indicators.get("pct_above_ma200", 50)
    blended = pct_20 * 0.40 + pct_50 * 0.35 + pct_200 * 0.25
    details.append({
        "name": "% Above MAs",
        "score": round(blended, 1),
        "weight": 0.50,
        "value": {"ma20": round(pct_20, 1), "ma50": round(pct_50, 1), "ma200": round(pct_200, 1)},
        "interpretation": f"{pct_20:.0f}% above 20d, {pct_50:.0f}% above 50d, {pct_200:.0f}% above 200d",
    })

    # A/D Estimate (30%)
    ad_ratio = indicators.get("advance_decline_ratio", 1.0)
    ad_score = max(0, min(100, ad_ratio * 20))
    details.append({
        "name": "A/D Estimate",
        "score": round(ad_score, 1),
        "weight": 0.30,
        "value": round(ad_ratio, 2),
        "interpretation": f"Advance/Decline ratio estimate: {ad_ratio:.2f}",
    })

    # New Highs/Lows (20%)
    sector_prices = {}
    sector_52w_high = indicators.get("sector_52w_high", {})
    sector_52w_low = indicators.get("sector_52w_low", {})

    near_high = 0
    near_low = 0
    for ticker in SECTOR_TICKERS:
        high = sector_52w_high.get(ticker)
        low = sector_52w_low.get(ticker)
        daily_change = indicators.get("sector_daily_changes", {}).get(ticker, 0)
        # Use sector_5d_returns to estimate proximity to 52w extremes
        five_d_ret = indicators.get("sector_5d_returns", {}).get(ticker, 0)

        if high is not None and low is not None and high != low:
            # Approximate: if 5d return is positive and strong, near high
            if five_d_ret > 1.0:
                near_high += 1
            elif five_d_ret < -1.0:
                near_low += 1

    total_near = near_high + near_low
    if total_near > 0:
        hl_score = (near_high / total_near) * 100
    else:
        hl_score = 50.0
    details.append({
        "name": "New Highs/Lows",
        "score": round(hl_score, 1),
        "weight": 0.20,
        "value": {"near_high": near_high, "near_low": near_low},
        "interpretation": f"{near_high} sectors near 52w high, {near_low} near 52w low",
    })

    composite = blended * 0.50 + ad_score * 0.30 + hl_score * 0.20

    return {
        "score": round(composite, 1),
        "details": details,
    }


def calc_macro_score(indicators: dict[str, Any], fomc_data: dict) -> dict[str, Any]:
    details: list[dict[str, Any]] = []

    # TNX Level (30%)
    tnx = indicators.get("tnx_level")
    if tnx is not None:
        if tnx < 3.5:
            tnx_score = 85
        elif tnx < 4.0:
            tnx_score = 75
        elif tnx < 4.5:
            tnx_score = 60
        elif tnx < 5.0:
            tnx_score = 40
        elif tnx < 5.5:
            tnx_score = 25
        else:
            tnx_score = 10
    else:
        tnx_score = 50
    details.append({
        "name": "TNX Level",
        "score": tnx_score,
        "weight": 0.30,
        "value": tnx,
        "interpretation": f"10yr yield at {tnx:.2f}%" if tnx is not None else "TNX unavailable",
    })

    # TNX 5d Trend (20%)
    tnx_trend = indicators.get("tnx_5d_trend", 0.0)
    if tnx_trend < -0.10:
        tnx_trend_score = 90
    elif tnx_trend < -0.03:
        tnx_trend_score = 70
    elif tnx_trend < 0.03:
        tnx_trend_score = 55
    elif tnx_trend < 0.10:
        tnx_trend_score = 35
    else:
        tnx_trend_score = 15
    details.append({
        "name": "TNX 5d Trend",
        "score": tnx_trend_score,
        "weight": 0.20,
        "value": round(tnx_trend, 3),
        "interpretation": f"10yr yield {'falling' if tnx_trend < 0 else 'rising'} {abs(tnx_trend):.3f} over 5 days",
    })

    # DXY 5d Trend (20%)
    dxy_trend = indicators.get("dxy_5d_trend", 0.0)
    if dxy_trend < -1.0:
        dxy_score = 85
    elif dxy_trend < -0.3:
        dxy_score = 70
    elif dxy_trend < 0.3:
        dxy_score = 55
    elif dxy_trend < 1.0:
        dxy_score = 35
    else:
        dxy_score = 15
    details.append({
        "name": "DXY 5d Trend",
        "score": dxy_score,
        "weight": 0.20,
        "value": round(dxy_trend, 2),
        "interpretation": f"Dollar index {'weakening' if dxy_trend < 0 else 'strengthening'} {abs(dxy_trend):.2f}% over 5 days",
    })

    # FOMC Proximity (30%)
    days_until = fomc_data.get("days_until", 30)
    if days_until <= 2:
        fomc_score = 20
    elif days_until <= 5:
        fomc_score = 40
    elif days_until <= 10:
        fomc_score = 60
    elif days_until <= 14:
        fomc_score = 75
    else:
        fomc_score = 90
    details.append({
        "name": "FOMC Proximity",
        "score": fomc_score,
        "weight": 0.30,
        "value": days_until,
        "interpretation": f"Next FOMC in {days_until} days" + (" - CAUTION" if days_until <= 5 else ""),
    })

    composite = tnx_score * 0.30 + tnx_trend_score * 0.20 + dxy_score * 0.20 + fomc_score * 0.30

    return {
        "score": round(composite, 1),
        "details": details,
    }


def calc_execution_window_score(indicators: dict[str, Any]) -> int:
    # VIX component (25%)
    vix_pct = indicators.get("vix_1yr_percentile", 50.0)
    vix_component = 100 - vix_pct

    # RSI component (30%)
    rsi = indicators.get("spy_rsi14", 50.0)
    if rsi is None:
        rsi = 50.0
    rsi_component = 100 - abs(rsi - 50) * 2

    # Spread component (20%)
    sector_changes = indicators.get("sector_daily_changes", {})
    changes = sorted(sector_changes.values())
    if len(changes) >= 6:
        top3_avg = sum(changes[-3:]) / 3
        bot3_avg = sum(changes[:3]) / 3
        spread = top3_avg - bot3_avg
    else:
        spread = 1.0
    spread_component = 100 - min(spread * 25, 100)

    # Trend alignment (25%)
    spy_price = indicators.get("spy_price")
    ma20 = indicators.get("spy_ma20")
    ma50 = indicators.get("spy_ma50")

    if (spy_price is not None and ma20 is not None and ma50 is not None
            and spy_price > ma20 > ma50):
        trend_alignment = 100
    elif spy_price is not None and ma50 is not None and spy_price > ma50:
        trend_alignment = 50
    else:
        trend_alignment = 20

    score = (
        vix_component * 0.25
        + rsi_component * 0.30
        + spread_component * 0.20
        + trend_alignment * 0.25
    )

    return round(max(0, min(100, score)))


def calc_market_quality(
    indicators: dict[str, Any],
    fomc_data: dict,
    mode: str = "swing",
) -> dict[str, Any]:
    vol = calc_volatility_score(indicators)
    mom = calc_momentum_score(indicators)
    trend = calc_trend_score(indicators)
    breadth = calc_breadth_score(indicators)
    macro = calc_macro_score(indicators, fomc_data)

    if mode == "day":
        weights = {"vol": 0.30, "mom": 0.30, "trend": 0.15, "breadth": 0.15, "macro": 0.10}
    else:
        weights = {"vol": 0.25, "mom": 0.25, "trend": 0.20, "breadth": 0.20, "macro": 0.10}

    market_quality_score = round(
        vol["score"] * weights["vol"]
        + mom["score"] * weights["mom"]
        + trend["score"] * weights["trend"]
        + breadth["score"] * weights["breadth"]
        + macro["score"] * weights["macro"],
        1,
    )

    execution_window_score = calc_execution_window_score(indicators)

    # Decision logic
    if market_quality_score >= 65 and execution_window_score >= 55:
        decision = "YES"
        decision_detail = "Conditions are favorable for trading."
    elif market_quality_score >= 45 or execution_window_score >= 45:
        decision = "CAUTION"
        decision_detail = "Mixed signals. Reduce position sizes and be selective."
    else:
        decision = "NO"
        decision_detail = "Conditions are unfavorable. Stay on the sidelines."

    subscores = {
        "volatility": {
            "score": vol["score"],
            "weight": weights["vol"],
            "contribution": round(vol["score"] * weights["vol"], 1),
            "direction": "bullish" if vol["score"] >= 60 else ("neutral" if vol["score"] >= 40 else "bearish"),
            "interpretation": f"Volatility score: {vol['score']:.0f}/100",
            "details": vol["details"],
        },
        "momentum": {
            "score": mom["score"],
            "weight": weights["mom"],
            "contribution": round(mom["score"] * weights["mom"], 1),
            "direction": "bullish" if mom["score"] >= 60 else ("neutral" if mom["score"] >= 40 else "bearish"),
            "interpretation": f"Momentum score: {mom['score']:.0f}/100",
            "details": mom["details"],
        },
        "trend": {
            "score": trend["score"],
            "weight": weights["trend"],
            "contribution": round(trend["score"] * weights["trend"], 1),
            "direction": "bullish" if trend["score"] >= 60 else ("neutral" if trend["score"] >= 40 else "bearish"),
            "interpretation": f"Trend score: {trend['score']:.0f}/100",
            "details": trend["details"],
        },
        "breadth": {
            "score": breadth["score"],
            "weight": weights["breadth"],
            "contribution": round(breadth["score"] * weights["breadth"], 1),
            "direction": "bullish" if breadth["score"] >= 60 else ("neutral" if breadth["score"] >= 40 else "bearish"),
            "interpretation": f"Breadth score: {breadth['score']:.0f}/100",
            "details": breadth["details"],
        },
        "macro": {
            "score": macro["score"],
            "weight": weights["macro"],
            "contribution": round(macro["score"] * weights["macro"], 1),
            "direction": "bullish" if macro["score"] >= 60 else ("neutral" if macro["score"] >= 40 else "bearish"),
            "interpretation": f"Macro score: {macro['score']:.0f}/100",
            "details": macro["details"],
        },
    }

    return {
        "market_quality_score": market_quality_score,
        "execution_window_score": execution_window_score,
        "decision": decision,
        "decision_detail": decision_detail,
        "mode": mode,
        "subscores": subscores,
    }
