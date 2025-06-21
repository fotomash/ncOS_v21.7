# zanzibar/loader/tick_processor.py
# Author: Tomasz Laskowski (& Gemini Co-pilot)
# License: Proprietary / Private
# Created: 2025-05-07
# Version: 2.0 (Implemented TickAggregator logic and ZBar metrics)
# Description: Loads raw tick files, normalizes, aggregates into ZBars
#              with price ladders, and computes derived ZBar metrics.

import pandas as pd
import numpy as np
from typing import List, Dict, Union, Any, Optional, Iterator
from datetime import datetime, timedelta, timezone
import logging

# Assuming config loader is available
try:
    # This assumes your project structure allows this import path
    # e.g., if 'zanzibar_analytics' is the root and contains 'zanzibar' package
    from zanzibar.config import load_settings
except ImportError:
    # Fallback for standalone development/testing if script is run directly
    # or if PYTHONPATH is not set up for the 'zanzibar' package.
    def load_settings(config_path="config/config.yaml"): # pragma: no cover
        print(f"WARN: Using dummy load_settings for {config_path}. Real loader not found.")
        # Provide a default structure that tick_processor might expect
        return {
            "tick_processor": {
                "active_profile": "default_test_profile", # Define a default active profile
                "profiles": {
                    "default_test_profile": { # Define the profile itself
                        "default_tz": "UTC",
                        "default_bar_interval": "1min",
                        "column_map": { # Example column map
                            "timestamp_source": ["<DATE>", "<TIME>"], # For combined date/time
                            "price_source": "<LAST>",
                            "volume_source": "<VOLUME>",
                            "bid_source": "<BID>",
                            "ask_source": "<ASK>",
                            "flags_source": "<FLAGS>"
                        },
                        "tick_side_logic": "use_l1_quote" # Default side logic
                    }
                }
            },
            "instrument": {"tick_size": 0.01}, # Example instrument config
            "data_loader": { # Minimal data_loader config for load_tick_data
                "active_profile": "default_tick_loader",
                "profiles": {
                    "default_tick_loader": {
                        "delimiter": "\t", # Default for your tick files
                        "encoding": "utf-8"
                    }
                }
            }
        }

log = logging.getLogger(__name__)
if not log.hasHandlers(): # Avoid adding multiple handlers if imported multiple times
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - [%(name)s:%(lineno)d] - %(message)s')

# --- Core Data Models (ZBar™) ---
# These definitions should ideally live in a central models file like
# zanzibar.data_management.models.py and be imported.
# For this module's development, they are included here with your implemented metrics.

@dataclass
class MarketOrderData:
    """ Represents aggregated order flow at a price level inside a ZBar. """
    bid_volume: int = 0
    ask_volume: int = 0
    total_volume: int = 0
    delta: int = 0  # ask_volume - bid_volume

    def update_from_tick_aggression(self, volume: int, is_buyer_initiated: bool):
        """Updates volumes based on inferred tick aggression."""
        self.total_volume += volume
        if is_buyer_initiated:
            self.ask_volume += volume
            self.delta += volume
        else:
            self.bid_volume += volume
            self.delta -= volume

@dataclass
class ZBar:
    """
    ZBAR™ - Proprietary Market Data Object
    Captures enhanced volume & delta metrics per bar for VSA/Wyckoff analysis.
    """
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int # Total bar volume from sum of ticks
    price_ladder: Dict[float, MarketOrderData] = field(default_factory=dict)

    # Derived metrics, populated by calculate_derived_metrics
    bar_delta: int = 0
    poc_price: Optional[float] = None
    poi_price: Optional[float] = None
    bid_volume_total: int = 0
    ask_volume_total: int = 0

    def calculate_derived_metrics(self) -> Dict[str, Any]:
        """
        Populate bar_delta, poc_price, poi_price, bid_volume_total, ask_volume_total
        from the price_ladder.
        This method is called after the price_ladder is fully populated for the bar.
        """
        log.debug(f"Calculating derived metrics for ZBar at {self.timestamp}")
        if not self.price_ladder:
            log.warning(f"Price ladder is empty for ZBar at {self.timestamp}. Derived metrics will be zero/None.")
            self.bar_delta = 0
            self.bid_volume_total = 0
            self.ask_volume_total = 0
            self.poc_price = None
            self.poi_price = None
            return {
                "bar_delta": self.bar_delta, "poc_price": self.poc_price, "poi_price": self.poi_price,
                "bid_volume_total": self.bid_volume_total, "ask_volume_total": self.ask_volume_total
            }

        current_bar_delta = 0
        current_bid_total = 0
        current_ask_total = 0
        
        # Ensure all MarketOrderData values are valid
        for price_level, mo_data in self.price_ladder.items():
            if not isinstance(mo_data, MarketOrderData):
                log.error(f"Invalid data type in price_ladder at price {price_level} for ZBar {self.timestamp}. Expected MarketOrderData, got {type(mo_data)}")
                # Skip this level or handle error appropriately
                continue
            current_bid_total += mo_data.bid_volume
            current_ask_total += mo_data.ask_volume
            current_bar_delta += mo_data.delta
        
        self.bid_volume_total = current_bid_total
        self.ask_volume_total = current_ask_total
        self.bar_delta = current_bar_delta

        max_vol_at_price = -1
        min_vol_at_price = float('inf')
        calculated_poc = None
        calculated_poi = None

        # Find POC based on total_volume at each price level
        for price, mo in self.price_ladder.items():
            if not isinstance(mo, MarketOrderData): continue # Skip if not MarketOrderData
            tv = mo.total_volume
            if tv > max_vol_at_price:
                max_vol_at_price = tv
                calculated_poc = price
            if 0 < tv < min_vol_at_price:
                min_vol_at_price = tv
                calculated_poi = price
        
        self.poc_price = calculated_poc
        self.poi_price = calculated_poi if min_vol_at_price != float('inf') else None # Ensure POI is None if no valid min_vol found
        
        log.debug(f"ZBar {self.timestamp}: Delta={self.bar_delta}, POC={self.poc_price}, POI={self.poi_price}, BidVol={self.bid_volume_total}, AskVol={self.ask_volume_total}")
        
        return {
            "bar_delta": self.bar_delta, "poc_price": self.poc_price, "poi_price": self.poi_price,
            "bid_volume_total": self.bid_volume_total, "ask_volume_total": self.ask_volume_total
        }

# --- Tick Aggregator Class ---
class TickAggregator:
    """ Internal class to manage the state of aggregating ticks into a single ZBar. """
    def __init__(self, bar_interval_str: str, column_map: Dict[str, str], config: Optional[Dict[str, Any]] = None):
        self.bar_interval_str = bar_interval_str
        # column_map here refers to the map for *source tick data columns* (e.g. <LAST>, <BID>)
        # to standard internal names used by _infer_tick_aggression if needed (e.g. 'price', 'bid', 'ask')
        self.source_column_map = column_map
        self.config = config if config else {}
        log.info(f"TickAggregator initialized. Interval: {self.bar_interval_str}, Side Logic: {self.config.get('tick_side_logic', 'lee_ready_simple')}")

        self.current_bar_start_time: Optional[datetime] = None
        self.current_bar_ticks_data: List[Dict[str, Any]] = [] # Stores standardized tick dicts
        self.bar_timedelta: timedelta = self._parse_interval(bar_interval_str)

        # Standardized internal keys expected in tick_data_standardized dicts
        self.ts_col = 'timestamp'
        self.price_col = 'price'
        self.volume_col = 'volume'
        
        # Standardized internal keys for optional side-related data
        self.bid_col_std = 'bid' # Standardized name after mapping by load_tick_data
        self.ask_col_std = 'ask' # Standardized name
        self.flags_col_std = 'flags' # Standardized name

        self.side_logic = self.config.get('tick_side_logic', 'lee_ready_simple')
        self.flags_buy_value = self.config.get('flags_buy_value') # Value in 'flags' col indicating buy
        self.flags_sell_value = self.config.get('flags_sell_value')# Value in 'flags' col indicating sell
        
        self.prev_tick_price: Optional[float] = None

    def _parse_interval(self, interval_str: str) -> timedelta:
        log.debug(f"Parsing bar interval string: {interval_str}")
        num_str = "".join(filter(str.isdigit, interval_str))
        unit_str = "".join(filter(str.isalpha, interval_str)).lower()
        
        if not num_str: raise ValueError(f"Invalid bar_interval format: {interval_str}. No numeric part.")
        num = int(num_str)

        if unit_str == "min" or unit_str == "t" or unit_str == "m": return timedelta(minutes=num)
        elif unit_str == "h": return timedelta(hours=num)
        elif unit_str == "s": return timedelta(seconds=num)
        raise ValueError(f"Unsupported bar_interval unit: {interval_str}. Use 'Xmin', 'XH', 'Xs'.")

    def _initialize_bar_from_tick(self, tick_timestamp: datetime):
        ts = tick_timestamp
        total_seconds = self.bar_timedelta.total_seconds()
        if total_seconds == 0: total_seconds = 60 # Default to 1 min if interval is 0 for some reason

        if total_seconds >= 86400: # Daily
             self.current_bar_start_time = ts.replace(hour=0, minute=0, second=0, microsecond=0)
        elif total_seconds >= 3600: # Hourly
             hour_interval = int(total_seconds / 3600)
             self.current_bar_start_time = ts.replace(hour=(ts.hour // hour_interval) * hour_interval, minute=0, second=0, microsecond=0)
        elif total_seconds >= 60: # Minutely
             minute_interval = int(total_seconds / 60)
             self.current_bar_start_time = ts.replace(minute=(ts.minute // minute_interval) * minute_interval, second=0, microsecond=0)
        else: # Second based
            self.current_bar_start_time = ts.replace(second=(ts.second // int(total_seconds)) * int(total_seconds), microsecond=0)
        
        self.current_bar_ticks_data = []
        self.prev_tick_price = None
        log.debug(f"Initialized new bar starting at: {self.current_bar_start_time}")

    def _infer_tick_aggression(self, tick: Dict[str, Any]) -> bool:
        """ Infers if the tick was buyer-initiated (True) or seller-initiated (False). """
        # tick dict uses *standardized* keys: 'price', 'volume', 'bid', 'ask', 'flags'
        tick_price = tick[self.price_col]

        if self.side_logic == "use_flags":
            if self.flags_col_std and self.flags_col_std in tick:
                flag_val = tick[self.flags_col_std]
                if self.flags_buy_value is not None and flag_val == self.flags_buy_value: return True
                if self.flags_sell_value is not None and flag_val == self.flags_sell_value: return False
            log.warning(f"Side logic 'use_flags' but flags_col ('{self.flags_col_std}') not in tick or values not matched. Tick: {tick.get(self.ts_col)}")
            return self.prev_tick_price is None or tick_price >= self.prev_tick_price

        elif self.side_logic == "use_l1_quote":
            bid = tick.get(self.bid_col_std) # Use standardized key
            ask = tick.get(self.ask_col_std) # Use standardized key

            if bid is not None and ask is not None and isinstance(bid, (int, float)) and isinstance(ask, (int, float)) and bid > 0 and ask > 0:
                if tick_price >= ask: return True
                if tick_price <= bid: return False
                if self.prev_tick_price is not None:
                    if tick_price > self.prev_tick_price: return True
                    if tick_price < self.prev_tick_price: return False
                return True
            log.warning(f"Side logic 'use_l1_quote' but bid/ask cols invalid in tick. Tick: {tick.get(self.ts_col)}. Falling back.")
            if self.prev_tick_price is not None:
                if tick_price > self.prev_tick_price: return True
                if tick_price < self.prev_tick_price: return False
            return True

        elif self.side_logic == "lee_ready_simple":
            if self.prev_tick_price is not None:
                if tick_price > self.prev_tick_price: return True
                if tick_price < self.prev_tick_price: return False
            return True
        else:
            log.warning(f"Unknown tick_side_logic: {self.side_logic}. Defaulting to buyer aggression.")
            return True

    def add_tick(self, tick_data_standardized: Dict[str, Any]) -> Optional[ZBar]:
        tick_timestamp = tick_data_standardized[self.ts_col]
        if not isinstance(tick_timestamp, datetime): # Ensure it's a datetime object
            log.error(f"Invalid timestamp type for tick: {tick_timestamp}. Skipping.")
            return None
        if tick_timestamp.tzinfo is None: # Ensure timezone aware
            tick_timestamp = tick_timestamp.replace(tzinfo=timezone.utc)
            tick_data_standardized[self.ts_col] = tick_timestamp


        if not self.current_bar_start_time:
            self._initialize_bar_from_tick(tick_timestamp)
        
        current_bar_end_time = self.current_bar_start_time + self.bar_timedelta
        completed_bar: Optional[ZBar] = None

        if tick_timestamp >= current_bar_end_time:
            if self.current_bar_ticks_data:
                completed_bar = self._finalize_bar()
            self._initialize_bar_from_tick(tick_timestamp)
        
        self.current_bar_ticks_data.append(tick_data_standardized)
        return completed_bar

    def _finalize_bar(self) -> Optional[ZBar]:
        if not self.current_bar_ticks_data or not self.current_bar_start_time:
            return None
        
        log.debug(f"Finalizing bar for {self.current_bar_start_time} with {len(self.current_bar_ticks_data)} ticks.")
        
        first_tick = self.current_bar_ticks_data[0]
        last_tick = self.current_bar_ticks_data[-1]

        open_price = float(first_tick[self.price_col])
        close_price = float(last_tick[self.price_col])
        
        current_high = -float('inf')
        current_low = float('inf')
        current_total_volume = 0
        
        price_ladder_data: Dict[float, MarketOrderData] = {}
        # Reset prev_tick_price for Lee-Ready logic *within* this bar's tick processing
        # This is important if L1 quote fails and Lee-Ready is used as fallback for a tick
        self.prev_tick_price = None 

        for tick_entry in self.current_bar_ticks_data:
            price = float(tick_entry[self.price_col])
            volume = int(tick_entry[self.volume_col])

            current_high = max(current_high, price)
            current_low = min(current_low, price)
            current_total_volume += volume

            is_buyer_aggression = self._infer_tick_aggression(tick_entry)
            self.prev_tick_price = price # Update for next tick in this bar

            if price not in price_ladder_data:
                price_ladder_data[price] = MarketOrderData()
            price_ladder_data[price].update_from_tick_aggression(volume=volume, is_buyer_initiated=is_buyer_aggression)
        
        zbar = ZBar(
            timestamp=self.current_bar_start_time,
            open=open_price, high=current_high, low=current_low, close=close_price,
            volume=current_total_volume, price_ladder=price_ladder_data
        )
        zbar.calculate_derived_metrics() # Populate delta, POC, POI etc.
        log.debug(f"Finalized ZBar: T={zbar.timestamp}, O={zbar.open}, H={zbar.high}, L={zbar.low}, C={zbar.close}, V={zbar.volume}, Delta={zbar.bar_delta}")
        return zbar

    def flush_final_bar(self) -> Optional[ZBar]:
        log.debug("Flushing final bar...")
        final_bar = self._finalize_bar()
        self.current_bar_ticks_data = []
        self.current_bar_start_time = None
        self.prev_tick_price = None
        return final_bar

# --- Public API Functions ---

def load_tick_data(
    filepath: str,
    config: Optional[Dict[str, Any]] = None
) -> pd.DataFrame:
    """
    Loads and standardizes tick data from a file.
    Uses 'data_loader' (for delimiter/encoding) and 'tick_processor' (for column_map, tz) from config.
    Returns a DataFrame with standardized columns: 'timestamp', 'price', 'volume', and optionally 'bid', 'ask', 'flags'.
    """
    if config is None: config = {}
    log.info(f"Loading tick data from: {filepath}")

    # Determine active profiles for loader (delimiter/encoding) and processor (column map/tz)
    dl_cfg = config.get("data_loader", {})
    tp_cfg = config.get("tick_processor", {})
    
    dl_profile_name = dl_cfg.get("active_profile", "default_tick_loader_profile") # Specific for ticks
    dl_profile = dl_cfg.get("profiles", {}).get(dl_profile_name, {})
    
    tp_profile_name = tp_cfg.get("active_profile", "default_tick_processor_profile")
    tp_profile = tp_cfg.get("profiles", {}).get(tp_profile_name, {})

    # Delimiter and Encoding
    delimiter = dl_profile.get("delimiter", tp_profile.get("delimiter")) # Processor can override
    encoding = dl_profile.get("encoding", tp_profile.get("encoding"))
    if not delimiter or delimiter.lower() == 'auto':
        # Simplified auto-detection for this context
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f_sniff:
                sample = f_sniff.read(1024)
                delimiter = '\t' if sample.count('\t') > sample.count(',') else ','
        except: delimiter = ',' # Fallback
    encoding = encoding or 'utf-8'
    log.info(f"Using delimiter: '{delimiter}', encoding: '{encoding}' for {filepath}")

    # Column map (Standard Name : Source Name in File)
    # This map is crucial for standardizing input from various tick file formats.
    column_map_source_to_std = tp_profile.get("column_map", {})
    if not column_map_source_to_std:
        raise ValueError(f"Tick processor 'column_map' is required in config profile '{tp_profile_name}'.")

    try:
        df_raw = pd.read_csv(filepath, sep=delimiter, encoding=encoding, on_bad_lines='warn', low_memory=False)
    except Exception as e:
        log.error(f"Failed to load tick file {filepath}: {e}"); raise
    log.info(f"Raw tick data loaded: {len(df_raw)} rows from {filepath}")
    if df_raw.empty: return pd.DataFrame()

    df = df_raw.copy()
    df.columns = [str(col).strip().strip('<>') for col in df.columns] # Clean source headers

    # --- Standardize to internal names: 'timestamp', 'price', 'volume', 'bid', 'ask', 'flags' ---
    df_std = pd.DataFrame()

    # Timestamp (mandatory)
    ts_source_config = column_map_source_to_std.get('timestamp_source', 'timestamp')
    if isinstance(ts_source_config, list) and len(ts_source_config) == 2:
        date_col_src, time_col_src = ts_source_config[0], ts_source_config[1]
        if date_col_src in df.columns and time_col_src in df.columns:
            df_std['timestamp'] = pd.to_datetime(df[date_col_src].astype(str) + ' ' + df[time_col_src].astype(str), errors='coerce')
        else: raise ValueError(f"Timestamp source columns {ts_source_config} not found in tick data columns: {df.columns.tolist()}.")
    elif ts_source_config in df.columns:
        df_std['timestamp'] = pd.to_datetime(df[ts_source_config], errors='coerce')
    else:
        raise ValueError(f"Timestamp source column '{ts_source_config}' not found in tick data columns: {df.columns.tolist()}.")
    
    df_std.dropna(subset=['timestamp'], inplace=True)
    default_tz = tp_profile.get("default_tz", "UTC")
    if df_std['timestamp'].dt.tz is None: df_std['timestamp'] = df_std['timestamp'].dt.tz_localize(default_tz)
    else: df_std['timestamp'] = df_std['timestamp'].dt.tz_convert(default_tz)
    # df_std.set_index('timestamp', inplace=True) # Keep as column for to_dict('records')

    # Price & Volume (mandatory)
    price_src_cfg = column_map_source_to_std.get('price_source', 'price')
    volume_src_cfg = column_map_source_to_std.get('volume_source', 'volume')
    if price_src_cfg not in df.columns or volume_src_cfg not in df.columns:
        raise ValueError(f"Price ('{price_src_cfg}') or Volume ('{volume_src_cfg}') source columns not found in {df.columns.tolist()}.")
    df_std['price'] = pd.to_numeric(df[price_src_cfg], errors='coerce')
    df_std['volume'] = pd.to_numeric(df[volume_src_cfg], errors='coerce').fillna(0).astype(int)

    # Optional Side-related columns (pass them through with standard names if mapped)
    optional_mappings = {
        'bid': column_map_source_to_std.get('bid_source'),
        'ask': column_map_source_to_std.get('ask_source'),
        'flags': column_map_source_to_std.get('flags_source')
    }
    for std_name, src_name in optional_mappings.items():
        if src_name and src_name in df.columns:
            df_std[std_name] = df[src_name] # Pass through; type coercion can happen in TickAggregator if needed

    df_std.dropna(subset=['price', 'volume'], inplace=True) # Drop rows where essential price/vol is NaN
    df_std.sort_values(by='timestamp', inplace=True) # Ensure chronological order
    log.info(f"Standardized tick data: {len(df_std)} rows. Columns for aggregator: {df_std.columns.tolist()}")
    return df_std


def aggregate_ticks_to_zbars(
    ticks_df: pd.DataFrame, # Expects DataFrame from load_tick_data
    bar_interval_rule: str = "1min",
    config: Optional[Dict[str, Any]] = None
) -> List[ZBar]:
    """ Aggregates standardized ticks into ZBar objects. """
    if config is None: config = {}
    processor_cfg = config.get("tick_processor", {})
    active_profile_name = processor_cfg.get("active_profile", "default_tick_profile")
    profile_cfg = processor_cfg.get("profiles", {}).get(active_profile_name, {})

    # TickAggregator uses the column_map from the *tick_processor profile* to know
    # the *original source names* for optional fields like bid, ask, flags,
    # because the tick_dict passed to it might still contain these if not standardized
    # by load_tick_data.
    # However, 'timestamp', 'price', 'volume' are expected to be standardized by load_tick_data.
    # The config for tick_side_logic is also in profile_cfg.
    aggregator_col_map_for_source_fields = profile_cfg.get("column_map", {})


    log.info(f"Aggregating {len(ticks_df)} standardized ticks into {bar_interval_rule} ZBars using profile '{active_profile_name}'.")
    if ticks_df.empty: return []

    # Initialize aggregator. It expects standardized 'timestamp', 'price', 'volume' in tick_data_dict.
    # For side inference, it will use its config and its own column_map to find source bid/ask/flags cols.
    aggregator = TickAggregator(
        bar_interval_str=bar_interval_rule,
        column_map=aggregator_col_map_for_source_fields, # This tells aggregator the *source* names for bid/ask/flags
        config=profile_cfg # This contains tick_side_logic and flag values
    )
    
    zbars_list: List[ZBar] = []
    
    # Iterate through the standardized DataFrame (which has 'timestamp', 'price', 'volume'
    # and potentially 'bid', 'ask', 'flags' if they were mapped by load_tick_data)
    for tick_data_dict in ticks_df.to_dict('records'):
        # The tick_data_dict contains standardized keys like 'timestamp', 'price', 'volume'.
        # It might also contain 'bid', 'ask', 'flags' if load_tick_data added them.
        # The TickAggregator's _infer_tick_aggression uses its self.bid_src_col, self.ask_src_col, self.flags_src_col
        # (which are derived from its own column_map pointing to *source* names) to look up these values
        # from the tick_data_dict. This requires tick_data_dict to hold original source columns
        # if side_logic depends on them.
        # This seems a bit convoluted.
        # Simpler: TickAggregator always expects standardized 'bid', 'ask', 'flags' keys if its logic uses them.
        # load_tick_data is responsible for ensuring these standardized keys are present if mapped.
        
        # Corrected: TickAggregator's _infer_tick_aggression will use standardized keys
        # 'bid', 'ask', 'flags' if present in the tick_data_dict.
        # Its own self.bid_src_col etc. are not strictly needed if it assumes std keys.
        # The config for tick_side_logic is the main driver.
        
        completed_bar = aggregator.add_tick(tick_data_dict) # Pass dict with std keys
        if completed_bar:
            zbars_list.append(completed_bar)
    
    final_bar = aggregator.flush_final_bar()
    if final_bar:
        zbars_list.append(final_bar)

    log.info(f"Aggregation complete. Generated {len(zbars_list)} ZBars.")
    return zbars_list

# --- Main Usage Example (Illustrative) ---
if __name__ == "__main__": # pragma: no cover
    log.info("--- Tick Processor Smoke Test ---")
    try:
        # Determine project root for config and data paths
        current_script_path = Path(__file__).resolve()
        project_root_path = current_script_path.parent.parent # Assumes loader is in zanzibar/loader
        
        cfg_path = project_root_path / "config" / "config.yaml"
        main_config = load_settings(config_path=str(cfg_path))
        log.info("Main config loaded for smoke test.")
    except FileNotFoundError:
        log.error(f"Main config file not found. Using dummy config for smoke test.")
        main_config = { # Fallback dummy config
            "data_loader": {"active_profile": "dummy_dl_ticks", "profiles": {"dummy_dl_ticks": {"delimiter": "\t", "encoding": "utf-8"}}},
            "tick_processor": {
                "active_profile": "dummy_tp_profile",
                "profiles": { "dummy_tp_profile": {
                        "default_tz": "UTC", "default_bar_interval": "1min",
                        "column_map": { "timestamp_source": ["<DATE>", "<TIME>"], "price_source": "<LAST>", "volume_source": "<VOLUME>", "bid_source": "<BID>", "ask_source": "<ASK>", "flags_source": "<FLAGS>"},
                        "tick_side_logic": "use_l1_quote"
                }}},
            "instrument": {"tick_size": 0.01} }
    
    # Use one of your uploaded tick files
    tick_file_path_relative = "data/XAUUSD_202505060800_202505061254.csv" # Relative to project root
    tick_file_path_abs = project_root_path / tick_file_path_relative

    if os.path.exists(tick_file_path_abs):
        try:
            log.info(f"Step 1: Loading tick data from {tick_file_path_abs}...")
            standardized_ticks_df = load_tick_data(str(tick_file_path_abs), config=main_config)

            if not standardized_ticks_df.empty:
                log.info(f"Step 2: Aggregating {len(standardized_ticks_df)} standardized ticks into ZBars...")
                active_tp_profile = main_config.get("tick_processor",{}).get("active_profile", "default_tick_profile")
                bar_interval = main_config.get("tick_processor",{}).get("profiles",{}).get(active_tp_profile,{}).get("default_bar_interval", "1min")
                
                zbars_result = aggregate_ticks_to_zbars(
                    ticks_df=standardized_ticks_df,
                    bar_interval_rule=bar_interval,
                    config=main_config
                )

                log.info(f"Step 3: ZBars computed. Count: {len(zbars_result)}")
                if zbars_result:
                    print("\n--- Sample ZBars (First 3) ---")
                    for i, zb in enumerate(zbars_result[:3]):
                        print(f"ZBar {i}: T={zb.timestamp}, O={zb.open}, H={zb.high}, L={zb.low}, C={zb.close}, V={zb.volume}, Delta={zb.bar_delta}, POC={zb.poc_price}")
                    print("\n--- Sample ZBars (Last 3) ---")
                    for i, zb in enumerate(zbars_result[-3:]):
                         print(f"ZBar {len(zbars_result)-3+i}: T={zb.timestamp}, O={zb.open}, H={zb.high}, L={zb.low}, C={zb.close}, V={zb.volume}, Delta={zb.bar_delta}, POC={zb.poc_price}")
            else:
                log.error("Tick loading resulted in an empty DataFrame.")
        except Exception as e:
            log.error(f"Tick Processor smoke test failed: {e}")
            log.error(traceback.format_exc())
    else:
        log.warning(f"Tick data file not found for smoke test: {tick_file_path_abs}")

