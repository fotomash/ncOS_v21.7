import logging
from datetime import datetime
from typing import Any, Dict

import pandas as pd

from ncos_risk_engine import calculate_sl_and_risk

logger = logging.getLogger(__name__)


class DivergenceStrategyAgent:
    """Execute RSI divergence strategy with integrated risk management."""

    def __init__(self, orchestrator: Any, agent_id: str, config: Dict[str, Any]):
        self.orchestrator = orchestrator
        self.agent_id = agent_id
        self.config = config or {}
        self.position = "flat"
        self.account_balance = self.config.get("account_balance", 100_000)
        self.conviction_score = self.config.get("risk_conviction_score", 4)
        self.risk_config = self.config.get("risk_engine_config", {})
        self.atr_config = self.config.get("atr_config", {})
        self.rr_ratio = self.config.get("risk_reward_ratio", 1.5)
        self.max_history_size = self.config.get("max_history_size", 50)
        self.historical_data = pd.DataFrame()

        logger.info("DivergenceStrategyAgent initialized. Position: %s", self.position)

    async def handle_trigger(self, trigger_name: str, payload: Dict[str, Any], session_state: Dict[str, Any]):
        if trigger_name == "data.bar.enriched.xauusd_4h":
            self._update_history(payload)
            await self.evaluate_strategy(payload)
        elif trigger_name == "event.trade.closed" and payload.get("agent_id") == self.agent_id:
            logger.info("Position closed. Resetting state to 'flat'. Reason: %s", payload.get("reason"))
            self.position = "flat"

    def _update_history(self, bar_data: Dict[str, Any]) -> None:
        try:
            new_row = pd.DataFrame([bar_data])
            new_row["timestamp"] = pd.to_datetime(new_row["timestamp"])
            new_row = new_row.set_index("timestamp")
            self.historical_data = pd.concat([self.historical_data, new_row])
            if len(self.historical_data) > self.max_history_size:
                self.historical_data = self.historical_data.iloc[-self.max_history_size :]
        except Exception as exc:  # pragma: no cover - logging
            logger.error("Failed to update historical data buffer: %s", exc)

    async def evaluate_strategy(self, bar_data: Dict[str, Any]) -> None:
        if self.position != "flat":
            return

        bar = pd.Series(bar_data)
        required_cols = ["rsi_bull_div", "rsi_bear_div", "close", "sma_20", "structure"]
        if bar.isnull().any() or not all(col in bar for col in required_cols):
            logger.debug("Skipping evaluation due to missing data in bar.")
            return

        if len(self.historical_data) < self.atr_config.get("period", 14) + 2:
            logger.debug("Skipping evaluation, not enough historical data: %s bars.", len(self.historical_data))
            return

        trade_type = None
        if bar["rsi_bull_div"] and bar["close"] < bar["sma_20"] and bar["structure"] != "bearish":
            trade_type = "buy"
        elif bar["rsi_bear_div"] and bar["close"] > bar["sma_20"] and bar["structure"] != "bullish":
            trade_type = "sell"

        if not trade_type:
            return

        try:
            entry_time = pd.to_datetime(bar["timestamp"]).tz_localize("UTC")
            ohlc_for_engine = self.historical_data.rename(columns={
                "open": "Open",
                "high": "High",
                "low": "Low",
                "close": "Close",
            })

            risk_result = calculate_sl_and_risk(
                account_balance=self.account_balance,
                conviction_score=self.conviction_score,
                entry_price=bar["close"],
                entry_time=entry_time,
                trade_type=trade_type,
                symbol="XAUUSD",
                ohlc_data=ohlc_for_engine,
                risk_config=self.risk_config,
                atr_config=self.atr_config,
            )

            if risk_result.get("status") == "success":
                self.position = "long" if trade_type == "buy" else "short"
                stop_loss = risk_result["final_sl"]
                lot_size = risk_result["lot_size"]
                sl_distance = abs(bar["close"] - stop_loss)
                tp_distance = sl_distance * self.rr_ratio
                take_profit = bar["close"] + tp_distance if trade_type == "buy" else bar["close"] - tp_distance

                trade_payload = {
                    "agent_id": self.agent_id,
                    "symbol": "XAUUSD",
                    "direction": self.position,
                    "entry_price": bar["close"],
                    "stop_loss": round(stop_loss, 2),
                    "take_profit": round(take_profit, 2),
                    "lot_size": lot_size,
                    "timestamp": bar["timestamp"],
                }
                logger.warning("%s SIGNAL DETECTED. Firing trade execution. Details: %s", self.position.upper(), trade_payload)
                await self.orchestrator.route_trigger("action.trade.execute", trade_payload, {})
            else:
                logger.error("Risk Engine failed to calculate parameters. Reason: %s", risk_result.get("error"))
        except Exception as exc:  # pragma: no cover - logging
            logger.error("Error during strategy evaluation with Risk Engine: %s", exc, exc_info=True)
