
"""
ncOS Unified v5.0 - Enhanced Menu with Voice Integration
Extends existing menu_system.py with voice command support
"""

from typing import Dict, List, Any
from menu_system import MenuSystem
from voice_tag_parser import VoiceTagParser, VoiceTag

class EnhancedMenuSystem(MenuSystem):
    """Menu system with voice command integration"""

    def __init__(self, config: Dict):
        super().__init__(config)
        self.voice_parser = VoiceTagParser()
        self.voice_history = []

    def process_voice_command(self, voice_input: str) -> Dict[str, Any]:
        """Process voice command and route to appropriate action"""
        # Parse voice input
        tag = self.voice_parser.parse(voice_input)
        self.voice_history.append(tag)

        # Convert to menu action
        menu_action = self.voice_parser.to_menu_action(tag)

        # Execute action based on confidence
        if tag.confidence >= 0.7:
            # High confidence - execute immediately
            result = self._execute_action(menu_action)
            return {
                "status": "executed",
                "tag": tag.__dict__,
                "action": menu_action,
                "result": result
            }
        elif tag.confidence >= 0.4:
            # Medium confidence - confirm with user
            return {
                "status": "confirm_needed",
                "tag": tag.__dict__,
                "action": menu_action,
                "message": f"Did you mean to {menu_action['action']} for {tag.symbol} {tag.timeframe}?"
            }
        else:
            # Low confidence - suggest alternatives
            suggestions = self._get_voice_suggestions(tag)
            return {
                "status": "clarification_needed",
                "tag": tag.__dict__,
                "suggestions": suggestions,
                "message": "I didn't quite understand. Did you mean one of these?"
            }

    def _execute_action(self, action: Dict) -> Any:
        """Execute menu action from voice command"""
        action_name = action["action"]
        params = action["params"]

        # Route to appropriate handler
        if action_name == "append_journal":
            return self._append_to_journal(params)
        elif action_name == "run_analysis":
            return self._run_zbar_analysis(params)
        elif action_name == "pattern_search":
            return self._run_pattern_search(params)
        elif action_name == "execute_strategy":
            return self._execute_strategy(params)
        else:
            return {"error": f"Unknown action: {action_name}"}

    def _get_voice_suggestions(self, tag: VoiceTag) -> List[Dict]:
        """Get suggestions for unclear voice commands"""
        suggestions = []

        # Suggest based on partial matches
        if tag.symbol:
            suggestions.append({
                "command": f"analyze {tag.symbol} on all timeframes",
                "action": "multi_timeframe_analysis"
            })

        if tag.bias:
            suggestions.append({
                "command": f"find {tag.bias} setups across all symbols",
                "action": "bias_scan"
            })

        # Add common commands
        suggestions.extend([
            {
                "command": "check current risk assessment",
                "action": "risk_check"
            },
            {
                "command": "show today's journal entries",
                "action": "journal_view"
            }
        ])

        return suggestions[:3]  # Return top 3 suggestions

    def get_voice_menu(self) -> Dict:
        """Get voice command menu"""
        return {
            "title": "🎤 Voice Commands",
            "examples": [
                "Mark gold bullish on H4",
                "Analyze EURUSD 15 minute chart",
                "Check London session setups",
                "Run ZBAR scan on all majors",
                "Log trade idea: potential reversal at support"
            ],
            "patterns": {
                "marking": "mark [symbol] [bias] on [timeframe]",
                "analysis": "analyze [symbol] [timeframe]",
                "scanning": "scan for [pattern] in [session]",
                "logging": "log [your notes here]"
            }
        }
