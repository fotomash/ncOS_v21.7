"""Chart Engine - LLM-native chart generation using matplotlib.

This module provides advanced charting utilities for visualizing trading data.
"""

from __future__ import annotations

import matplotlib

# Use Agg backend for headless environments
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


class ChartEngine:
    """Advanced charting capabilities for trading data."""

    def __init__(self, style: str = "dark_background") -> None:
        self.style = style
        plt.style.use(self.style)

    def generate_price_chart(self, df: pd.DataFrame, title: str = "Price Chart") -> str:
        """Generate a price chart with optional moving averages.

        Parameters
        ----------
        df: pd.DataFrame
            DataFrame indexed by datetime with at least ``close`` and ``volume`` columns.
        title: str, optional
            Chart title.

        Returns
        -------
        str
            Filename of the saved chart image.
        """
        fig, (ax1, ax2) = plt.subplots(
            2,
            1,
            figsize=(12, 8),
            gridspec_kw={"height_ratios": [3, 1]},
        )

        ax1.plot(df.index, df["close"], label="Close", color="cyan", linewidth=2)
        if "sma_20" in df.columns:
            ax1.plot(df.index, df["sma_20"], label="SMA 20", color="yellow", alpha=0.7)
        if "sma_50" in df.columns:
            ax1.plot(df.index, df["sma_50"], label="SMA 50", color="orange", alpha=0.7)

        ax1.set_title(title, fontsize=16, fontweight="bold")
        ax1.set_ylabel("Price", fontsize=12)
        ax1.legend(loc="upper left")
        ax1.grid(True, alpha=0.3)

        ax2.bar(df.index, df["volume"], color="green", alpha=0.7)
        ax2.set_ylabel("Volume", fontsize=12)
        ax2.set_xlabel("Time", fontsize=12)
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        filename = f"chart_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(filename, dpi=300, bbox_inches="tight")
        plt.close()
        return filename

    def generate_heatmap(self, correlation_matrix: pd.DataFrame) -> str:
        """Generate a correlation heatmap.

        Parameters
        ----------
        correlation_matrix: pd.DataFrame
            Matrix of correlation values ranging from -1 to 1.

        Returns
        -------
        str
            Filename of the generated heatmap image.
        """
        fig, ax = plt.subplots(figsize=(10, 8))

        im = ax.imshow(correlation_matrix, cmap="RdBu", aspect="auto", vmin=-1, vmax=1)
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label("Correlation", fontsize=12)

        ax.set_xticks(np.arange(len(correlation_matrix.columns)))
        ax.set_yticks(np.arange(len(correlation_matrix.index)))
        ax.set_xticklabels(correlation_matrix.columns, rotation=45, ha="right")
        ax.set_yticklabels(correlation_matrix.index)
        ax.set_title("Feature Correlation Heatmap", fontsize=16, fontweight="bold")

        plt.tight_layout()
        filename = f"heatmap_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(filename, dpi=300, bbox_inches="tight")
        plt.close()
        return filename
