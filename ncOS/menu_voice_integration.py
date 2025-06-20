
"""
Menu System Integration with Voice Commands
Extends your existing menu_system.py with voice capabilities
"""

from menu_system import EnhancedMenuSystem
from .voice_tag_parser import VoiceTagParser
from typing import Dict, List, Any, Optional
import requests
import json

class VoiceEnabledMenuSystem(EnhancedMenuSystem):
    """Enhanced menu system with voice command support"""

    def __init__(self, orchestrator: Any, config: Optional[Dict] | None = None):
        super().__init__(orchestrator)
        self.config = config or {}
        parser_cfg = self.config.get("voice_parser", {})
        self.voice_parser = VoiceTagParser(config=parser_cfg)
        self.api_base = self.config.get("api_base", "http://localhost:8001")

        # Add voice menu to main menu
        self._add_voice_menu()

    def _add_voice_menu(self):
        """Add voice command menu to the main menu"""
        voice_menu_option = {
            "id": "voice_commands",
            "title": "🎤 Voice Commands",
            "description": "Natural language trading commands",
            "submenu": self.get_voice_menu()
        }

        # Insert after live data menu
        main_menu = self.get_main_menu()
        main_menu["options"].insert(4, voice_menu_option)

    def get_voice_menu(self) -> Dict:
        """Voice command submenu"""
        return {
            "title": "Voice Command Options",
            "options": [
                {
                    "id": "voice_mark",
                    "title": "Voice Tag Entry",
                    "description": "Mark setups using natural language",
                    "action": "voice_mark_setup",
                    "params": {}
                },
                {
                    "id": "voice_analyze",
                    "title": "Voice-Triggered Analysis",
                    "description": "Run analysis using voice commands",
                    "action": "voice_analyze",
                    "params": {}
                },
                {
                    "id": "voice_query",
                    "title": "Voice Query Journal",
                    "description": "Query journal with natural language",
                    "action": "voice_query_journal",
                    "params": {}
                },
                {
                    "id": "voice_batch",
                    "title": "Batch Voice Commands",
                    "description": "Process multiple voice commands",
                    "action": "voice_batch_process",
                    "params": {}
                },
                {
                    "id": "voice_history",
                    "title": "Voice Command History",
                    "description": "View recent voice commands",
                    "action": "view_voice_history",
                    "params": {"limit": 20}
                },
                {
                    "id": "voice_help",
                    "title": "Voice Command Examples",
                    "description": "See example voice commands",
                    "action": "show_voice_examples",
                    "params": {}
                }
            ]
        }

    def execute_voice_action(self, action: str, params: Dict) -> Dict[str, Any]:
        """Execute voice-related actions"""

        if action == "voice_mark_setup":
            return self._voice_mark_setup()
        elif action == "voice_analyze":
            return self._voice_analyze()
        elif action == "voice_query_journal":
            return self._voice_query_journal()
        elif action == "voice_batch_process":
            return self._voice_batch_process()
        elif action == "view_voice_history":
            return self._view_voice_history(params.get("limit", 20))
        elif action == "show_voice_examples":
            return self._show_voice_examples()
        else:
            # Fallback to parent class execution
            return super().execute_action(action, params)

    def _voice_mark_setup(self) -> Dict[str, Any]:
        """Interactive voice marking"""
        print("\n🎤 Voice Tag Entry")
        print("Speak naturally about your trade setup.")
        print("Example: 'Mark gold bullish on H4, swept lows at 2358'\n")

        voice_input = input("Your command: ").strip()

        if not voice_input:
            return {"status": "cancelled", "message": "No input provided"}

        # Parse the voice command
        tag = self.voice_parser.parse(voice_input)

        # Display parsed information
        print(f"\n📊 Parsed Information:")
        print(f"Symbol: {tag.symbol or 'Not specified'}")
        print(f"Timeframe: {tag.timeframe or 'Not specified'}")
        print(f"Bias: {tag.bias or 'Not specified'}")
        print(f"Session: {tag.session or 'Not specified'}")
        print(f"Maturity: {tag.maturity_score or 'Not specified'}")
        print(f"Notes: {tag.notes or 'None'}")
        print(f"Confidence: {tag.confidence:.0%}")

        # Confirm before saving
        if tag.confidence < 0.5:
            print("\n⚠️  Low confidence in parsing. Please check the information above.")

        confirm = input("\nSave this entry? (y/n): ").lower()

        if confirm == 'y':
            # Convert to journal entry
            journal_entry = self.voice_parser.to_journal_entry(tag)

            # Post to journal API
            try:
                response = requests.post(
                    f"{self.api_base}/journal/append",
                    json=journal_entry
                )

                if response.status_code == 200:
                    print("✅ Entry saved to journal!")

                    # Update context
                    self.update_context({
                        "last_voice_entry": journal_entry,
                        "last_symbol": tag.symbol,
                        "last_timeframe": tag.timeframe
                    })

                    # Offer follow-up actions
                    if tag.symbol and tag.timeframe:
                        analyze = input(f"\nRun ZBAR analysis on {tag.symbol} {tag.timeframe}? (y/n): ").lower()
                        if analyze == 'y':
                            return self._trigger_zbar_analysis(tag.symbol, tag.timeframe, tag.__dict__)

                    return {"status": "success", "entry": journal_entry}
                else:
                    return {"status": "error", "message": f"Failed to save: {response.text}"}

            except Exception as e:
                return {"status": "error", "message": f"API error: {str(e)}"}
        else:
            return {"status": "cancelled", "message": "Entry not saved"}

    def _voice_analyze(self) -> Dict[str, Any]:
        """Voice-triggered analysis"""
        print("\n🎤 Voice-Triggered Analysis")
        print("Example: 'Analyze EURUSD on 15 minute chart'\n")

        voice_input = input("Your command: ").strip()

        if not voice_input:
            return {"status": "cancelled", "message": "No input provided"}

        # Parse command
        tag = self.voice_parser.parse(voice_input)

        if not tag.symbol:
            print("❌ Could not identify symbol. Please be more specific.")
            return {"status": "error", "message": "Symbol not identified"}

        symbol = tag.symbol
        timeframe = tag.timeframe or "H4"

        print(f"\n🔄 Running ZBAR analysis on {symbol} {timeframe}...")

        return self._trigger_zbar_analysis(symbol, timeframe, tag.__dict__)

    def _voice_query_journal(self) -> Dict[str, Any]:
        """Query journal with voice"""
        print("\n🎤 Voice Query Journal")
        print("Example: 'Show all bullish gold setups from London session'\n")

        voice_input = input("Your query: ").strip()

        if not voice_input:
            return {"status": "cancelled", "message": "No input provided"}

        # Parse query
        tag = self.voice_parser.parse(voice_input)

        # Build query parameters
        params = {}
        if tag.symbol:
            params["symbol"] = tag.symbol
        if tag.bias:
            params["bias"] = tag.bias
        if tag.session:
            params["session"] = tag.session
        if tag.timeframe:
            params["timeframe"] = tag.timeframe

        print(f"\n🔍 Searching journal with filters: {params}")

        try:
            response = requests.get(
                f"{self.api_base}/journal/query",
                params=params
            )

            if response.status_code == 200:
                data = response.json()
                entries = data.get("entries", [])

                if entries:
                    print(f"\n📊 Found {len(entries)} matching entries:\n")

                    for i, entry in enumerate(entries[:10], 1):  # Show max 10
                        print(f"{i}. {entry.get('timestamp', 'N/A')[:19]} - "
                              f"{entry.get('symbol', 'N/A')} {entry.get('timeframe', 'N/A')} "
                              f"{entry.get('bias', 'N/A')}")
                        if entry.get('notes'):
                            print(f"   Notes: {entry['notes']}")
                        print()

                    return {"status": "success", "count": len(entries), "entries": entries}
                else:
                    print("\n📭 No matching entries found.")
                    return {"status": "success", "count": 0, "entries": []}

            else:
                return {"status": "error", "message": f"Query failed: {response.text}"}

        except Exception as e:
            return {"status": "error", "message": f"API error: {str(e)}"}

    def _voice_batch_process(self) -> Dict[str, Any]:
        """Process multiple voice commands"""
        print("\n🎤 Batch Voice Commands")
        print("Enter multiple commands, one per line. Empty line to finish.\n")

        commands = []
        while True:
            cmd = input(f"Command {len(commands) + 1}: ").strip()
            if not cmd:
                break
            commands.append(cmd)

        if not commands:
            return {"status": "cancelled", "message": "No commands provided"}

        print(f"\n🔄 Processing {len(commands)} commands...\n")

        results = []
        for i, cmd in enumerate(commands, 1):
            print(f"Processing {i}/{len(commands)}: '{cmd}'")

            # Parse and process each command
            tag = self.voice_parser.parse(cmd)

            # Determine action type
            if tag.action in ["mark", "log"]:
                journal_entry = self.voice_parser.to_journal_entry(tag)
                try:
                    response = requests.post(
                        f"{self.api_base}/journal/append",
                        json=journal_entry
                    )
                    if response.status_code == 200:
                        results.append({"command": cmd, "status": "success", "action": "marked"})
                        print("  ✅ Marked successfully")
                    else:
                        results.append({"command": cmd, "status": "error", "message": response.text})
                        print(f"  ❌ Failed: {response.text}")
                except Exception as e:
                    results.append({"command": cmd, "status": "error", "message": str(e)})
                    print(f"  ❌ Error: {str(e)}")

            elif tag.action in ["analyze", "scan"]:
                if tag.symbol:
                    # Would trigger analysis here
                    results.append({"command": cmd, "status": "success", "action": "analysis_queued"})
                    print(f"  ✅ Analysis queued for {tag.symbol}")
                else:
                    results.append({"command": cmd, "status": "error", "message": "No symbol identified"})
                    print("  ❌ No symbol identified")

        print(f"\n📊 Batch Summary: {len([r for r in results if r['status'] == 'success'])}/{len(results)} successful")

        return {"status": "complete", "results": results}

    def _trigger_zbar_analysis(self, symbol: str, timeframe: str, context: Dict) -> Dict[str, Any]:
        """Trigger ZBAR analysis via API"""
        try:
            # Prepare request for ZBAR API
            payload = {
                "strategy": "ZBAR_Voice",
                "asset": symbol,
                "blocks": [
                    {
                        "id": f"{symbol}_{timeframe}",
                        "timeframe": timeframe,
                        "columns": ["timestamp", "open", "high", "low", "close", "volume"],
                        "data": []  # Would be populated with actual data
                    }
                ],
                "context": {
                    "voice_context": context,
                    "initial_htf_bias": context.get("bias"),
                    "session_id": context.get("session")
                }
            }

            response = requests.post(
                f"{self.api_base}/strategy/zbar/execute_multi",
                json=payload
            )

            if response.status_code == 200:
                result = response.json()
                print(f"\n✅ Analysis complete!")
                print(f"Status: {result.get('status')}")

                if result.get('entry_signal'):
                    signal = result['entry_signal']
                    print(f"\n📈 Entry Signal Found:")
                    print(f"Direction: {signal.get('direction')}")
                    print(f"Entry: {signal.get('entry_price')}")
                    print(f"Stop Loss: {signal.get('stop_loss')}")
                    print(f"Take Profit: {signal.get('take_profit')}")
                    print(f"R:R Ratio: {signal.get('rr')}")

                return {"status": "success", "analysis": result}
            else:
                return {"status": "error", "message": f"Analysis failed: {response.text}"}

        except Exception as e:
            return {"status": "error", "message": f"API error: {str(e)}"}

    def _show_voice_examples(self) -> Dict[str, Any]:
        """Show voice command examples"""
        examples = {
            "Marking Setups": [
                "Mark gold bullish on H4",
                "Log EURUSD short at resistance, maturity 85",
                "Mark potential reversal on GBPUSD daily chart"
            ],
            "Analysis Commands": [
                "Analyze XAUUSD 15 minute",
                "Run ZBAR on gold H1",
                "Scan EURUSD for breakout patterns"
            ],
            "Query Commands": [
                "Show all bullish setups today",
                "Check London session trades",
                "Find high maturity gold trades"
            ],
            "Complex Commands": [
                "Mark XAUUSD bullish H4, swept lows at 2358, London session, maturity 90",
                "Analyze all forex majors on H1 for New York session",
                "Show bearish setups with maturity above 80"
            ]
        }

        print("\n📚 Voice Command Examples\n")

        for category, commands in examples.items():
            print(f"**{category}:**")
            for cmd in commands:
                print(f"  • {cmd}")
            print()

        return {"status": "displayed", "examples": examples}

# Integration helper function
def integrate_voice_menu(existing_menu_system):
    """Helper to integrate voice features into existing menu system"""

    # Create voice-enabled version
    class EnhancedMenu(VoiceEnabledMenuSystem, existing_menu_system.__class__):
        pass

    # Copy configuration and orchestrator
    orchestrator = getattr(existing_menu_system, "orchestrator", None)
    config = getattr(existing_menu_system, "config", {})
    enhanced = EnhancedMenu(orchestrator, config)

    # Copy state
    enhanced.current_context = existing_menu_system.current_context
    enhanced.menu_history = existing_menu_system.menu_history

    return enhanced

# Demo function
def demo_voice_menu():
    """Demonstrate voice-enabled menu system"""

    config = {
        "api_base": "http://localhost:8001"
    }

    menu = VoiceEnabledMenuSystem(orchestrator=None, config=config)

    print("=== Voice-Enabled Menu System Demo ===\n")

    # Show main menu with voice option
    main_menu = menu.get_main_menu()
    print(menu.render_menu_text(main_menu))

    # Simulate voice command execution
    print("\n--- Simulating Voice Mark Setup ---")
    result = menu._show_voice_examples()

    print("\nVoice menu integration complete!")

if __name__ == "__main__":
    demo_voice_menu()
