"""
FVG Locator – Step 4 gate in the ZANFLOW ISPTS pipeline (CTO-grade refactor).

Responsibilities
----------------
1. Confirm an entry-worthy Fair Value Gap created by the impulse leg that
   produced the validated CHoCH / BoS.
2. Remain fully deterministic, direction-aware, and configuration-driven.
3. Emit a structured result dict and never mutate inbound ``state``.
4. Provide trace-grade logging for audit / RCA.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TypedDict, List, Dict, Any

from pydantic import BaseModel, ValidationError


class Candle(TypedDict):
    open: float
    high: float
    low: float
    close: float


class FVGLocatorConfig(BaseModel):
    max_fvg_size_pips: int = 12
    pip_precision: int = 5
    use_midpoint: bool = True
    scan_depth: int = 3
    inclusive: bool = True


class FVGLocator:
    MODULE = "FVGLocator"

    def __init__(self, logger=None):
        self._log = logger or (lambda *_a, **_kw: None)

    def run(
        self,
        data: List[Candle],
        state: Dict[str, Any],
        raw_cfg: Dict[str, Any],
    ) -> Dict[str, Any]:
        if not state.get("Structural_Shift_Detected"):
            return self._fail("NO_STRUCTURAL_SHIFT")

        try:
            cfg = FVGLocatorConfig(**raw_cfg)
        except ValidationError as exc:
            self._log(self.MODULE, {"level": "ERROR", "error": exc.errors()})
            return self._fail("CONFIG_VALIDATION_ERROR")

        if len(data) < cfg.scan_depth:
            return self._fail("NOT_ENOUGH_DATA")

        direction: str = state.get("direction", "bullish")
        pip = Decimal(10) ** (-cfg.pip_precision)

        scan_range = range(-cfg.scan_depth, 0)
        for i in scan_range:
            c1: Candle = data[i - 2]
            c3: Candle = data[i]

            if self._gap_is_valid(c1, c3, direction, cfg, pip):
                entry_price = (
                    (Decimal(c1["low"]) + Decimal(c3["high"])) / 2
                    if direction == "bullish" and cfg.use_midpoint
                    else Decimal(c3["high"])
                    if direction == "bullish"
                    else (Decimal(c1["high"]) + Decimal(c3["low"])) / 2
                    if cfg.use_midpoint
                    else Decimal(c3["low"])
                )

                result = {
                    "status": "PASS",
                    "entry_price": float(entry_price),
                    "fvg_bounds": [
                        round(float(c3["high" if direction == "bullish" else "low"]), cfg.pip_precision),
                        round(float(c1["low" if direction == "bullish" else "high"]), cfg.pip_precision),
                    ],
                    "direction": direction,
                }
                self._log(self.MODULE, result)
                return result

        return self._fail("NO_FVG_FOUND")

    def _gap_is_valid(
        self,
        c1: Candle,
        c3: Candle,
        direction: str,
        cfg: FVGLocatorConfig,
        pip: Decimal,
    ) -> bool:
        if direction == "bullish" and c1["low"] > c3["high"]:
            gap_size = (Decimal(c1["low"]) - Decimal(c3["high"])) / pip
        elif direction == "bearish" and c1["high"] < c3["low"]:
            gap_size = (Decimal(c3["low"]) - Decimal(c1["high"])) / pip
        else:
            return False

        return gap_size <= cfg.max_fvg_size_pips if cfg.inclusive else gap_size < cfg.max_fvg_size_pips

    def _fail(self, reason: str) -> Dict[str, str]:
        payload = {"status": "FAIL", "reason": reason}
        self._log(self.MODULE, payload)
        return payload
