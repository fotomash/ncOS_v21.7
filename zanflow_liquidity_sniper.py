#!/usr/bin/env python3
'''
Enhanced Liquidity Sniper Agent for ZANFLOW v18
Integrates ZAnalytics 5 liquidity detection with precision targeting
'''

from datetime import datetime
from typing import Dict, List


class LiquiditySniperAgent:
    '''Precision liquidity targeting agent with ZAnalytics integration'''

    def __init__(self, config: Dict):
        self.config = config
        self.agent_id = "liquidity_sniper"
        self.active = True
        self.analysis_history = []

        # Liquidity parameters
        self.min_probability = config.get('min_probability', 0.7)
        self.precision_level = config.get('precision', 'sub_pip')
        self.sweep_detection_sensitivity = config.get('sweep_sensitivity', 0.8)
        self.liquidity_timeframes = config.get('timeframes', ['M5', 'M15', 'H1'])

    def analyze(self, request: Dict) -> Dict:
        '''Analyze liquidity opportunities'''
        try:
            data = request.get('data', {})
            analysis_type = request.get('type', 'market_analysis')

            if analysis_type == 'trade_decision':
                return self._analyze_liquidity_trade(data)
            elif analysis_type == 'market_analysis':
                return self._analyze_liquidity_landscape(data)
            else:
                return self._default_liquidity_analysis(data)

        except Exception as e:
            return {
                'decision': 'hold',
                'confidence': 0.0,
                'reasoning': f'Liquidity analysis error: {str(e)}',
                'liquidity_analysis': {}
            }

    def _analyze_liquidity_trade(self, data: Dict) -> Dict:
        '''Analyze trade opportunity based on liquidity'''
        symbol = data.get('symbol', 'UNKNOWN')
        bid = data.get('bid', 0)
        ask = data.get('ask', 0)
        spread = ask - bid if ask and bid else 0

        # Liquidity analysis components
        liquidity_analysis = {
            'sweep_probability': self._calculate_sweep_probability(data),
            'liquidity_pools': self._identify_liquidity_pools(data),
            'sweep_targets': self._identify_sweep_targets(data),
            'entry_precision': self._calculate_entry_precision(data),
            'liquidity_flow': self._analyze_liquidity_flow(data)
        }

        # Decision based on liquidity analysis
        decision = self._make_liquidity_decision(liquidity_analysis, data)
        confidence = self._calculate_liquidity_confidence(liquidity_analysis)
        reasoning = self._generate_liquidity_reasoning(liquidity_analysis, decision)

        result = {
            'decision': decision,
            'confidence': confidence,
            'reasoning': reasoning,
            'liquidity_analysis': liquidity_analysis,
            'agent_id': self.agent_id,
            'timestamp': datetime.now().isoformat()
        }

        self.analysis_history.append(result)
        return result

    def _calculate_sweep_probability(self, data: Dict) -> float:
        '''Calculate probability of liquidity sweep'''
        # Factors affecting sweep probability
        factors = []

        # Price proximity to key levels
        bid = data.get('bid', 0)
        ask = data.get('ask', 0)

        # Volume analysis (if available)
        volume = data.get('volume', 0)
        if volume > 0:
            factors.append(min(volume / 1000000, 1.0))  # Normalize volume

        # Time-based factors
        current_hour = datetime.now().hour
        if 8 <= current_hour <= 17:  # London/NY session
            factors.append(0.8)
        elif 0 <= current_hour <= 3:  # Asian session
            factors.append(0.6)
        else:
            factors.append(0.4)

        # Spread analysis
        if ask and bid:
            spread = ask - bid
            if spread < 0.0002:  # Tight spread
                factors.append(0.9)
            elif spread < 0.0005:
                factors.append(0.7)
            else:
                factors.append(0.5)

        return sum(factors) / len(factors) if factors else 0.5

    def _identify_liquidity_pools(self, data: Dict) -> List[Dict]:
        '''Identify liquidity pools for targeting'''
        pools = []

        bid = data.get('bid', 0)
        ask = data.get('ask', 0)

        if bid and ask:
            # Buy-side liquidity (above current price)
            pools.append({
                'type': 'buy_side',
                'level': ask + 0.0015,  # 15 pips above
                'size': 'medium',
                'probability': 0.7,
                'timeframe': 'H1'
            })

            # Sell-side liquidity (below current price)
            pools.append({
                'type': 'sell_side',
                'level': bid - 0.0015,  # 15 pips below
                'size': 'medium',
                'probability': 0.7,
                'timeframe': 'H1'
            })

            # Equal highs/lows liquidity
            pools.append({
                'type': 'equal_highs',
                'level': ask + 0.0008,
                'size': 'small',
                'probability': 0.6,
                'timeframe': 'M15'
            })

        return pools

    def _identify_sweep_targets(self, data: Dict) -> List[Dict]:
        '''Identify optimal sweep targets'''
        targets = []
        pools = self._identify_liquidity_pools(data)

        for pool in pools:
            if pool['probability'] >= self.min_probability:
                targets.append({
                    'target_level': pool['level'],
                    'target_type': pool['type'],
                    'entry_level': self._calculate_entry_level(pool, data),
                    'stop_loss': self._calculate_stop_loss(pool, data),
                    'take_profit': self._calculate_take_profit(pool, data),
                    'risk_reward': self._calculate_risk_reward(pool, data)
                })

        return targets

    def _calculate_entry_precision(self, data: Dict) -> float:
        '''Determine entry precision offset based on configured level'''
        if self.precision_level == 'sub_pip':
            return 0.0001
        if self.precision_level == 'pip':
            return 0.001
        return 0.0005

    def _calculate_entry_level(self, pool: Dict, data: Dict) -> float:
        '''Calculate precise entry level'''
        target_level = pool['level']
        current_price = (data.get('bid', 0) + data.get('ask', 0)) / 2

        if pool['type'] == 'buy_side':
            # Enter on sweep and reversal
            return target_level - 0.0003  # 3 pips before target
        elif pool['type'] == 'sell_side':
            # Enter on sweep and reversal
            return target_level + 0.0003  # 3 pips before target

        return current_price

    def _calculate_stop_loss(self, pool: Dict, data: Dict) -> float:
        '''Calculate stop loss level'''
        entry_level = self._calculate_entry_level(pool, data)

        if pool['type'] == 'buy_side':
            return entry_level - 0.0010  # 10 pip stop
        elif pool['type'] == 'sell_side':
            return entry_level + 0.0010  # 10 pip stop

        return entry_level

    def _calculate_take_profit(self, pool: Dict, data: Dict) -> float:
        '''Calculate take profit level'''
        entry_level = self._calculate_entry_level(pool, data)

        if pool['type'] == 'buy_side':
            return entry_level - 0.0020  # 20 pip target (reversal)
        elif pool['type'] == 'sell_side':
            return entry_level + 0.0020  # 20 pip target (reversal)

        return entry_level

    def _calculate_risk_reward(self, pool: Dict, data: Dict) -> float:
        '''Calculate risk-reward ratio'''
        entry = self._calculate_entry_level(pool, data)
        stop = self._calculate_stop_loss(pool, data)
        target = self._calculate_take_profit(pool, data)

        risk = abs(entry - stop)
        reward = abs(target - entry)

        return reward / risk if risk > 0 else 0

    def _analyze_liquidity_flow(self, data: Dict) -> Dict:
        '''Analyze liquidity flow direction'''
        return {
            'direction': 'neutral',
            'strength': 0.5,
            'timeframe': 'M15',
            'confidence': 0.6
        }

    def _make_liquidity_decision(self, liquidity_analysis: Dict, data: Dict) -> str:
        '''Make decision based on liquidity analysis'''
        sweep_probability = liquidity_analysis.get('sweep_probability', 0)
        sweep_targets = liquidity_analysis.get('sweep_targets', [])

        # Decision logic
        if sweep_probability >= self.min_probability and sweep_targets:
            # Find best target
            best_target = max(sweep_targets, key=lambda x: x.get('risk_reward', 0))

            if best_target['risk_reward'] >= 2.0:  # Minimum 2:1 RR
                if best_target['target_type'] == 'buy_side':
                    return 'sell'  # Sell on buy-side liquidity sweep
                elif best_target['target_type'] == 'sell_side':
                    return 'buy'   # Buy on sell-side liquidity sweep

        return 'hold'

    def _calculate_liquidity_confidence(self, liquidity_analysis: Dict) -> float:
        '''Calculate confidence in liquidity analysis'''
        factors = []

        # Sweep probability factor
        sweep_prob = liquidity_analysis.get('sweep_probability', 0)
        factors.append(sweep_prob)

        # Number of targets factor
        targets = liquidity_analysis.get('sweep_targets', [])
        if targets:
            avg_rr = sum(t.get('risk_reward', 0) for t in targets) / len(targets)
            factors.append(min(avg_rr / 3.0, 1.0))  # Normalize to max 3:1 RR

        # Liquidity flow factor
        flow = liquidity_analysis.get('liquidity_flow', {})
        factors.append(flow.get('confidence', 0.5))

        return sum(factors) / len(factors) if factors else 0.5

    def _generate_liquidity_reasoning(self, liquidity_analysis: Dict, decision: str) -> str:
        '''Generate reasoning for liquidity decision'''
        reasoning_parts = []

        sweep_prob = liquidity_analysis.get('sweep_probability', 0)
        reasoning_parts.append(f"Sweep probability: {sweep_prob:.1%}")

        targets = liquidity_analysis.get('sweep_targets', [])
        if targets:
            best_rr = max(t.get('risk_reward', 0) for t in targets)
            reasoning_parts.append(f"Best R:R ratio: {best_rr:.1f}")

        pools = liquidity_analysis.get('liquidity_pools', [])
        reasoning_parts.append(f"{len(pools)} liquidity pools identified")

        return f"Liquidity Analysis: {'; '.join(reasoning_parts)}. Decision: {decision}"

    def _analyze_liquidity_landscape(self, data: Dict) -> Dict:
        '''Analyze overall liquidity landscape'''
        return {
            'decision': 'analyze',
            'confidence': 0.7,
            'reasoning': 'Liquidity landscape analysis completed',
            'liquidity_analysis': {
                'total_pools': len(self._identify_liquidity_pools(data)),
                'sweep_probability': self._calculate_sweep_probability(data)
            },
            'agent_id': self.agent_id
        }

    def _default_liquidity_analysis(self, data: Dict) -> Dict:
        '''Default liquidity analysis'''
        return {
            'decision': 'hold',
            'confidence': 0.5,
            'reasoning': 'Default liquidity analysis - monitoring',
            'liquidity_analysis': {},
            'agent_id': self.agent_id
        }

    def is_active(self) -> bool:
        return self.active

    def emergency_stop(self):
        self.active = False
        print(f"\U0001F6D1 {self.agent_id} emergency stopped")
