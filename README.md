# 🎓 Agentic Pathshala — AI Learning Coach

An agentic AI coaching system built with **LangGraph**, **FastMCP**, and **Groq LLM**. The system routes learner queries through a multi-node graph and serves data via an MCP server.

---

## ✅ Completed Work

### 1. 🏗️ Project Foundation
- **Project structure** scaffolded with clear separation of concerns:
  - `orchestrator/` — LangGraph graph, nodes, state, routing
  - `mcp_server/` — FastMCP tool server
  - `utils/` — Data storage utilities
  - `data/` — Local file-based data storage (`storage/`, `documents/`)
  - `scripts/` — Seed & helper scripts
- **Environment config** set up with `.env` and `.env.example` (supports `GROQ_API_KEY`, `CHROMA_PATH`, `STORE_PATH`, `MODEL_NAME`)
- **`requirements.txt`** defined with all dependencies: `langgraph`, `langchain`, `langchain-groq`, `chromadb`, `sentence-transformers`, `fastmcp`, `openpyxl`, `pydantic`, `pytest`, etc.
- **`.gitignore`** configured

---

### 2. 🧠 LangGraph Orchestrator (`orchestrator/`)

| File | Status | Description |
|---|---|---|
| `state.py` | ✅ Done | Defines `CoachState` TypedDict with `user_input`, `currunt_intent`, `tool_result`, `retrieved_docs`, `final_response`, `execution_path` |
| `routes.py` | ✅ Done | `route_intent()` routing function — reads intent from state and dispatches to the correct node |
| `node.py` | ✅ Done | All 6 node functions implemented: `coordinator_node`, `router_node`, `assignment_node`, `general_node`, `response_node`, `fallback_node` |
| `graph.py` | ✅ Done | Full LangGraph `StateGraph` built and compiled with nodes, edges, and conditional routing |

**Graph Flow:**
```
START → coordinator → router ──→ assignment ──→ response → END
                             ├──→ general   ──┘
                             └──→ fallback  ──┘
```

**Routing logic (keyword-based, placeholder):**
- `"assignment"` in query → `assignment` node
- `"hello"` in query → `general` node
- Anything else → `fallback` node

---

### 3. 🔌 MCP Server (`mcp_server/`)

| File | Status | Description |
|---|---|---|
| `server.py` | ✅ Done | FastMCP server named `"AI Learning Coach MCP Server"`, runs on `host=0.0.0.0`, `port=8000` via SSE transport |

**Registered MCP Tools:**
- `ping()` — Health check, returns `{"status": "working"}`
- `get_learners()` — Reads learner records from Excel storage and returns count + list

---

### 4. 💾 Data Storage Utilities (`utils/`)

#### `excel_store.py` ✅ Done
Thread-safe Excel (`.xlsx`) CRUD operations backed by `openpyxl`:
- `read_records(filename)` — Read all rows as list of dicts
- `write_record(filename, record)` — Append a new row (auto-creates file + headers)
- `update_record(filename, match_key, match_value, updates)` — In-place cell updates
- `delete_record(filename, match_key, match_value)` — Row deletion by match
- `get_record(filename, match_key, match_value)` — Fetch first matching record
- Per-file `threading.Lock` for concurrency safety

#### `txt_store.py` ✅ Done
Thread-safe JSON-lines (`.txt`) CRUD operations:
- `read_records(filename)` — Read all JSON-line records
- `write_record(filename, record)` — Append JSON record
- `update_record(filename, match_key, match_value, updates)` — Update matching records in-place

---

### 5. 🌱 Seed Script (`scripts/`)

| File | Status | Description |
|---|---|---|
| `seed_storage.py` | ✅ Done | Seeds `learners.txt`, `assignments.txt`, `progress.txt`, `notes.txt` with sample data |

**Seeded entities:**
- **Learners:** Alice (L001), Bob (L002), Charlie (L003)
- **Assignments:** `week1_python` — submitted / pending
- **Progress:** Python Basics scores (85, 60)
- **Notes:** RAG/ChromaDB topic note

---

### 6. 🚀 Entry Point (`main.py`) ✅ Done
Interactive CLI loop:
- Takes user input from terminal
- Invokes the LangGraph graph
- Prints `execution_path` and the AI response

---

## 🚧 Work In Progress / Planned

- [ ] LLM-based intent classification (replace keyword router with Groq LLM call)
- [ ] Implement `assignment_node` logic (look up assignments from storage)
- [ ] RAG pipeline integration (ChromaDB + HuggingFace embeddings)
- [ ] Full `general_node` with LLM response generation
- [ ] Additional MCP tools (assignments, progress tracking)
- [ ] Pydantic settings integration for env management
- [ ] Unit tests with `pytest`

---

## ⚙️ Setup & Run

```bash
# 1. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Fill in your GROQ_API_KEY and other values

# 4. (Optional) Seed local storage
python -m scripts.seed_storage

# 5. Run the CLI coach
python main.py

# 6. (Optional) Start the MCP server
python -m mcp_server.server
```

---

## 📦 Tech Stack

| Technology | Purpose |
|---|---|
| [LangGraph](https://github.com/langchain-ai/langgraph) | Agentic graph orchestration |
| [LangChain](https://www.langchain.com/) | LLM tooling & chains |
| [Groq](https://groq.com/) | Fast LLM inference (`llama-3.3-70b-versatile`) |
| [FastMCP](https://github.com/jlowin/fastmcp) | MCP tool server |
| [ChromaDB](https://www.trychroma.com/) | Vector store for RAG |
| [HuggingFace](https://huggingface.co/) | Sentence embeddings |
| [openpyxl](https://openpyxl.readthedocs.io/) | Excel-based local storage |
| [Pydantic](https://docs.pydantic.dev/) | Data validation & settings |
