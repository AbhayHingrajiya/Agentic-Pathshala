# Agentic Pathshala

**Agentic Pathshala** is a terminal-based **AI learning coach**. Learners sign in, review assignments stored in Excel, and chat with a **LangGraph**-orchestrated coach that routes questions to **RAG** (Chroma + Hugging Face embeddings) or **assignment-aware** answers via **Groq** LLMs and an optional **FastMCP** server (SSE).

---

## What you get

| Capability | Description |
|------------|-------------|
| **Rich CLI** | Banner, login, menu, and status spinners for long operations. |
| **Intent routing** | Coordinator classifies the user message (`assignment_query`, `notes_query`, etc.). |
| **Notes / RAG** | Retrieves top chunks from Chroma (`rag/retriever.py`), then answers with `notes_agent`. |
| **Assignments** | Assignment branch loads learner-specific rows via MCP tool `get_assignments_for_learner`. |
| **Local data** | Learners, assignments, progress, and notes live under `data/storage/` as `.xlsx` files (`utils/excel_store.py`). |

---

## Architecture (high level)

```
┌─────────────┐     ┌─────────────────────────────────────────────────────┐
│  main.py    │────▶│ LangGraph (orchestrator/graph.py)                   │
│  Rich UI    │     │  START → coordinator → route → notes | assignment | │
└──────┬──────┘     │  fallback → response → END                           │
       │            └───────────┬─────────────────────┬───────────────────┘
       │                        │                     │
       ▼                        ▼                     ▼
┌──────────────┐         ┌─────────────┐       ┌──────────────────────────┐
│ auth / UI    │         │ RAG         │       │ MCP (SSE) — chat path    │
│ (Excel via   │         │ Chroma + HF │       │ utils/mcp_client.py      │
│  server fns) │         │ embeddings  │       │                          │
└──────────────┘         └─────────────┘       └──────────────────────────┘
```

**Important distinction:** `auth/login_handler.py` and `UI/assignment_handler.py` import tool functions from `mcp_server/server.py` **directly** (same process, Excel-backed). The **chat coach** (`main.py` option 4) uses `utils/mcp_client.call_mcp_tool`, which talks to the MCP server over **SSE**. For assignment routing in chat, run `python -m mcp_server.server` so `http://<host>:<port>/sse` is available.

---

## Repository layout

```
Agentic-Pathshala/
├── agents/                 # coordinator_agent, notes_agent; assignment_agent module
├── auth/                   # LoginHandler — Rich prompts, validates learners
├── config/                 # Pydantic settings from .env
├── data/
│   ├── chroma_db/          # Chroma persistence (after ingestion)
│   ├── documents/          # Source files for RAG (.pdf, .txt, .md, .docx)
│   └── storage/            # Excel workbooks (*.xlsx)
├── mcp_server/
│   ├── server.py           # FastMCP tools (SSE when run as server)
│   └── mcp_client.py       # Additional client helpers (graph uses utils/mcp_client)
├── orchestrator/
│   ├── graph.py            # StateGraph: coordinator → route → agents → response
│   ├── node.py             # coordinator, notes_agent, assignment, fallback, response
│   ├── routes.py           # intent → next node name
│   └── state.py            # CoachState TypedDict
├── prompts/                # YAML prompts (coordinator, notes, assignment, + stubs)
├── rag/                    # loaders, chunker, embeddings, vectorstore, ingestion, retriever
├── scripts/
│   └── seed_storage.py     # Seed learners, assignments, progress, notes (extend for login)
├── test/                   # pytest suite
├── UI/                     # MenuHandler, AssignmentHandler
├── utils/                  # llm, prompt_loader, excel_store, txt_store, mcp_client
├── .env.example
├── main.py                 # Application entrypoint
└── requirements.txt
```

---

## Coach state (`orchestrator/state.py`)

The graph carries: `user_input`, `learner_id`, `current_intent`, `retrieved_context`, `agent_response`, `execution_path`.

---

## MCP tools (`mcp_server/server.py`)

| Tool | Purpose |
|------|---------|
| `ping` | Health check. |
| `get_learners` | Rows from `learners.xlsx`. |
| `get_assignments` | Rows from `assignments.xlsx`. |
| `get_assignments_for_learner` | Assignments filtered by `learner_id`. |

---

## Configuration (`config/settings.py`)

| Variable | Role |
|----------|------|
| `GROQ_API_KEY` | **Required** — Groq API access. |
| `CHROMA_PATH`, `DOCUMENTS_PATH`, `STORE_PATH` | Paths for vector DB, RAG sources, Excel store (defaults under `data/`). |
| `MODEL_NAME`, `EMBEDDING_MODEL`, `TEMPERATURE` | LLM and embedding defaults. |
| `COLLECTION_NAME` | Chroma collection name. |
| `MCP_SERVER_URL` | **Base URL only** — no `/sse` suffix. The client builds `{MCP_SERVER_URL}/sse` (see `utils/mcp_client.py`). Example: `http://localhost:8000`. Match the host/port passed to `mcp.run()` in `mcp_server/server.py`. |
| `MAX_SIMILARITY_SCORE` | Distance ceiling in `retrieve_documents` (tune for your embedding metric). |

Copy `.env.example` to `.env` and set values. Avoid spaces around `=` in `.env` lines when possible.

---

## Prerequisites

- **Python** 3.10+ recommended (project uses type hints and modern LangChain/LangGraph).
- **Groq** API key.
- Optional: GPU not required for default MiniLM embeddings; first run may download the embedding model.

---

## Setup and run

### 1. Environment

```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# Edit .env — set GROQ_API_KEY, paths, COLLECTION_NAME, MCP_SERVER_URL
```

On macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### 2. Seed storage (optional)

```powershell
python -m scripts.seed_storage
```

`seed_storage.py` creates sample **learners** (id + name only), **assignments**, **progress**, and **notes**. **Login** expects `email` and `password` on each learner row (`auth/login_handler.py`). Either extend the seed script and re-run, or edit `data/storage/learners.xlsx` to add those columns. The login UI ships with **demo defaults** in the prompt text; replace with your own test users in Excel.

### 3. Ingest documents for RAG (optional)

Place `.pdf`, `.txt`, `.md`, or `.docx` under `data/documents/`, then from the project root:

```powershell
python -c "from rag import ingest_documents; ingest_documents()"
```

### 4. Start the MCP server (for chat assignment branch)

Required when the coordinator routes to `assignment_query` in **option 4** (SSE client):

```powershell
python -m mcp_server.server
```

Default listen: `0.0.0.0:8000` with `transport="sse"`.

### 5. Start the app

```powershell
python main.py
```

### 6. Tests

```powershell
pytest test/
```

---

## Main menu (`main.py`)

| Option | Description |
|--------|-------------|
| **1** | List assignments for the logged-in learner (in-process read from seeded Excel / MCP helpers). |
| **2** | “Available” assignments (rows where `learner_id` differs); uses the same data source as option 1. |
| **3** | Assessment / hybrid search — **not wired**: `MainApp` has no `question_handler`; choosing this will raise `AttributeError` until implemented or removed. |
| **4** | Chat with the AI coach — invokes LangGraph with `user_input` and `learner_id`. |
| **5** | Exit. |

Options **2–4** ask for a free-text prompt after you choose the menu item.

---

## LangGraph routing note

`prompts/coordinator.yaml` allows intents such as `progress_query`, `recommendation`, and `evaluation_request`. `orchestrator/routes.py` maps those to node names like `progress_agent` and `recommendation_agent`, but **`graph.py` only registers** `notes_agent`, `assignment`, and `fallback` in the conditional edge map. Intents that resolve to unmapped node names can break routing at runtime.

**Mitigations:** map those intents to `fallback` (or `notes_agent`) in `routes.py`, or add matching nodes and edges in `graph.py`. Prompt YAML files under `prompts/` for progress / recommendation / evaluation exist as placeholders for future agents.

---

## Tech stack

| Piece | Use |
|-------|-----|
| LangGraph / LangChain | Graph orchestration and LCEL chains |
| Groq (`langchain-groq`) | Chat model |
| Chroma + Hugging Face (`langchain-huggingface`) | Vector store and embeddings |
| FastMCP | MCP tools over SSE |
| openpyxl | Excel persistence |
| Pydantic Settings | Environment configuration |
| Rich | Terminal UI |
| pytest | Tests under `test/` |

---

## License / contributing

Add your license and contribution guidelines here if applicable.
