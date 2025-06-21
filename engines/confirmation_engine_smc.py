"""Confirmation Engine SMC
"""

from __future__ import annotations

import json
import traceback
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd


class ConfirmationConstants:
    CHOCH = "CHoCH"
    BOS = "BOS"
    LTF = "LTF"


def _find_ltf_swing_points(series: pd.Series, n: int = 2) -> pd.Series:
    """Identify swing points in a series."""
    if not isinstance(series, pd.Series) or series.empty or len(series) < 2 * n + 1:
        return pd.Series(dtype=float)

    local_max = series.rolling(window=2 * n + 1, center=True, min_periods=n + 1).max()
    local_min = series.rolling(window=2 * n + 1, center=True, min_periods=n + 1).min()
    swing_points = pd.Series(np.nan, index=series.index)
    swing_points[series == local_max] = series[series == local_max]
    swing_points[series == local_min] = series[series == local_min]
    return swing_points


def _find_ltf_poi_candle(
    df_slice: pd.DataFrame, break_candle_index: int, is_bullish_break: bool
) -> Optional[Tuple[pd.Timestamp, List[float], str]]:
    """Find the candle likely causing the structure break."""
    if break_candle_index <= 0 or break_candle_index >= len(df_slice):
        print("[WARN][ConfirmEngine] Invalid break_candle_index provided to _find_ltf_poi_candle.")
        return None

    lookback_limit = 10
    search_end_idx = break_candle_index - 1
    search_start_idx = max(0, search_end_idx - lookback_limit)

    origin_candle = None
    origin_candle_iloc = -1

    for i in range(search_end_idx, search_start_idx - 1, -1):
        if i < 0 or i >= len(df_slice):
            continue
        try:
            candle = df_slice.iloc[i]
            if not all(col in candle.index for col in ["Close", "Open"]):
                continue
            if candle[["Close", "Open"]].isnull().any():
                continue
            is_bullish_candle = candle["Close"] > candle["Open"]
            is_bearish_candle = candle["Close"] < candle["Open"]

            if is_bullish_break and is_bearish_candle:
                origin_candle = candle
                origin_candle_iloc = i
                break
            elif not is_bullish_break and is_bullish_candle:
                origin_candle = candle
                origin_candle_iloc = i
                break
        except IndexError:
            print(
                f"[WARN][ConfirmEngine] IndexError accessing candle at iloc {i} in _find_ltf_poi_candle."
            )
            continue

    if origin_candle is not None and not origin_candle.isnull().all():
        poi_timestamp = origin_candle.name
        if all(
            col in origin_candle.index and pd.notna(origin_candle[col])
            for col in ["Low", "High"]
        ):
            poi_range = [origin_candle["Low"], origin_candle["High"]]
            poi_type = "OB"
            print(
                f"[DEBUG][ConfirmEngine] Found potential LTF POI candle ({poi_type}) at index {origin_candle_iloc} ({poi_timestamp}) Range: {poi_range}"
            )
            if not isinstance(poi_timestamp, pd.Timestamp):
                poi_timestamp = pd.Timestamp(poi_timestamp)
            return poi_timestamp, poi_range, poi_type
        print(
            f"[WARN][ConfirmEngine] Identified POI candle at {origin_candle_iloc} has missing High/Low values."
        )
        return None
    print(
        f"[DEBUG][ConfirmEngine] No clear origin POI candle found within lookback before break at index {break_candle_index}"
    )
    return None


def confirm_smc_entry(
    htf_poi: Dict,
    ltf_data: pd.DataFrame,
    strategy_variant: str,
    config: Optional[Dict] = None,
    structure_context: Optional[Dict] = None,
) -> Dict[str, Any]:
    """Confirm potential trade entry using LTF structure."""
    print(
        f"[INFO][ConfirmEngine] Running Confirmation Engine for HTF POI Type: {htf_poi.get('type')}..."
    )
    result: Dict[str, Any] = {
        "confirmation_status": False,
        "confirmation_type": None,
        "choch_details": None,
        "bos_details": None,
        "ltf_poi_range": None,
        "ltf_poi_timestamp": None,
        "ltf_poi_type": None,
        "conviction_score": 3,
        "error": None,
    }

    if ltf_data is None or ltf_data.empty:
        result["error"] = "LTF data for confirmation is missing or empty."
        print(f"[ERROR][ConfirmEngine] {result['error']}")
        return result
    if not isinstance(ltf_data.index, pd.DatetimeIndex):
        result["error"] = "LTF data index must be a DatetimeIndex."
        print(f"[ERROR][ConfirmEngine] {result['error']}")
        return result
    if not all(col in ltf_data.columns for col in ["High", "Low", "Close"]):
        result["error"] = "LTF data missing required High/Low/Close columns."
        print(f"[ERROR][ConfirmEngine] {result['error']}")
        return result

    htf_poi_type = htf_poi.get("type")
    if htf_poi_type not in ["Bullish", "Bearish"]:
        result["error"] = f"Invalid HTF POI type: {htf_poi_type}"
        print(f"[ERROR][ConfirmEngine] {result['error']}")
        return result

    if config is None:
        config = {}
    confirmation_lookback = config.get("confirmation_lookback", 30)
    swing_n = config.get("swing_n", 2)
    require_bos = config.get("require_bos", False)

    analysis_df = ltf_data.tail(confirmation_lookback).copy()
    if len(analysis_df) < (2 * swing_n + 3):
        result[
            "error"
        ] = f"Insufficient LTF data ({len(analysis_df)}) for confirmation lookback ({confirmation_lookback}) and swing detection (n={swing_n})."
        print(f"[WARN][ConfirmEngine] {result['error']}")
        return result

    print(f"[DEBUG][ConfirmEngine] Analyzing last {len(analysis_df)} bars of LTF data.")

    try:
        local_highs = _find_ltf_swing_points(analysis_df["High"], n=swing_n)
        local_lows = _find_ltf_swing_points(analysis_df["Low"], n=swing_n)

        swings = []
        for idx, price in local_highs.dropna().items():
            try:
                loc = analysis_df.index.get_loc(idx)
                swings.append({"timestamp": idx, "price": price, "type": "High", "iloc": loc})
            except KeyError:
                print(f"[WARN][ConfirmEngine] Could not get iloc for swing high at {idx}")
        for idx, price in local_lows.dropna().items():
            try:
                loc = analysis_df.index.get_loc(idx)
                swings.append({"timestamp": idx, "price": price, "type": "Low", "iloc": loc})
            except KeyError:
                print(f"[WARN][ConfirmEngine] Could not get iloc for swing low at {idx}")

        swings.sort(key=lambda x: x["timestamp"])

        if len(swings) < 2:
            result["error"] = "Not enough swing points identified in the LTF confirmation window."
            print(f"[INFO][ConfirmEngine] {result['error']}")
            return result

        print(f"[DEBUG][ConfirmEngine] Identified {len(swings)} local swing points in confirmation window.")

        def detect_structure_break(direction: str, swings: List[dict], analysis_df: pd.DataFrame):
            break_found = False
            break_type = None
            break_details: Dict[str, Any] = {}
            ltf_poi_details = None
            if direction == "Bullish":
                last_high = next((s for s in reversed(swings) if s["type"] == "High"), None)
                if last_high is None:
                    return False, None, {}, None
                target_break_level = last_high["price"]
                target_break_time = last_high["timestamp"]
                break_check_df = analysis_df[analysis_df.index > target_break_time]
                if not break_check_df.empty:
                    break_candle_mask = break_check_df["Close"] > target_break_level
                    if break_candle_mask.any():
                        first_break_candle_timestamp = break_check_df[break_candle_mask].index[0]
                        first_break_candle_price = break_check_df.loc[
                            first_break_candle_timestamp, "Close"
                        ]
                        break_found = True
                        break_type = ConfirmationConstants.CHOCH
                        break_details = {
                            "timestamp": first_break_candle_timestamp.isoformat(),
                            "price": first_break_candle_price,
                            "type": "Bullish",
                            "broken_swing_timestamp": target_break_time.isoformat(),
                        }
                        print(
                            f"[INFO][ConfirmEngine] Bullish {break_type} confirmed at {break_details['timestamp']} (Price: {break_details['price']:.5f}), broke high at {target_break_time}"
                        )
                        try:
                            break_candle_iloc = analysis_df.index.get_loc(
                                first_break_candle_timestamp
                            )
                            ltf_poi_details = _find_ltf_poi_candle(
                                analysis_df, break_candle_iloc, is_bullish_break=True
                            )
                        except KeyError:
                            print(
                                f"[WARN][ConfirmEngine] Could not get iloc for break candle at {first_break_candle_timestamp} to find POI."
                            )
            elif direction == "Bearish":
                last_low = next((s for s in reversed(swings) if s["type"] == "Low"), None)
                if last_low is None:
                    return False, None, {}, None
                target_break_level = last_low["price"]
                target_break_time = last_low["timestamp"]
                break_check_df = analysis_df[analysis_df.index > target_break_time]
                if not break_check_df.empty:
                    break_candle_mask = break_check_df["Close"] < target_break_level
                    if break_candle_mask.any():
                        first_break_candle_timestamp = break_check_df[break_candle_mask].index[0]
                        first_break_candle_price = break_check_df.loc[
                            first_break_candle_timestamp, "Close"
                        ]
                        break_found = True
                        break_type = ConfirmationConstants.CHOCH
                        break_details = {
                            "timestamp": first_break_candle_timestamp.isoformat(),
                            "price": first_break_candle_price,
                            "type": "Bearish",
                            "broken_swing_timestamp": target_break_time.isoformat(),
                        }
                        print(
                            f"[INFO][ConfirmEngine] Bearish {break_type} confirmed at {break_details['timestamp']} (Price: {break_details['price']:.5f}), broke low at {target_break_time}"
                        )
                        try:
                            break_candle_iloc = analysis_df.index.get_loc(
                                first_break_candle_timestamp
                            )
                            ltf_poi_details = _find_ltf_poi_candle(
                                analysis_df, break_candle_iloc, is_bullish_break=False
                            )
                        except KeyError:
                            print(
                                f"[WARN][ConfirmEngine] Could not get iloc for break candle at {first_break_candle_timestamp} to find POI."
                            )
            return break_found, break_type, break_details, ltf_poi_details

        break_found, break_type, break_details, ltf_poi_details = detect_structure_break(
            htf_poi_type, swings, analysis_df
        )

        if break_found:
            tf_prefix = ConfirmationConstants.LTF
            if hasattr(analysis_df.index, "freqstr") and analysis_df.index.freqstr:
                freq = analysis_df.index.freqstr.upper()
                freq_num = "".join(filter(str.isdigit, freq))
                freq_unit = "".join(filter(str.isalpha, freq))
                if freq_unit in ["T", "MIN"]:
                    tf_prefix = f"M{freq_num}"
                elif freq_unit == "H":
                    tf_prefix = f"H{freq_num}"
                elif freq_unit == "D":
                    tf_prefix = f"D{freq_num}"

            result["confirmation_status"] = True
            result["confirmation_type"] = f"{tf_prefix}_{break_type}"
            if break_type == ConfirmationConstants.CHOCH:
                result["choch_details"] = break_details
            elif break_type == ConfirmationConstants.BOS:
                result["bos_details"] = break_details
            else:
                result["choch_details"] = break_details
            if ltf_poi_details:
                result["ltf_poi_timestamp"] = (
                    ltf_poi_details[0].isoformat()
                    if isinstance(ltf_poi_details[0], pd.Timestamp)
                    else None
                )
                result["ltf_poi_range"] = ltf_poi_details[1]
                result["ltf_poi_type"] = ltf_poi_details[2]
            else:
                print(
                    "[WARN][ConfirmEngine] Confirmation break found, but failed to identify originating LTF POI candle."
                )
        else:
            print(
                "[INFO][ConfirmEngine] No confirming LTF structure break (CHoCH/BOS) found in the lookback window."
            )
            result["confirmation_status"] = False

    except Exception as exc:  # pragma: no cover - debugging helper
        result["error"] = f"Error during confirmation analysis: {exc}"
        print(f"[ERROR][ConfirmEngine] {result['error']}")
        traceback.print_exc()
        result["confirmation_status"] = False

    print(f"[INFO][ConfirmEngine] Confirmation Status: {result['confirmation_status']}")
    return result


if __name__ == "__main__":  # pragma: no cover - simple smoke test
    print("--- Testing Confirmation Engine (SMC) ---")

    htf_poi_bullish = {"type": "Bullish", "range": [1.0990, 1.0995]}
    htf_poi_bearish = {"type": "Bearish", "range": [1.1055, 1.1060]}

    base_time = pd.Timestamp("2024-04-28 14:00:00", tz="UTC")
    periods = 40
    timestamps = pd.date_range(start=base_time, periods=periods, freq="15T")

    data1 = {
        "Open": np.linspace(1.1005, 1.0998, periods),
        "Close": np.linspace(1.1003, 1.0996, periods),
    }
    data1["High"] = np.maximum(data1["Open"], data1["Close"]) + 0.0003
    data1["Low"] = np.minimum(data1["Open"], data1["Close"]) - 0.0003
    ltf_df1 = pd.DataFrame(data1, index=timestamps)
    swing_low_iloc = 10
    swing_high_iloc = 20
    break_iloc = 30
    ltf_df1.iloc[swing_low_iloc, ltf_df1.columns.get_loc("Low")] = 1.0992
    ltf_df1.iloc[swing_high_iloc, ltf_df1.columns.get_loc("High")] = 1.1002
    ltf_df1.iloc[break_iloc, ltf_df1.columns.get_loc("Close")] = 1.1005
    ltf_df1.iloc[break_iloc - 1, ltf_df1.columns.get_loc("Open")] = (
        ltf_df1.iloc[break_iloc - 1]["Close"] + 0.0001
    )
    ltf_df1.iloc[break_iloc - 1, ltf_df1.columns.get_loc("Low")] = (
        ltf_df1.iloc[break_iloc - 1]["Close"] - 0.0002
    )
    ltf_df1.iloc[break_iloc - 1, ltf_df1.columns.get_loc("High")] = (
        ltf_df1.iloc[break_iloc - 1]["Open"] + 0.00005
    )

    print("\n--- Testing Bullish Confirmation ---")
    result1 = confirm_smc_entry(htf_poi_bullish, ltf_df1, "Inv")
    print(json.dumps(result1, indent=2, default=str))

    data2 = {
        "Open": np.linspace(1.1045, 1.1052, periods),
        "Close": np.linspace(1.1047, 1.1054, periods),
    }
    data2["High"] = np.maximum(data2["Open"], data2["Close"]) + 0.0003
    data2["Low"] = np.minimum(data2["Open"], data2["Close"]) - 0.0003
    ltf_df2 = pd.DataFrame(data2, index=timestamps)
    swing_high_iloc = 10
    swing_low_iloc = 20
    break_iloc = 30
    ltf_df2.iloc[swing_high_iloc, ltf_df2.columns.get_loc("High")] = 1.1058
    ltf_df2.iloc[swing_low_iloc, ltf_df2.columns.get_loc("Low")] = 1.1048
    ltf_df2.iloc[break_iloc, ltf_df2.columns.get_loc("Close")] = 1.1045
    ltf_df2.iloc[break_iloc - 1, ltf_df2.columns.get_loc("Open")] = (
        ltf_df2.iloc[break_iloc - 1]["Close"] - 0.0001
    )
    ltf_df2.iloc[break_iloc - 1, ltf_df2.columns.get_loc("High")] = (
        ltf_df2.iloc[break_iloc - 1]["Open"] + 0.0002
    )
    ltf_df2.iloc[break_iloc - 1, ltf_df2.columns.get_loc("Low")] = (
        ltf_df2.iloc[break_iloc - 1]["Open"] - 0.00005
    )

    print("\n--- Testing Bearish Confirmation ---")
    result2 = confirm_smc_entry(htf_poi_bearish, ltf_df2, "Inv")
    print(json.dumps(result2, indent=2, default=str))

    data3 = {
        "Open": np.linspace(1.1000, 1.0990, periods),
        "Close": np.linspace(1.0998, 1.0988, periods),
    }
    data3["High"] = np.maximum(data3["Open"], data3["Close"]) + 0.0002
    data3["Low"] = np.minimum(data3["Open"], data3["Close"]) - 0.0002
    ltf_df3 = pd.DataFrame(data3, index=timestamps)

    print("\n--- Testing No Confirmation ---")
    result3 = confirm_smc_entry(htf_poi_bullish, ltf_df3, "Inv")
    print(json.dumps(result3, indent=2, default=str))

    print("\n--- Test Complete ---")
