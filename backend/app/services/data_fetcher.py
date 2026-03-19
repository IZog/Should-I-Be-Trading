import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Any

import numpy as np
import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)

TICKERS = [
    "SPY", "QQQ", "^VIX", "^VVIX", "DX-Y.NYB", "^TNX",
    "XLK", "XLF", "XLE", "XLV", "XLI", "XLY", "XLP", "XLU", "XLB", "XLRE", "XLC",
]

SECTOR_NAMES = {
    "XLK": "Technology",
    "XLF": "Financials",
    "XLE": "Energy",
    "XLV": "Health Care",
    "XLI": "Industrials",
    "XLY": "Consumer Discretionary",
    "XLP": "Consumer Staples",
    "XLU": "Utilities",
    "XLB": "Materials",
    "XLRE": "Real Estate",
    "XLC": "Communication Services",
}

SECTOR_TICKERS = list(SECTOR_NAMES.keys())

_executor = ThreadPoolExecutor(max_workers=4)


def _download_data() -> dict[str, Any]:
    """Synchronous download of all market data via yfinance."""
    result: dict[str, Any] = {}

    try:
        tickers_str = " ".join(TICKERS)
        df = yf.download(tickers_str, period="1y", group_by="ticker", progress=False, threads=True)

        for ticker in TICKERS:
            try:
                if len(TICKERS) == 1:
                    ticker_df = df
                else:
                    ticker_df = df[ticker] if ticker in df.columns.get_level_values(0) else pd.DataFrame()

                if ticker_df.empty or ticker_df["Close"].dropna().empty:
                    raise ValueError(f"No data for {ticker}")

                closes = ticker_df["Close"].dropna()
                current_price = float(closes.iloc[-1])
                prev_close = float(closes.iloc[-2]) if len(closes) >= 2 else current_price

                history = closes.values.astype(float)
                history = history[~np.isnan(history)]

                result[ticker] = {
                    "current_price": current_price,
                    "prev_close": prev_close,
                    "change_pct": ((current_price - prev_close) / prev_close * 100) if prev_close != 0 else 0.0,
                    "history": history.tolist(),
                    "closes": closes,
                }

                # 5-day data
                if len(closes) >= 6:
                    price_5d_ago = float(closes.iloc[-6])
                    result[ticker]["price_5d_ago"] = price_5d_ago
                    result[ticker]["change_5d_pct"] = ((current_price - price_5d_ago) / price_5d_ago * 100) if price_5d_ago != 0 else 0.0
                else:
                    result[ticker]["price_5d_ago"] = current_price
                    result[ticker]["change_5d_pct"] = 0.0

                # 52-week high/low
                result[ticker]["high_52w"] = float(np.max(history))
                result[ticker]["low_52w"] = float(np.min(history))

            except Exception as e:
                logger.warning(f"Failed to process {ticker}: {e}")
                result[ticker] = _neutral_ticker_data(ticker)

    except Exception as e:
        logger.error(f"Bulk download failed: {e}")
        for ticker in TICKERS:
            result[ticker] = _neutral_ticker_data(ticker)

    # DXY fallback to UUP
    if result.get("DX-Y.NYB", {}).get("current_price") is None:
        try:
            uup_df = yf.download("UUP", period="1y", progress=False)
            if not uup_df.empty:
                closes = uup_df["Close"].dropna()
                current_price = float(closes.iloc[-1])
                prev_close = float(closes.iloc[-2]) if len(closes) >= 2 else current_price
                history = closes.values.astype(float)
                history = history[~np.isnan(history)]
                result["DX-Y.NYB"] = {
                    "current_price": current_price,
                    "prev_close": prev_close,
                    "change_pct": ((current_price - prev_close) / prev_close * 100) if prev_close != 0 else 0.0,
                    "history": history.tolist(),
                    "closes": closes,
                    "price_5d_ago": float(closes.iloc[-6]) if len(closes) >= 6 else current_price,
                    "change_5d_pct": 0.0,
                    "high_52w": float(np.max(history)),
                    "low_52w": float(np.min(history)),
                    "is_uup_proxy": True,
                }
                if len(closes) >= 6:
                    result["DX-Y.NYB"]["change_5d_pct"] = (
                        (current_price - float(closes.iloc[-6])) / float(closes.iloc[-6]) * 100
                    )
        except Exception as e:
            logger.warning(f"UUP fallback also failed: {e}")

    # VVIX: if unavailable, set to None
    if result.get("^VVIX", {}).get("current_price") is None:
        result["^VVIX"] = _neutral_ticker_data("^VVIX")
        result["^VVIX"]["current_price"] = None

    return result


def _neutral_ticker_data(ticker: str) -> dict[str, Any]:
    return {
        "current_price": None,
        "prev_close": None,
        "change_pct": 0.0,
        "history": [],
        "closes": pd.Series(dtype=float),
        "price_5d_ago": None,
        "change_5d_pct": 0.0,
        "high_52w": None,
        "low_52w": None,
    }


async def fetch_all_data() -> dict[str, Any]:
    """Async wrapper that runs yfinance download in a thread pool."""
    loop = asyncio.get_event_loop()
    data = await loop.run_in_executor(_executor, _download_data)
    return data
