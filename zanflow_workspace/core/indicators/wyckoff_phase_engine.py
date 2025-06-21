# core/indicators/wyckoff_phase_engine_v1.py
# Author: ZANZIBAR LLM Assistant (Generated for Tomasz)
# Date: 2025-04-29
# Version: 1.0.0 (Wyckoff Accumulation Phase Detector - Basic)
# Description:
#   Detects Wyckoff Accumulation schematics from HTF OHLCV data (Simplified V1).
#   Outputs potential phase points (SC, AR, ST, Spring, Test, LPS, SOS)
#   and phase classification (A/B/C/D/E). Includes basic PnF target estimation.

import pandas as pd
import numpy as np
from typing import Dict, Optional, Any
import traceback
from datetime import timezone # Import timezone

# --- Wyckoff Event Detection (Simplified V1) ---
def _detect_wyckoff_events(ohlcv: pd.DataFrame, config: Dict) -> Dict:
    """
    Detect Wyckoff schematic key events (SC, AR, ST, Spring, Test, LPS, SOS).
    NOTE: This is a simplified V1 implementation using basic min/max and volume checks.
          Does not perform full VSA or detailed schematic sequence validation.
    """
    events = {}
    if ohlcv.empty or len(ohlcv) < 10: # Need some data
        print("[WARN][WyckoffDetect] Insufficient data for event detection.")
        return events

    # --- Configuration ---
    pivot_lookback = config.get("pivot_lookback", 20)
    min_volume_multiplier = config.get("min_volume_surge_multiplier", 1.8) # Default multiplier for climax volume
    spring_test_lookback = config.get("spring_test_lookback", 5) # Bars after Spring/ST to look for Test/LPS

    try:
        # --- Ensure Volume & Calculate Avg Volume ---
        if 'Volume' in ohlcv.columns:
            min_vol_periods = max(1, int(pivot_lookback / 2))
            ohlcv['Avg_Volume'] = ohlcv['Volume'].rolling(window=pivot_lookback, min_periods=min_vol_periods).mean()
            first_valid_avg_vol = ohlcv['Avg_Volume'].dropna().iloc[0] if not ohlcv['Avg_Volume'].dropna().empty else 1
            ohlcv['Avg_Volume'] = ohlcv['Avg_Volume'].fillna(first_valid_avg_vol).fillna(1) # Fill NaNs
        else:
            print("[WARN][WyckoffDetect] Volume data missing. Event detection accuracy reduced.")
            ohlcv['Avg_Volume'] = 1 # Assign dummy value to avoid errors

        # --- SC (Selling Climax) Detection ---
        sc_idx = ohlcv['Low'].idxmin()
        sc_value = ohlcv.loc[sc_idx, 'Low'] if pd.notna(sc_idx) else np.nan

        if pd.notna(sc_idx):
            sc_volume = ohlcv.loc[sc_idx, 'Volume'] if 'Volume' in ohlcv.columns else 0
            avg_volume_at_sc = ohlcv.loc[sc_idx, 'Avg_Volume']
            if sc_volume >= min_volume_multiplier * avg_volume_at_sc:
                events['SC'] = {"price": sc_value, "time": sc_idx, "volume": sc_volume}
                print(f"[DEBUG][WyckoffDetect] Potential SC detected at {sc_idx} (Price: {sc_value:.4f}, Vol: {sc_volume})")
            else:
                 events['LowPoint1'] = {"price": sc_value, "time": sc_idx, "volume": sc_volume}
                 print(f"[DEBUG][WyckoffDetect] Low point detected at {sc_idx} (Price: {sc_value:.4f}, Vol: {sc_volume}) - Volume below SC threshold.")
        else:
            print("[WARN][WyckoffDetect] Could not find minimum low for SC detection.")
            return events

        ref_low_event = events.get('SC') or events.get('LowPoint1')
        if not ref_low_event: return events

        # --- AR (Automatic Rally) Detection ---
        post_sc_df = ohlcv.loc[ref_low_event['time']:]
        if not post_sc_df.empty and len(post_sc_df) > 1:
            ar_idx = post_sc_df['High'].iloc[1:].idxmax()
            ar_value = post_sc_df.loc[ar_idx, 'High'] if pd.notna(ar_idx) else np.nan
            if pd.notna(ar_idx):
                events['AR'] = {"price": ar_value, "time": ar_idx}
                print(f"[DEBUG][WyckoffDetect] Potential AR detected at {ar_idx} (Price: {ar_value:.4f})")
            else: print("[WARN][WyckoffDetect] Could not find max high for AR detection after SC."); return events
        else: return events

        # --- ST (Secondary Test) Detection ---
        post_ar_df = post_sc_df.loc[events['AR']['time']:]
        if not post_ar_df.empty and len(post_ar_df) > 1:
            st_idx = post_ar_df['Low'].iloc[1:].idxmin()
            st_value = post_ar_df.loc[st_idx, 'Low'] if pd.notna(st_idx) else np.nan
            if pd.notna(st_idx):
                 st_volume = ohlcv.loc[st_idx, 'Volume'] if 'Volume' in ohlcv.columns else 0
                 events['ST'] = {"price": st_value, "time": st_idx, "volume": st_volume}
                 print(f"[DEBUG][WyckoffDetect] Potential ST detected at {st_idx} (Price: {st_value:.4f}, Vol: {st_volume})")
            else: print("[WARN][WyckoffDetect] Could not find min low for ST detection after AR.")
        else: return events

        # --- Spring / Shakeout (Phase C) Detection ---
        st_event = events.get('ST')
        if st_event:
            support_level = min(ref_low_event['price'], st_event['price'])
            post_st_df = post_ar_df.loc[st_event['time']:]
            if not post_st_df.empty and len(post_st_df) > 1:
                 possible_spring_df = post_st_df.iloc[1:][post_st_df['Low'].iloc[1:] < support_level]
                 if not possible_spring_df.empty:
                      spring_idx = possible_spring_df['Low'].idxmin()
                      spring_value = possible_spring_df.loc[spring_idx, 'Low']
                      spring_volume = ohlcv.loc[spring_idx, 'Volume'] if 'Volume' in ohlcv.columns else 0
                      events['Spring'] = {"price": spring_value, "time": spring_idx, "volume": spring_volume}
                      print(f"[DEBUG][WyckoffDetect] Potential Spring detected at {spring_idx} (Price: {spring_value:.4f}, Vol: {spring_volume}) below support {support_level:.4f}")

                      # --- Test of Spring Detection ---
                      post_spring_df = post_st_df.loc[spring_idx:]
                      if len(post_spring_df) > 1:
                           test_candidates = post_spring_df.iloc[1:spring_test_lookback+1]
                           if not test_candidates.empty:
                                test_idx = test_candidates['Low'].idxmin()
                                test_value = test_candidates.loc[test_idx, 'Low']
                                if test_value > spring_value:
                                     test_volume = ohlcv.loc[test_idx, 'Volume'] if 'Volume' in ohlcv.columns else 0
                                     events['Test'] = {"price": test_value, "time": test_idx, "volume": test_volume}
                                     print(f"[DEBUG][WyckoffDetect] Potential Test of Spring detected at {test_idx} (Price: {test_value:.4f}, Vol: {test_volume})")

        # --- LPS (Last Point of Support) Detection ---
        ref_point_for_lps = events.get('Test') or events.get('Spring') or events.get('ST')
        if ref_point_for_lps:
            post_ref_df = ohlcv.loc[ref_point_for_lps['time']:]
            if len(post_ref_df) > spring_test_lookback:
                 lps_candidates_df = post_ref_df.iloc[1:spring_test_lookback+1]
                 if not lps_candidates_df.empty:
                      min_low_after_ref = lps_candidates_df['Low'].min()
                      if min_low_after_ref > ref_point_for_lps['price']:
                           lps_idx = lps_candidates_df['Low'].idxmin()
                           lps_value = min_low_after_ref
                           lps_volume = ohlcv.loc[lps_idx, 'Volume'] if 'Volume' in ohlcv.columns else 0
                           events['LPS'] = {"price": lps_value, "time": lps_idx, "volume": lps_volume}
                           print(f"[DEBUG][WyckoffDetect] Potential LPS detected at {lps_idx} (Price: {lps_value:.4f}, Vol: {lps_volume})")

        # --- SOS (Sign of Strength) Detection ---
        phase_c_event = events.get('Test') or events.get('Spring') or events.get('LPS')
        ar_event = events.get('AR')
        if ar_event and phase_c_event:
             resistance_level = ar_event['price']
             post_phase_c_df = ohlcv.loc[phase_c_event['time']:]
             if not post_phase_c_df.empty and len(post_phase_c_df) > 1:
                  possible_sos_df = post_phase_c_df.iloc[1:][post_phase_c_df['Close'].iloc[1:] > resistance_level]
                  if not possible_sos_df.empty:
                       sos_idx = possible_sos_df.index[0]
                       sos_value = possible_sos_df.loc[sos_idx, 'Close']
                       sos_volume = ohlcv.loc[sos_idx, 'Volume'] if 'Volume' in ohlcv.columns else 0
                       events['SOS'] = {"price": sos_value, "time": sos_idx, "volume": sos_volume}
                       print(f"[DEBUG][WyckoffDetect] Potential SOS detected at {sos_idx} (Price: {sos_value:.4f}, Vol: {sos_volume}) breaking resistance {resistance_level:.4f}")

    except Exception as e:
        print(f"[ERROR][WyckoffDetect] Error during Wyckoff event detection: {e}")
        traceback.print_exc()
        events['error'] = str(e)

    # Clean up helper column
    if 'Avg_Volume' in ohlcv.columns:
         ohlcv.drop(columns=['Avg_Volume'], inplace=True, errors='ignore')

    return events


def _classify_phases(events: Dict, config: Dict) -> Dict:
    """
    Classify Wyckoff Schematic phases A/B/C/D/E based on detected events.
    Returns a dictionary mapping phase names to start/end times.
    """
    phases = {}
    last_event_time = None

    # Phase A: Stopping the prior trend (SC to AR)
    sc_event = events.get('SC') or events.get('LowPoint1')
    ar_event = events.get('AR')
    if sc_event and ar_event and isinstance(sc_event.get('time'), pd.Timestamp) and isinstance(ar_event.get('time'), pd.Timestamp):
        phases['A'] = {'start': sc_event['time'], 'end': ar_event['time'], 'description': 'Stopping Action'}
        last_event_time = ar_event['time']
    else: return phases # Cannot define phases without initial range

    # Phase B: Building the cause (AR to ST)
    st_event = events.get('ST')
    if st_event and last_event_time and isinstance(st_event.get('time'), pd.Timestamp) and st_event['time'] > last_event_time:
        phases['B'] = {'start': last_event_time, 'end': st_event['time'], 'description': 'Building Cause'}
        last_event_time = st_event['time']
    else: pass # Continue check

    # Phase C: The test (Spring or LPS if no Spring)
    spring_event = events.get('Spring')
    test_event = events.get('Test')
    lps_event_after_b = events.get('LPS') if events.get('LPS') and last_event_time and isinstance(events['LPS'].get('time'), pd.Timestamp) and events['LPS']['time'] > last_event_time else None

    phase_c_start_time = last_event_time
    phase_c_end_time = None

    if spring_event and isinstance(spring_event.get('time'), pd.Timestamp) and spring_event['time'] > phase_c_start_time:
        phase_c_end_event = test_event if test_event and isinstance(test_event.get('time'), pd.Timestamp) and test_event['time'] > spring_event['time'] else spring_event
        phases['C'] = {'start': phase_c_start_time, 'end': phase_c_end_event['time'], 'description': 'Test (Spring/Test)'}
        phase_c_end_time = phase_c_end_event['time']
    elif lps_event_after_b:
        phases['C'] = {'start': phase_c_start_time, 'end': lps_event_after_b['time'], 'description': 'Test (LPS)'}
        phase_c_end_time = lps_event_after_b['time']

    last_event_time = phase_c_end_time if phase_c_end_time else last_event_time

    # Phase D: Breaking out of the range (SOS or LPS after Phase C)
    sos_event = events.get('SOS')
    lps_event_phase_d = events.get('LPS')

    phase_d_start_time = last_event_time
    phase_d_end_time = None

    if sos_event and phase_d_start_time and isinstance(sos_event.get('time'), pd.Timestamp) and sos_event['time'] > phase_d_start_time:
        phases['D'] = {'start': phase_d_start_time, 'end': sos_event['time'], 'description': 'Markup within Range / SOS'}
        phase_d_end_time = sos_event['time']
    elif lps_event_phase_d and phase_d_start_time and isinstance(lps_event_phase_d.get('time'), pd.Timestamp) and lps_event_phase_d['time'] > phase_d_start_time:
         if phase_c_end_time is None or lps_event_phase_d['time'] > phase_c_end_time:
              phases['D'] = {'start': phase_d_start_time, 'end': lps_event_phase_d['time'], 'description': 'Markup within Range (LPS)'}
              phase_d_end_time = lps_event_phase_d['time']

    last_event_time = phase_d_end_time if phase_d_end_time else last_event_time

    # Phase E: Markup outside the range
    if phases.get('D') and last_event_time:
        phases['E'] = {'start': last_event_time, 'end': None, 'description': 'Markup Trend'}

    return phases


def _generate_pnf_target(events: Dict, config: Dict) -> Dict:
    """
    Simple PnF target projection from Spring or LPS (Placeholder Calculation).
    Requires actual PnF chart construction for accurate counts.
    """
    # --- Placeholder PnF Logic ---
    box_size = config.get("pnf_box_size", 1.0)
    reversal = config.get("pnf_reversal", 3)
    pnf_count_base = config.get("pnf_count_base", 10) # *** PLACEHOLDER BOX COUNT ***

    target_conservative = np.nan; target_aggressive = np.nan; base_low_price = np.nan
    base_event = events.get('LPS') or events.get('Spring') or events.get('ST')

    if base_event:
        base_low_price = base_event.get('price', np.nan)
        if pd.notna(base_low_price):
            target_conservative = base_low_price + (pnf_count_base * box_size * reversal)
            aggressive_count = pnf_count_base * config.get("pnf_aggressive_multiplier", 1.5)
            target_aggressive = base_low_price + (aggressive_count * box_size * reversal)

    return {
        "target_conservative": round(target_conservative, 2) if pd.notna(target_conservative) else None,
        "target_aggressive": round(target_aggressive, 2) if pd.notna(target_aggressive) else None,
        "pnf_count_base": pnf_count_base, "box_size": box_size, "reversal": reversal,
        "projection_base_price": round(base_low_price, 2) if pd.notna(base_low_price) else None,
        "calculation_note": "Placeholder PnF count used. Requires real PnF chart analysis."
    }

# --- Main Detection Function ---
def detect_wyckoff_phases_and_events(
    df: pd.DataFrame,
    timeframe: str, # Added timeframe for context
    config: Optional[Dict] = None
    ) -> Dict[str, Any]:
    """
    Analyzes HTF price action to assign a probable Wyckoff phase and detect key events.
    Focuses on Accumulation for V1.

    Args:
        df (pd.DataFrame): HTF OHLCV dataframe with DatetimeIndex. Requires 'High', 'Low', 'Close', 'Volume'.
        timeframe (str): Identifier for the timeframe being analyzed (e.g., 'H1', 'D1').
        config (Dict, optional): Configuration parameters for event detection, PnF, etc.

    Returns:
        Dict: { 'detected_events': Dict, 'phase_classification': Dict, 'current_phase': str, 'pnf_targets': Dict | None, 'error': str | None }
    """
    print(f"[INFO][WyckoffEngineV1] Running Wyckoff Phase Detection for TF={timeframe}...")
    result = { 'detected_events': {}, 'phase_classification': {}, 'current_phase': 'Unknown', 'pnf_targets': None, 'error': None }
    # --- Input Validation ---
    if df is None or df.empty or len(df) < 20: result['error'] = "Insufficient data"; print(f"[WARN][WyckoffEngineV1] {result['error']}"); return result
    if not all(col in df.columns for col in ['High', 'Low', 'Close', 'Volume']): result['error'] = "Missing required OHLCV columns."; print(f"[WARN][WyckoffEngineV1] {result['error']}"); return result
    if not isinstance(df.index, pd.DatetimeIndex) or df.index.tz is None:
         if isinstance(df.index, pd.DatetimeIndex) and df.index.tz is None:
              print(f"[WARN][WyckoffEngineV1] Input DataFrame index is timezone-naive. Assuming UTC.")
              try: df = df.tz_localize('UTC')
              except Exception as tz_err: result['error'] = f"Failed to localize index: {tz_err}"; print(f"[ERROR][WyckoffEngineV1] {result['error']}"); return result
         else: result['error'] = "Input DataFrame must have a DatetimeIndex."; print(f"[WARN][WyckoffEngineV1] {result['error']}"); return result
    if config is None: config = {}

    try:
        # 1. Detect Key Events
        events = _detect_wyckoff_events(df.copy(), config) # Pass copy to avoid modifying original df
        result['detected_events'] = { k: {**v, 'time': v['time'].isoformat()} for k, v in events.items() if k != 'error' and isinstance(v.get('time'), pd.Timestamp) }
        if 'error' in events: result['error'] = f"Event detection error: {events['error']}"

        # 2. Classify Phases based on events (use original events dict with Timestamps)
        phases = _classify_phases(events, config)
        result['phase_classification'] = { k: {**v, 'start': v['start'].isoformat(), 'end': v['end'].isoformat() if isinstance(v.get('end'), pd.Timestamp) else None} for k, v in phases.items() if isinstance(v.get('start'), pd.Timestamp) }

        # 3. Determine Current Phase
        if not phases: result['current_phase'] = 'Unknown (No Phases)'
        else:
            last_timestamp = df.index[-1]; current_phase = 'Unknown'
            valid_phases = {k:v for k,v in phases.items() if isinstance(v.get('start'), pd.Timestamp)}
            sorted_phases = sorted(valid_phases.items(), key=lambda item: item[1]['start'])
            for phase_name, phase_info in sorted_phases:
                start_time = phase_info['start']; end_time = phase_info.get('end')
                if last_timestamp >= start_time:
                    if end_time is None or last_timestamp <= end_time: current_phase = phase_name
                    elif end_time and last_timestamp > end_time: continue
            result['current_phase'] = current_phase if current_phase != 'Unknown' else (sorted_phases[-1][0] if sorted_phases else 'Unknown')

        # 4. Generate PnF Targets
        if config.get("enable_pnf_projection", True) and ('Spring' in events or 'LPS' in events or 'ST' in events):
            result['pnf_targets'] = _generate_pnf_target(events, config)

        print(f"[INFO][WyckoffEngineV1] Wyckoff Analysis Complete. Current Phase: {result['current_phase']}")

    except Exception as e:
        result['error'] = f"Error during Wyckoff phase analysis: {e}"; print(f"[ERROR][WyckoffEngineV1] {result['error']}"); traceback.print_exc()

    return result

# --- Example Usage ---
# Removed for operational code
# if __name__ == '__main__':
#    ... (testing code removed) ...
