
import asyncio
import pandas as pd
import logging
from ncos_base_agent import NCOSBaseAgent

logger = logging.getLogger(__name__)

class MarketManipulationAgent(NCOSBaseAgent):
    """
    Detects market manipulation patterns in real-time tick data.
    """
    def __init__(self, orchestrator, agent_id, config):
        super().__init__(orchestrator, agent_id, config)
        self.thresholds = self.config.get('manipulation_thresholds', {})
        self.stats = {
            'ticks_processed': 0,
            'spread_events': 0,
            'quote_stuffing_events': 0
        }

    async def handle_trigger(self, trigger_name, payload, session_state):
        if trigger_name == 'data.tick.xauusd':
            await self.analyze_tick(payload)

    async def analyze_tick(self, tick_data):
        """Analyzes a single tick for manipulation patterns."""
        self.stats['ticks_processed'] += 1

        try:
            bid = float(tick_data.get('bid', 0))
            ask = float(tick_data.get('ask', 0))
            timestamp = tick_data.get('timestamp')

            if bid and ask:
                spread = ask - bid
                spread_config = self.thresholds.get('spread_manipulation', {})
                alert_threshold = spread_config.get('alert_threshold', 999)

                if spread > alert_threshold:
                    self.stats['spread_events'] += 1
                    severity = min(10, int(spread / spread_config.get('normal_spread', 0.25) * 2))

                    event_payload = {
                        'symbol': 'XAUUSD',
                        'spread': round(spread, 4),
                        'severity': severity,
                        'timestamp': timestamp
                    }
                    await self.orchestrator.route_trigger('analysis.manipulation.spread_detected', event_payload, {})

        except Exception as e:
            logger.error(f"Error analyzing tick: {e}")

    def get_status(self):
        return {**super().get_status(), **self.stats}
