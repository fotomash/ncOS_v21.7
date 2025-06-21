from __future__ import annotations

import argparse
import csv
import json
from typing import Any, Dict, List, Sequence

import numpy as np
import pandas as pd


class BacktestEngine:
    """Simple backtesting engine for NCOS strategies."""

    def __init__(self, strategies: Sequence[Any], initial_capital: float = 10000.0) -> None:
        self.strategies = list(strategies)
        self.initial_capital = initial_capital
        self.reset()

    def reset(self) -> None:
        """Reset engine state."""
        self.cash = self.initial_capital
        self.position = 0.0
        self.trades: List[Dict[str, Any]] = []
        self.equity: List[float] = []

    @staticmethod
    def load_csv(path: str) -> pd.DataFrame:
        """Load historical data from CSV.

        The CSV must contain a ``close`` column and use the first column as the
        datetime index.
        """
        df = pd.read_csv(path, parse_dates=True, index_col=0)
        if "close" not in df.columns:
            raise ValueError("CSV must contain a 'close' column")
        return df

    def run(self, data: pd.DataFrame, symbol: str = "TEST") -> Dict[str, float]:
        """Run backtest on provided data."""
        self.reset()
        total = len(data)
        for i, (timestamp, row) in enumerate(data.iterrows()):
            market_data = {
                "prices": data.loc[:timestamp, "close"].tolist(),
                "current_price": row["close"],
                "symbol": symbol,
                "index": i,
                "last_index": total - 1,
            }
            for strat in self.strategies:
                if hasattr(strat, "generate_signals"):
                    signals = strat.generate_signals(market_data)
                    for sig in signals:
                        self._execute_signal(sig, row["close"], timestamp)
            self.equity.append(self.cash + self.position * row["close"])
        return self._compute_metrics()

    def _execute_signal(self, signal: Dict[str, Any], price: float, timestamp: Any) -> None:
        action = signal.get("type") or signal.get("action")
        if action in {"buy", "long", "entry_long"} and self.position == 0:
            qty = self.cash / price
            self.position = qty
            self.cash -= qty * price
            self.trades.append({"entry_time": str(timestamp), "entry_price": price})
        elif action in {"sell", "short", "exit_long"} and self.position > 0:
            pnl = (price - self.trades[-1]["entry_price"]) * self.position
            self.cash += self.position * price
            self.position = 0
            self.trades[-1].update(
                {"exit_time": str(timestamp), "exit_price": price, "pnl": pnl}
            )

    def _compute_metrics(self) -> Dict[str, float]:
        eq = np.array(self.equity, dtype=float)
        if len(eq) < 2:
            returns = np.array([])
        else:
            returns = np.diff(eq) / eq[:-1]
        sharpe = (
            float(np.mean(returns) / np.std(returns) * np.sqrt(252))
            if len(returns) > 1 and np.std(returns) > 0
            else 0.0
        )
        running_max = np.maximum.accumulate(eq) if len(eq) else np.array([])
        drawdowns = (eq - running_max) / running_max if len(eq) else np.array([])
        max_drawdown = float(drawdowns.min()) if len(drawdowns) else 0.0
        profits = [t["pnl"] for t in self.trades if t.get("pnl", 0) > 0]
        losses = [-t["pnl"] for t in self.trades if t.get("pnl", 0) < 0]
        if losses:
            profit_factor = float(sum(profits) / sum(losses)) if profits else 0.0
        else:
            profit_factor = float("inf") if profits else 0.0
        return {
            "sharpe_ratio": sharpe,
            "max_drawdown": max_drawdown,
            "profit_factor": profit_factor,
        }

    def save_results(self, result_path: str, trades_path: str) -> None:
        """Save metrics and trade log."""
        metrics = self._compute_metrics()
        with open(result_path, "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2)
        if self.trades:
            with open(trades_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=list(self.trades[0].keys()))
                writer.writeheader()
                writer.writerows(self.trades)


def _cli() -> None:
    parser = argparse.ArgumentParser(description="NCOS backtesting engine")
    parser.add_argument("data", help="CSV file with historical price data")
    parser.add_argument(
        "--strategy",
        choices=["maz2", "tmc"],
        default="maz2",
        help="Strategy to run",
    )
    parser.add_argument("--output_json", default="backtest_results.json")
    parser.add_argument("--output_csv", default="trades.csv")
    args = parser.parse_args()

    df = BacktestEngine.load_csv(args.data)
    if args.strategy == "tmc":
        from agents.tmc_executor import TMCExecutor

        strategy = TMCExecutor({})
    else:
        from agents.maz2_executor import MAZ2Executor

        strategy = MAZ2Executor({})

    engine = BacktestEngine([strategy])
    metrics = engine.run(df)
    engine.save_results(args.output_json, args.output_csv)
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    _cli()
