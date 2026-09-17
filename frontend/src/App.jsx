import { useEffect, useState } from "react";
import "./App.css";


const API_URL = "http://127.0.0.1:8000";


function App() {
  const [tasks, setTasks] = useState([]);
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [taskLoading, setTaskLoading] = useState(true);
  const [error, setError] = useState("");
  const [agentInfo, setAgentInfo] = useState({
    delegatedTo: null,
    selectedSkill: null,
  });

  const conversationId = "frontend-agent-workspace";


  async function loadTasks() {
    try {
      setTaskLoading(true);

      const response = await fetch(`${API_URL}/tasks/`);

      if (!response.ok) {
        throw new Error("Failed to load tasks.");
      }

      const data = await response.json();
      setTasks(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setTaskLoading(false);
    }
  }


  useEffect(() => {
    loadTasks();
  }, []);


  async function sendMessage(event) {
    event.preventDefault();

    const trimmedMessage = message.trim();

    if (!trimmedMessage || loading) {
      return;
    }

    const userMessage = {
      role: "user",
      content: trimmedMessage,
    };

    setMessages((current) => [
      ...current,
      userMessage,
    ]);

    setMessage("");
    setError("");
    setLoading(true);

    try {
      const response = await fetch(
        `${API_URL}/ai/chat`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            conversation_id: conversationId,
            message: trimmedMessage,
          }),
        }
      );

      if (!response.ok) {
        throw new Error(
          "The agent request failed."
        );
      }

      const data = await response.json();

      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content: data.response,
        },
      ]);

      setAgentInfo({
        delegatedTo: data.delegated_to,
        selectedSkill: data.selected_skill,
      });

      await loadTasks();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }


  const unfinishedTasks = tasks.filter(
    (task) => task.status !== "done"
  );

  const completedTasks = tasks.filter(
    (task) => task.status === "done"
  );


  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">
            AGENTIC APPLICATION
          </p>

          <h1>
            AI Task & Research Workspace
          </h1>
        </div>

        <div className="status-badge">
          <span className="status-dot" />
          System Online
        </div>
      </header>

      <main className="workspace">
        <aside className="task-panel">
          <div className="panel-heading">
            <div>
              <p className="panel-label">
                TASK SYSTEM
              </p>

              <h2>Your Tasks</h2>
            </div>

            <button
              className="refresh-button"
              onClick={loadTasks}
              type="button"
            >
              Refresh
            </button>
          </div>

          <div className="task-stats">
            <div>
              <strong>{tasks.length}</strong>
              <span>Total</span>
            </div>

            <div>
              <strong>
                {unfinishedTasks.length}
              </strong>
              <span>Open</span>
            </div>

            <div>
              <strong>
                {completedTasks.length}
              </strong>
              <span>Done</span>
            </div>
          </div>

          <div className="task-list">
            {taskLoading && (
              <p className="muted">
                Loading tasks...
              </p>
            )}

            {!taskLoading &&
              tasks.map((task) => (
                <article
                  className="task-card"
                  key={task.id}
                >
                  <div
                    className={`task-indicator ${task.status}`}
                  />

                  <div className="task-content">
                    <strong>{task.title}</strong>

                    <span>
                      ID {task.id} · {task.status}
                    </span>
                  </div>
                </article>
              ))}
          </div>
        </aside>

        <section className="agent-panel">
          <div className="agent-header">
            <div>
              <p className="panel-label">
                MULTI-AGENT SYSTEM
              </p>

              <h2>Agent Chat</h2>
            </div>

            <div className="agent-metadata">
              <div>
                <span>Agent</span>
                <strong>
                  {agentInfo.delegatedTo ||
                    "Waiting"}
                </strong>
              </div>

              <div>
                <span>Skill</span>
                <strong>
                  {agentInfo.selectedSkill ||
                    "None"}
                </strong>
              </div>
            </div>
          </div>

          <div className="chat-window">
            {messages.length === 0 && (
              <div className="empty-state">
                <div className="agent-icon">
                  AI
                </div>

                <h3>
                  Your agent workspace is ready.
                </h3>

                <p>
                  Ask about your tasks, request a
                  plan, audit your task list, or
                  research a technical topic.
                </p>

                <div className="suggestions">
                  <button
                    type="button"
                    onClick={() =>
                      setMessage(
                        "What should I work on next?"
                      )
                    }
                  >
                    Plan my tasks
                  </button>

                  <button
                    type="button"
                    onClick={() =>
                      setMessage(
                        "Audit my task list for duplicates and malformed titles."
                      )
                    }
                  >
                    Audit tasks
                  </button>

                  <button
                    type="button"
                    onClick={() =>
                      setMessage(
                        "What is Model Context Protocol?"
                      )
                    }
                  >
                    Research MCP
                  </button>
                </div>
              </div>
            )}

            {messages.map((item, index) => (
              <div
                className={`message ${item.role}`}
                key={`${item.role}-${index}`}
              >
                <span className="message-role">
                  {item.role === "user"
                    ? "You"
                    : "Agent"}
                </span>

                <p>{item.content}</p>
              </div>
            ))}

            {loading && (
              <div className="message assistant">
                <span className="message-role">
                  Agent
                </span>

                <p>Thinking...</p>
              </div>
            )}
          </div>

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          <form
            className="chat-form"
            onSubmit={sendMessage}
          >
            <input
              type="text"
              value={message}
              onChange={(event) =>
                setMessage(event.target.value)
              }
              placeholder="Ask your agent..."
            />

            <button
              type="submit"
              disabled={loading}
            >
              {loading ? "Running..." : "Send"}
            </button>
          </form>
        </section>
      </main>

      <footer className="activity-bar">
        <div>
          <span>Orchestrator</span>
          <strong>Main Agent</strong>
        </div>

        <div>
          <span>Task Access</span>
          <strong>MCP</strong>
        </div>

        <div>
          <span>Database</span>
          <strong>PostgreSQL</strong>
        </div>

        <div>
          <span>Research</span>
          <strong>Live Web</strong>
        </div>

        <div>
          <span>Automation</span>
          <strong>APScheduler</strong>
        </div>
      </footer>
    </div>
  );
}


export default App;