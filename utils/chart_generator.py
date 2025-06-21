"""ncOS Unified v5.0 - Chart Generator
Advanced charting with matplotlib for LLM-native visualization"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

try:
    import seaborn as sns
except Exception:  # pragma: no cover - seaborn optional
    sns = None


class ChartGenerator:
    """Advanced chart generation for trading analysis"""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        self.style = self.config.get("style", "dark")
        self.dpi = self.config.get("dpi", 100)
        self.figsize = self.config.get("figsize", (12, 8))

        if self.style == "dark":
            plt.style.use("dark_background")
            self.colors = {
                "bullish": "#00ff88",
                "bearish": "#ff4444",
                "volume": "#888888",
                "ma": "#ffaa00",
                "support": "#00aaff",
                "resistance": "#ff00aa",
            }
        else:
            plt.style.use("default")
            self.colors = {
                "bullish": "#26a69a",
                "bearish": "#ef5350",
                "volume": "#666666",
                "ma": "#ff9800",
                "support": "#2196f3",
                "resistance": "#e91e63",
            }

    # Only include method we need for tests
    def create_correlation_heatmap(
        self, correlation_matrix: pd.DataFrame, title: str = "Correlation Matrix"
    ) -> str:
        """Create correlation heatmap and save to file."""

        fig, ax = plt.subplots(figsize=(10, 8))

        if sns is not None:
            sns.heatmap(
                correlation_matrix,
                annot=True,
                cmap="RdYlBu_r",
                center=0,
                square=True,
                linewidths=0.5,
                cbar_kws={"shrink": 0.8},
            )
        else:  # fallback if seaborn not installed
            im = ax.imshow(
                correlation_matrix,
                cmap="RdYlBu_r",
                vmin=-1,
                vmax=1,
                aspect="auto",
            )
            plt.colorbar(im, ax=ax)
            ax.set_xticks(np.arange(len(correlation_matrix.columns)))
            ax.set_yticks(np.arange(len(correlation_matrix.index)))
            ax.set_xticklabels(correlation_matrix.columns, rotation=45, ha="right")
            ax.set_yticklabels(correlation_matrix.index)

        ax.set_title(title, fontsize=14, fontweight="bold")
        plt.tight_layout()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"correlation_heatmap_{timestamp}.png"
        filepath = Path("charts") / filename
        filepath.parent.mkdir(exist_ok=True)
        plt.savefig(filepath, dpi=self.dpi, bbox_inches="tight")
        plt.close()
        return str(filepath)
