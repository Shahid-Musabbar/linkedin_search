# LinkedIn Lead Capturing Agent (for AI Agencies)

This repository provides a **LinkedIn Lead Capturing Agent** designed as a plug‑and‑play tool for AI agencies to discover high‑value companies and surface senior decision‑makers’ LinkedIn profiles using Google Custom Search and a LangGraph/LangChain agent. [page:0][page:1][page:2]

---

## What This Agent Does

- Identifies companies in your target niche (e.g., healthcare, fintech, SaaS, AI) that meet specific revenue or scale criteria (ARR/MRR/annual revenue). [page:1]
- Finds senior decision‑makers’ LinkedIn profiles (C‑suite, founders, VPs, directors, senior engineering leaders) at those companies. [page:1]
- Uses Google Custom Search to:
  - Query `site:linkedin.com/in` for individual profiles. [page:2]
  - Query `site:linkedin.com/company` for company pages. [page:2]
- Wraps everything into a ReAct‑style LangGraph/LangChain agent, ready to be integrated into your AI agency workflows (inbound qualification, outbound prospecting, or SDR copilot tools). [page:1]

---

## How AI Agencies Can Use It

AI agencies can use this agent as a **lead capture and enrichment backend**:

- Plug into:
  - Web forms: Enrich incoming leads with matching decision‑makers.  
  - Internal SDR tools: Let reps ask, “Find AI‑ready e‑commerce brands in the US with >$10M revenue and give me CTO/Head of Data profiles.” [page:1]
  - Outreach automation: Generate targeted LinkedIn lead lists per campaign or niche. [page:1]
- The agent is instructed to:
  - Always return people, not just company information.  
  - Return up to 10 leads formatted as:  
    `Name | Title | Company | Location | LinkedIn URL`. [page:1]
  - Avoid fabricating names or LinkedIn URLs and rely on web search instead. [page:1]

---

## Project Structure

- `linkedin_agent.py`  
  - Initializes the LangGraph ReAct agent that orchestrates Google search tools and the LLM. [page:1]  
  - Core entry points:
    - `init_agent()` – builds and returns the agent. [page:1]  
    - `chat_with_agent(user_input)` – async helper to send a natural language query and get a normalized response (lead list). [page:1]  
    - `main()` – sample run that searches for healthcare companies in California with > $20M annual earnings and surfaces relevant decision‑makers. [page:1]

- `search_tools_google.py`  
  - Google Custom Search wrappers:
    - `search_linkedin_profile(name: str, num_results: int = 10)` – searches LinkedIn profiles (`site:linkedin.com/in`). [page:2]
    - `search_linkedin_company(company_name: str, num_results: int = 10)` – searches company pages (`site:linkedin.com/company`). [page:2]
  - Includes a daily usage quota with JSON‑based tracking. [page:2]

- `google_cse_usage.json`  
  - Stores the current date and the number of Google Custom Search calls made today to enforce the daily cap. [page:1][page:2]

- `requirements.txt`  
  - Python dependencies (LangChain, LangGraph, OpenAI SDK, requests, python-dotenv, etc.). [page:1][page:2]

---

## Setup

### Prerequisites

- Python 3.9+ recommended. [page:1][page:2]
- Keys and IDs:
  - `OPENAI_API_KEY` – for the OpenAI chat model (`gpt-4o-mini`). [page:1]
  - `GOOGLE_API_KEY` – Google Custom Search API key. [page:2]
  - `SEARCH_ENGINE_ID` – Google Custom Search Engine (CSE) ID. [page:2]

Create a `.env` file in the project root: [page:1][page:2]

```env
OPENAI_API_KEY=your_openai_api_key
GOOGLE_API_KEY=your_google_cse_api_key
SEARCH_ENGINE_ID=your_google_cse_id
