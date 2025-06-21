# ncos_risk_engine.py
"""Core NCOS module for calculating blended stop-loss, volatility-adjusted risk, and lot size."""

import logging
from datetime import datetime
from typing import Any, Dict, Optional, Tuple, List

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# --- Optional Dependencies --------------------------------------------------
try:
    from core.mentfx_stoploss_model_v2_adaptive import compute_mentfx_stop_loss_adaptive

    MENTFX_SL_AVAILABLE = True
    logger.info("[RiskEngine] Imported mentfx_stoploss_model_v2_adaptive.")
except Exception:  # pragma: no cover - optional
    MENTFX_SL_AVAILABLE = False
    logger.warning(
        "[RiskEngine] mentfx_stoploss_model_v2_adaptive.py not found. Structural SL calculation disabled."
    )

try:
    from core.volatility_engine import get_volatility_profile

    VOLATILITY_ENGINE_AVAILABLE = True
    logger.info("[RiskEngine] Imported volatility_engine.")
except Exception:  # pragma: no cover - optional
    VOLATILITY_ENGINE_AVAILABLE = False
    logger.warning(
        "[RiskEngine] volatility_engine.py not found. Volatility regime adjustment disabled."
    )

try:
    import talib

    TALIB_AVAILABLE = True
    logger.info("[RiskEngine] TA-Lib found for ATR calculation.")
except Exception:  # pragma: no cover - optional
    TALIB_AVAILABLE = False
    logger.warning("[RiskEngine] TA-Lib not found. Using pandas for ATR calculation.")

# --- Cross-Domain Risk Analyzer ---------------------------------------------
try:
    from engines.cross_domain_risk_analyzer import CrossDomainRiskAnalyzer, RiskFactor

    CROSS_DOMAIN_AVAILABLE = True
    _cross_domain_analyzer = CrossDomainRiskAnalyzer()
    logger.info("[RiskEngine] CrossDomainRiskAnalyzer initialized.")
except Exception as exc:  # pragma: no cover - optional
    CROSS_DOMAIN_AVAILABLE = False
    _cross_domain_analyzer = None
    logger.warning("[RiskEngine] CrossDomainRiskAnalyzer unavailable: %s", exc)


# --- Dummy Fallbacks --------------------------------------------------------
def _dummy_mentfx_sl(**kwargs) -> Dict[str, Any]:
    logger.debug("[RiskEngine] Using dummy structural SL function.")
    return {"computed_stop_loss": np.nan, "error": "Module not available"}


def _dummy_volatility_profile(**kwargs) -> Dict[str, Any]:
    logger.debug("[RiskEngine] Using dummy volatility profile function.")
    return {"volatility_regime": "Normal", "error": "Module not available"}


if not MENTFX_SL_AVAILABLE:
    compute_mentfx_stop_loss_adaptive = _dummy_mentfx_sl  # type: ignore

if not VOLATILITY_ENGINE_AVAILABLE:
    get_volatility_profile = _dummy_volatility_profile  # type: ignore


# --- Helpers ----------------------------------------------------------------
def calculate_atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """Calculate ATR using TA-Lib if available, otherwise pandas."""
    min_len = period + 1
    if high.isnull().all() or low.isnull().all() or close.isnull().all() or len(high) < min_len:
        return pd.Series(np.nan, index=high.index)

    if TALIB_AVAILABLE:
        try:
            return talib.ATR(high.astype(float), low.astype(float), close.astype(float), timeperiod=period)
        except Exception as exc:  # pragma: no cover - optional
            logger.error("[RiskEngine] TA-Lib ATR calculation failed: %s. Falling back to pandas.", exc)

    high_low = high - low
    high_close_prev = (high - close.shift(1)).abs()
    low_close_prev = (low - close.shift(1)).abs()
    tr = pd.DataFrame({"hl": high_low, "hc": high_close_prev, "lc": low_close_prev}).max(axis=1)
    atr = tr.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    return atr


def get_pip_point_value(symbol: str, account_currency: str = "USD") -> Optional[Tuple[float, int]]:
    """Return point value and decimal precision for a symbol."""
    if not isinstance(symbol, str) or not symbol:
        logger.error("[RiskEngine] Invalid symbol provided to get_pip_point_value: %s", symbol)
        return None

    cleaned = symbol.upper()
    for prefix in [
        "OANDA:",
        "FXCM:",
        "PEPPERSTONE:",
        "ICMARKETS:",
        "FTMO/",
        "FUNDEDTRADINGPLUS/",
    ]:
        if cleaned.startswith(prefix):
            cleaned = cleaned[len(prefix):]
    cleaned = cleaned.replace("_", "").replace("/", "").replace("-", "").replace(".", "")

    aliases = {
        "SPX500": "US500",
        "SPX500USD": "US500",
        "US500CASH": "US500",
        "S&P500": "US500",
        "ES": "US500",
        "NAS100": "USTEC",
        "NAS100USD": "USTEC",
        "USTEC100": "USTEC",
        "NASDAQ100": "USTEC",
        "NQ": "USTEC",
        "GER40": "DE40",
        "DE30": "DE40",
        "DAX40": "DE40",
        "DAX": "DE40",
        "US30": "US30",
        "DOWJONES": "US30",
        "DJ30": "US30",
        "YM": "US30",
        "UK100": "UK100",
        "FTSE100": "UK100",
        "XAUUSD": "XAUUSD",
        "GOLD": "XAUUSD",
        "XAGUSD": "XAGUSD",
        "SILVER": "XAGUSD",
        "BTCUSD": "BTCUSD",
        "BTC": "BTCUSD",
        "ETHUSD": "ETHUSD",
        "ETH": "ETHUSD",
        "USOIL": "WTI",
        "OILUSD": "WTI",
        "OIL": "WTI",
        "CL": "WTI",
        "UKOIL": "BRENT",
        "OILBRENT": "BRENT",
    }
    cleaned = aliases.get(cleaned, cleaned)
    logger.debug("[RiskEngine] Cleaned symbol for Pip/Point lookup: %s", cleaned)

    mapping = {
        "EURUSD": (1.0, 5),
        "GBPUSD": (1.0, 5),
        "AUDUSD": (1.0, 5),
        "NZDUSD": (1.0, 5),
        "USDCAD": (1.0, 5),
        "USDCHF": (1.0, 5),
        "USDJPY": (100.0, 3),
        "EURJPY": (100.0, 3),
        "GBPJPY": (100.0, 3),
        "AUDJPY": (100.0, 3),
        "NZDJPY": (100.0, 3),
        "CADJPY": (100.0, 3),
        "CHFJPY": (100.0, 3),
        "EURGBP": (1.0, 5),
        "EURCHF": (1.0, 5),
        "EURAUD": (1.0, 5),
        "EURCAD": (1.0, 5),
        "EURNZD": (1.0, 5),
        "GBPAUD": (1.0, 5),
        "GBPCAD": (1.0, 5),
        "GBPCHF": (1.0, 5),
        "GBPNZD": (1.0, 5),
        "AUDCAD": (1.0, 5),
        "AUDCHF": (1.0, 5),
        "AUDNZD": (1.0, 5),
        "CADCHF": (1.0, 5),
        "NZDCAD": (1.0, 5),
        "NZDCHF": (1.0, 5),
        "XAUUSD": (1.0, 2),
        "XAGUSD": (5.0, 3),
        "US500": (1.0, 2),
        "USTEC": (1.0, 2),
        "US30": (1.0, 2),
        "DE40": (1.0, 2),
        "UK100": (1.0, 2),
        "JP225": (100.0, 2),
        "AUS200": (1.0, 1),
        "BTCUSD": (1.0, 2),
        "ETHUSD": (1.0, 2),
        "WTI": (1.0, 2),
        "BRENT": (1.0, 2),
    }

    if cleaned in mapping:
        return mapping[cleaned]

    logger.warning(
        "[RiskEngine] Pip/Point value mapping not found for symbol '%s'. Using default FX Major (Point Value=1.0, Decimals=5).",
        symbol,
    )
    return 1.0, 5


def map_conviction_to_risk(score: int) -> float:
    """Map conviction score 1-5 to a risk percentage (decimal)."""
    if not isinstance(score, int) or not 1 <= score <= 5:
        logger.warning(
            "[RiskEngine] Invalid conviction score '%s'. Defaulting to minimum risk (0.25%%).",
            score,
        )
        score = 1
    mapping = {5: 1.00, 4: 0.75, 3: 0.50, 2: 0.35, 1: 0.25}
    return mapping.get(score, 0.25) / 100.0


# --- Main API ----------------------------------------------------------------
def calculate_sl_and_risk(
        account_balance: float,
        conviction_score: int,
        entry_price: float,
        entry_time: datetime,
        trade_type: str,
        symbol: str,
        ohlc_data: pd.DataFrame,
        mentfx_sl_config: Optional[Dict[str, Any]] = None,
        atr_config: Optional[Dict[str, Any]] = None,
        risk_config: Optional[Dict[str, Any]] = None,
        volatility_config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Calculate blended stop-loss and lot size."""
    output: Dict[str, Any] = {
        "status": "error",
        "risk_percent_final": None,
        "final_sl": None,
        "lot_size": None,
        "error": None,
    }

    mentfx_sl_config = mentfx_sl_config or {}
    atr_config = atr_config or {}
    risk_config = risk_config or {}
    volatility_config = volatility_config or {}

    atr_period = atr_config.get("period", 14)
    atr_multiplier = atr_config.get("multiplier", 1.5)

    try:
        risk_percent_base_dec = map_conviction_to_risk(conviction_score)

        vol_profile = get_volatility_profile(ohlc_data, config=volatility_config)
        regime = vol_profile.get("volatility_regime", "Normal")
        output["volatility_regime"] = regime

        adjustment_factor = risk_config.get("vol_adjustment_normal", 1.0)
        if regime == "Explosive":
            adjustment_factor = risk_config.get("vol_adjustment_explosive", 0.75)
        elif regime == "Quiet":
            adjustment_factor = risk_config.get("vol_adjustment_quiet", 1.0)

        adjusted_risk_percent_dec = min(
            risk_percent_base_dec * adjustment_factor,
            risk_config.get("max_risk_percent", 1.0) / 100.0,
        )
        output["risk_percent_final"] = round(adjusted_risk_percent_dec * 100, 2)

        structural_sl = np.nan
        if MENTFX_SL_AVAILABLE:
            logger.debug("[RiskEngine] Skipping Structural SL: tick_data not implemented.")

        atr_sl = np.nan
        if not ohlc_data.empty and all(c in ohlc_data for c in ["High", "Low", "Close"]):
            atr_series = calculate_atr(
                ohlc_data["High"],
                ohlc_data["Low"],
                ohlc_data["Close"],
                period=atr_period,
            )
            atr_value = atr_series.iloc[-1] if not atr_series.empty else np.nan
            if pd.notna(atr_value):
                buffer_val = atr_value * atr_multiplier
                atr_sl = entry_price - buffer_val if trade_type == "buy" else entry_price + buffer_val
            else:
                logger.warning("[RiskEngine] Could not get valid ATR value.")

        blend_logic = risk_config.get("sl_blend_logic", "wider")
        final_sl = np.nan
        valid_structural = pd.notna(structural_sl)
        valid_atr = pd.notna(atr_sl)

        if valid_structural and valid_atr:
            if blend_logic == "atr_priority":
                final_sl = atr_sl
            else:
                if trade_type == "buy":
                    final_sl = min(structural_sl, atr_sl)
                else:
                    final_sl = max(structural_sl, atr_sl)
        elif valid_atr:
            final_sl = atr_sl
        else:
            output["error"] = "ATR SL calculation failed."
            logger.error("[RiskEngine] %s", output["error"])
            return output

        output["final_sl"] = round(final_sl, 5)

        sl_distance_price = abs(entry_price - final_sl)
        point_info = get_pip_point_value(symbol)
        if point_info is None:
            output["error"] = f"Cannot calculate lot size: Point value unknown for {symbol}."
            logger.error("[RiskEngine] %s", output["error"])
            return output

        point_value_per_lot, price_decimals = point_info
        point_increment = 1 / (10 ** price_decimals)
        sl_distance_points = sl_distance_price / point_increment

        if sl_distance_points <= 1e-9:
            output["error"] = "Invalid SL distance (zero or negative)."
            logger.error("[RiskEngine] %s", output["error"])
            return output

        risk_amount_usd = account_balance * adjusted_risk_percent_dec
        denominator = sl_distance_points * point_value_per_lot
        if abs(denominator) < 1e-9:
            output["error"] = "Cannot calculate lot size: Zero denominator."
            logger.error("[RiskEngine] %s", output["error"])
            return output

        raw_lot = risk_amount_usd / denominator
        min_lot_step = risk_config.get("min_lot_step", 0.01)
        lot_size = max(min_lot_step, np.ceil(raw_lot / min_lot_step - 1e-9) * min_lot_step)

        max_lot = risk_config.get("max_lot_size")
        if max_lot and lot_size > max_lot:
            lot_size = max_lot
            logger.warning("[RiskEngine] Calculated lot size exceeds max cap. Clamping to %s.", max_lot)

        output["lot_size"] = round(lot_size, 2)
        output["status"] = "success"
        output["error"] = None

    except Exception as exc:  # pragma: no cover - logging
        output["error"] = f"Unexpected error in calculate_sl_and_risk: {exc}"
        logger.error("[RiskEngine] %s", output["error"], exc_info=True)

    return output


# ---------------------------------------------------------------------------
def add_cross_domain_risk_factor(factor: RiskFactor) -> None:
    """Record a risk factor for cross-domain analysis."""
    if CROSS_DOMAIN_AVAILABLE and _cross_domain_analyzer:
        _cross_domain_analyzer.add_risk_factor(factor)


def get_unified_risk_score() -> Dict[str, Any]:
    """Return unified risk metrics from the cross-domain analyzer."""
    if not CROSS_DOMAIN_AVAILABLE or not _cross_domain_analyzer:
        return {
            "overall_risk": 0.0,
            "domain_risks": {},
            "high_correlations": 0,
            "mitigation_available": 0,
            "risk_trend": "stable",
        }

    return _cross_domain_analyzer.get_unified_risk_score()


def get_mitigation_recommendations() -> List[Dict[str, Any]]:
    """Return mitigation recommendations from the cross-domain analyzer."""
    if CROSS_DOMAIN_AVAILABLE and _cross_domain_analyzer:
        return _cross_domain_analyzer.get_mitigation_recommendations()
    return []


__all__ = [
    "calculate_sl_and_risk",
    "add_cross_domain_risk_factor",
    "get_unified_risk_score",
    "get_mitigation_recommendations",
    "RiskFactor",
]
