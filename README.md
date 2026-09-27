# AI Core Agent (First-Principles ReAct Engine)

A custom, frameworkless implementation of an autonomous AI Agent built on first principles using the **ReAct (Reasoning + Acting)** pattern. Packaged as a production-grade microservice with FastAPI, containerized with Docker, and deployed on an AWS EC2 cloud instance.

---

## Architecture & Core Philosophy

Most agent implementations rely on heavy abstraction frameworks (e.g., LangChain, CrewAI). This project intentionally implements the agent orchestration loop from scratch using pure Python to expose and master the underlying mechanics:

- **Reasoning Loop:** Native LLM instruction prompting enforcing deterministic outputs (`Thought`, `Action`, `Action Input`, `Observation`, `Final Answer`).
- **Tool Dispatcher:** Regex/string-based output parsing to dynamically execute Python functions and inject tool outputs back into the LLM context.
- **REST API:** Fully asynchronous HTTP service with automated OpenAPI validation via FastAPI and Pydantic.
- **Infrastructure:** Isolated Docker containerization with secure environment management (`.env`, `.dockerignore`) running live on an AWS EC2 Linux instance.

```text
       +-------------------------------------------------+
       |                    User / Client                |
       +-------------------------------------------------+
                               |
                        HTTP POST /chat
                               v
       +-------------------------------------------------+
       |                 FastAPI Server                  |
       +-------------------------------------------------+
                               |
                               v
            +---------------------------------------+
            |        Custom ReAct Controller        |
            +---------------------------------------+
              |                                   ^
       Thought / Action                      Observation
              v                                   |
      +---------------+                   +---------------+
      |   Groq API    |                   |  Tools Engine |
      | (Qwen 3 27B)  |                   | (Calculator)  |
      +---------------+                   +---------------+