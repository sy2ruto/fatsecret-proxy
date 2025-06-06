#!/usr/bin/env python3
"""Simple monitor for sudden stock drops using Alpha Vantage data."""
import os
import time
import requests
from typing import Dict, List

API_KEY = os.environ.get("ALPHA_VANTAGE_API_KEY")
BASE_URL = "https://www.alphavantage.co/query"


def get_current_price(symbol: str) -> float:
    """Fetch the latest closing price for a stock symbol."""
    if not API_KEY:
        raise RuntimeError("Missing ALPHA_VANTAGE_API_KEY environment variable")
    params = {
        "function": "TIME_SERIES_INTRADAY",
        "symbol": symbol,
        "interval": "1min",
        "apikey": API_KEY,
    }
    response = requests.get(BASE_URL, params=params, timeout=10)
    data = response.json()
    series = data.get("Time Series (1min)")
    if not series:
        raise ValueError(f"Unexpected response for {symbol}: {data}")
    # The first entry is the most recent timestamp
    latest = next(iter(series.values()))
    return float(latest["4. close"])


def monitor_drops(symbols: List[str], threshold: float = 0.05, interval: int = 60) -> None:
    """Monitor symbols and print a message if the price drops beyond threshold."""
    last_prices: Dict[str, float] = {}
    for symbol in symbols:
        last_prices[symbol] = get_current_price(symbol)
        print(f"Initial price for {symbol}: {last_prices[symbol]}")

    while True:
        time.sleep(interval)
        for symbol in symbols:
            current = get_current_price(symbol)
            last = last_prices[symbol]
            drop = (last - current) / last
            if drop >= threshold:
                print(f"{symbol} dropped {drop * 100:.2f}% from {last} to {current}")
            last_prices[symbol] = current


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Monitor sudden stock drops")
    parser.add_argument("symbols", nargs="+", help="Stock symbols to monitor")
    parser.add_argument("--threshold", type=float, default=0.05, help="Drop threshold as a fraction")
    parser.add_argument("--interval", type=int, default=60, help="Check interval in seconds")
    args = parser.parse_args()
    monitor_drops(args.symbols, args.threshold, args.interval)
