# Frontend: AI Task & Research Workspace

This React and Vite interface shows tasks and provides a chat panel for task requests and research questions. It displays the delegated agent and selected task skill returned by the API. The frontend calls `http://127.0.0.1:8000` directly, so the FastAPI backend must be running there.

From this directory, after completing the backend and environment setup in the [root README](../README.md):

```sh
npm install
npm run dev
```

Open the local URL printed by Vite. The full setup, architecture, automation, and test commands are in the [root README](../README.md).
