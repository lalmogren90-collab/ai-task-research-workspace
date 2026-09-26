---
name: task-project
description: Understand and work with the AI Task & Research Workspace project.
---

# Task Project Skill

Use this skill when working with the AI Task & Research Workspace.

## Architecture

The project is a full-stack agentic application.

- React provides the frontend.
- FastAPI provides the backend API.
- PostgreSQL stores task data.
- Docker runs PostgreSQL.
- The Main Agent routes requests to specialized agents.
- The Task Agent accesses task data through MCP.
- The Research Agent performs live web research.
- ChromaDB provides the project's RAG vector database.
- A multimodal VLM analyzes images and text.
- Python analytics can generate task statistics and Matplotlib charts.

## Task Operations

When task data is needed, prefer the configured MCP task server rather than directly accessing PostgreSQL.

Do not invent tasks, statuses, dependencies, deadlines, or database results.

## Safety

Do not modify or delete task data unless the user explicitly requests the mutation.
