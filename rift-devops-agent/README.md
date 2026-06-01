# 🤖 RIFT DevOps Agent

> **Autonomous CI/CD Healing Agent with Multi-Agent Architecture**

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://reactjs.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.0.26-orange.svg)](https://langchain.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🎯 Overview

The **RIFT DevOps Agent** is an autonomous CI/CD healing system that:

- 🔍 **Analyzes** GitHub repositories for code issues
- 🧠 **Learns** from past fixes using vector memory
- 🔧 **Fixes** bugs automatically (linting, syntax, type errors, etc.)
- 📤 **Commits** fixes with `[AI-AGENT]` prefix
- 👀 **Monitors** CI/CD pipeline until all tests pass
- 📊 **Visualizes** everything in a beautiful React dashboard

## ✨ Key Features

### Multi-Agent Architecture (LangGraph)
- **Analyzer Agent**: Clones repos, detects issues using pylint, flake8, mypy, bandit
- **Learner Agent**: Searches vector memory for similar bug patterns
- **Fixer Agent**: Generates and applies fixes using LLM + rule-based approaches
- **Committer Agent**: Creates branches, commits fixes, pushes to remote
- **CI Watcher Agent**: Monitors pipeline, retries if needed

### 🧠 Intelligent Memory System
- Vector database (ChromaDB) stores bug patterns
- Learns from each fix - gets smarter over time
- Retrieves similar patterns for faster fixes

### 📊 Real-Time Dashboard
- **Live Architecture Visualization**: See agents working in real-time
- **WebSocket Streaming**: Watch the agent "think" live
- **Code Diff Viewer**: Before/after comparison for every fix
- **Repository File Tree**: Color-coded error visualization
- **Bug Heatmap**: Identify problematic directories
- **Historical Comparison**: Compare runs and track improvement

### 🎨 Modern UI/UX
- Dark/Light mode toggle
- Responsive design (desktop + mobile)
- Exportable PDF reports
- Shareable run URLs

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- Docker (optional)
- GitHub Personal Access Token
- OpenAI API Key

### Environment Setup

1. **Clone the repository**
```bash
git clone https://github.com/your-team/rift-devops-agent.git
cd rift-devops-agent
```

2. **Set up environment variables**
```bash
# Backend
export OPENAI_API_KEY="your-openai-api-key"
export GITHUB_TOKEN="your-github-token"

# Frontend (optional)
export VITE_API_URL="http://localhost:8000"
```

### Option 1: Docker (Recommended)

```bash
cd docker
docker-compose up --build
```

Access the dashboard at: http://localhost

### Option 2: Local Development

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:socket_app --host 0.0.0.0 --port 8000 --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

Access the dashboard at: http://localhost:5173

## 📁 Project Structure

```
rift-devops-agent/
├── backend/                    # FastAPI + LangGraph backend
│   ├── app/
│   │   ├── main.py            # FastAPI application entry
│   │   ├── core/              # Config, database
│   │   └── models/            # Pydantic schemas
│   ├── agents/                # Multi-agent system
│   │   ├── orchestrator.py    # LangGraph workflow
│   │   ├── analyzer.py        # Repository analysis
│   │   ├── learner.py         # Pattern learning
│   │   ├── fixer.py           # Fix generation
│   │   ├── committer.py       # Git operations
│   │   └── ci_watcher.py      # CI/CD monitoring
│   ├── services/              # Business logic
│   │   ├── github_service.py  # GitHub API
│   │   ├── memory_service.py  # Vector DB
│   │   └── report_service.py  # PDF generation
│   └── requirements.txt
├── frontend/                   # React + Vite frontend
│   ├── src/
│   │   ├── sections/          # Dashboard sections
│   │   ├── hooks/             # Custom React hooks
│   │   └── types/             # TypeScript types
│   └── package.json
├── docker/                     # Docker configuration
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   ├── docker-compose.yml
│   └── nginx.conf
├── k8s/                        # Kubernetes manifests
│   ├── namespace.yaml
│   ├── backend-deployment.yaml
│   ├── frontend-deployment.yaml
│   └── secrets.yaml
└── README.md
```

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API info |
| `/health` | GET | Health check |
| `/api/v1/run` | POST | Start agent run |
| `/api/v1/status/{run_id}` | GET | Get run status |
| `/api/v1/results/{run_id}` | GET | Get run results |
| `/api/v1/runs` | GET | List all runs |
| `/api/v1/runs/{run_id}/report` | GET | Download PDF report |
| `/api/v1/runs/{run_id}/heatmap` | GET | Get bug heatmap |
| `/api/v1/bug-patterns` | GET | Get learned patterns |

## 🐛 Supported Bug Types

| Type | Description | Example |
|------|-------------|---------|
| `LINTING` | Style issues, unused imports | `Unused import 'os'` |
| `SYNTAX` | Syntax errors | `Missing colon` |
| `TYPE_ERROR` | Type mismatches | `Expected str, got int` |
| `IMPORT` | Import issues | `Module not found` |
| `LOGIC` | Logic errors | `Undefined variable` |
| `INDENTATION` | Indentation errors | `Mixed tabs and spaces` |
| `SECURITY` | Security issues | `Hardcoded password` |

## 🌐 WebSocket Events

| Event | Direction | Description |
|-------|-----------|-------------|
| `connect` | Client → Server | Connection established |
| `subscribe_run` | Client → Server | Subscribe to run updates |
| `run_update` | Server → Client | Real-time run progress |

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Input Form  │  │ Dashboard   │  │ Live Architecture   │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼ WebSocket / HTTP
┌─────────────────────────────────────────────────────────────┐
│                      Backend (FastAPI)                      │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              Agent Orchestrator (LangGraph)            │ │
│  │  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌────────┐  │ │
│  │  │Analyzer │ → │ Learner │ → │  Fixer  │ → │Committe │ │ │
│  │  └─────────┘   └─────────┘   └─────────┘   └────────┘  │ │
│  │       ↑                                      ↓         │ │
│  │       └────────────── CI Watcher ←───────────┘         │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ GitHub API  │  │ ChromaDB    │  │ PDF Generator       │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 🚢 Deployment

### Docker Compose
```bash
cd docker
docker-compose up -d
```

### Kubernetes
```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Create secrets (edit with your keys first)
kubectl apply -f k8s/secrets.yaml

# Deploy backend and frontend
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml
```

### Cloud Deployment

**Vercel (Frontend):**
```bash
cd frontend
vercel --prod
```

**Railway/Render (Backend):**
```bash
# Set environment variables in dashboard
# Deploy from GitHub repository
```

## 🧪 Testing

**Backend tests:**
```bash
cd backend
pytest tests/ -v --cov=.
```

**Frontend tests:**
```bash
cd frontend
npm test
```

## 📈 Performance

- **Average fix time**: ~30 seconds per issue
- **CI/CD monitoring**: Up to 10 minutes (configurable)
- **Max iterations**: 5 (configurable)
- **Memory usage**: ~500MB for backend
- **Vector DB**: Persistent storage for learned patterns

## 🔒 Security

- GitHub token stored as environment variable
- Sandboxed code execution (Docker recommended)
- No sensitive data in logs
- CORS configured for frontend

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏆 Team

**RIFT ORGANISERS**
- Team Leader: Saiyam Kumar

## 📞 Support

- GitHub Issues: [Create an issue](https://github.com/your-team/rift-devops-agent/issues)
- LinkedIn: Tag @RIFT2026

## 🔗 Links

- [Live Demo](https://your-deployment-url.com)
- [Demo Video](https://linkedin.com/your-video)
- [Documentation](https://your-docs-url.com)

---

<p align="center">
  Built with ❤️ for RIFT 2026 Hackathon
</p>
