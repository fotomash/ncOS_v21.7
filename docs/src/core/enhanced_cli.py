import asyncio
from datetime import datetime
from typing import Dict, Any

import yaml
from config.gpt_instructions import (
    get_auto_progression_config,
)


class EnhancedLLMCLI:
    """Enhanced LLM Native CLI with auto-progression and vector awareness"""

    def __init__(self, bootstrap_system: Any) -> None:
        self.bootstrap = bootstrap_system
        self.auto_progression = get_auto_progression_config()
        self.session_active = False
        self.last_progression = datetime.now()

    async def start(self) -> None:
        """Start the enhanced CLI with auto-progression"""
        print("🚀 Bootstrap OS v5.5.2 Enhanced CLI Started")
        print("Features: Vector Memory, Auto-Progression, Token Optimization")
        print("Type 'help' for commands or use natural language")

        self.session_active = True
        asyncio.create_task(self._auto_progression_monitor())

        while self.session_active:
            try:
                user_input = input("\nBootstrap OS> ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ["exit", "quit"]:
                    await self._graceful_shutdown()
                    break

                response = await self._process_command_with_vectors(user_input)
                print(f"\n{response}")
            except KeyboardInterrupt:
                await self._graceful_shutdown()
                break
            except Exception as e:  # pragma: no cover - runtime safeguard
                print(f"Error: {e}")

    async def _process_command_with_vectors(self, command: str) -> str:
        """Process command with vector memory integration"""

        vector_integration = self.bootstrap.get_component("vector")

        relevant_context = vector_integration.query_agent_knowledge(
            query=command,
            knowledge_type="trading_patterns",
        )

        if any(k in command.lower() for k in ["pattern", "detect", "analyze"]):
            return await self._handle_pattern_command(command, relevant_context)
        if any(k in command.lower() for k in ["risk", "position", "size"]):
            return await self._handle_risk_command(command, relevant_context)
        if any(k in command.lower() for k in ["signal", "trade", "buy", "sell"]):
            return await self._handle_signal_command(command, relevant_context)
        return await self._handle_general_command(command, relevant_context)

    async def _handle_pattern_command(self, command: str, context: list) -> str:
        """Handle pattern detection commands"""
        orchestrator = self.bootstrap.get_component("orchestrator")

        task = {
            "type": "pattern_detection",
            "command": command,
            "context": context,
            "timestamp": datetime.now().isoformat(),
        }

        result = await orchestrator.execute_agent_task("pattern_scanner", task)

        if result.get("confidence", 0) > self.auto_progression["triggers"][
            "pattern_confidence_threshold"
        ]:
            await self._trigger_auto_progression("high_confidence_pattern", result)

        return self._format_yaml_response(result)

    async def _handle_risk_command(self, command: str, context: list) -> str:
        """Handle risk analysis commands"""
        risk_guardian = self.bootstrap.get_component("risk_guardian")

        risk_analysis = await risk_guardian.analyze_with_context(command, context)

        if risk_analysis.get("risk_score", 0) > self.auto_progression["triggers"][
            "risk_score_threshold"
        ]:
            await self._trigger_auto_progression("high_risk", risk_analysis)

        return self._format_yaml_response(risk_analysis)

    async def _handle_signal_command(self, command: str, context: list) -> str:
        """Handle trading signal commands"""
        orchestrator = self.bootstrap.get_component("orchestrator")

        signal_task = {
            "type": "signal_generation",
            "command": command,
            "context": context,
            "requires_consensus": True,
        }

        result = await orchestrator.execute_with_consensus(signal_task)

        consensus_score = result.get("consensus_score", 0)
        if consensus_score >= self.auto_progression["triggers"]["consensus_threshold"]:
            await self._trigger_auto_progression("consensus_reached", result)

        return self._format_yaml_response(result)

    async def _handle_general_command(self, command: str, context: list) -> str:
        """Handle general system commands"""

        if "status" in command.lower():
            return await self._get_system_status()
        if "agents" in command.lower():
            return await self._get_agent_status()
        if "memory" in command.lower():
            return await self._get_memory_status()
        if "performance" in command.lower():
            if "start" in command.lower():
                return await self._start_performance_monitor()
            if "stop" in command.lower():
                return await self._stop_performance_monitor()
            return await self._get_performance_report()
        if "help" in command.lower():
            return self._get_help_text()
        return "Command not recognized. Type 'help' for available commands."

    async def _auto_progression_monitor(self) -> None:
        """Monitor for auto-progression triggers"""
        while self.session_active:
            try:
                time_since_last = (datetime.now() - self.last_progression).total_seconds()
                if (
                        time_since_last
                        > self.auto_progression["triggers"]["session_save_interval"]
                ):
                    await self._trigger_auto_progression("session_save", {})

                orchestrator = self.bootstrap.get_component("orchestrator")
                if hasattr(orchestrator, "check_agent_timeouts"):
                    timeouts = await orchestrator.check_agent_timeouts()
                    if timeouts:
                        await self._trigger_auto_progression("timeout", timeouts)

                await asyncio.sleep(30)
            except Exception as e:  # pragma: no cover - safety
                print(f"Auto-progression monitor error: {e}")
                await asyncio.sleep(60)

    async def _trigger_auto_progression(self, trigger_type: str, data: Dict[str, Any]) -> None:
        """Trigger auto-progression action"""
        action = self.auto_progression["actions"].get(trigger_type)
        if not action:
            return

        print(f"\n🤖 Auto-progression triggered: {trigger_type} -> {action}")

        if action == "generate_signal":
            await self._auto_generate_signal(data)
        elif action == "halt_trading":
            await self._auto_halt_trading(data)
        elif action == "execute_recommendation":
            await self._auto_execute_recommendation(data)
        elif action == "save_session_and_escalate":
            await self._auto_save_and_escalate(data)
        elif action == "request_human_review":
            await self._auto_request_review(data)

        self.last_progression = datetime.now()

    async def _auto_generate_signal(self, data: Dict[str, Any]) -> None:
        """Auto-generate trading signal"""
        print("📊 Auto-generating trading signal based on high-confidence pattern...")

    async def _auto_halt_trading(self, data: Dict[str, Any]) -> None:
        """Auto-halt trading due to high risk"""
        print("🛑 Auto-halting trading due to high risk score...")

    async def _auto_execute_recommendation(self, data: Dict[str, Any]) -> None:
        """Auto-execute consensus recommendation"""
        print("✅ Auto-executing consensus recommendation...")

    async def _auto_save_and_escalate(self, data: Dict[str, Any]) -> None:
        """Auto-save session and escalate to human"""
        session_manager = self.bootstrap.get_component("session_manager")
        session_id = await session_manager.save_session(
            {
                "trigger": "timeout",
                "data": data,
                "timestamp": datetime.now().isoformat(),
            }
        )
        print(f"💾 Session auto-saved: {session_id}")
        print("🚨 Escalating to human review due to timeout...")

    async def _auto_request_review(self, data: Dict[str, Any]) -> None:
        """Auto-request human review"""
        print("👤 Requesting human review due to agent disagreement...")

    def _format_yaml_response(self, data: Dict[str, Any]) -> str:
        """Format response as YAML for token optimization"""
        try:
            return yaml.dump(data, default_flow_style=False, sort_keys=False)
        except Exception:  # pragma: no cover - fallback
            return str(data)

    async def _get_system_status(self) -> str:
        """Get comprehensive system status"""
        status = {
            "system": "Bootstrap OS v5.5.2",
            "status": "active",
            "auto_progression": "enabled",
            "vector_memory": "connected",
            "agents": len(self.bootstrap.get_component("orchestrator").list_agents()),
            "last_progression": self.last_progression.isoformat(),
        }
        return self._format_yaml_response(status)

    async def _get_agent_status(self) -> str:
        orchestrator = self.bootstrap.get_component("orchestrator")
        if orchestrator and hasattr(orchestrator, "get_status"):
            return self._format_yaml_response(orchestrator.get_status())
        return "Agents unavailable"

    async def _get_memory_status(self) -> str:
        vector = self.bootstrap.get_component("vector")
        if vector and hasattr(vector, "get_vector_store_stats"):
            stats = vector.get_vector_store_stats()
            return self._format_yaml_response(stats)
        return "Vector memory unavailable"

    async def _get_performance_report(self) -> str:
        monitor = self.bootstrap.get_component("performance_monitor")
        if monitor and hasattr(monitor, "get_report"):
            report = monitor.get_report()
            if report:
                return self._format_yaml_response(report)
            return "No performance data available"
        return "Performance monitor unavailable"

    async def _start_performance_monitor(self) -> str:
        orchestrator = self.bootstrap.get_component("orchestrator")
        if orchestrator and hasattr(orchestrator, "activate_performance_monitor"):
            await orchestrator.activate_performance_monitor()
            return "Performance monitor started"
        return "Performance monitor unavailable"

    async def _stop_performance_monitor(self) -> str:
        orchestrator = self.bootstrap.get_component("orchestrator")
        if orchestrator and hasattr(orchestrator, "deactivate_performance_monitor"):
            await orchestrator.deactivate_performance_monitor()
            return "Performance monitor stopped"
        return "Performance monitor unavailable"

    async def _graceful_shutdown(self) -> None:
        """Gracefully shutdown the CLI"""
        print("\n🔄 Gracefully shutting down...")
        self.session_active = False
        await self._trigger_auto_progression("session_save", {"reason": "shutdown"})
        print("✅ Bootstrap OS CLI shutdown complete")

    def _get_help_text(self) -> str:
        """Get help text"""
        return """
🎯 Bootstrap OS v5.5.2 Enhanced CLI Commands:

Pattern Analysis:
  • "detect patterns in XAUUSD"
  • "analyze order blocks"
  • "find fair value gaps"

Risk Management:
  • "calculate risk for 0.1 lot EURUSD"
  • "show risk parameters"
  • "validate position size"

Trading Signals:
  • "generate buy signal for XAUUSD"
  • "create trading recommendation"
  • "consensus decision on GBPUSD"

System Commands:
  • "system status"
  • "list agents"
  • "memory status"
  • "performance report"
  • "start performance monitor"
  • "stop performance monitor"
  • "help"

Features:
  ✓ Vector memory integration
  ✓ Auto-progression on triggers
  ✓ Token-optimized responses
  ✓ Multi-agent consensus
  ✓ Session auto-save
        """


async def _run_cli() -> None:
    """Launch the enhanced CLI after bootstrapping the system."""
    from ..launch_ncos_v21_7_1_enhanced_complete import (
        launch_ncos_enhanced_complete,
    )

    orchestrator = await launch_ncos_enhanced_complete(None)
    cli = EnhancedLLMCLI(orchestrator)
    await cli.start()


def main() -> None:
    """Entry point for the ``ncos`` console script."""
    asyncio.run(_run_cli())


__all__ = ["EnhancedLLMCLI", "main"]
