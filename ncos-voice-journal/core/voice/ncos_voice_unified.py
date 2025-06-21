
"""
Unified Voice Integration for NCOS ZBAR System
Brings together ZBAR agent and menu system with voice capabilities
"""

from zbar_voice_integration import VoiceEnabledZBARAgent
from menu_voice_integration import VoiceEnabledMenuSystem
from typing import Dict, Any
import asyncio

class NCOSVoiceSystem:
    """Unified voice system for NCOS"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.zbar_agent = VoiceEnabledZBARAgent(config.get("zbar_config", "zbar_config.yaml"))
        self.menu_system = VoiceEnabledMenuSystem(config)

        # Link systems
        self.menu_system.zbar_agent = self.zbar_agent

    async def process_voice_command(self, voice_input: str) -> Dict[str, Any]:
        """Process voice command through appropriate system"""

        # First, parse to understand intent
        tag = self.menu_system.voice_parser.parse(voice_input)

        # Route based on primary action
        if tag.action in ["mark", "log"]:
            # Use menu system for journal entries
            return self.menu_system._voice_mark_setup()

        elif tag.action in ["analyze", "scan", "run"]:
            # Use ZBAR agent for analysis
            return self.zbar_agent.process_voice_command(voice_input)

        elif tag.action in ["check", "show", "find", "query"]:
            # Use menu system for queries
            return self.menu_system._voice_query_journal()

        else:
            # Default to ZBAR agent
            return self.zbar_agent.process_voice_command(voice_input)

    def start_interactive_session(self):
        """Start interactive voice command session"""

        print("🎤 NCOS Voice Command System")
        print("Type 'help' for examples, 'quit' to exit\n")

        while True:
            try:
                command = input("Voice> ").strip()

                if command.lower() == 'quit':
                    break
                elif command.lower() == 'help':
                    self.menu_system._show_voice_examples()
                    continue
                elif not command:
                    continue

                # Process command
                result = asyncio.run(self.process_voice_command(command))

                # Display result
                if result.get("status") == "success":
                    print(f"✅ {result.get('message', 'Command executed successfully')}")
                else:
                    print(f"❌ {result.get('message', 'Command failed')}")

                # Show any additional info
                if result.get("journal_entry"):
                    print(f"📝 Journal: {result['journal_entry']['symbol']} "
                          f"{result['journal_entry']['timeframe']} "
                          f"{result['journal_entry']['bias']}")

                if result.get("analysis"):
                    analysis = result["analysis"]
                    if analysis.get("entry_signal"):
                        print(f"📈 Signal: {analysis['entry_signal']['direction']} "
                              f"@ {analysis['entry_signal']['entry_price']}")

            except KeyboardInterrupt:
                print("\n\nExiting...")
                break
            except Exception as e:
                print(f"Error: {str(e)}")

        print("\nThank you for using NCOS Voice System!")

# Quick start function
def quick_start():
    """Quick start the voice system"""

    config = {
        "api_base": "http://localhost:8001",
        "zbar_config": "zbar_config.yaml"
    }

    system = NCOSVoiceSystem(config)
    system.start_interactive_session()

if __name__ == "__main__":
    quick_start()
