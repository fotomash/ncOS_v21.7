from datetime import datetime
from typing import Dict, Any
import pandas as pd

from core.context_analyzer import ContextConfig, ContextAnalyzer
from core.liquidity_engine import LiquidityConfig, LiquidityEngine
from core.structure_validator import StructureConfig, StructureValidator
from core.entry_trigger import EntryConfig, EntryTrigger
from core.risk_manager import RiskConfig, RiskManager
from core.confluence_stacker import ConfluenceConfig, ConfluenceStacker
from core.journal import JournalConfig, Journal

class OrchestratorConfig:
    """
    Configuration for full pipeline orchestration.

    Attributes:
      symbol_list: list of symbols to process
      save_logs: bool to automatically persist logs after running
    """
    symbol_list: list = ['EURUSD', 'GBPUSD']
    save_logs: bool = False

class Orchestrator:
    """
    Sequencing of core pipeline modules for trade signal generation.
    """
    def __init__(self, config: OrchestratorConfig):
        self.config = config
        self.journal = Journal(JournalConfig())

    def run_for_symbol(self, symbol: str) -> None:
        """
        Execute pipeline for a single trading symbol.
        """
        data: Dict[str, pd.DataFrame] = {}  # TO BE FILLED with your data loader

        # 1. Context
        ctx_cfg = ContextConfig()
        ctx_analyzer = ContextAnalyzer(ctx_cfg)
        ctx_res = ctx_analyzer.analyze(symbol)

        # 2. Liquidity
        liq_cfg = LiquidityConfig()
        liq_eng = LiquidityEngine(liq_cfg)
        liq_res = liq_eng.analyze(symbol, data)

        # 3. Structure
        struct_cfg = StructureConfig()
        struct_val = StructureValidator(struct_cfg)
        struct_res = struct_val.validate(symbol, data, ctx_res['bias'])

        # 4. Entry
        entry_cfg = EntryConfig()
        entry_trig = EntryTrigger(entry_cfg)
        entry_res = entry_trig.generate_entries(symbol, data)

        # 5. Risk
        risk_cfg = RiskConfig()
        risk_mgr = RiskManager(risk_cfg)
        is_long = ctx_res['bias'] == 'bullish'
        valid_entries = risk_mgr.analyze(entry_res['entries'], struct_res['swing_origin'][ 'swing_low' if is_long else 'swing_high'], is_long)

        # 6. Confluence
        conf_cfg = ConfluenceConfig()
        conf_stack = ConfluenceStacker(conf_cfg)
        prices = [e['entry'] for e in valid_entries if e['valid']]
        conf_res = conf_stack.analyze(symbol, data, prices)

        # 7. Logging
        timestamp = datetime.utcnow()
        self.journal.log_setup(
            symbol,
            timestamp,
            context=ctx_res,
            liquidity=liq_res,
            structure=struct_res,
            entries=entry_res['entries'],
            risk=valid_entries,
            confluence=conf_res
        )

    def run(self):
        """
        Run orchestration across all configured symbols and persist logs if requested.
        """
        for sym in self.config.symbol_list:
            self.run_for_symbol(sym)
        if self.config.save_logs:
            self.journal.persist()
