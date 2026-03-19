from typing import Any


def generate_summary(scores: dict[str, Any], indicators: dict[str, Any]) -> str:
    mq = scores["market_quality_score"]
    ew = scores["execution_window_score"]
    decision = scores["decision"]
    regime = indicators.get("regime", "UPTREND")
    vix = indicators.get("vix_level")
    rsi = indicators.get("spy_rsi14")
    mode = scores.get("mode", "swing")

    sections: list[str] = []

    # Overall assessment
    if decision == "YES":
        sections.append(
            f"Market conditions are favorable for {mode} trading. "
            f"The overall market quality score is {mq:.0f}/100 with an execution window score of {ew}/100."
        )
    elif decision == "CAUTION":
        sections.append(
            f"Market conditions are mixed for {mode} trading. Proceed with caution. "
            f"The overall market quality score is {mq:.0f}/100 with an execution window score of {ew}/100. "
            "Consider reducing position sizes."
        )
    else:
        sections.append(
            f"Market conditions are unfavorable for {mode} trading. "
            f"The overall market quality score is {mq:.0f}/100 with an execution window score of {ew}/100. "
            "Consider staying on the sidelines or hedging existing positions."
        )

    # Volatility context
    vol_score = scores["subscores"]["volatility"]["score"]
    if vix is not None:
        if vol_score >= 70:
            sections.append(
                f"Volatility is low and supportive. VIX at {vix:.1f} suggests calm markets and favorable conditions for directional trades."
            )
        elif vol_score >= 45:
            sections.append(
                f"Volatility is moderate. VIX at {vix:.1f} is in a neutral zone. Watch for sudden spikes that could signal regime change."
            )
        else:
            sections.append(
                f"Volatility is elevated. VIX at {vix:.1f} indicates heightened fear. "
                "Consider tighter stops and smaller position sizes."
            )

    # Trend and momentum
    trend_score = scores["subscores"]["trend"]["score"]
    mom_score = scores["subscores"]["momentum"]["score"]

    regime_text = {
        "UPTREND": "a confirmed uptrend with prices above key moving averages",
        "PULLBACK_IN_UPTREND": "a pullback within a broader uptrend. This could be a buying opportunity if support holds",
        "BEAR_RALLY": "a bear market rally. Rallies in downtrends tend to be sharp but short-lived",
        "DOWNTREND": "a downtrend with prices below key moving averages. Caution is warranted",
    }
    sections.append(f"The market regime is {regime_text.get(regime, 'unclear')}.")

    if mom_score >= 65:
        sections.append("Momentum is broad-based and healthy, with most sectors participating in the move.")
    elif mom_score >= 40:
        sections.append("Momentum is mixed, with uneven sector participation. Be selective in entries.")
    else:
        sections.append("Momentum is weak and narrow. Few sectors are showing strength.")

    # Breadth
    breadth_score = scores["subscores"]["breadth"]["score"]
    pct_50 = indicators.get("pct_above_ma50", 50)
    if breadth_score >= 65:
        sections.append(
            f"Market breadth is healthy. {pct_50:.0f}% of sectors are above their 50-day moving average, "
            "indicating broad participation."
        )
    elif breadth_score >= 40:
        sections.append(
            f"Breadth is average with {pct_50:.0f}% of sectors above their 50-day MA. "
            "The rally may be narrowing."
        )
    else:
        sections.append(
            f"Breadth is poor with only {pct_50:.0f}% of sectors above their 50-day MA. "
            "The market is being carried by few sectors."
        )

    # Macro risks
    macro_score = scores["subscores"]["macro"]["score"]
    fomc_details = [d for d in scores["subscores"]["macro"]["details"] if d["name"] == "FOMC Proximity"]
    if fomc_details and fomc_details[0]["value"] <= 5:
        sections.append(
            f"FOMC meeting is {fomc_details[0]['value']} days away. "
            "Expect increased uncertainty and potential volatility around the announcement. "
            "Consider waiting until after the decision."
        )
    if macro_score < 40:
        sections.append(
            "Macro headwinds are significant. Rising yields or a strong dollar may weigh on equities."
        )

    # Actionable advice
    if decision == "YES":
        if rsi is not None and rsi > 65:
            sections.append(
                "RSI is approaching overbought territory. While the trend supports entries, "
                "avoid chasing. Look for intraday pullbacks to enter."
            )
        else:
            sections.append(
                "Look for setups aligned with the trend. Focus on sectors showing relative strength."
            )
    elif decision == "CAUTION":
        sections.append(
            "If trading, use smaller position sizes (50-75% of normal). "
            "Focus on high-conviction setups with clear risk/reward. Keep stops tight."
        )
    else:
        sections.append(
            "This is not a favorable environment for new positions. "
            "Focus on capital preservation, hedging, or paper trading until conditions improve."
        )

    return " ".join(sections)
