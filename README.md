# 🎓 Agentic Pathshala — AI Learning Coach

An agentic AI coaching system built with **LangGraph**, **FastMCP**, and **Groq LLM**. The system routes learner queries through a multi-node graph, retrieves context via a RAG pipeline, and serves data through an MCP server — all backed by Excel-based local storage and configurable via Pydantic settings.

---

## 📁 Project Structure

```
Agentic-Pathshala/
├── agents/                  # Specialized agent implementations
│   └── coordinator.py       # Coordinator agent (LLM-based intent classification)
├── config/                  # Application configuration
│   ├── __init__.py
│   └── settings.py          # Pydantic-based settings (env, paths, models)
├── data/                    # Local data storage
│   ├── chroma_db/           # ChromaDB vector store persistence
│   ├── documents/           # Source documents for RAG ingestion
│   └── storage/             # Excel-based record storage (.xlsx)
├── mcp_server/              # MCP tool server
│   ├── __init__.py
│   └── server.py            # FastMCP server with registered tools
├── orchestrator/            # LangGraph orchestration engine
│   ├── __init__.py
│   ├── graph.py             # StateGraph definition & compilation
│   ├── mcp_adapter.py       # LangChain tool wrappers for MCP
│   ├── node.py              # All graph node functions
│   ├── routes.py            # Conditional routing logic
│   └── state.py             # CoachState TypedDict definition
├── prompts/                 # YAML prompt templates for each agent
│   ├── assignment_agent.yaml
│   ├── coordinator.yaml
│   ├── evaluation_agent.yaml
│   ├── notes_agent.yaml
│   ├── progress_agent.yaml
│   └── recommendation_agent.yaml
├── rag/                     # RAG (Retrieval-Augmented Generation) pipeline
│   ├── __init__.py
│   ├── chunker.py           # Document chunking with RecursiveCharacterTextSplitter
│   ├── embeddings.py        # HuggingFace embedding model (singleton)
│   ├── ingestion.py         # Full document ingestion pipeline
│   ├── loaders.py           # Multi-format document loaders
│   ├── retriever.py         # Similarity search with score filtering
│   └── vectorstore.py       # ChromaDB vector store (singleton)
├── scripts/                 # Helper & seed scripts
│   └── seed_storage.py      # Seeds sample data into Excel storage
├── test/                    # Unit & integration tests
│   ├── test_chunking.py
│   ├── test_coordinator.py
│   ├── test_embeddings.py
│   ├── test_full_flow.py
│   ├── test_graph.py
│   ├── test_ingestion.py
│   ├── test_llm.py
│   ├── test_prompt_loader.py
│   ├── test_retriever.py
│   ├── test_router.py
│   ├── test_settings.py
│   └── test_vectorstore.py
├── utils/                   # Shared utility modules
│   ├── excel_store.py       # Thread-safe Excel CRUD operations
│   ├── llm.py               # Groq LLM singleton instance
│   ├── prompt_loader.py     # YAML prompt → ChatPromptTemplate loader
│   └── txt_store.py         # Thread-safe JSON-lines CRUD operations
├── .env.example             # Environment variable template
├── .gitignore
├── main.py                  # CLI entry point
└── requirements.txt         # Python dependencies
```

---

## ✅ Completed Work

### 1. 🏗️ Project Foundation
- **Project structure** scaffolded with clear separation of concerns across `orchestrator/`, `agents/`, `rag/`, `mcp_server/`, `config/`, `prompts/`, `utils/`, `scripts/`, and `test/`
- **Environment config** set up with `.env` and `.env.example` supporting `GROQ_API_KEY`, `CHROMA_PATH`, `DOCUMENTS_PATH`, `STORE_PATH`, `MODEL_NAME`, `EMBEDDING_MODEL`, `COLLECTION_NAME`, `MCP_SERVER_URL`
- **`requirements.txt`** defined with all dependencies
- **`.gitignore`** configured

---

### 2. ⚙️ Configuration System (`config/`)

| File | Status | Description |
|---|---|---|
| `settings.py` | ✅ Done | Pydantic `BaseSettings` class with auto `.env` loading |

**Managed settings:**
- `GROQ_API_KEY` — API key for Groq LLM inference
- `CHROMA_PATH` — ChromaDB persistence directory (`data/chroma_db`)
- `DOCUMENTS_PATH` — Source documents directory (`data/documents`)
- `STORE_PATH` — Excel storage directory (`data/storage`)
- `MODEL_NAME` — LLM model (`llama-3.3-70b-versatile`)
- `EMBEDDING_MODEL` — Embedding model (`sentence-transformers/all-MiniLM-L6-v2`)
- `COLLECTION_NAME` — ChromaDB collection name (`learning_coach_kb`)
- `MCP_SERVER_URL` — MCP server endpoint
- `TEMPERATURE` — LLM temperature (`0.2`)

---

### 3. 🧠 LangGraph Orchestrator (`orchestrator/`)

| File | Status | Description |
|---|---|---|
| `state.py` | ✅ Done | Defines `CoachState` TypedDict with `messages`, `user_role`, `learner_id`, `current_intent`, `retrieved_context`, `tool_results`, `requires_approval`, `final_response` |
| `routes.py` | ✅ Done | `route_intent()` routing function — maps intents (`assignment_query`, `progress_query`, `recommendation`, `evaluation_request`, `notes_query`) to specialized agent nodes |
| `node.py` | ✅ Done | All 6 node functions: `coordinator_node`, `router_node`, `assignment_node`, `general_node`, `response_node`, `fallback_node` — each with error handling and execution path tracking |
| `graph.py` | ✅ Done | Full LangGraph `StateGraph` built and compiled with nodes, edges, and conditional routing |
| `mcp_adapter.py` | ✅ Done | LangChain `@tool` wrapper — `get_assignment_status_tool` for querying assignment status via MCP |

**Graph Flow:**
```
START → coordinator → router ──→ assignment ──→ response → END
                             ├──→ general   ──┘
                             └──→ fallback  ──┘
```

**Current routing (keyword-based, placeholder):**
- `"assignment"` in query → `assignment` node
- `"hello"` in query → `general` node
- Anything else → `fallback` node

---

### 4. 🤖 Agents (`agents/`)

| File | Status | Description |
|---|---|---|
| `coordinator.py` | ✅ Done | LLM-powered coordinator agent using Groq — classifies learner intent from queries using the `coordinator.yaml` prompt template |

**How it works:**
1. Extracts the latest user message from state
2. Loads the coordinator prompt template via `prompt_loader`
3. Chains prompt → LLM (Groq) and invokes
4. Sets `current_intent` in state to the classified intent

---

### 5. 📝 Prompt Templates (`prompts/`)

All agent prompts are defined as YAML files and loaded dynamically via `utils/prompt_loader.py`:

| Prompt File | Status | Description |
|---|---|---|
| `coordinator.yaml` | ✅ Done | Classifies learner intent into: `assignment_query`, `progress_query`, `recommendation`, `evaluation_request`, `notes_query`, or `unknown` |
| `assignment_agent.yaml` | ✅ Done | Manages assignments — viewing, submitting, tracking status, generating reports |
| `evaluation_agent.yaml` | ✅ Done | Evaluates submissions with rubric scoring (accuracy, completeness, clarity, reasoning, effort) |
| `progress_agent.yaml` | ✅ Done | Tracks learner progress — completion rates, score trends, knowledge gaps, recommendations |
| `recommendation_agent.yaml` | ✅ Done | Recommends next learning steps — study plans, topic reviews, future guidance |
| `notes_agent.yaml` | ✅ Done | Notes management agent |

---

### 6. 📚 RAG Pipeline (`rag/`)

A complete Retrieval-Augmented Generation pipeline using ChromaDB and HuggingFace embeddings:

| File | Status | Description |
|---|---|---|
| `loaders.py` | ✅ Done | Multi-format document loader supporting `.pdf`, `.txt`, `.md`, `.docx` — auto-tags metadata with source filename and document type |
| `chunker.py` | ✅ Done | `DocumentChunker` class using `RecursiveCharacterTextSplitter` (chunk size: 500, overlap: 50) with smart separators |
| `embeddings.py` | ✅ Done | Singleton `HuggingFaceEmbeddings` instance using `sentence-transformers/all-MiniLM-L6-v2` |
| `vectorstore.py` | ✅ Done | Singleton `Chroma` vector store with persistence, plus `reset_collection()` for re-ingestion |
| `ingestion.py` | ✅ Done | Full ingestion pipeline: load docs → chunk → reset collection → add to vector store |
| `retriever.py` | ✅ Done | `retrieve_documents()` with similarity search + score filtering (`MAX_SIMILARITY_SCORE = 0.8`) |

**RAG Flow:**
```
Documents (PDF/TXT/MD/DOCX)
        ↓
   loaders.py          → Load & tag with metadata
        ↓
   chunker.py          → Split into 500-char chunks (50 overlap)
        ↓
   embeddings.py       → Generate embeddings (all-MiniLM-L6-v2)
        ↓
   vectorstore.py      → Store in ChromaDB
        ↓
   retriever.py        → Similarity search with score filtering
```

---

### 7. 🔌 MCP Server (`mcp_server/`)

| File | Status | Description |
|---|---|---|
| `server.py` | ✅ Done | FastMCP server named `"AI Learning Coach MCP Server"`, runs on `host=0.0.0.0`, `port=8000` via SSE transport |

**Registered MCP Tools:**
- `ping()` — Health check, returns `{"status": "working"}`
- `get_learners()` — Reads learner records from Excel storage and returns count + list

---

### 8. 💾 Data Storage Utilities (`utils/`)

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

#### `llm.py` ✅ Done
- Singleton `ChatGroq` LLM instance configured from settings (`model`, `api_key`, `temperature`)

#### `prompt_loader.py` ✅ Done
- `load_prompt(prompt_name)` — Loads YAML prompt files and returns a `ChatPromptTemplate` with system + human messages

---

### 9. 🌱 Seed Script (`scripts/`)

| File | Status | Description |
|---|---|---|
| `seed_storage.py` | ✅ Done | Seeds Excel storage with sample learners, assignments, progress, and notes |

**Seeded entities:**
- **Learners:** Alice (L001), Bob (L002), Charlie (L003)
- **Assignments:** `week1_python` — submitted (L001) / pending (L002)
- **Progress:** Python Basics scores — 85 (L001), 60 (L002)
- **Notes:** RAG/ChromaDB topic note (L001)

---

### 10. 🚀 Entry Point (`main.py`) ✅ Done
Interactive CLI loop:
- Takes user input from terminal
- Invokes the LangGraph graph with user input
- Prints `execution_path` (shows which nodes were traversed) and the AI response
- Type `exit` to quit

---

### 11. 🧪 Tests (`test/`)

| Test File | Description |
|---|---|
| `test_settings.py` | Validates Pydantic settings loading |
| `test_llm.py` | Tests Groq LLM singleton |
| `test_prompt_loader.py` | Tests YAML prompt loading |
| `test_graph.py` | Tests LangGraph compilation |
| `test_router.py` | Tests intent routing logic |
| `test_coordinator.py` | Tests coordinator agent |
| `test_embeddings.py` | Tests HuggingFace embedding generation |
| `test_chunking.py` | Tests document chunking |
| `test_vectorstore.py` | Tests ChromaDB vector store |
| `test_ingestion.py` | Tests document ingestion pipeline |
| `test_retriever.py` | Tests similarity search retrieval |
| `test_full_flow.py` | End-to-end flow test |

---

## 🚧 Work In Progress / Planned

- [ ] Wire LLM-based coordinator agent into the graph (replace keyword router with `agents/coordinator.py`)
- [ ] Implement full `assignment_node` logic (look up assignments from Excel storage)
- [ ] Implement specialized agent nodes (progress, recommendation, evaluation, notes)
- [ ] Integrate RAG retrieval into agent nodes for context-aware responses
- [ ] Full `general_node` with LLM response generation
- [ ] Add more MCP tools (assignments CRUD, progress tracking, notes management)
- [ ] Connect MCP adapter tools to the orchestrator graph
- [ ] Human-in-the-loop approval flow (uses `requires_approval` in state)
- [ ] Frontend / API layer

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

# 4. (Optional) Seed local storage with sample data
python -m scripts.seed_storage

# 5. (Optional) Ingest documents into ChromaDB
# Place documents in data/documents/ then run ingestion

# 6. Run the CLI coach
python main.py

# 7. (Optional) Start the MCP server
python -m mcp_server.server

# 8. Run tests
pytest test/
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
| [HuggingFace](https://huggingface.co/) | Sentence embeddings (`all-MiniLM-L6-v2`) |
| [openpyxl](https://openpyxl.readthedocs.io/) | Excel-based local storage |
| [Pydantic](https://docs.pydantic.dev/) | Data validation & settings management |
| [PyYAML](https://pyyaml.org/) | Prompt template loading |
| [pytest](https://docs.pytest.org/) | Testing framework |
