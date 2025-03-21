## Lego

Python utilities initially for ChatBot Development and Cloud Engineering.

## Structure

- `utils`, `settings.py`, `models.py`, `lego_types.py` ─ probably the most
  (if not only) useful part of this projects:
  - some handy type definitions,
  - settings for different services (e.g., those of AWS),
  - models for switching between `camelStyle` and `snake_case_style`.
  - other utilities (profiling, downloading, and etc.)
- `messages` ─ models for parsing messages to standardized view for further
  processing and storing.
- `llm` ─ a package with a simple router for load balancing of requests to
  OpenAI API-like services  
  (with key rotation, retrial policies, and fallbacks).
- `rag` ─ a demo of RAG pipeline based on LlamaIndex and MilvusDB  
  (getting obsolete since is not maintained and LlamaIndex is rapidly developing).
