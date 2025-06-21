#!/usr/bin/env python3
# Imports
import os, sys
from pathlib import Path
# Ensure the 'core' folder is importable
script_dir = Path(__file__).parent
core_dir = script_dir / "core"
if core_dir.exists() and str(core_dir) not in sys.path:
    sys.path.insert(0, str(core_dir))

# Knowledge base
KNOWLEDGE_FOLDER = Path("knowledge")
if KNOWLEDGE_FOLDER.exists():
    print(f"[KNOWLEDGE] Referencing core knowledge files from: {KNOWLEDGE_FOLDER}")
    for kf in sorted(KNOWLEDGE_FOLDER.iterdir()):
        if kf.suffix in (".txt", ".md"):
            print(f"  - {kf.name}")
else:
    print("[KNOWLEDGE] No knowledge folder found. Skipping...")
# These files should be treated as institutional-grade strategy references by all agents

import sys
import json
from pathlib import Path
from datetime import datetime
import click
import pandas as pd
import re
from core.data_pipeline import DataPipeline

# Additional analysis engines
from core.phase_detector_wyckoff_v1 import detect_wyckoff_phases_and_events
from core.smc_enrichment_engine import tag_smc_zones
from core.indicators import add_indicators_multi_tf

# Boot and config merging
from core.startup_loading import load_core_configs  # loads copilot_config, chart_config, strategy_profiles, scalp_config
from trait_engine.merge_config import merge_configs
# Sentiment injection
from core.intermarket_sentiment import inject_sentiment
from core.macro_sentiment_enricher import enrich_with_macro_sentiment
# Orchestrators
from advanced_smc_orchestrator import run_advanced_smc_strategy
from copilot_orchestrator import run_full_analysis as run_copilot_strategy

# --- MICROSTRUCTURE PHASE STACK (ZANALYTICS AI) ---
# This orchestrator integrates HTF Wyckoff detection with LTF Microstructure context:
# - Calls `detect_micro_wyckoff_phase()` inside `phase_detector_wyckoff_v1`
# - Connects Spring, CHoCH, BOS, LPS to H1/H4 context
# - Phase classification: AR, ST, LPS, Spring, Test, SOS
# - Copilot and Advanced modes inherit `micro_context` via config injection

# CLI definition
@click.command()
@click.option('--variant', '-v', default='default', help='Strategy variant name.')
@click.option('--symbol', '-s', default='XAUUSD', help='Trading symbol, e.g. XAUUSD.')
@click.option('--mode', '-m', type=click.Choice(['adv_smc', 'copilot', 'session', 'boot']), default='adv_smc', help='Orchestration mode.')
@click.option('--timestamp', '-t', default=None, help='Timestamp for analysis (UTC), e.g. "2025-05-22T10:00:00".')
@click.option('--wyckoff/--no-wyckoff', default=True, help='Enable Wyckoff phase analysis.')
@click.option('--smc/--no-smc', default=True, help='Enable Smart-Money Concepts zone tagging.')
def main(variant, symbol, mode, timestamp, wyckoff, smc):
    """Unified orchestrator for ZANALYTICS session."""
    # 1. Load and merge configs
    core_configs = load_core_configs()  # dict of all core JSON configs
    config = merge_configs(core_configs, variant)

    # 2. Fetch raw M1 and resample to HTF CSVs
    dp = DataPipeline(config)
    dp.fetch_pairs()
    dp.resample_htf()

    # 3. Load HTF data from generated CSVs
    htf_dir = Path("tick_data/htf")
    all_tf_data = {}
    symbol_pattern = re.compile(rf"{symbol}_(?P<tf>[A-Za-z0-9]+)_.*\.csv")
    for csv_path in htf_dir.glob(f"{symbol}_*.csv"):
        m = symbol_pattern.match(csv_path.name)
        if not m:
            continue
        tf = m.group('tf').lower()
        try:
            df = pd.read_csv(csv_path, parse_dates=True, index_col=0)
            all_tf_data[tf] = df
            print(f"[INFO] Loaded {tf.upper()} data for {symbol} from {csv_path.name}")
        except Exception as e:
            print(f"[ERROR] Failed to load {csv_path.name}: {e}")

    # 3b. Auto-resample missing frames from M1 if needed
    if 'm1' in all_tf_data:
        from core.resample_m1_to_htf import Resampler
        resampler = Resampler(all_tf_data['m1'])
        for tf in config.get('timeframes', []):
            if tf not in all_tf_data:
                try:
                    all_tf_data[tf] = resampler.get_ohlc(tf.upper())
                    print(f"[INFO] Resampled M1 → {tf.upper()} successfully.")
                except Exception as e:
                    print(f"[ERROR] Resampling M1 → {tf.upper()} failed: {e}")

    # 3c. Enrich all timeframes with indicators
    indicator_profiles = config.get('indicator_profiles', {})
    try:
        enriched_tf_data = add_indicators_multi_tf(all_tf_data, indicator_profiles)
        all_tf_data = enriched_tf_data
        print("[INFO] Enriched all timeframes with configured indicators.")
    except Exception as e:
        print(f"[ERROR] Indicator enrichment failed: {e}")

    # 4a. SMC zone tagging
    if smc:
        for tf, df in all_tf_data.items():
            try:
                all_tf_data[tf] = tag_smc_zones(df, tf.upper(), config.get('smc_config', {}))
            except Exception as e:
                print(f"[Unified] SMC tagging failed for {tf}: {e}")

    # 4b. Wyckoff phase analysis (on H1)
    wyckoff_result = None
    if wyckoff and 'h1' in all_tf_data:
        try:
            wyckoff_result = detect_wyckoff_phases_and_events(
                df=all_tf_data['h1'], timeframe='H1', config=config.get('wyckoff_config', {})
            )
            config['wyckoff_result'] = wyckoff_result
            config['micro_context'] = wyckoff_result.get('micro_context') if isinstance(wyckoff_result, dict) else None
        except Exception as e:
            print(f"[Unified] Wyckoff analysis failed: {e}")

    # 4. Inject intermarket sentiment into config
    sentiment = inject_sentiment(core_configs.get('intermarket_config', {}))
    config['sentiment_snapshot'] = sentiment
    # Inject macro sentiment
    config = enrich_with_macro_sentiment(config, config.get('macro_sentiment_config'))

    # 4c. Initialize and evaluate AI agents
    from agent_initializer import initialize_agents
    agents = initialize_agents(config)
    semantic_result = agents['semantic_dss'].analyze()
    print(f"[SEMANTIC DSS] {semantic_result['combined_interpretation']}")

    journal_dir = Path("journal")
    journal_dir.mkdir(exist_ok=True)
    semantic_md_path = journal_dir / f"summary_semantic_{symbol}.md"
    with open(semantic_md_path, "w") as f:
        f.write(f"# Semantic DSS Summary for {symbol}\n\n")
        f.write(f"- **Wyckoff Phase:** {semantic_result['wyckoff_phase']}\n")
        f.write(f"- **Macro Bias:** {semantic_result['macro_bias']}\n")
        f.write(f"- **Interpretation:** {semantic_result['combined_interpretation']}\n")
    print(f"[JOURNAL] Semantic summary saved to {semantic_md_path}")

    strategist_result = agents['micro_strategist'].evaluate_microstructure_phase_trigger()
    macro_result = agents['macro_analyzer'].evaluate_macro_bias()
    risk_result = agents['risk_manager'].evaluate_risk_profile()
    trust_score = agents["reputation_auditor"].score(agents["trade_journalist"].history)
    strategist_result["trust_score"] = trust_score

    from core.trade_risk_model import calculate_trade_risk

    risk_projection = calculate_trade_risk(
        entry_price=strategist_result.get("poi_price", 0),
        bias=macro_result.get("bias", "neutral"),
        phase=htf_result.get("phase", "NA"),
        volatility=risk_result.get("volatility", 0)
    )

    strategist_result.update(risk_projection)

    journal_entry = agents['trade_journalist'].log_decision(strategist_result, macro_result, risk_result, semantic_result)

    print(f"[AI DECISION] {journal_entry['summary']}")

    try:
        alert_msg = f"""📈 New Signal: {symbol}
🕒 {journal_entry['timestamp']}
🔹 Trigger: {journal_entry['trigger']}
🔹 Signal: {journal_entry['entry_signal']}
📊 Confidence: {journal_entry['confidence']} | Risk: {journal_entry['risk_level']}
📐 Phase: {journal_entry['phase_context']} | Macro: {journal_entry['macro_bias']} | Trust: {journal_entry.get('trust_score')}
🎯 POI: {risk_projection['poi_price']} | TP: {risk_projection['tp']} | SL: {risk_projection['sl']} | R: {risk_projection['r_multiple']}

Summary: {journal_entry['summary']}"""

        from telegram_alert_engine import send_simple_summary_alert
        send_simple_summary_alert(alert_msg)
    except Exception as e:
        print(f"[TELEGRAM] Failed to send signal alert: {e}")

    # --- Write per-entry Markdown summary ---
    entry_ts = journal_entry["timestamp"].replace(":", "").replace("-", "").replace("T", "_")[:15]
    entry_md_path = journal_dir / f"entry_{symbol}_{entry_ts}.md"
    with open(entry_md_path, "w") as f:
        f.write(f"# Trade Entry Summary: {symbol}\n\n")
        f.write(f"- **Time:** {journal_entry['timestamp']}\n")
        f.write(f"- **Trigger:** {journal_entry['trigger']}\n")
        f.write(f"- **Signal:** {journal_entry['entry_signal']}\n")
        f.write(f"- **Confidence:** {journal_entry['confidence']}\n")
        f.write(f"- **Phase:** {journal_entry['phase_context']}\n")
        f.write(f"- **Macro Bias:** {journal_entry['macro_bias']}\n")
        f.write(f"- **Semantic Bias:** {journal_entry['semantic_bias']}\n")
        f.write(f"- **Trust Score:** {journal_entry.get('trust_score')}\n")
        f.write(f"- **Risk Level:** {journal_entry['risk_level']}\n")
        f.write(f"\n---\n\n**Summary**\n\n{journal_entry['summary']}\n")
    print(f"[JOURNAL] Per-entry log written to {entry_md_path}")

    # --- Export signal attributes to journal/signals.csv ---
    signal_log_path = journal_dir / "signals.csv"
    signal_data = {
        "timestamp": journal_entry["timestamp"],
        "symbol": journal_entry["symbol"],
        "entry_signal": journal_entry["entry_signal"],
        "trigger": journal_entry["trigger"],
        "confidence": journal_entry["confidence"],
        "phase": journal_entry["phase_context"],
        "macro_bias": journal_entry["macro_bias"],
        "semantic_bias": journal_entry["semantic_bias"],
        "trust_score": journal_entry.get("trust_score"),
        "risk_level": journal_entry["risk_level"]
    }

    write_header = not signal_log_path.exists()
    with open(signal_log_path, "a") as f:
        df = pd.DataFrame([signal_data])
        df.to_csv(f, index=False, header=write_header)
    print(f"[LOG] Signal appended to {signal_log_path}")

    # Also append signal to signals.jsonl
    signal_jsonl_path = journal_dir / "signals.jsonl"
    with open(signal_jsonl_path, "a") as jf:
        jf.write(json.dumps(signal_data) + "\n")
    print(f"[LOG] Signal appended to {signal_jsonl_path}")

    # Log HTF phase analyst output (Rysiek)
    htf_result = agents["htf_phase_analyst"].evaluate_wyckoff_phase_context()
    # Save HTF phase summary to Markdown
    phase_md_path = journal_dir / f"summary_phase_{symbol}.md"
    with open(phase_md_path, "w") as f:
        f.write(agents["htf_phase_analyst"].to_markdown_summary())
    print(f"[JOURNAL] HTF phase summary written to {phase_md_path}")
    print(f"[HTF PHASE] {htf_result['phase']} → Bias: {htf_result['bias']} | Reason: {htf_result['reason']}")
    try:
        from telegram_alert_engine import send_simple_summary_alert
        send_simple_summary_alert(f"[HTF] {htf_result['phase']} | Bias: {htf_result['bias']} — {htf_result['reason']}")
    except Exception as e:
        print(f"[TELEGRAM] Failed to alert HTF phase: {e}")

    # 5. Determine analysis timestamp
    if timestamp:
        ts = pd.to_datetime(timestamp, utc=True)
    else:
        ts = pd.Timestamp.utcnow()

    # 6. Dispatch to chosen mode
    if mode == 'adv_smc':
        result = run_advanced_smc_strategy(
            all_tf_data=all_tf_data,
            strategy_variant=variant,
            target_timestamp=ts,
            symbol=symbol
        )
    elif mode == 'copilot':
        # Copilot expects specific args
        result = run_copilot_strategy(
            all_tf_data=all_tf_data,
            strategy_variant=variant,
            timestamp_str=ts.strftime('%Y-%m-%d %H:%M:%S'),
            pair=symbol
        )
    elif mode == 'session':
        from core.run_zanalytics_session import main as run_session
        result = run_session(
            all_tf_data=all_tf_data,
            strategy_variant=variant,
            timestamp=ts,
            symbol=symbol
        )
    elif mode == 'boot':
        from core.boot_zanalytics_5_1_9 import main as run_boot
        result = run_boot()

    # 7. Output and journal
    summary = {
        'results': result,
        'wyckoff_result': wyckoff_result
    }
    click.echo(json.dumps(summary, indent=2, default=str))
    # Save summary to markdown
    md_path = journal_dir / f"summary_{mode}_{variant}_{symbol}_{ts.strftime('%Y%m%d_%H%M%S')}.md"
    with open(md_path, 'w') as f:
        f.write(f"# ZANALYTICS Unified Summary\n\n```\n{json.dumps(summary, indent=2, default=str)}\n```\n")
    click.echo(f"Summary written to {md_path}")

if __name__ == "__main__":
    main()