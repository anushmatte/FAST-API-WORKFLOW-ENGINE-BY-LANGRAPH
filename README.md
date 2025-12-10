# FAST-API-WORKFLOW-ENGINE-BY-LANGRAPH
Quantum Workflow Backend is an extensible workflow engine built with FastAPI. It lets you define directed node-graphs (workflows), register processing nodes (functions that transform a run state), start runs via a REST API, and observe execution results . The included example code_review_v1 graph analyzes submitted source code for simple issues .

# Quantum Workflow Backend

A lightweight, extensible **workflow engine** built using **FastAPI**.  
This backend allows you to define *graphs of processing nodes*, execute them as workflows, log every step, and retrieve the results via REST APIs.

The project includes a fully functional example workflow:  
**`code_review_v1`** — a simple code-analysis pipeline that:
- extracts functions from source code,
- checks complexity,
- detects basic issues,
- generates quality suggestions.

---

## ✨ Features

- 🧩 **Custom workflow engine** using directed node graphs  
- ⚙️ **Node registration system** (plug in any function as a processing node)  
- 🚀 **Run workflows asynchronously** using FastAPI Background Tasks  
- 📜 **Detailed execution logs** per node  
- 🧮 **Mutable workflow state** passed between nodes  
- 📘 **Swagger UI** for API testing (`/docs`)  
- 🐳 **Dockerfile included**  
- 🔧 **GitHub Actions CI workflow** included  
- 📦 Ready for extension (LLMs, databases, queues, frontend dashboards, etc.)

---

## 📁 Project Structure
quantum-workflow-backend/
│
├── app/
│ ├── main.py # API endpoints & graph registration
│ ├── engine.py # Core workflow engine
│ ├── models.py # Pydantic models (RunState, GraphDef, RunRequest, etc.)
│ ├── tools.py # Helper utilities (optional)
│ └── workflows.py # Node implementations (extract, analyze, detect, suggest)
├── requirements.txt
├── .gitignore
├── README.md
├── LICENSE
└── .github/
└── workflows/
└── python-app.yml # CI pipeline

