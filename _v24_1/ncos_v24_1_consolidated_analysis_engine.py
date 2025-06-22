
"""
NCOS v24.1 - Consolidated Analysis Engine
Integrates all analysis components: SMC, Wyckoff, Liquidity, Structure
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone, timedelta
import json
import logging
from pathlib import Path
import asyncio

logger = logging.getLogger('NCOS_v24.1.AnalysisEngine')

class ConsolidatedAnalysisEngine:
    """Unified analysis engine integrating all NCOS analysis components"""

    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.analysis_cache = {}
        self.performance_metrics = {}

        # Initialize analysis modules
        self.structure_analyzer = StructureAnalyzer()
        self.wyckoff_analyzer = WyckoffAnalyzer()
        self.liquidity_analyzer = LiquidityAnalyzer()
        self.smc_analyzer = SMCAnalyzer()
        self.confluence_calculator = ConfluenceCalculator()

        logger.info("Consolidated Analysis Engine v24.1 initialized")

    async def analyze_comprehensive(self, symbol: str, data: Dict[str, pd.DataFrame], timeframe_focus: str = 'h1') -> Dict:
        """Perform comprehensive multi-dimensional analysis"""
        try:
            logger.info(f"Starting comprehensive analysis for {symbol} (focus: {timeframe_focus})")

            # 1. Market Structure Analysis
            structure_result = await self.structure_analyzer.analyze(symbol, data, timeframe_focus)

            # 2. Wyckoff Phase Analysis
            wyckoff_result = await self.wyckoff_analyzer.analyze(symbol, data, timeframe_focus)

            # 3. Liquidity Analysis
            liquidity_result = await self.liquidity_analyzer.analyze(symbol, data, timeframe_focus)

            # 4. Smart Money Concepts Analysis
            smc_result = await self.smc_analyzer.analyze(symbol, data, timeframe_focus)

            # 5. Calculate Confluence
            confluence_result = await self.confluence_calculator.calculate(
                structure_result, wyckoff_result, liquidity_result, smc_result
            )

            # 6. Generate Overall Assessment
            overall_assessment = self._generate_overall_assessment(
                structure_result, wyckoff_result, liquidity_result, smc_result, confluence_result
            )

            # Compile final result
            comprehensive_result = {
                'symbol': symbol,
                'timeframe_focus': timeframe_focus,
                'timestamp': datetime.utcnow().isoformat(),
                'structure_analysis': structure_result,
                'wyckoff_analysis': wyckoff_result,
                'liquidity_analysis': liquidity_result,
                'smc_analysis': smc_result,
                'confluence_analysis': confluence_result,
                'overall_assessment': overall_assessment,
                'analysis_quality': self._assess_analysis_quality(structure_result, wyckoff_result, liquidity_result, smc_result)
            }

            # Cache result
            self.analysis_cache[f"{symbol}_{timeframe_focus}"] = comprehensive_result

            return comprehensive_result

        except Exception as e:
            logger.error(f"Comprehensive analysis failed for {symbol}: {e}")
            return {
                'symbol': symbol,
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

    def _generate_overall_assessment(self, structure: Dict, wyckoff: Dict, liquidity: Dict, smc: Dict, confluence: Dict) -> Dict:
        """Generate overall market assessment from all analysis components"""

        # Extract key signals
        structure_bias = structure.get('market_bias', 'neutral')
        wyckoff_phase = wyckoff.get('current_phase', 'unknown')
        liquidity_pressure = liquidity.get('pressure_direction', 'neutral')
        smc_bias = smc.get('institutional_bias', 'neutral')

        # Calculate confidence scores
        structure_confidence = structure.get('confidence_score', 0)
        wyckoff_confidence = wyckoff.get('confidence_score', 0)
        liquidity_confidence = liquidity.get('confidence_score', 0)
        smc_confidence = smc.get('confidence_score', 0)

        overall_confidence = np.mean([structure_confidence, wyckoff_confidence, liquidity_confidence, smc_confidence])

        # Determine consensus direction
        bias_votes = [structure_bias, liquidity_pressure, smc_bias]
        bullish_votes = sum(1 for bias in bias_votes if bias.lower() in ['bullish', 'up', 'long'])
        bearish_votes = sum(1 for bias in bias_votes if bias.lower() in ['bearish', 'down', 'short'])

        if bullish_votes > bearish_votes:
            consensus_direction = 'bullish'
        elif bearish_votes > bullish_votes:
            consensus_direction = 'bearish'
        else:
            consensus_direction = 'neutral'

        # Assess market phase
        market_phase = self._determine_market_phase(wyckoff_phase, structure, liquidity)

        # Generate trading recommendation
        recommendation = self._generate_trading_recommendation(
            consensus_direction, overall_confidence, market_phase, confluence
        )

        return {
            'consensus_direction': consensus_direction,
            'overall_confidence': round(overall_confidence, 3),
            'market_phase': market_phase,
            'bias_alignment': {
                'structure': structure_bias,
                'wyckoff': wyckoff_phase,
                'liquidity': liquidity_pressure,
                'smc': smc_bias
            },
            'confidence_breakdown': {
                'structure': structure_confidence,
                'wyckoff': wyckoff_confidence,
                'liquidity': liquidity_confidence,
                'smc': smc_confidence
            },
            'trading_recommendation': recommendation,
            'key_levels': self._extract_key_levels(structure, liquidity, smc),
            'risk_assessment': self._assess_market_risk(structure, wyckoff, liquidity)
        }

    def _determine_market_phase(self, wyckoff_phase: str, structure: Dict, liquidity: Dict) -> str:
        """Determine current market phase from multiple indicators"""

        # Wyckoff phase mapping
        if 'accumulation' in wyckoff_phase.lower():
            return 'accumulation'
        elif 'distribution' in wyckoff_phase.lower():
            return 'distribution'
        elif 'markup' in wyckoff_phase.lower():
            return 'trending_up'
        elif 'markdown' in wyckoff_phase.lower():
            return 'trending_down'

        # Fallback to structure analysis
        if structure.get('trend_strength', 0) > 0.7:
            return 'trending'
        elif structure.get('consolidation_detected', False):
            return 'consolidation'
        else:
            return 'transitional'

    def _generate_trading_recommendation(self, direction: str, confidence: float, phase: str, confluence: Dict) -> Dict:
        """Generate actionable trading recommendation"""

        confluence_score = confluence.get('overall_score', 0)

        # Determine recommendation strength
        if confidence >= 0.8 and confluence_score >= 0.75:
            strength = 'strong'
        elif confidence >= 0.65 and confluence_score >= 0.6:
            strength = 'moderate'
        elif confidence >= 0.5:
            strength = 'weak'
        else:
            strength = 'avoid'

        # Phase-specific recommendations
        phase_recommendations = {
            'accumulation': 'Look for long entries on pullbacks',
            'distribution': 'Look for short entries on rallies',
            'trending_up': 'Follow trend with pullback entries',
            'trending_down': 'Follow trend with bounce entries',
            'consolidation': 'Range trading or await breakout',
            'transitional': 'Wait for clearer direction'
        }

        return {
            'action': 'buy' if direction == 'bullish' else ('sell' if direction == 'bearish' else 'wait'),
            'strength': strength,
            'confidence': confidence,
            'phase_guidance': phase_recommendations.get(phase, 'Assess market conditions'),
            'entry_timing': self._suggest_entry_timing(phase, direction, confluence_score),
            'risk_level': 'high' if confidence < 0.6 else ('medium' if confidence < 0.75 else 'low')
        }

    def _suggest_entry_timing(self, phase: str, direction: str, confluence_score: float) -> str:
        """Suggest optimal entry timing based on analysis"""

        if confluence_score >= 0.8:
            return 'immediate'
        elif confluence_score >= 0.65:
            return 'next_pullback'
        elif phase in ['accumulation', 'distribution']:
            return 'wait_for_confirmation'
        else:
            return 'monitor_closely'

    def _extract_key_levels(self, structure: Dict, liquidity: Dict, smc: Dict) -> Dict:
        """Extract key price levels from all analysis components"""

        key_levels = {
            'support_levels': [],
            'resistance_levels': [],
            'liquidity_zones': [],
            'poi_levels': []
        }

        # From structure analysis
        if 'support_levels' in structure:
            key_levels['support_levels'].extend(structure['support_levels'])
        if 'resistance_levels' in structure:
            key_levels['resistance_levels'].extend(structure['resistance_levels'])

        # From liquidity analysis
        if 'liquidity_pools' in liquidity:
            key_levels['liquidity_zones'].extend(liquidity['liquidity_pools'])

        # From SMC analysis
        if 'poi_zones' in smc:
            key_levels['poi_levels'].extend(smc['poi_zones'])

        return key_levels

    def _assess_market_risk(self, structure: Dict, wyckoff: Dict, liquidity: Dict) -> Dict:
        """Assess overall market risk from multiple perspectives"""

        risk_factors = []
        risk_score = 0

        # Structure risk factors
        if structure.get('volatility_high', False):
            risk_factors.append('High volatility detected')
            risk_score += 0.3

        # Wyckoff risk factors
        if 'distribution' in wyckoff.get('current_phase', '').lower():
            risk_factors.append('Distribution phase - elevated risk')
            risk_score += 0.4

        # Liquidity risk factors
        if liquidity.get('liquidity_thin', False):
            risk_factors.append('Thin liquidity conditions')
            risk_score += 0.3

        risk_level = 'low' if risk_score < 0.3 else ('medium' if risk_score < 0.6 else 'high')

        return {
            'risk_level': risk_level,
            'risk_score': round(risk_score, 2),
            'risk_factors': risk_factors,
            'mitigation_suggestions': self._suggest_risk_mitigation(risk_level, risk_factors)
        }

    def _suggest_risk_mitigation(self, risk_level: str, risk_factors: List[str]) -> List[str]:
        """Suggest risk mitigation strategies"""

        suggestions = []

        if risk_level == 'high':
            suggestions.extend([
                'Reduce position size',
                'Use tighter stop losses',
                'Consider staying out of market'
            ])
        elif risk_level == 'medium':
            suggestions.extend([
                'Use standard position sizing',
                'Monitor closely for changes',
                'Consider partial entries'
            ])
        else:
            suggestions.append('Normal risk management applies')

        # Factor-specific suggestions
        if 'High volatility' in str(risk_factors):
            suggestions.append('Widen stop losses for volatility')

        if 'Thin liquidity' in str(risk_factors):
            suggestions.append('Use limit orders and avoid market orders')

        return suggestions

    def _assess_analysis_quality(self, structure: Dict, wyckoff: Dict, liquidity: Dict, smc: Dict) -> Dict:
        """Assess the quality and reliability of the analysis"""

        quality_scores = {}

        # Check data completeness
        data_completeness = sum([
            1 if structure.get('data_quality') == 'good' else 0,
            1 if wyckoff.get('data_quality') == 'good' else 0,
            1 if liquidity.get('data_quality') == 'good' else 0,
            1 if smc.get('data_quality') == 'good' else 0
        ]) / 4

        # Check confidence alignment
        confidences = [
            structure.get('confidence_score', 0),
            wyckoff.get('confidence_score', 0),
            liquidity.get('confidence_score', 0),
            smc.get('confidence_score', 0)
        ]

        confidence_std = np.std(confidences)
        alignment_score = max(0, 1 - confidence_std)  # Lower std = better alignment

        overall_quality = (data_completeness + alignment_score) / 2

        return {
            'overall_quality': round(overall_quality, 3),
            'data_completeness': round(data_completeness, 3),
            'confidence_alignment': round(alignment_score, 3),
            'individual_confidences': {
                'structure': confidences[0],
                'wyckoff': confidences[1],
                'liquidity': confidences[2],
                'smc': confidences[3]
            },
            'quality_rating': 'excellent' if overall_quality >= 0.9 else (
                'good' if overall_quality >= 0.7 else (
                'fair' if overall_quality >= 0.5 else 'poor'
                )
            )
        }

# Individual analyzer classes (simplified implementations for consolidation)

class StructureAnalyzer:
    """Market structure analysis component"""

    async def analyze(self, symbol: str, data: Dict, timeframe: str) -> Dict:
        """Analyze market structure"""
        df = data.get(timeframe)
        if df is None or df.empty:
            return {'error': 'No data available for structure analysis'}

        # Simplified structure analysis
        close_prices = df['Close'].values
        highs = df['High'].values
        lows = df['Low'].values

        # Trend analysis
        trend_slope = np.polyfit(range(len(close_prices)), close_prices, 1)[0]
        trend_strength = abs(trend_slope) / np.std(close_prices)

        # Volatility analysis
        volatility = np.std(close_prices) / np.mean(close_prices)

        # Support/Resistance levels (simplified)
        support_levels = [np.min(lows[-20:]), np.min(lows[-50:])]
        resistance_levels = [np.max(highs[-20:]), np.max(highs[-50:])]

        return {
            'market_bias': 'bullish' if trend_slope > 0 else 'bearish',
            'trend_strength': round(trend_strength, 3),
            'volatility_high': volatility > 0.02,
            'support_levels': support_levels,
            'resistance_levels': resistance_levels,
            'confidence_score': min(1.0, trend_strength),
            'data_quality': 'good',
            'consolidation_detected': trend_strength < 0.3
        }

class WyckoffAnalyzer:
    """Wyckoff methodology analysis component"""

    async def analyze(self, symbol: str, data: Dict, timeframe: str) -> Dict:
        """Analyze Wyckoff phases"""
        df = data.get(timeframe)
        if df is None or df.empty:
            return {'error': 'No data available for Wyckoff analysis'}

        # Simplified Wyckoff analysis
        volume = df.get('Volume', pd.Series([100] * len(df))).values
        close_prices = df['Close'].values

        # Volume analysis
        avg_volume = np.mean(volume[-20:])
        volume_trend = np.polyfit(range(len(volume[-20:])), volume[-20:], 1)[0]

        # Price vs Volume analysis
        price_change = close_prices[-1] - close_prices[-20]

        # Determine phase (simplified)
        if volume_trend > 0 and price_change > 0:
            phase = 'Accumulation Phase C (Markup)'
        elif volume_trend > 0 and price_change < 0:
            phase = 'Distribution Phase C (Markdown)'
        elif volume_trend < 0:
            phase = 'Accumulation Phase B'
        else:
            phase = 'Transitional Phase'

        return {
            'current_phase': phase,
            'confidence_score': 0.7,  # Simplified
            'volume_trend': 'increasing' if volume_trend > 0 else 'decreasing',
            'price_volume_relationship': 'healthy' if (price_change > 0 and volume_trend > 0) else 'divergent',
            'data_quality': 'good'
        }

class LiquidityAnalyzer:
    """Liquidity analysis component"""

    async def analyze(self, symbol: str, data: Dict, timeframe: str) -> Dict:
        """Analyze liquidity conditions"""
        df = data.get(timeframe)
        if df is None or df.empty:
            return {'error': 'No data available for liquidity analysis'}

        # Simplified liquidity analysis
        highs = df['High'].values
        lows = df['Low'].values
        volume = df.get('Volume', pd.Series([100] * len(df))).values

        # Liquidity pools (areas of high volume)
        recent_highs = highs[-10:]
        recent_lows = lows[-10:]

        liquidity_pools = [
            {'level': np.max(recent_highs), 'type': 'resistance', 'strength': 0.8},
            {'level': np.min(recent_lows), 'type': 'support', 'strength': 0.7}
        ]

        # Pressure direction
        recent_closes = df['Close'].values[-5:]
        pressure = 'up' if recent_closes[-1] > recent_closes[0] else 'down'

        return {
            'pressure_direction': pressure,
            'liquidity_pools': liquidity_pools,
            'liquidity_thin': np.std(volume) > np.mean(volume),
            'confidence_score': 0.65,
            'data_quality': 'good'
        }

class SMCAnalyzer:
    """Smart Money Concepts analysis component"""

    async def analyze(self, symbol: str, data: Dict, timeframe: str) -> Dict:
        """Analyze Smart Money Concepts"""
        df = data.get(timeframe)
        if df is None or df.empty:
            return {'error': 'No data available for SMC analysis'}

        # Simplified SMC analysis
        close_prices = df['Close'].values
        highs = df['High'].values
        lows = df['Low'].values

        # Order blocks (simplified)
        order_blocks = []

        # FVG zones (simplified)
        fvg_zones = []

        # Institutional bias
        institutional_bias = 'bullish' if close_prices[-1] > np.mean(close_prices[-20:]) else 'bearish'

        # POI zones
        poi_zones = [
            {'level': np.mean(highs[-5:]), 'type': 'supply'},
            {'level': np.mean(lows[-5:]), 'type': 'demand'}
        ]

        return {
            'institutional_bias': institutional_bias,
            'order_blocks': order_blocks,
            'fvg_zones': fvg_zones,
            'poi_zones': poi_zones,
            'confidence_score': 0.6,
            'data_quality': 'good'
        }

class ConfluenceCalculator:
    """Calculate confluence between different analysis methods"""

    async def calculate(self, structure: Dict, wyckoff: Dict, liquidity: Dict, smc: Dict) -> Dict:
        """Calculate overall confluence score"""

        # Extract directional biases
        structure_bullish = structure.get('market_bias') == 'bullish'
        liquidity_bullish = liquidity.get('pressure_direction') == 'up'
        smc_bullish = smc.get('institutional_bias') == 'bullish'

        # Count agreements
        bullish_count = sum([structure_bullish, liquidity_bullish, smc_bullish])
        total_indicators = 3

        agreement_score = bullish_count / total_indicators if bullish_count > total_indicators / 2 else (total_indicators - bullish_count) / total_indicators

        # Factor in confidence scores
        confidence_scores = [
            structure.get('confidence_score', 0),
            wyckoff.get('confidence_score', 0),
            liquidity.get('confidence_score', 0),
            smc.get('confidence_score', 0)
        ]

        avg_confidence = np.mean(confidence_scores)

        # Overall confluence
        overall_score = (agreement_score + avg_confidence) / 2

        return {
            'overall_score': round(overall_score, 3),
            'directional_agreement': agreement_score,
            'average_confidence': round(avg_confidence, 3),
            'individual_agreements': {
                'structure_liquidity': structure_bullish == liquidity_bullish,
                'structure_smc': structure_bullish == smc_bullish,
                'liquidity_smc': liquidity_bullish == smc_bullish
            },
            'confluence_rating': 'high' if overall_score >= 0.8 else (
                'medium' if overall_score >= 0.6 else 'low'
            )
        }

# Example usage
async def test_analysis_engine():
    """Test the consolidated analysis engine"""

    # Create mock data
    dates = pd.date_range(end=pd.Timestamp.now(), periods=100, freq='1H')
    mock_data = {
        'h1': pd.DataFrame({
            'Open': np.random.normal(1.1000, 0.001, 100),
            'High': np.random.normal(1.1005, 0.001, 100),
            'Low': np.random.normal(1.0995, 0.001, 100),
            'Close': np.random.normal(1.1000, 0.001, 100),
            'Volume': np.random.randint(100, 1000, 100)
        }, index=dates)
    }

    # Create analysis engine
    engine = ConsolidatedAnalysisEngine()

    # Run comprehensive analysis
    result = await engine.analyze_comprehensive("EURUSD", mock_data, "h1")

    print("Comprehensive Analysis Result:")
    print(f"Consensus Direction: {result['overall_assessment']['consensus_direction']}")
    print(f"Overall Confidence: {result['overall_assessment']['overall_confidence']}")
    print(f"Market Phase: {result['overall_assessment']['market_phase']}")
    print(f"Trading Recommendation: {result['overall_assessment']['trading_recommendation']['action']}")
    print(f"Analysis Quality: {result['analysis_quality']['quality_rating']}")

if __name__ == "__main__":
    asyncio.run(test_analysis_engine())
