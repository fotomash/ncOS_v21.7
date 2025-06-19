"""
NCOS Predictive Engine
Core module for predictive scoring and quality assessment of trading setups
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime, timezone
from pathlib import Path
import json
import yaml

from ncos_predictive_schemas import (
    PredictiveEngineConfig, FactorWeights, GradeThresholds,
    ConflictDetectionConfig, PredictiveScorerConfig
)

logger = logging.getLogger(__name__)

class PredictiveScorer:
    """
    Calculates maturity scores and grades for trading setups based on multiple factors.
    """

    def __init__(self, config: PredictiveScorerConfig):
        self.config = config
        self.factor_weights = config.factor_weights
        self.grade_thresholds = config.grade_thresholds
        self.conflict_detection = config.conflict_detection_settings
        logger.info(f"PredictiveScorer initialized with min_entry_score: {config.min_score_to_emit_potential_entry}")

    def calculate_maturity_score(self, features: Dict[str, float]) -> Tuple[float, str, Dict[str, Any]]:
        """
        Calculate the overall maturity score based on weighted features.

        Returns:
            Tuple of (maturity_score, grade, scoring_details)
        """
        if not self.config.enabled:
            return 0.0, "N/A", {"enabled": False}

        # Extract weights as a dict
        weights = self.factor_weights.dict()

        # Calculate weighted score
        weighted_sum = 0.0
        weight_sum = 0.0
        factor_scores = {}

        for factor, weight in weights.items():
            if factor in features:
                score = features[factor]
                # Ensure score is between 0 and 1
                score = max(0.0, min(1.0, score))
                weighted_sum += score * weight
                weight_sum += weight
                factor_scores[factor] = {
                    "raw_score": score,
                    "weight": weight,
                    "weighted_score": score * weight
                }

        # Normalize by actual weight sum (in case some factors are missing)
        maturity_score = weighted_sum / weight_sum if weight_sum > 0 else 0.0

        # Determine grade
        grade = self._calculate_grade(maturity_score)

        # Compile scoring details
        scoring_details = {
            "maturity_score": round(maturity_score, 4),
            "grade": grade,
            "factor_scores": factor_scores,
            "total_weight_used": round(weight_sum, 4),
            "potential_entry": maturity_score >= self.config.min_score_to_emit_potential_entry
        }

        logger.debug(f"Calculated maturity score: {maturity_score:.4f} (Grade: {grade})")

        return maturity_score, grade, scoring_details

    def _calculate_grade(self, score: float) -> str:
        """Assign a grade based on the maturity score."""
        if score >= self.grade_thresholds.A:
            return "A"
        elif score >= self.grade_thresholds.B:
            return "B"
        elif score >= self.grade_thresholds.C:
            return "C"
        else:
            return "D"

    def check_conflict_with_active_trades(
        self, 
        new_setup_score: float,
        new_setup_direction: str,
        active_trades: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Check if a new setup conflicts with existing active trades.

        Returns conflict analysis including recommendations.
        """
        if not self.conflict_detection.enabled or not active_trades:
            return {"has_conflict": False}

        conflicts = []

        for trade in active_trades:
            # Check for opposite direction trades
            if trade.get("direction") != new_setup_direction:
                conflict_info = {
                    "trade_id": trade.get("id"),
                    "trade_direction": trade.get("direction"),
                    "conflict_type": "opposite_direction"
                }

                # Add recommendation based on new setup quality
                if new_setup_score >= self.conflict_detection.suggest_review_trade_if_new_setup_maturity_above:
                    conflict_info["recommendation"] = "review_active_trade"
                    conflict_info["reason"] = f"New {new_setup_direction} setup has very high quality ({new_setup_score:.2f})"
                elif new_setup_score >= self.conflict_detection.min_new_setup_maturity_for_conflict_alert:
                    conflict_info["recommendation"] = "monitor_both"
                    conflict_info["reason"] = f"New setup quality ({new_setup_score:.2f}) warrants attention"
                else:
                    conflict_info["recommendation"] = "ignore_new_setup"
                    conflict_info["reason"] = f"New setup quality ({new_setup_score:.2f}) too low"

                conflicts.append(conflict_info)

        return {
            "has_conflict": len(conflicts) > 0,
            "conflicts": conflicts,
            "new_setup_score": new_setup_score,
            "new_setup_direction": new_setup_direction
        }


class PredictiveJournal:
    """
    Handles logging and persistence of predictive scoring results.
    """

    def __init__(self, config: PredictiveJournalingConfig):
        self.config = config
        self.log_dir = Path(config.log_directory)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"PredictiveJournal initialized. Log directory: {self.log_dir}")

    def log_evaluation(
        self, 
        timestamp: datetime,
        symbol: str,
        features: Dict[str, float],
        scoring_result: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ):
        """Log a predictive evaluation if it meets the criteria."""
        if not self.config.enabled:
            return

        maturity_score = scoring_result.get("maturity_score", 0.0)

        # Check if we should log this evaluation
        if not self.config.log_all_evaluations and maturity_score < self.config.min_maturity_score_to_log:
            return

        # Prepare log entry
        log_entry = {
            "timestamp": timestamp.isoformat(),
            "symbol": symbol,
            "features": features,
            "scoring_result": scoring_result,
            "context": context or {}
        }

        # Generate filename
        date_str = timestamp.strftime("%Y%m%d")
        base_filename = f"predictive_journal_{symbol}_{date_str}"

        # Write log based on format preference
        if self.config.log_format in ["json", "both"]:
            json_file = self.log_dir / f"{base_filename}.json"
            self._append_json_log(json_file, log_entry)

        if self.config.log_format in ["yaml", "both"]:
            yaml_file = self.log_dir / f"{base_filename}.yaml"
            self._append_yaml_log(yaml_file, log_entry)

        logger.info(f"Logged predictive evaluation: {symbol} @ {timestamp} (Score: {maturity_score:.4f})")

    def _append_json_log(self, filepath: Path, entry: Dict[str, Any]):
        """Append entry to JSON log file."""
        if filepath.exists():
            with open(filepath, 'r') as f:
                data = json.load(f)
        else:
            data = {"entries": []}

        data["entries"].append(entry)

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    def _append_yaml_log(self, filepath: Path, entry: Dict[str, Any]):
        """Append entry to YAML log file."""
        if filepath.exists():
            with open(filepath, 'r') as f:
                data = yaml.safe_load(f) or {"entries": []}
        else:
            data = {"entries": []}

        data["entries"].append(entry)

        with open(filepath, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)


class NCOSPredictiveEngine:
    """
    Main orchestrator for the NCOS Predictive Engine.
    Coordinates feature extraction, scoring, and journaling.
    """

    def __init__(self, config: PredictiveEngineConfig):
        self.config = config
        self.scorer = PredictiveScorer(config.predictive_scorer)
        self.journal = PredictiveJournal(config.journaling)
        logger.info("NCOS Predictive Engine initialized")

    def evaluate_setup(
        self,
        timestamp: datetime,
        symbol: str,
        features: Dict[str, float],
        active_trades: Optional[List[Dict[str, Any]]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate a trading setup and return comprehensive analysis.
        """
        # Calculate maturity score
        maturity_score, grade, scoring_details = self.scorer.calculate_maturity_score(features)

        # Check for conflicts if applicable
        conflict_analysis = {}
        if active_trades and context and "direction" in context:
            conflict_analysis = self.scorer.check_conflict_with_active_trades(
                maturity_score,
                context["direction"],
                active_trades
            )

        # Compile full evaluation result
        evaluation_result = {
            "timestamp": timestamp.isoformat(),
            "symbol": symbol,
            "scoring": scoring_details,
            "conflict_analysis": conflict_analysis,
            "recommendation": self._generate_recommendation(scoring_details, conflict_analysis)
        }

        # Log the evaluation
        self.journal.log_evaluation(timestamp, symbol, features, scoring_details, context)

        return evaluation_result

    def _generate_recommendation(
        self, 
        scoring_details: Dict[str, Any], 
        conflict_analysis: Dict[str, Any]
    ) -> str:
        """Generate a trading recommendation based on scoring and conflicts."""
        grade = scoring_details.get("grade", "D")
        potential_entry = scoring_details.get("potential_entry", False)
        has_conflict = conflict_analysis.get("has_conflict", False)

        if not potential_entry:
            return "SKIP - Quality too low"

        if has_conflict:
            conflicts = conflict_analysis.get("conflicts", [])
            if any(c.get("recommendation") == "review_active_trade" for c in conflicts):
                return "REVIEW_ACTIVE - New setup superior"
            else:
                return "MONITOR - Conflict detected"

        if grade == "A":
            return "EXECUTE - High quality setup"
        elif grade == "B":
            return "EXECUTE_REDUCED - Good quality setup"
        elif grade == "C":
            return "CONSIDER - Moderate quality setup"
        else:
            return "SKIP - Below minimum quality"
