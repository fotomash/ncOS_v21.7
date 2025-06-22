# zanlink/memory/README.md

This folder stores future memory modules for persistent agent recall.

While currently unused, this will later include:
- LangChain memory wrappers (e.g., journal memory, session tags)
- Retrieval tools for confluence scores or failed setup histories

When you're ready to integrate memory:
- Create `memory_router.py` for managing queries
- Add Chroma/FAISS or other vector stores here for private recall

This enables GPT to remember context between sessions, logs, and setups.
