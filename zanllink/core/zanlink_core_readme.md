# zanlink/core/README.md

This folder contains the core business logic for ZanLink.

Each module defines a clean, testable function that can be reused by:
- CLI tools in `zanlink/cli/`
- API endpoints in `zanlink/routes/`
- Orchestration layers like LangGraph or GPT Function Calling

Modules:
- `strategy.py`: runs strategy logic such as ZBAR, structure checks, signal generation
- `charts.py`: generates charts from enriched bar data
- `journal.py`: reads and summarizes trade journal files

All logic should be stateless and pure where possible. File I/O should happen in CLI or API layers, not here.
