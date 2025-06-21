# 🧠 ZANALYTICS — Institutional-Grade Trading Intelligence System

ZANALYTICS is a modular, macro-aware trading platform that integrates:

- Smart Money Concepts (SMC)
- Wyckoff Market Phase Detection
- Tick-Level Microstructure Filtering
- Intermarket Sentiment Context
- Telegram Alerting for Confirmed Entries
- Dynamic Risk Management (Swing + Scalp Modes)

---

## 🧠 ZANALYTICS SESSION INITIALIZATION (v5.2.1 + Full Agent Stack)

When you receive a `zanalytics_<version>.zip`, initialize with:

```bash
unzip zanalytics_*.zip -d ./zanalytics_workspace/
cd ./zanalytics_workspace/
python runtime/boot_zanalytics_5_2.py \
  --zip-path /mnt/data/zanalytics_5.2.zip \
  --unpack-dir ./zanalytics_workspace \
  --enable-scalping true
```

### 🚀 Boot Phases
1. Load & merge config → `trait_engine.merge_config()`
2. M1 + Tick ingestion → auto HTF resample
3. Intermarket sentiment injection
4. Microstructure filters (CHoCH, BOS, Spring)
5. Full copilot + advanced strategy orchestration
6. Agent stack execution + journaling

### 🧠 Active Agents
- `Bożenka`: microstructure trigger detection
- `Rysiek`: H1/H4 phase logic (C/D/E)
- `Zdzisiek`: risk profile (spread, volatility)
- `MacroAgent`: sentiment bias
- `Stefania`: reputation scoring and trust audit
- `Lusia`: semantic DSS + confluence analysis
- `TradeJournal`: Markdown + CSV logs

### 📝 Logs
- Confirmed entries → `journal/accepted_entry_*.md`
- Rejections → `journal/rejected_entry_*.md`
- ZBAR mini-journals → `journal/entry_<SYMBOL>_<TIMESTAMP>.md`
- Semantic DSS summaries → `journal/summary_semantic_<SYMBOL>.md`
- HTF Wyckoff summaries → `journal/summary_phase_<SYMBOL>.md`
- CSV + JSONL signal ledger → `journal/signals.csv`, `journal/signals.jsonl`
- Macro snapshot → `journal/sentiment_snapshot.json`
- Markdown + Telegram alerts (if enabled)
- Git commits for full audit trail (if repo present)

To start:

```bash
python main_orchestrator.py --variant Inv --symbol XAUUSD
```

Or run interactively via the notebook:
`notebooks/zanalytics_agent_training.ipynb`

## 📁 Directory Overview

### `/config/`
Environment and behavior configuration.

| File | Description |
|------|-------------|
| `scalp_config.json` | Microstructure filters, thresholds, risk per trade |
| `webhook_settings.json` | Telegram bot credentials and toggle |
| `trait_config.json` | SMC-related heuristics and routing traits |
| `chart_config.json` | Chart rendering styles |
| `strategy_profiles.json` | Predefined strategy templates |

---

### `/core/`
Primary analysis engines and logic modules.

| Module | Function |
|--------|----------|
| `microstructure_filter.py` | Tick-level validation |
| `micro_wyckoff_phase_engine.py` | Spring/Test/LPS detection |
| `intermarket_sentiment.py` | Macro bias context |
| `entry_executor_smc.py` | Executes filtered entries |
| `scalp_filters.py` | Signal validation logic |
| `scalp_session_filter.py` | Session-based filtering |
| `telegram_alert_engine.py` | Sends alerts to Telegram |
| `copilot_awareness_engine.py` | LLM context and sentiment alignment |

---

### `/runtime/`
Session orchestration.

| Script | Role |
|--------|------|
| `copilot_orchestrator.py` | Routing + bias management |
| `run_zanalytics_session.py` | CLI runner |
| `boot_zanalytics_5_2.py` | Startup CLI with flags |

---

### `/journal/`
Auto-logged trade decisions and meta outputs.

| File | Contents |
|------|----------|
| `zanalytics_log.json` | Full session metadata |
| `sentiment_snapshot.json` | Macro + strategy bias |
| `accepted_entry_*.md` | Confirmed entries |
| `micro_rejections.md` | Failed microstructure filters |
| `session_log.csv` | Timeline journal |
| `trade_log.csv` | Historical trades |

---

### `/tick_data/`
Feed for M1 and tick-level CSVs.

- Raw M1 and tick CSVs go in `tick_data/m1/`
- Higher-timeframe CSVs are auto-generated in `tick_data/htf/`
- Expect files named like `SYMBOL_M1_*.csv` or tick feeds with `<Date>,<Time>,<Bid>,<Ask>,<Volume>` columns.

---

## 🧪 Strategy Stack

- ✅ SMC + Wyckoff detection (macro)
- ✅ Entry confirmation via CHoCH, BOS, mitigation
- ✅ Risk and SL/TP model
- ✅ Scalp triggers from Spring/LPS
- ✅ Telegram alerts (configurable)
- ✅ Markdown journaling

---

## 🚀 Launch

```bash
python runtime/boot_zanalytics_5_2.py \
  --zip-path /mnt/data/zanalytics_5.2.zip \
  --unpack-dir ./zanalytics_workspace \
  --enable-scalping true
```

# Real-Data Pipeline
This system uses real OHLCV CSVs for M1 and auto-resamples
to H1/H4/D1/W1 via `resample_m1_to_htf_parallel.py`. No dummy
data generators are used.

# Macro Data Integration
You can now feed macroeconomic data through
the `analysis/macro` pipeline to enrich intermarket sentiment.

---

## 🛰️ Telegram

When `webhook_settings.json` is active:
- Sends alerts for all confirmed trades
- Supports markdown and formatting for easy mobile parsing

---

## 🛠️ Roadmap

- [x] Multi-agent AI orchestration: microstructure + macro bias + risk journaling
- [ ] Socket listener for live tick injection
- [ ] GUI/Notebook chart sync
- [ ] Full session replay from logs
- [ ] Risk telemetry feedback via Telegram or Notion

---
