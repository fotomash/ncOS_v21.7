# zanlink/schemas/smc_signal_event_schema.json

{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ZanLink SMC Signal Event",
  "description": "Defines a standard format for strategy output signals for GPT and memory integration",
  "type": "object",
  "properties": {
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "Bar close time in ISO format"
    },
    "timeframe": {
      "type": "string",
      "enum": ["1T", "5T", "15T", "30T", "1H", "4H", "1D"],
      "description": "Chart timeframe used for analysis"
    },
    "event_type": {
      "type": "string",
      "description": "Detected signal or pattern type (e.g. RSI_Oversold, CHoCH, BOS, OB, FVG)"
    },
    "indicator_value": {
      "type": ["number", "null"],
      "description": "Numeric value of the triggering indicator, if applicable"
    },
    "price": {
      "type": ["number", "null"],
      "description": "Price at the time of signal (usually close)"
    },
    "structure_context": {
      "type": ["string", "null"],
      "enum": ["bullish", "bearish", "neutral"],
      "description": "Market structure state during signal"
    },
    "notes": {
      "type": ["string", "null"],
      "description": "Optional strategy or signal notes"
    },
    "signal_score": {
      "type": ["number", "null"],
      "description": "Optional predictive confidence score (0–1.0)"
    }
  },
  "required": ["timestamp", "timeframe", "event_type"]
}
