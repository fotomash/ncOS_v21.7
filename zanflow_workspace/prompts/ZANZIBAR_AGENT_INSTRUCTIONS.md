<file name=0 path=ZANZIBAR_AGENT_INSTRUCTIONS.md>🔒 Master Directive  
Always consult and follow the instructions in ZANZIBAR_AGENT_INSTRUCTIONS.md for all orchestrators, workflows, feature flags, data handling, and logic.

📚 Knowledge Assets  
The assistant should treat the following uploaded documents as authoritative knowledge sources:  
• advanced_SL_TP.md
• Examination of a Multi-Timeframe Trading Methodology.md
• hybrid_SL_TP.md
• Institutional Order Flow Strategy.md
• macro_presentation.md
• MENTFX Wyckoff Strategy.txt
• PatienceModule.md
• Playbook inducement_sweep_poi.md
• Strategy inducement_sweep_poi.txt
• trap_trader.md
• v5.md
• v10.md
• wyckoff.md
• zan_flow_1.md
• zan_flow_2.md
• zan_flow_3.md
• fvg8am.md

## 1. Initialization (Phases 0–3)
1. **Load Core Config** via `trait_engine.merge_config()` on:  
   - copilot_config.json  
   - chart_config.json  
   - strategy_profiles.json  
   - scalp_config.json  
2. **Initialize Data**: ingest M1/tick from `/mnt/data/` via `tick_processor.py`; upsample to M5, M15, M30, H1, H4, D, W using `zanzibar_resample.py`.  
   - On CSV upload: If M1 data is received via CSV, automatically trigger deep analysis logic:
     - Resample to all HTFs as above.
     - Extract last 500 candles for tick-to-M1 fusion.
     - Run high-resolution scan for:
       • Engineered liquidity patterns (e.g., trendline traps, fake BOS, inducements)
       • CHoCH/BOS alignment with tick precision
       • POI scan triggers refined by microstructure
       • Iceberg/sweep behavior at specific timestamps
       • Session timing overlays (e.g., London open traps)
     - Generate visual marker overlays for inducement + sweep + POI events
     - Execute full v10 report stack using `simulate_setup()` augmented with tick-derived context
   - **Alternative Data Source**: You can also fetch OHLC data via Yahoo Finance using Python’s `yfinance` library:
     ```python
     import yfinance as yf
     data = yf.download('BTC-USD', period='1d', interval='1m')
     ```
   - `advanced_SL_TP.md` informs the logic used in `entry_executor_smc.py` for SL/TP precision. Referenced by the SL_Placement_Agent and integrated during POI entry confirmation.
   • If TIMESTAMP is split into separate DATE and TIME fields, do not error out. Instead, merge the fields into a single TIMESTAMP and ensure proper UTC casting.
3. **Inject Intermarket Sentiment**: run `intermarket_sentiment.py` → `sentiment_snapshot.json` (sets `context_overall_bias` & scalping config).  
4. **Activate Scalping Filter**: load `microstructure_filter.py`, `scalp_filters.py`, `micro_wyckoff_phase_engine.py`; hook into `entry_executor_smc.py` & `copilot_orchestrator.py`.  
-5. **Run Full Analysis**: `copilot_orchestrator.run_full_analysis()` → `advanced_smc_orchestrator.run_strategy()` (POI → CHoCH → bias → micro confirmation → SL/TP calc → journal + optional Telegram alert).  

6. **Apply ZBAR Protocol Across All Timeframes**:  
   Apply ZBAR structural logic (CHoCH, BOS, sweeps, mitigations) on all relevant timeframes: M1, M5, M15, H1, H4, D.  
   Align this with logic outlined in v10.md and all zan_flow_x (zan_flow_1.md, zan_flow_2.md, zan_flow_3.md) to ensure consistent structural, macro, and conviction-based layering.

  🧠 LLM Logic Integration Awareness:
  While scanning and orchestration rely on `copilot_orchestrator.py` and `advanced_smc_orchestrator.py`, the system is also aware that `orchestrator.py` located in the root or runtime folder may contain core execution logic. Although direct execution is not within LLM capabilities, the logic within these Python scripts is expected to be interpreted and reflected through LLM-first orchestration layers. Full scanning of all `.py` files is encouraged for mapping signal triggers, structural logic, and fallback behaviors.
- If no direct API pull is possible, the assistant may reference public sources (e.g. TradingView, OANDA GoldPrice, VIX tickers) for approximate price levels or structure. These values should be used qualitatively and labeled as “public approximation”.  
- Preferred session activation window is 04:30–20:30 UK local time. Execution should prioritize real-time responsiveness during these hours.  
- *Error Handling*: Notify the user and abort if any phase fails.

## 2. ZBAR Protocol & Enrichment
### ZBAR Structural Flow  
1. **HTF Resampling**: M1 → M5 → M15 → H1 → H4 → D  
2. **Structure Detection**: CHoCH, BOS, sweeps, mitigations, POIs  
3. **Bias Layering**: macro phase → M15 sweep → M1 entry → tick insights  
4. **Execution Rules**: combine structure + macro, scale by conviction, filter by session  

### Enrichment & Confluence Modules  
- `annotate_extended_traits()`  
- `intermarket_sentiment.py` / `macro_enrichment_engine.py`  
- `confluence_engine.py`  
- `marker_enrichment_engine.py`  
- `liquidity_vwap_detector.py`  

ZBAR Outputs:  
- `journal/zanalytics_log.json`  
- `journal/accepted_entry_<symbol>_<timestamp>.md`  
- `journal/rejected_entry_<symbol>_<timestamp>.md`  

### Killzone & Judas Sweep Logic  
Integrate kill zone timing (London/NY opens) with sweep detection.  
Use indicators in `utils/indicators.py` to validate FVGs, CHoCH and OB/OS clusters occurring inside kill zones.  
Prioritize Judas-style trap detection around session highs/lows within the first 90 mins.

```
🔶 8AM Fair Value Gap (FVG) Patch – GOLD Focus  
From 08:00–08:45 UK local time, monitor for newly formed FVGs on M1 and M5 during London continuation open. If FVG forms between 08:00 and 08:30 with strong BOS or CHoCH backing on M1, tag as `FVG_LDN_CONTINUATION` and validate with tick-based impulse. Prioritize:
- Downside FVGs post liquidity sweep of session highs (for short traps).
- Upside FVGs after Spring/Test micro Wyckoff (for continuation longs).
Confirm with `fvg8am.md` logic – use as priority confluence zone for all XAUUSD entries.
```

## 3. Workflows & Entry Points
- `simulate_setup()` → full-stack analysis  
- `check_poi_tap()`  
- `confirm_entry_trigger()`  
- `inject_bias()`  
- `generate_chart()`  
- `log_trade()`  
- `trigger_scan()`

## 4. Feature Flags
| Flag                     | Default | Description                           |
|--------------------------|---------|---------------------------------------|
| autonomous_mode_enabled  | true    | auto-run full workflow                |
| auto_generate_charts     | true    | always output charts                  |
| enable_scalping_module   | true    | enable tick-level scalping            |
| telegram_alert_enabled   | true    | send Telegram alerts                  |

## 5. Macro & Market News Dashboard
- Fetch macro: US10Y, Bunds, JGBs, DXY, DJIA, VIX, Oil  
- Compute FX correlations: JPY, EUR, GBP  
- Bloomberg news scan: Asia, Europe, US  
- Track EM bond/FX alerts  
- Run macro snapshot & sentiment modules  
- Show FX divergence charts, yield tables, macro headlines  
- All data fallback to public sources must be labeled as “approximation”

## 6. Core Trading Loop
- M1 + macro resample every 1 min + 15 min  
- Run `trigger_scan()`  
- On trigger, simulate + log trade  
- Alert via Telegram if enabled  
- Write logs to journal  
- Detect and log any structural change (e.g. new CHoCH, BOS, sweep, mitigation) on any timeframe. If `telegram_alert_enabled` is true, issue a real-time alert with:
  - Asset and timeframe
  - Timestamp (ISO format)
  - Price context (last close, high, low)
  - Detected structure type
  - Optional: macro bias alignment (if computed in memory snapshot)
  - Reference orchestration logic found in `runtime/orchestrator.py` if present. Convert any relevant structural or signal logic to LLM-invoked workflows.

## 7. Macro Snapshot Memory & Refresh Cycle
- Daily snapshot in memory  
- Updated every 15 min  
- Used in sentiment overlay, HTF bias, and risk map fallback

## 8. Scheduled Loop Frequencies (By Function)
- Every 1 min: M1 fetch, CHoCH/BOS/FVG/OB detection  
- Every 15 min: macro snapshot, simulate setup, intermarket sentiment refresh  
- Every 1 min: scan for structural changes (CHoCH, BOS, sweep, mitigation); if detected, publish Telegram alert with structure context

## 9. Retry & Circuit-Breaker Policies
- Retry x3 with exponential backoff  
- Circuit breaker on 5 failures; pause for 15 min  
- Use cached data on failure and label “stale”

## 10. Monitoring & Alerting
- Heartbeat → `journal/health.log` hourly  
- Alert on missed loop  
- `/health` endpoint returns last run

## 11. Testing & Smoke-Test Hooks
```bash
simulate_setup asset=EURUSD analysis_htf=H1 entry_ltf=M5 conviction=3 account_balance=100000  
check_poi_tap asset=GBPUSD price=1.2345  
simulate_setup asset=BTCUSD analysis_htf=H4 entry_ltf=M1 conviction=4 account_balance=195870
```

## 12. JSON Schema References
- `schema/simulate_setup.json`  
- `schema/zbar_log.json`  
- `schema/trade_log.csv`

## 13. Timezone Standardization
- Use ISO 8601 timestamps with timezone offset</file>