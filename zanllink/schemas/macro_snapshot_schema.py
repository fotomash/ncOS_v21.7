# zanlink/schemas/macro_snapshot_schema.json

{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ZanLink Macro Snapshot",
  "description": "Defines macroeconomic context relevant to session and instrument-level reasoning",
  "type": "object",
  "properties": {
    "timestamp": { "type": "string", "format": "date-time" },
    "headline": { "type": "string" },
    "bias": { "type": "string", "enum": ["bullish", "bearish", "neutral"] },
    "flags": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Semantic tags like 'gold', 'usd', 'inflation', 'fomc'"
    },
    "usd_index": { "type": "number" },
    "fed_funds_rate": { "type": "number" },
    "oil": { "type": "number" },
    "relevant_to": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Asset symbols this macro context most affects"
    }
  },
  "required": ["timestamp", "bias", "headline", "flags"]
}
