# /run_test_pipeline.py
# Author: Tomasz Laskowski (& CTO Co-pilot)
# Version: 5.0 (Calculate Heuristic Delta before Enrichment)
# Description: Runs the full ZANZIBAR pipeline: Load -> Map -> Calc Delta -> Enrich -> Detect -> State Track

import sys
import os
import json
import yaml
import logging
import traceback
import pandas as pd
from typing import List, Dict, Any
from datetime import datetime, timezone
from pathlib import Path

# --- Add project root to path ---
project_root = os.path.dirname(os.path.abspath(__file__))
if os.path.isdir(os.path.join(project_root, 'zanzibar')): sys.path.insert(0, project_root)
else:
    project_root_parent = os.path.abspath(os.path.join(project_root, '..'))
    if os.path.isdir(os.path.join(project_root_parent, 'zanzibar')):
         if project_root_parent not in sys.path: sys.path.insert(0, project_root_parent)
         project_root = project_root_parent
    else: print("ERROR: Cannot determine project root."); sys.exit(1)

# --- Imports ---
try:
    from zanzibar.loader.csv_loader import load_dataframe_from_file
    from zanzibar.utils.zbar_mapper import map_dataframe_to_zbars
    # Import ZBar from its definitive location
    from zanzibar.analysis.wyckoff.event_detector import find_initial_wyckoff_events, ZBar
    from zanzibar.analysis.wyckoff.state_machine import WyckoffStateMachine
    from zanzibar.config import load_settings
    from zanzibar.utils.indicators import add_indicators_to_df
except ImportError as e: print(f"CRITICAL: Import Error: {e}\nsys.path: {sys.path}"); sys.exit(1)

# --- Setup Logging & Error Handling ---
LOG_DIR = os.path.join(project_root, "logs")
LOG_FILE = os.path.join(LOG_DIR, "pipeline_run.log")
os.makedirs(LOG_DIR, exist_ok=True)
root_logger = logging.getLogger()
for handler in root_logger.handlers[:]: root_logger.removeHandler(handler) # Remove existing handlers
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(name)s:%(lineno)d] - %(message)s',
    handlers=[ logging.FileHandler(LOG_FILE, mode='w'), logging.StreamHandler(sys.stdout) ]
)
log = logging.getLogger("PipelineRunner")
def handle_exception(exc_type, exc_value, exc_traceback):
    log.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    print(f"🚨 Pipeline halted: critical error logged. Check {LOG_FILE}.")
sys.excepthook = handle_exception

# --- Main Pipeline Function ---
def run_pipeline(file_path: str, config_path: str = "config/config.yaml"):
    log.info(f"--- Starting Zanzibar Test Pipeline Run (v5 - Heuristic Delta) ---")
    log.info(f"Config Path: {config_path}")
    log.info(f"Data File Path: {file_path}")

    # 1. Load Config
    config = load_settings(config_path)
    log.info(f"Configuration loaded successfully.")
    log_level_str = config.get("logging", {}).get("level", "INFO").upper()
    log_level = getattr(logging, log_level_str, logging.INFO)
    logging.getLogger().setLevel(log_level) # Set root logger level
    log.info(f"Logging level set to: {log_level_str}")
    tick_size = float(config.get("instrument", {}).get("tick_size", 0.01))
    log.info(f"Using Tick Size: {tick_size}")

    # 2. Load DataFrame
    df_loaded = load_dataframe_from_file(file_path, config=config)
    if df_loaded.empty: log.critical("Loaded DataFrame is empty."); return

    # 3. Map DataFrame to ZBars
    log.info("Mapping DataFrame to ZBar objects...")
    standard_col_map = {k:k for k in ['timestamp', 'open', 'high', 'low', 'close', 'volume']}
    zbars: List[ZBar] = map_dataframe_to_zbars(df_loaded, standard_col_map, config=config)
    if not zbars: log.critical("Mapping to ZBars failed."); return

    # 4. Calculate Heuristic Delta for each ZBar (NEW STEP)
    log.info("Calculating heuristic delta for ZBars...")
    calculated_deltas = []
    for zbar in zbars:
        # This will calculate heuristic delta only if price_ladder is empty
        delta_val = zbar.calculate_heuristic_delta()
        calculated_deltas.append(delta_val if delta_val is not None else 0) # Use 0 if None returned
    log.info("Heuristic delta calculation complete.")

    # 5. Enrich DataFrame with Indicators (using calculated deltas)
    log.info("Applying indicator enrichment...")
    # Add the calculated deltas as a new column to the original DataFrame
    # Need to align indices if zbars list doesn't perfectly match df_loaded rows (e.g., due to skips)
    # Safer approach: create delta series with matching index
    if len(calculated_deltas) == len(df_loaded.index):
         df_loaded['Delta'] = pd.Series(calculated_deltas, index=df_loaded.index)
         log.info("Added 'Delta' column (heuristic) to DataFrame for enrichment.")
    else:
         log.warning(f"Length mismatch between ZBars ({len(zbars)}) and loaded DataFrame ({len(df_loaded)}). Cannot add heuristic Delta column for enrichment.")

    df_enriched = add_indicators_to_df(df_loaded, config=config) # Pass DF with potential 'Delta'
    log.info(f"Enrichment complete. DataFrame shape: {df_enriched.shape}")
    if log.isEnabledFor(logging.DEBUG): print(df_enriched.head())

    # 6. Run Wyckoff Event Detection (uses ZBars, which now have bar_delta populated)
    log.info("Running Wyckoff event detection...")
    detector_config = config.get("wyckoff_detector", {})
    # The event detector V4 now uses zbar.bar_delta property, which accesses the calculated delta
    events: Dict[str, List[int]] = find_initial_wyckoff_events(zbars, tick_size, config=detector_config)
    log.info("Wyckoff event detection complete.")
    print("\n--- Detected Events ---")
    # ... (event printing logic remains same) ...
    found_any_events = False
    for event_type, indices in events.items():
        if indices and isinstance(indices, list): print(f"{event_type}: {indices}"); found_any_events = True
    if not found_any_events: print("No significant Wyckoff events detected.")


    # 7. Run Wyckoff State Machine
    log.info("Running Wyckoff state machine...")
    sm_config = config.get("wyckoff_state_machine", {})
    state_machine = WyckoffStateMachine(config=sm_config)
    all_event_tuples = sorted([(idx, et) for et, idx_list in events.items() if isinstance(idx_list, list) for idx in idx_list], key=lambda x: x[0])
    log.info(f"Feeding {len(all_event_tuples)} sorted events to state machine...")
    for index, event_type in all_event_tuples:
        state_machine.process_event(event_type, index)
    log.info("Wyckoff state machine processing complete.")
    state_machine.summarize()

    # 8. (Optional) Output Snapshot
    # ... (snapshot logic remains same) ...

    log.info(f"--- Zanzibar Test Pipeline Run Finished Successfully ---")

# --- CLI Entry Point (Same as V4) ---
if __name__ == '__main__':
    default_data_file = "data/XAUUSD_M1_202504280105_202505061254.csv"
    default_config_file = "config/config.yaml"
    data_file = sys.argv[1] if len(sys.argv) > 1 else default_data_file
    config_file = sys.argv[2] if len(sys.argv) > 2 else default_config_file
    if not os.path.isabs(config_file): config_file = os.path.join(project_root, config_file)
    if not os.path.isabs(data_file): data_file = os.path.join(project_root, data_file)
    log_dir_abs = os.path.join(project_root, "logs")
    os.makedirs(log_dir_abs, exist_ok=True)
    LOG_FILE = os.path.join(log_dir_abs, "pipeline_run.log")
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        if isinstance(handler, logging.FileHandler): handler.close(); root_logger.removeHandler(handler)
    file_handler = logging.FileHandler(LOG_FILE, mode='w')
    # Ensure formatter exists before copying
    if root_logger.handlers: file_handler.setFormatter(root_logger.handlers[0].formatter)
    else: file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - [%(name)s:%(lineno)d] - %(message)s'))
    root_logger.addHandler(file_handler)
    # Set level from config after basicConfig might have run
    try: log_level_cfg = load_settings(config_file).get("logging", {}).get("level", "INFO").upper(); root_logger.setLevel(getattr(logging, log_level_cfg, logging.INFO))
    except: pass # Ignore if config load fails here, basicConfig level applies

    if not os.path.exists(data_file): log.error(f"CRITICAL: Data file not found at '{data_file}'"); sys.exit(1)
    if not os.path.exists(config_file): log.error(f"CRITICAL: Config file not found at '{config_file}'"); sys.exit(1)

    run_pipeline(data_file, config_file)


