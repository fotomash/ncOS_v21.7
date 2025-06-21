from pydantic import BaseModel
from typing import Any, Dict, List, Optional
import json
import datetime

class JournalConfig(BaseModel):
    """
    Configuration for journaling setups and trades:
    - output_format: 'json' or 'markdown'
    - include_filtered: whether to log setups filtered out by RR or other rules
    - conviction_threshold: float threshold for marking high-confidence setups
    - destination: optional path or URI to persist logs
    """
    output_format: str = 'json'
    include_filtered: bool = True
    conviction_threshold: Optional[float] = None
    destination: Optional[str] = None

class Journal:
    """
    Log every considered setup with structured detail.
    """
    def __init__(self, config: JournalConfig):
        self.config = config
        self.entries: List[Dict[str, Any]] = []

    def log_setup(
        self,
        symbol: str,
        timestamp: datetime.datetime,
        context: Dict[str, Any],
        liquidity: Dict[str, Any],
        structure: Dict[str, Any],
        entries: List[Dict[str, Any]],
        risk: List[Dict[str, Any]],
        confluence: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Record a single trading setup evaluation.
        """
        record = {
            'symbol': symbol,
            'timestamp': timestamp.isoformat(),
            'context': context,
            'liquidity': liquidity,
            'structure': structure,
            'entries': entries,
            'risk': risk,
            'confluence': confluence
        }
        if self.config.include_filtered or any(r['valid'] for r in risk):
            self.entries.append(record)

    def persist(self) -> None:
        """
        Persist logged entries to configured destination in the chosen format.
        """
        if self.config.output_format == 'json':
            data = json.dumps(self.entries, indent=2)
        else:
            md_lines = []
            for rec in self.entries:
                md_lines.append(f"### Setup for {rec['symbol']} at {rec['timestamp']}")
                md_lines.append(f"**Context:** {rec['context']}\n")
                md_lines.append(f"**Liquidity:** {rec['liquidity']}\n")
                md_lines.append(f"**Structure:** {rec['structure']}\n")
                md_lines.append(f"**Entries:** {rec['entries']}\n")
                md_lines.append(f"**Risk & RR:** {rec['risk']}\n")
                if rec.get('confluence') is not None:
                    md_lines.append(f"**Confluence:** {rec['confluence']}\n")
            data = '\n'.join(md_lines)
        if self.config.destination:
            with open(self.config.destination, 'w', encoding='utf-8') as f:
                f.write(data)
        else:
            print(data)
