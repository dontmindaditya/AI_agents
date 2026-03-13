# Webby Backend - Multi-Agent AI System

A comprehensive multi-agent AI system built with FastAPI, LangChain, LangGraph, and CrewAI. This platform provides various AI agents for different tasks including frontend code generation, backend development, customer support, debugging/optimization, and converting research papers to code.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Available Agents](#available-agents)
4. [Prerequisites](#prerequisites)
5. [Installation](#installation)
6. [Configuration](#configuration)
7. [Running the Project](#running-the-project)
8. [Running Individual Agents](#running-individual-agents)
9. [API Endpoints](#api-endpoints)
10. [Environment Variables](#environment-variables)
11. [Development](#development)
12. [Testing](#testing)

---

## Project Overview

This is a **multi-agent AI platform** that orchestrates various specialized agents to handle different tasks:

- **Frontend Agent** - Generate production-ready React, Vue, or Vanilla JS code
- **Backend Agent** - Create robust API routes and database schemas
- **Customer Support Agent** - Intelligent query routing and response system
- **Debug & Optimization Agent** - Code analysis, profiling, and optimization suggestions
- **Paper2Code Agent** - Transform research papers and algorithms into working code

The system uses:
- **FastAPI** for the web framework
- **LangChain & LangGraph** for agent orchestration
- **CrewAI** for multi-agent collaboration
- **Supabase** for database storage
- **WebSockets** for real-time communication

---

## Architecture

```
d:/backend/
├── main.py                 # Main FastAPI application entry point
├── config.py               # Global configuration settings
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (create this)
│
├── agents/                 # Agent implementations
│   ├── base.py            # BaseAgent abstract class
│   ├── registry.py        # Agent auto-discovery registry
│   ├── frontend_agent/    # Frontend code generation agent
│   ├── backend-agent/     # Backend development agent
│   ├── customer-support-agent/  # Customer support chatbot
│   ├── debug-optimization-agent/ # Code analysis & optimization
│   └── paper2code/        # Research paper to code converter
│
├── pipeline/              # Pipeline orchestration (if exists)
├── routers/               # API route handlers (if exists)
├── services/              # Shared services (if exists)
└── utils/                 # Utility functions
```

---

## Available Agents

### 1. Frontend Agent (`agents/frontend_agent/`)
Generates production-ready frontend code using AI.

**Features:**
- Multi-framework support: React, Vue, Vanilla JS
- Code analysis and validation
- Accessibility and performance scoring
- Component-based code generation

**Run:**
```bash
cd agents/frontend_agent
python main.py --help
```

### 2. Backend Agent (`agents/backend-agent/`)
AI-powered backend development with LangChain and LangGraph.

**Features:**
- API route generation
- Database schema design
- Multi-agent orchestration
- Supabase integration

**Run:**
```bash
cd agents/backend-agent
python -m uvicorn main:app --reload --port 8001
```

### 3. Customer Support Agent (`agents/customer-support-agent/`)
Intelligent query routing and response system using LangGraph.

**Features:**
- Query classification
- Sentiment analysis
- Intent detection
- Automated responses

**Run:**
```bash
cd agents/customer-support-agent
python main.py
```

### 4. Debug & Optimization Agent (`agents/debug-optimization-agent/`)
AI-powered code analysis, profiling, and optimization.

**Features:**
- Static code analysis
- Runtime profiling
- Performance bottleneck detection
- Memory leak analysis
- Optimization suggestions
- Code quality metrics

**Run:**
```bash
cd agents/debug-optimization-agent

# Analyze a file
python main.py --file path/to/your_file.py

# Analyze code string
python main.py --code "def hello(): print('hello')"

# Save results to JSON
python main.py --file path/to/your_file.py --output results.json

# Skip profiling (static analysis only)
python main.py --file path/to/your_file.py --no-profiling
```

### 5. Paper2Code Agent (`agents/paper2code/`)
Transform research papers and algorithm descriptions into working code.

**Features:**
- PDF parsing
- LaTeX support
- Multi-language code generation (Python, JavaScript, TypeScript, Java, C++)
- Test file generation
- Code review and quality scoring

**Run:**
```bash
cd agents/paper2code

# Convert PDF to Python
python main.py convert paper.pdf -o ./output -l python

# Interactive mode
python main.py interactive

# Show system info
python main.py info
```

---

## Prerequisites

- **Python 3.10+**
- **API Keys** for LLM providers (OpenAI, Anthropic, Google, Groq)
- **Supabase** account (optional, for database features)

---

## Installation

1. **Clone the repository:**
```bash
cd d:/backend
```

2. **Create a virtual environment (recommended):**
```bash
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on Linux/Mac
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Create environment file:**
Create a `.env` file in the project root with the following variables:

```env
# Application Settings
APP_NAME="Webby Backend"
DEBUG=true
ENVIRONMENT=development
HOST=0.0.0.0
PORT=8000

# Supabase (Optional)
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
SUPABASE_SERVICE_KEY=your_service_key

# LLM API Keys (At least one required)
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
GROQ_API_KEY=your_groq_key
GEMINI_API_KEY=your_google_key

# Model Settings
CLAUDE_MODEL=claude-sonnet-4-20250514
GPT_MODEL=gpt-4o
GROQ_MODEL=llama-3.1-70b-versatile
GEMINI_MODEL=gemini-1.5-pro

# Logging
LOG_LEVEL=INFO
```

---

## Running the Project

### Option 1: Run Main FastAPI Server

```bash
# From project root
python main.py
```

The server will start at `http://localhost:8000`

### Option 2: Run with Uvicorn

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Access API Documentation

Once running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## Running Individual Agents

### Frontend Agent

```bash
# Interactive mode
cd agents/frontend_agent
python main.py -i

# CLI mode
python main.py "A modern todo list app" -f react -o ./output

# With verbose output
python main.py "Build a calculator" -f vue -v
```

### Backend Agent (as FastAPI server)

```bash
cd agents/backend-agent
python -m uvicorn main:app --reload --port 8001
```

### Customer Support Agent

```bash
cd agents/customer-support-agent
python main.py
# Select option 1 for single query, 2 for test queries
```

### Debug & Optimization Agent

```bash
cd agents/debug-optimization-agent

# Basic analysis
python main.py --file my_app.py

# Full analysis with profiling
python main.py --file my_app.py --output analysis.json

# Static analysis only (faster)
python main.py --file my_app.py --no-profiling
```

### Paper2Code Agent

```bash
cd agents/paper2code

# Convert PDF
python main.py convert research_paper.pdf -o ./output -l python

# From text description
python main.py convert algorithm.txt -l javascript

# Interactive mode
python main.py interactive
```

---

## API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Root endpoint |
| GET | `/health` | Health check |
| WS | `/ws/{project_id}` | WebSocket for real-time updates |

### Pipeline Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/pipeline/execute` | Execute a pipeline (requires API key) |
| GET | `/api/pipeline/status/{project_id}` | Get pipeline status (requires API key) |
| POST | `/api/pipeline/cancel/{project_id}` | Cancel a pipeline (requires API key) |

### Agent Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/agents/execute` | Execute a specific agent (requires API key) |

---

## Environment Variables

| Variable | Required | Description | Default |
|----------|----------|--------------|---------|
| `APP_NAME` | No | Application name | "Webby Backend" |
| `DEBUG` | No | Debug mode | false |
| `HOST` | No | Server host | "0.0.0.0" |
| `PORT` | No | Server port | 8000 |
| `OPENAI_API_KEY` | Yes* | OpenAI API key | - |
| `ANTHROPIC_API_KEY` | Yes* | Anthropic API key | - |
| `GROQ_API_KEY` | Yes* | Groq API key | - |
| `GEMINI_API_KEY` | Yes* | Google Gemini API key | - |
| `SUPABASE_URL` | No | Supabase URL | - |
| `SUPABASE_KEY` | No | Supabase key | - |
| `API_KEY_ENABLED` | No | Enable API key authentication | true |
| `API_KEYS` | No | List of valid API keys (comma-separated) | - |
| `RATE_LIMIT_ENABLED` | No | Enable rate limiting | true |
| `RATE_LIMIT_DEFAULT` | No | Default rate limit | "100/minute" |
| `RATE_LIMIT_PIPELINE` | No | Pipeline endpoint limit | "10/minute" |
| `RATE_LIMIT_AGENTS` | No | Agent endpoint limit | "30/minute" |

*At least one LLM API key is required for agent functionality.

---

## Security Features

### API Key Authentication
All agent endpoints require API key authentication via the `X-API-Key` header.

```bash
# Example request with API key
curl -H "X-API-Key: your-api-key" http://localhost:8000/api/agents/list
```

### Rate Limiting
Rate limiting is enabled by default to prevent abuse:
- Default: 100 requests/minute
- Pipeline endpoints: 10 requests/minute
- Agent endpoints: 30 requests/minute
- Health check: 200 requests/minute

When rate limit is exceeded, returns HTTP 429 with:
```json
{
  "detail": "Your limit is exceeded. Please wait for sometime before making another request.",
  "retry_after": "60 per 1 minute"
}
```

### Input Validation
All API endpoints include robust input validation:
- Project ID: alphanumeric with hyphens/underscores only
- Agent type: must be one of allowed types
- Project type: must be web, mobile, desktop, api, fullstack, or library
- Framework: must be react, vue, angular, nextjs, django, fastapi, flask, express, or spring
- String fields: min/max length limits
- Dictionary fields: max key limits

---

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run specific agent tests
pytest agents/frontend_agent/tests/
pytest agents/backend-agent/tests/

# With coverage
pytest --cov=. --cov-report=html
```

### Project Structure

Each agent follows a consistent structure:

```
agent_name/
├── main.py              # Entry point
├── config/              # Configuration
├── src/                 # Source code
│   ├── agents/          # Agent implementations
│   ├── graph/           # LangGraph definitions
│   ├── tools/           # Tools for agents
│   └── utils/           # Utilities
├── tests/              # Unit tests
└── examples/            # Example usage
```

---

## Troubleshooting

### Common Issues

1. **No LLM API Key configured:**
   ```
   WARNING: No LLM provider API keys configured!
   ```
   Solution: Set at least one of `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GROQ_API_KEY`, or `GEMINI_API_KEY` in your `.env` file.

2. **Database not configured:**
   ```
   WARNING: Database not configured!
   ```
   Solution: Set `SUPABASE_URL` and `SUPABASE_KEY` in your `.env` file if you need persistence.

3. **Module import errors:**
   Solution: Ensure you're running from the correct directory and virtual environment is activated.

4. **Port already in use:**
   Solution: Change the port in your `.env` file or kill the process using the port.

### Getting Help

- Check the individual agent's `README.md` for agent-specific documentation
- Review the configuration files in each agent's `config/` directory
- Examine the test files for usage examples

---

## License

This project is part of the Webby Backend system.

---

## Support

For issues and questions, please refer to the project documentation or contact the development team.
