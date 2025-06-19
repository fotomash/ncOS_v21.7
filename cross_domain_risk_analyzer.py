"""Cross-Domain Risk Analyzer for Bootstrap v14
Analyzes and correlates risks across deployment and trading domains
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import Any, Dict, List, Optional

import numpy as np


@dataclass
class RiskFactor:
    domain: str
    factor_name: str
    severity: float  # 0.0 to 1.0
    impact_radius: List[str]
    mitigation_available: bool


@dataclass
class RiskCorrelation:
    factor1: RiskFactor
    factor2: RiskFactor
    correlation_strength: float  # -1.0 to 1.0
    lag_time: timedelta  # How long before correlation manifests


class CrossDomainRiskAnalyzer:
    """Analyze and correlate risks across multiple operational domains."""

    def __init__(self) -> None:
        self.risk_factors: Dict[str, List[RiskFactor]] = {
            "deployment": [],
            "trading": [],
            "infrastructure": [],
            "business": [],
        }
        self.correlations: List[RiskCorrelation] = []
        self.risk_history: List[float] = []

    def add_risk_factor(self, risk: RiskFactor) -> None:
        """Add a new risk factor to track."""
        domain = risk.domain
        if domain in self.risk_factors:
            self.risk_factors[domain].append(risk)
            self._update_correlations()

    # ------------------------------------------------------------------
    def _update_correlations(self) -> None:
        """Update risk correlations across domains."""
        correlation_pairs = [
            ("deployment.database_migration", "trading.position_management"),
            ("deployment.api_changes", "trading.order_execution"),
            ("infrastructure.latency", "trading.slippage"),
            ("business.trust_score", "trading.position_sizing"),
            ("deployment.rollback", "trading.emergency_close"),
        ]

        for pair in correlation_pairs:
            factor1 = self._find_factor(pair[0])
            factor2 = self._find_factor(pair[1])
            if factor1 and factor2:
                self.correlations.append(self._calculate_correlation(factor1, factor2))

    def _find_factor(self, factor_path: str) -> Optional[RiskFactor]:
        """Find a risk factor by ``domain.name`` path."""
        domain, name = factor_path.split(".")
        if domain in self.risk_factors:
            for factor in self.risk_factors[domain]:
                if factor.factor_name == name:
                    return factor
        return None

    def _calculate_correlation(self, factor1: RiskFactor, factor2: RiskFactor) -> RiskCorrelation:
        """Calculate correlation between two risk factors."""
        base_correlation = 0.0

        if factor1.domain == "deployment" and factor2.domain == "trading":
            if factor1.severity > 0.7:
                base_correlation = 0.8
                lag = timedelta(minutes=5)
            else:
                base_correlation = 0.3
                lag = timedelta(hours=1)
        elif factor1.domain == "infrastructure":
            base_correlation = 0.9
            lag = timedelta(seconds=30)
        elif factor1.domain == "business" and factor2.domain == "trading":
            if "trust" in factor1.factor_name:
                base_correlation = 0.6
                lag = timedelta(hours=24)
        else:
            lag = timedelta(0)

        return RiskCorrelation(
            factor1=factor1,
            factor2=factor2,
            correlation_strength=base_correlation * factor1.severity,
            lag_time=lag,
        )

    # ------------------------------------------------------------------
    def get_unified_risk_score(self) -> Dict[str, Any]:
        """Return a dictionary with aggregated risk metrics."""
        domain_scores: Dict[str, float] = {}
        for domain, factors in self.risk_factors.items():
            if factors:
                domain_scores[domain] = float(np.mean([f.severity for f in factors]))
            else:
                domain_scores[domain] = 0.0

        correlation_multiplier = 1.0
        for corr in self.correlations:
            if corr.correlation_strength > 0.7:
                correlation_multiplier *= 1.1

        overall_risk = float(np.mean(list(domain_scores.values()))) * correlation_multiplier
        overall_risk = min(overall_risk, 1.0)

        return {
            "overall_risk": round(overall_risk, 3),
            "domain_risks": domain_scores,
            "high_correlations": len([c for c in self.correlations if c.correlation_strength > 0.7]),
            "mitigation_available": sum(
                1 for factors in self.risk_factors.values() for f in factors if f.mitigation_available
            ),
            "risk_trend": self._calculate_risk_trend(),
        }

    def _calculate_risk_trend(self) -> str:
        if len(self.risk_history) < 2:
            return "stable"

        recent = self.risk_history[-5:]
        if len(recent) < 2:
            return "stable"

        trend = recent[-1] - recent[0]
        if trend > 0.1:
            return "increasing"
        if trend < -0.1:
            return "decreasing"
        return "stable"

    # ------------------------------------------------------------------
    def get_mitigation_recommendations(self) -> List[Dict[str, Any]]:
        """Return recommended mitigation actions for high risks."""
        recommendations: List[Dict[str, Any]] = []
        for domain, factors in self.risk_factors.items():
            for factor in factors:
                if factor.severity > 0.7 and factor.mitigation_available:
                    recommendations.append(
                        {
                            "domain": domain,
                            "risk": factor.factor_name,
                            "severity": factor.severity,
                            "action": self._get_mitigation_action(domain, factor),
                            "priority": "high" if factor.severity > 0.8 else "medium",
                        }
                    )

        for corr in self.correlations:
            if corr.correlation_strength > 0.8:
                recommendations.append(
                    {
                        "type": "correlation",
                        "factors": f"{corr.factor1.factor_name} <-> {corr.factor2.factor_name}",
                        "action": "Consider decoupling or adding circuit breakers",
                        "priority": "high",
                    }
                )

        return sorted(recommendations, key=lambda x: x.get("priority", "low"))

    def _get_mitigation_action(self, domain: str, factor: RiskFactor) -> str:
        mitigation_map = {
            "deployment": {
                "database_migration": "Run migration in maintenance window",
                "api_changes": "Implement versioning and gradual rollout",
                "rollback": "Prepare automated rollback procedures",
            },
            "trading": {
                "position_management": "Reduce position sizes temporarily",
                "order_execution": "Switch to limit orders only",
                "slippage": "Widen spread tolerance",
            },
            "infrastructure": {
                "latency": "Scale up servers or optimize queries",
                "memory": "Implement memory cleanup routines",
                "cpu": "Distribute load across more instances",
            },
            "business": {
                "trust_score": "Investigate user feedback and address concerns",
                "revenue": "Review pricing model and user engagement",
                "churn": "Implement retention campaigns",
            },
        }
        return mitigation_map.get(domain, {}).get(factor.factor_name, "Review and address root cause")


__all__ = [
    "CrossDomainRiskAnalyzer",
    "RiskFactor",
    "RiskCorrelation",
]
