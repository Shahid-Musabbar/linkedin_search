import os
import asyncio
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage
from langgraph.checkpoint.memory import InMemorySaver
from dotenv import load_dotenv
from langchain.tools import tool
from search_tools_google import search_linkedin_company

load_dotenv()
from openai import OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai_client= OpenAI(api_key=OPENAI_API_KEY)
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

def init_agent():
    tool = {"type": "web_search_preview"}
    toolbox = [
        tool,
        # search_linkedin_company
    ]

    prompt = (
    f"""You are a LinkedIn Search Agent whose primary role is to locate and return LinkedIn profiles for senior technical and executive roles (for example: CTOs, CEOs, Founders) or any specific designation the user requests.

Core Responsibilities:
- Given a company name, domain, or a user-supplied query, search LinkedIn and related public sources to find relevant profiles that match the requested designation(s).
- If only company/domain is provided, infer likely senior technical/executive roles to search for (e.g., CTO, VP of Engineering, Head of Technology).
- For each found profile, return a structured output including: full name, current title, company, LinkedIn profile URL, location, and any public contact or website listed.
- Prioritize accuracy: prefer official company pages, verified LinkedIn profiles, or consistent cross-references (company website, Twitter, Crunchbase).
- When the user supplies filters (location, region, seniority, number of employees), apply them to narrow results.

Workflow and Tool Use:
1) Search: Use available web search tools and LinkedIn queries to discover candidate profiles for the requested designation.
2) Gather: Collect profile details and return results in a compact, structured format (list of profiles with the fields described above). Stick to public information only.
3) Output: Present up to the top 20 matching profiles by relevance, and include short reasoning why each profile matches (1–2 lines).

Important Rules:
- Strictly follow the expected output format.
- Always look for people and not companies , meaning if they mention companies also look for executives and not for the company itself.
- Always look for C level executives, Founders, Co-Founders, VPs, Directors, Engineering Leaders, Tech Leaders when requested on any company or domain.
- Do not fabricate contact details or private data; only include information that is publicly visible on the profile or linked pages.
- Respect rate limits on repeated searches; avoid repeating the same search tool more than 5 times per user request.
- If multiple people match the same title at a company, include the most senior or most publicly prominent first.
- If a domain is provided, prioritize people who list that domain or company in their profile.

Example user requests you should support:
- "Find CTO profiles at Acme Corp in the US"
- "Search for Founders in the fintech space in Europe the companies which earn over $10M annually"
- "Find the CEO and CTO for healthcare startups in California with earnings over $20M annually"

Expected Output Format:
- A short header summarizing the query and applied filters.
- A numbered list of profiles with: `Name | Title | Company | Location | LinkedIn URL` .
Example Output:
Search Query: "Find the CEO and CTO for healthcare startups in California with earnings over $20M annually"
Lloyd H. Dean (CEO, Dignity Health)
https://www.linkedin.com/in/lloyd-h-dean-3b8b8b8

Gregory Adams (CEO, Kaiser Foundation Health Plan)
https://www.linkedin.com/in/gregory-adams-4a5b6b7

Sam Hazen (CEO, HCA Healthcare)
https://www.linkedin.com/in/sam-hazen-8a9b0b1

Answer with only the structured profile list and no additional commentary or questions""")

    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)
    llm_with_tools = llm.bind_tools(toolbox)
    # structured_llm_tools = llm.with_structured_output(EmailListOutput, tools=toolbox)
    checkpointer = InMemorySaver()

    agent = create_react_agent(
        # structured_llm_tools,
        llm_with_tools,
        tools=toolbox,
        prompt=prompt,
        checkpointer=checkpointer,
    )

    return agent

agent = init_agent()

async def chat_with_agent(user_input):
    config = {"configurable": {"thread_id": "uniquer_thread_id12334239894"}}
    response = await agent.ainvoke({"messages": f"User Query: {user_input}"}, config=config)
    # print(response.output_parsed)
    print(response)
    ai_messages = [m for m in response["messages"] if isinstance(m, AIMessage)]
    # Normalize: extract text content properly
    last_message = ai_messages[-1].content
    if isinstance(last_message, list):
        # Extract all 'text' fields if present
        texts = []
        for part in last_message:
            if isinstance(part, dict) and "text" in part:
                texts.append(part["text"])
            else:
                texts.append(str(part))
        return texts
    elif isinstance(last_message, str):
        return [last_message]
    else:
        return [str(last_message)]

async def main():
    agent = init_agent()
    query = "Companies in healthcare space in New York with earnings over $20M annually"
    response = await chat_with_agent(query)
    print("Agent Response:")
    print(response)

if __name__ == "__main__":
    asyncio.run(main())