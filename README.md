🔬 Autonomous Multi-Agent Research System

An autonomous AI research application that uses LangGraph, LangChain,
Groq, and Tavily to plan research, search the web in parallel, analyze
evidence, validate claims, and generate a structured research report.

🚀 Overview

The system takes a research topic and autonomously performs a
multi-stage research workflow:

Query Planner --- creates focused, non-duplicative research
queries.

Research Agent --- performs parallel web searches using Tavily.

Analyst Agent --- extracts evidence-backed claims and identifies
missing information.

Autonomous Research Loop --- performs targeted follow-up
research when information is insufficient.

Citation Validator --- checks claims against their supplied
evidence.

Writer Agent --- generates the final Markdown research report.

The application is exposed through a simple Streamlit interface and
can be run locally or with Docker Compose.

🏗️ Architecture

flowchart TD
    A[User enters research topic] --> B[Query Planner]

    B --> C[Research Agent]

    C --> D[Tavily Web Search]
    D --> C

    C --> E[Analyst Agent]

    E --> F{More research needed?}

    F -- Yes --> G[Generate targeted follow-up queries]
    G --> C

    F -- No --> H[Citation Validator]

    H --> I[Writer Agent]

    I --> J[Final Research Report]

    J --> K[Streamlit UI]

Backend workflow

User
  │
  ▼
Query Planner
  │
  ▼
Parallel Web Research
  │
  ▼
Analyst
  │
  ├── More information needed ──► Follow-up Research
  │                                  │
  │                                  ▼
  │                                Analyst
  │
  ▼
Citation Validator
  │
  ▼
Writer
  │
  ▼
Final Report

✨ Features

🧠 Autonomous research query generation

🔎 Parallel web research

🌐 Tavily web search integration

📊 Evidence-based analysis

📌 Structured claims and evidence

🔄 Multi-round autonomous research

🔍 Citation and claim validation

✍️ LLM-generated research reports

⭐ Source quality scoring

🔐 Runtime API key support

⚡ Groq LLM integration

🦜 LangChain

🔗 LangGraph workflow orchestration

🎨 Streamlit interface

📥 Markdown and text report downloads

🐳 Docker support

📦 Docker Compose support

📝 Research session history

🛠️ Tech Stack

Technology       Purpose

Python           Core application
LangGraph        Agent workflow orchestration
LangChain        LLM application framework
Groq             LLM inference
Tavily           Web search
Streamlit        User interface
Pydantic         Structured data validation
python-dotenv    Environment configuration
Docker           Containerization
Docker Compose   Local container orchestration

📁 Project Structure

np1/
│
├── app.py
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .env
├── requirements.txt
│
├── agents/
│   ├── __init__.py
│   ├── query_planner.py
│   ├── research_agent.py
│   ├── analyst_agent.py
│   ├── validator_agent.py
│   └── writer_agent.py
│
├── tools/
│   ├── __init__.py
│   └── web_search.py
│
├── workflow/
│   ├── __init__.py
│   ├── state.py
│   └── orchestrator.py
│
├── models/
│   ├── __init__.py
│   └── schemas.py
│
├── utils/
│   ├── __init__.py
│   ├── helpers.py
│   ├── retry.py
│   └── source_utils.py
│
├── config/
│   ├── __init__.py
│   └── runtime.py
│
├── reports/
│
└── tests/

🔄 How It Works

1. Query Planning

The Query Planner receives the user's topic and generates multiple
focused search queries covering areas such as:

Current state

Statistics

Recent developments

Challenges

Opportunities

Future outlook

The planner returns structured JSON containing the research queries.

2. Parallel Research

The Research Agent sends multiple queries to Tavily concurrently.

This reduces the time required to collect sources compared with
sequential searches.

The system also:

Removes duplicate URLs

Scores source quality

Preserves source metadata

Combines results across research rounds

3. Evidence Analysis

The Analyst Agent receives the collected sources and extracts:

Key findings

Factual claims

Supporting evidence

Missing information

Confidence score

Claims must reference source IDs supplied by the research system.

4. Autonomous Research Loop

If the Analyst determines that important information is missing,
LangGraph routes the workflow back to research.

The Query Planner creates targeted follow-up queries from the missing
information.

The process continues until:

The research is considered sufficient, or

The configured maximum number of research rounds is reached.

5. Citation Validation

The Validator Agent checks claims against their supplied evidence.

It identifies:

Unsupported claims

Weak evidence

Invalid source references

Source conflicts

Validation score

6. Report Generation

The Writer Agent converts the validated research into a structured
Markdown report containing:

Executive Summary

Introduction

Key Findings

Current State

Statistics and Trends

Challenges

Opportunities

Future Outlook

Conclusion

Sources

🔐 API Keys

Create a .env file:

GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key

Do not commit .env to GitHub.

The Streamlit application also supports entering API keys at runtime.

💻 Local Installation

Clone the repository:

git clone YOUR_GITHUB_REPOSITORY_URL
cd np1

Create a virtual environment:

python -m venv .venv

Activate it on Windows:

.venv\Scripts\activate

Install dependencies:

pip install -r requirements.txt

Run Streamlit:

streamlit run app.py

Open:

http://localhost:8501

🐳 Docker

Build the image:

docker compose build

Start the application:

docker compose up

Open:

http://localhost:8501

Stop the application:

docker compose down

🧪 Testing

Run the test suite with:

pytest

Or, when using uv:

uv run pytest

📊 Example Research Topics

The system can be used for research topics such as:

AI adoption in healthcare

Electric vehicle market in India

Agricultural drone market

Generative AI industry trends

Battery swapping business

Future of autonomous AI agents

AI applications in financial services

For best results, use a topic that can be investigated through multiple
factual dimensions.

🧩 Design Principles

Evidence First

The system is designed so that factual claims should be connected to
supplied evidence.

Autonomous Iteration

The workflow can recognize missing information and perform additional
targeted research.

Modular Agents

Each major responsibility is isolated into its own module, making the
system easier to test and extend.

Structured Outputs

Pydantic models are used for important structured results such as
claims, evidence, and validation results.

Token Efficiency

The system limits the amount of research context passed to downstream
LLM calls to reduce unnecessary token usage.

Fault Tolerance

Retry logic is used for external API operations that may temporarily
fail.

⚠️ Limitations

Web search results depend on Tavily.

Source quality scoring uses predefined domain categories and should
not be treated as an absolute measure of source reliability.

LLM-generated analysis can still contain errors.

Claim validation is based on the evidence supplied to the validator.

The system does not guarantee that every generated statement is
correct.

API rate limits can affect large research tasks.

Research quality depends on the quality and availability of web
sources.

🔮 Future Improvements

Potential future improvements include:

Persistent database-backed research history

More advanced source credibility evaluation

Semantic source deduplication

Human-in-the-loop verification

Better citation extraction

PDF report generation

Authentication

Background research jobs

Research result caching

Observability and tracing

Automated evaluation of research quality

Cloud deployment

API endpoint using FastAPI

🎯 Project Goal

The goal of this project is to demonstrate how multiple specialized AI
agents can be orchestrated into an autonomous research workflow.

Rather than using a single LLM call, the system separates research
planning, information retrieval, analysis, validation, and report
generation into distinct stages connected through a LangGraph workflow.

👨‍💻 Author

Aman Jakhar

AI/ML Engineer | Generative AI | Agentic AI | Machine Learning

⭐ Project Highlights

This project demonstrates practical experience with:

Python
LangChain
LangGraph
LLMs
Multi-Agent Systems
Prompt Engineering
Web Search APIs
Evidence-Based Research
Structured Outputs
Pydantic
Streamlit
Docker
API Integration
Workflow Orchestration