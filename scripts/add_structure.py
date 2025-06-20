#!/usr/bin/env python3
"""Utility to compute fractal points and basic market structure.

This module exposes two functions:
- ``calculate_fractals`` computes fractal high/low points for a price series.
- ``calculate_structure`` derives a simple bullish/bearish/neutral structure
  based on fractal breaks.

The script can also be executed directly. See ``main`` for CLI usage.
"""
from __future__ import annotations

import argparse
import pandas as pd
from typing import Tuple


def calculate_fractals(df: pd.DataFrame, window: int = 2) -> pd.DataFrame:
    """Identify fractal highs and lows.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame with ``High`` and ``Low`` columns.
    window : int, optional
        Number of bars on each side used to detect a fractal. Default ``2``.

    Returns
    -------
    pandas.DataFrame
        DataFrame containing boolean ``fractal_high`` and ``fractal_low`` columns.
    """
    if not {"High", "Low"}.issubset(df.columns):
        raise ValueError("DataFrame must contain 'High' and 'Low' columns")

    fractals = pd.DataFrame(False, index=df.index, columns=["fractal_high", "fractal_low"])

    highs = df["High"].values
    lows = df["Low"].values

    for i in range(window, len(df) - window):
        hi_slice = highs[i - window : i + window + 1]
        lo_slice = lows[i - window : i + window + 1]
        if highs[i] == hi_slice.max():
            fractals.iat[i, 0] = True
        if lows[i] == lo_slice.min():
            fractals.iat[i, 1] = True

    return fractals


def calculate_structure(df: pd.DataFrame, fractals: pd.DataFrame) -> pd.Series:
    """Derive a simple market structure series.

    The structure is updated when price closes above the last fractal high
    or below the last fractal low.
    """
    if not {"Close"}.issubset(df.columns):
        raise ValueError("DataFrame must contain 'Close' column")

    structure = pd.Series("neutral", index=df.index, dtype=object)
    last_high: float | None = None
    last_low: float | None = None
    current = "neutral"

    for idx in range(len(df)):
        if fractals["fractal_high"].iat[idx]:
            last_high = df["High"].iat[idx]
        if fractals["fractal_low"].iat[idx]:
            last_low = df["Low"].iat[idx]

        close_price = df["Close"].iat[idx]
        if last_high is not None and close_price > last_high:
            current = "bullish"
            last_low = None
        elif last_low is not None and close_price < last_low:
            current = "bearish"
            last_high = None

        structure.iat[idx] = current

    return structure


def _load_dataframe(path: str) -> pd.DataFrame:
    """Load a CSV file with a date index."""
    df = pd.read_csv(path, parse_dates=True, index_col=0)
    return df


def main(argv: Tuple[str, ...] | None = None) -> None:
    """Entry point for the command line interface."""
    parser = argparse.ArgumentParser(description="Append fractal and structure data to a CSV file")
    parser.add_argument("input", help="Path to input CSV containing OHLC data")
    parser.add_argument("-o", "--output", help="Optional path to save the annotated CSV")
    parser.add_argument("-n", "--window", type=int, default=2, help="Fractal window size")
    args = parser.parse_args(argv)

    df = _load_dataframe(args.input)
    fractals = calculate_fractals(df, window=args.window)
    df = df.join(fractals)
    df["structure"] = calculate_structure(df, fractals)

    if args.output:
        df.to_csv(args.output)
    else:
        print(df.to_csv())


if __name__ == "__main__":
    main()
