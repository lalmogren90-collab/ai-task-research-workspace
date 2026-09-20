# AI Task & Research Workspace

AI Task & Research Workspace is a local task manager and research assistant. The React interface shows tasks and sends chat requests to a FastAPI backend. A main orchestrator delegates task requests to a Task Agent and research questions to a Research Agent. The project demonstrates agent delegation, tool use, task-specific instructions, and scheduled agent work.

## Architecture

```text
React UI
  → FastAPI API
    → Main Orchestrator
      ├─ Task Agent → dynamic Skill Selector → optional task skill → MCP → PostgreSQL
      └─ Research Agent → Tavily web search → response grounded in search results
```

The orchestrator uses a Groq-hosted model to choose a subagent. The Task Agent selects a skill for each user turn, then uses MCP tools to read or change tasks in PostgreSQL. The Research Agent requests web searches through Tavily and uses the returned results to write its answer. Groq powers the model calls in both paths.

The Task Agent keeps conversation history by `conversation_id` in process memory so it can interpret references to earlier turns. Its agent harness records steps, tool calls, tool results, and errors in the run result; this is not persistent storage. APScheduler runs a separate local process for the daily summary and unfinished-task monitor.

## Technology stack

Python, FastAPI, PostgreSQL, SQLAlchemy, MCP (Model Context Protocol), Groq, Tavily, APScheduler, React, Vite, and Docker Compose.

## Repository structure

| Path | Purpose |
| --- | --- |
| `backend/app/main.py` | FastAPI app and API router registration |
| `backend/app/routers/` | Task CRUD and agent chat endpoints |
| `backend/app/agents/` | Orchestrator, subagents, Task Agent, and execution harness |
| `backend/app/skills/` | Dynamic selector and `task_planning` / `task_cleanup` skill instructions |
| `backend/app/mcp/` | Local MCP server and client helpers for task operations |
| `backend/app/db/`, `backend/app/models/`, `backend/app/schemas/` | Database connection, task model, and API schemas |
| `backend/app/memory/` | In-memory conversation history and agent state |
| `backend/app/tools/` | Tool registry and Tavily web search implementation |
| `backend/app/automation/` | Scheduler, daily summary, and unfinished-task monitor |
| `frontend/` | React and Vite interface |
| `tests/` | Isolated unit tests and live integration smoke test |

## Prerequisites

- Python with `venv` and `pip`
- Node.js and npm
- Docker with Docker Compose
- Groq and Tavily API credentials for model and research requests

No separate PostgreSQL installation is needed when using the supplied Compose service. Run the commands below from the repository root unless a step says otherwise.

## Environment configuration

Copy the example file, then replace its API key placeholders with your own credentials:

```sh
cp .env.example .env
```

| Variable | Use |
| --- | --- |
| `GROQ_API_KEY` | Required for Groq model calls; loaded from `.env` by the agent client |
| `TAVILY_API_KEY` | Required for live web research; loaded from `.env` by the search tool |
| `DATABASE_URL` | Optional database connection override; without it, the backend uses the local PostgreSQL configuration from Compose |
| `AUTOMATION_TIMEZONE` | Optional scheduler timezone |
| `DAILY_SUMMARY_HOUR` | Optional hour for the daily summary |
| `TASK_MONITOR_MINUTES` | Optional unfinished-task check interval |

`DATABASE_URL` and the scheduler settings are read from the process environment. For consistent overrides across FastAPI, the scheduler, and MCP subprocesses, export them before launch. In particular, the FastAPI entry point imports database configuration before the agent client loads `.env`. The supplied local database setup works without an override.

## Local setup

Create and activate a Python virtual environment from the repository root:

```sh
python -m venv .venv
source .venv/bin/activate
```

On Windows, activate it with `.venv\Scripts\activate` instead. Install backend dependencies and start PostgreSQL:

```sh
python -m pip install -r requirements.txt
docker compose up -d postgres
```

After configuring `.env`, start the FastAPI server from the repository root:

```sh
python -m uvicorn backend.app.main:app --reload
```

In another terminal, install frontend dependencies and start Vite:

```sh
cd frontend
npm install
npm run dev
```

## Running the application

Keep PostgreSQL and FastAPI running, then open the local URL printed by Vite (normally `http://localhost:5173`). The frontend calls the backend at `http://127.0.0.1:8000`; the API also exposes interactive documentation at `http://127.0.0.1:8000/docs`. The interface displays the task list and offers agent chat for task requests and research questions. The scheduler is a separate optional process and does not start with FastAPI.

## MCP and task operations

The Task Agent invokes `get_tasks`, `create_task`, `update_task`, and `delete_task` through the local MCP client. The client starts `backend/app/mcp/server.py` with the `mcp run` command. The server uses SQLAlchemy to access the PostgreSQL task table. FastAPI also exposes direct task CRUD endpoints; the current UI uses the task-list endpoint to display tasks.

## Dynamic task skills

`task_planning` guides prioritization and action plans based on the retrieved task data. `task_cleanup` guides reviews for duplicates, unclear titles, and other task-list quality issues; it suggests changes rather than applying them automatically. The selector runs independently on every Task Agent user turn. Ordinary task CRUD requests can proceed without either skill, and conversation history does not lock a skill to later turns.

## Automation

`backend/app/automation/daily_tasks.py` asks the orchestrator for a daily summary focused on unfinished tasks. `backend/app/automation/task_monitor.py` retrieves tasks through MCP; when unfinished tasks exist, it asks for a short prioritized plan without changing tasks. A retrieval failure is reported as an error, not as an empty task list. Results are printed locally.

Start the APScheduler process separately from the repository root, with the Python environment active:

```sh
python -m backend.app.automation.scheduler
```

The scheduler runs the summary daily and checks unfinished tasks on an interval. Configure its timezone, summary hour, and monitor interval with `AUTOMATION_TIMEZONE`, `DAILY_SUMMARY_HOUR`, and `TASK_MONITOR_MINUTES` in the process environment.

## Testing

Run the isolated unit tests from the repository root. They mock external dependencies and do not require live APIs or PostgreSQL:

```sh
python -m unittest discover -s tests -p 'test_*.py' -v
```

The live integration smoke test exercises skill selection, MCP task retrieval, task delegation, and research delegation:

```sh
python -m tests.final_smoke_test
```

Run that smoke test only with working Groq and Tavily API configuration, network access, and the PostgreSQL/MCP environment available. It calls live services and is separate from the isolated unit tests.

## Current limitations

- Conversation memory is process-local and in-memory; it is lost on restart and is not shared across processes.
- The application is intended primarily for local development and training.
- Automation writes its output to local stdout; it does not send notifications.
- Research and LLM functionality require configured external APIs and network access.

## Security notes

Keep `.env` out of Git. Store actual secrets in environment variables or the local `.env`, never in source or documentation. The API key entries in `.env.example` are placeholders; replace them locally and do not commit real credentials.

## Agent engineering concepts demonstrated

The project brings together orchestration and delegation to subagents, model tool calling, dynamic task skills, MCP access to task data, conversation memory, an agent execution harness, Tavily-grounded research, scheduled automation, isolated and live testing, and coding-agent-assisted development.
