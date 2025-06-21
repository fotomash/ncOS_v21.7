# Integration Guide for Enhanced Components

## Overview

The enhanced components add comprehensive journaling capabilities to your existing XANFLOW/ZANFLOW system.

## 1. Enhanced Conflict Detector

### Key Features:

- Automatic journal logging of all conflict analyses
- Detailed risk assessment documentation
- Session-based conflict tracking
- Correlation analysis between assets

### Integration:

```python
from enhanced_conflict_detector import EnhancedConflictDetector, ActiveTradeContext, MaturingSetupContext

# Initialize detector
detector = EnhancedConflictDetector()

# Check conflicts and auto-log to journal
report = detector.check_for_conflict(active_trade, maturing_setup)
```

## 2. Enhanced XANFLOW Orchestrator

### Key Features:

- Pipeline execution logging
- Stage-by-stage tracking
- Automatic trade decision logging
- Performance metrics per pipeline

### Integration:

```python
from enhanced_xanflow_orchestrator import EnhancedXanflowOrchestrator

# Initialize orchestrator
orchestrator = EnhancedXanflowOrchestrator()

# Execute pipeline with full logging
result = orchestrator.execute_ispts_pipeline(
    symbol="XAUUSD",
    timeframe="M15",
    session_id="session_20250621",
    initial_context={...}
)
```

## 3. Enhanced Trade Narrative LLM

### Key Features:

- Multiple narrative templates
- Automatic journal entry creation
- Session summaries
- Pattern performance analysis

### Integration:

```python
from enhanced_trade_narrative_llm import EnhancedTradeNarrativeLLM

# Initialize narrator
narrator = EnhancedTradeNarrativeLLM()

# Generate and log narratives
narrative = narrator.generate_trade_narrative(
    trade_context={...},
    narrative_type="trade_setup"  # or "trade_review", "session_summary"
)
```

## Benefits of Integration:

1. **Complete Audit Trail**: Every decision, conflict check, and pipeline execution is logged
2. **Pattern Analysis**: Track which patterns and setups work best over time
3. **Session Review**: Comprehensive session summaries for continuous improvement
4. **Risk Documentation**: All risk assessments are permanently recorded
5. **Performance Tracking**: Measure pipeline and strategy effectiveness

## Quick Start:

1. Ensure the journal API is running:
   ```bash
   ./ncos_journal/launch.sh
   ```

2. Import enhanced components in your existing code:
   ```python
   # Replace imports
   # from conflict_detector import ConflictDetector
   from enhanced_conflict_detector import EnhancedConflictDetector

   # from xanflow_orchestrator import XanflowOrchestrator  
   from enhanced_xanflow_orchestrator import EnhancedXanflowOrchestrator

   # from trade_narrative_llm import TradeNarrativeLLM
   from enhanced_trade_narrative_llm import EnhancedTradeNarrativeLLM
   ```

3. All logging happens automatically - no additional code needed!

## Viewing Logs:

Access the dashboard at http://localhost:8501 to see:

- Conflict analyses under "Analysis"
- Pipeline executions under "Journal"
- Trade narratives under "Journal"
- Session summaries under "ZBAR Analysis"
