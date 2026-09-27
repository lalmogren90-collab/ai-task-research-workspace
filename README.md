# AI Task & Research Workspace

AI Task & Research Workspace is a full-stack agentic AI application that combines task management, AI assistance, live research, multimodal image analysis, knowledge retrieval, analytics, and automation in one workspace.

The project was developed as a practical environment for applying software engineering and agentic AI concepts, including React, FastAPI, PostgreSQL, Docker, LLM/VLM integration, multi-agent orchestration, RAG, vector databases, Tools, Skills, MCP, memory, agent harnesses, automation, coding agents, and Hermes Agent.

## Key Features

* Full-stack React + FastAPI application
* PostgreSQL task storage running with Docker
* Task CRUD operations
* Main Agent with dynamic subagent routing
* Specialized Task Agent and Research Agent
* Groq-powered LLM integration
* Tavily live web research
* Multimodal VLM image analysis
* RAG with ChromaDB
* Deterministic local vector embeddings
* Dynamic Skills for task planning and cleanup
* MCP-based task operations
* Conversation memory
* Agent execution harness and tool loop
* Agent-triggered Python analytics
* Matplotlib chart generation
* APScheduler automation
* Hermes Agent integration
* Repository-local Hermes Skill
* Hermes MCP integration
* Hermes Cron scheduled task
* Automated unit and integration testing
* AI-assisted development with Codex

## Architecture

```text
React UI
   |
   v
FastAPI Backend
   |
   v
Main Agent / Orchestrator
   |
   +--> Task Agent
   |      |
   |      +--> Dynamic Skill Selector
   |      +--> Tools
   |      +--> MCP
   |      +--> PostgreSQL
   |      +--> Task Analytics
   |
   +--> Research Agent
          |
          +--> Tavily Live Web Search

Additional AI Services
   |
   +--> Multimodal VLM
   +--> RAG Pipeline
          |
          +--> ChromaDB Vector Store

Automation
   |
   +--> APScheduler
   +--> Hermes Cron

External Agent
   |
   +--> Hermes Agent
          |
          +--> task-project Skill
          +--> Project MCP Server
```

The Main Agent acts as the orchestrator. Task-related requests are delegated to the Task Agent, while requests requiring external information are delegated to the Research Agent.

The Task Agent dynamically selects specialized Skills when required and accesses task data through MCP rather than directly querying PostgreSQL.

The Research Agent uses Tavily to retrieve live web information before generating its response.

## Technology Stack

### Frontend

* React
* Vite
* JavaScript
* React Markdown

### Backend

* Python
* FastAPI
* SQLAlchemy
* Pydantic

### Database

* PostgreSQL
* Docker Compose

### AI & Agentic Components

* Groq LLM/VLM API
* Multi-agent orchestration
* Tavily live web search
* Model Context Protocol (MCP)
* Dynamic Skills
* Conversation memory
* Agent execution harness
* Tool-calling loop

### RAG & Vector Retrieval

* ChromaDB
* Deterministic local vector embeddings
* Retrieval-Augmented Generation

### Analytics

* Python
* Matplotlib

### Automation

* APScheduler
* Hermes Cron

### Agent Frameworks & Development

* Hermes Agent
* Codex

## Repository Structure

```text
.
├── .hermes/
│   └── skills/
│       └── task-project/
│           └── SKILL.md
│
├── backend/
│   └── app/
│       ├── agents/
│       ├── automation/
│       ├── db/
│       ├── mcp/
│       ├── memory/
│       ├── models/
│       ├── rag/
│       ├── routers/
│       ├── schemas/
│       ├── skills/
│       ├── tools/
│       └── main.py
│
├── frontend/
├── tests/
├── .env.example
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Task Management & CRUD

The application supports standard task operations:

* Create tasks
* Read tasks
* Update tasks
* Delete tasks

FastAPI exposes task CRUD endpoints and PostgreSQL provides persistent storage.

The React interface displays the current task list and communicates with the FastAPI backend.

## Multi-Agent System

The application uses specialized agents instead of sending every request through a single workflow.

### Main Agent

The Main Agent analyzes the user's request and delegates it to the appropriate specialized agent.

### Task Agent

The Task Agent handles requests involving the user's task data, including:

* Viewing tasks
* Creating tasks
* Updating tasks
* Deleting tasks
* Task planning
* Task cleanup
* Task analytics

Task operations are performed through MCP tools.

### Research Agent

The Research Agent handles questions requiring external or current information.

It uses Tavily live web search and generates responses based on retrieved search results.

## Dynamic Skills

The Task Agent can dynamically select reusable Skills according to the user's request.

### `task_planning`

Used for:

* Prioritization
* Planning
* Recommended next actions

### `task_cleanup`

Used for:

* Duplicate detection
* Unclear task titles
* Task-list quality review
* Cleanup recommendations

Ordinary CRUD requests can execute without selecting either Skill.

## Model Context Protocol (MCP)

The project includes a local MCP server that exposes structured task tools:

```text
get_tasks
create_task
update_task
delete_task
```

The Task Agent uses these MCP tools instead of directly accessing PostgreSQL.

This separates agent reasoning from database implementation and provides a structured tool interface.

## LLM Integration

Groq-hosted models are used for agent reasoning and response generation.

LLM calls support:

* Agent routing
* Task reasoning
* Research synthesis
* Tool selection
* Skill-guided responses
* RAG response generation

## VLM & Multimodal Analysis

The application includes a multimodal pipeline that accepts both an image and a text prompt.

The React interface allows users to select an image and request visual analysis. The FastAPI backend sends the image and prompt to a vision-language model and returns the resulting analysis.

This demonstrates a combined language-and-vision workflow within the same application.

## RAG & ChromaDB

A Retrieval-Augmented Generation pipeline provides grounded answers from local project knowledge.

The pipeline:

1. Loads project knowledge.
2. Splits the knowledge into retrievable chunks.
3. Generates deterministic local vector embeddings.
4. Stores the vectors in ChromaDB.
5. Retrieves the most relevant chunks for a question.
6. Supplies the retrieved context to the LLM.
7. Generates an answer grounded in the retrieved information.

This provides a practical implementation of RAG and vector similarity retrieval.

## Agent Tools & Analytics

The Task Agent includes a controlled Python analytics tool.

When requested, the agent can:

1. Retrieve live task data through MCP.
2. Calculate task statistics.
3. Compute completion progress.
4. Generate a task-status chart using Matplotlib.
5. Return the analytical result to the user.

This demonstrates agent-triggered Python execution and analytical output generation.

## Conversation Memory

Task Agent conversations maintain history using a `conversation_id`.

The memory implementation allows the agent to interpret references to earlier messages within the same running process.

Memory is currently process-local and is not persistent across application restarts.

## Agent Harness & Execution Loop

The project includes an execution harness that records:

* Agent steps
* Tool calls
* Tool results
* Errors

The execution loop coordinates model reasoning, tool selection, tool execution, observations, and final response generation.

This makes agent behavior more observable and easier to test and debug.

## Automation

### APScheduler

Application-level automation is implemented with APScheduler.

Scheduled workflows include:

* Daily task summaries
* Monitoring unfinished tasks
* Generating prioritized task guidance

Run the scheduler with:

```bash
python -m backend.app.automation.scheduler
```

Scheduler behavior can be configured using environment variables such as:

```text
AUTOMATION_TIMEZONE
DAILY_SUMMARY_HOUR
TASK_MONITOR_MINUTES
```

## Hermes Agent Integration

Hermes Agent was configured as an external agent framework for the project.

A repository-local Skill is stored at:

```text
.hermes/skills/task-project/SKILL.md
```

The Skill provides Hermes with project-specific information about:

* Application architecture
* Task operations
* MCP usage
* RAG
* VLM
* Analytics
* Safety rules

### Hermes + MCP

Hermes was connected to the project's MCP server.

The connection exposes the project's four task tools:

```text
get_tasks
create_task
update_task
delete_task
```

Hermes successfully discovered and invoked the MCP task tools to retrieve live project task data.

### Hermes Cron

A recurring Hermes Cron job named:

```text
Daily Task Summary
```

was configured with the local `task-project` Skill.

The scheduled job demonstrates agent-level automation and was manually triggered successfully during validation.

## AI-Assisted Development

Codex was used as an AI coding agent during development to support:

* Project inspection
* Code modification
* Debugging
* Implementation assistance
* Validation workflows

## Environment Configuration

Copy the example environment file:

```bash
cp .env.example .env
```

Configure the required API credentials locally.

Important environment variables include:

```text
GROQ_API_KEY
TAVILY_API_KEY
DATABASE_URL
AUTOMATION_TIMEZONE
DAILY_SUMMARY_HOUR
TASK_MONITOR_MINUTES
```

Never commit real API credentials to Git.

## Local Setup

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install backend dependencies:

```bash
python -m pip install -r requirements.txt
```

Start PostgreSQL:

```bash
docker compose up -d postgres
```

Start FastAPI:

```bash
python -m uvicorn backend.app.main:app --reload
```

In another terminal, start the React frontend:

```bash
cd frontend
npm install
npm run dev
```

Open the local URL displayed by Vite.

## Testing

### Unit Tests

Run:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

Final validation:

```text
Ran 9 tests
OK
```

### Integration Smoke Test

Run:

```bash
python -m tests.final_smoke_test
```

The smoke test validates:

* Skill discovery
* Dynamic Skill selection
* MCP task retrieval
* Task Agent delegation
* Research Agent delegation
* Agent responses

Final validation completed successfully.

### Frontend Production Build

The React frontend was also validated with:

```bash
cd frontend
npm run build
```

The production build completed successfully.

## Security Notes

* Do not commit `.env`.
* Do not store real API keys in source code.
* `.env.example` contains configuration placeholders only.
* Agent task modifications should only occur when explicitly requested.
* Task data is accessed through structured MCP tools.

## Current Limitations

* Conversation memory is process-local and is lost when the application restarts.
* The project is designed primarily as a local development and training environment.
* APScheduler output is local and does not send external notifications.
* LLM, VLM, and live research functionality require configured external APIs.
* Hermes Cron was configured and manually validated; continuous background gateway execution was not part of the final validation.

## Agentic AI Concepts Demonstrated

This project practically demonstrates:

* LLM integration
* VLM integration
* Multimodal AI
* RAG
* Vector databases
* Multi-agent orchestration
* Subagent delegation
* Prompt engineering
* Context engineering
* Harness engineering
* Loop engineering
* Tool calling
* Dynamic Skills
* MCP
* Conversation memory
* Live web research
* Controlled Python analytics
* Automation
* Agent scheduling
* Coding agents
* Hermes Agent integration
* Full-stack AI application development

## Project Purpose

The project was created as a practical implementation of software engineering and agentic AI concepts within one integrated application.

Rather than demonstrating each concept in isolation, the workspace connects frontend development, backend APIs, databases, AI models, agents, retrieval, tools, protocols, analytics, and automation into a single working system.
