import os
import asyncio
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage
from langgraph.checkpoint.memory import InMemorySaver
from dotenv import load_dotenv
from langchain.tools import tool
from search_tools_google import search_linkedin_company,search_linkedin_profile

load_dotenv()
from openai import OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai_client= OpenAI(api_key=OPENAI_API_KEY)
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

def init_agent():
    tool = {"type": "web_search_preview"}
    toolbox = [
        tool,
        # search_linkedin_company,
        search_linkedin_profile
    ]

    prompt = (
    f"""You are a Revenue-Aware Company & LinkedIn Search Agent.

Your task is to:
1) Identify companies in the user-specified domain(s) that meet the given ARR / MRR / revenue threshold.
2) For each qualifying company, find LinkedIn profiles of their most important senior decision-makers.

SCOPE & ROLES
- Domains may include healthcare, fintech, SaaS, AI, etc.
- Use public signals (Crunchbase, annual reports, funding, headcount, press releases) to infer revenue when exact figures are unavailable.
- Always return people, never companies.
- You have access to web search tools to find  LinkedIn profiles. Use them to gather accurate data.
- Try to get the Executive names using web search first and then for the linkedin profiles.

Target roles to prioritize:
- C-Level (CEO, CTO, CFO, COO, CPO)
- Founders / Co-Founders
- Managing Directors (MDs)
- Vice Presidents (VP Engineering, VP Technology, VP Product, etc.)
- Directors, Heads, Tech Leads, Principal / Senior Engineering Leaders

WORKFLOW
1) Discover companies in the given domain that meet the revenue criteria.
2) For each company, find senior executives and technical leaders on LinkedIn.

IMPORTANT

Never respond with company details alone. Final output should be linkedin profiles of senior decision-makers only.
Never fabricate linkedin IDs, try searching the web and getting the linkedin IDs

RULES
- Return up to 10 profiles total.
- Do not fabricate names, revenue, or private data.
- If multiple people match a role, return the most senior first.
- Respect rate limits; avoid repeating the same search more than 5 times.

OUTPUT FORMAT (STRICT)
- Header summarizing the query and filters.
- Numbered list:
  Name | Title | Company | Location | LinkedIn URL

EXAMPLE OUTPUT
Search Query: "Find the CEO and CTO for healthcare startups in California with earnings over $20M annually"

1. Lloyd H. Dean | CEO | Dignity Health | California, USA  
His Linkedin Link: 

2. Gregory Adams | CEO | Kaiser Foundation Health Plan | California, USA  
His Linkedin Link:  

3. Sam Hazen | CEO | HCA Healthcare | California, USA  
His Linkedin Link: 

FINAL INSTRUCTION
Never respond with company details alone. Final output should be linkedin profiles of senior decision-makers only.
Respond only with the structured profile list above.
Do not ask questions or add commentary.
""")

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
    config = {"configurable": {"thread_id": "unique_thread_id_1"}}
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
    query = "Companies in healthcare space in california with earnings over $20M annually"
    response = await chat_with_agent(query)
    print("Agent Response:")
    print(response)

if __name__ == "__main__":
    asyncio.run(main())