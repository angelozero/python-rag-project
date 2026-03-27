from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from src.config.llm_factory import chat_model
from tavily import TavilyClient

load_dotenv()
tavily = TavilyClient()


def tavily_execute():
    llm = chat_model()
    tools = [search]
    agent = create_agent(model=llm, tools=tools, debug=True)
    result = agent.invoke(
        {
            "messages": [
                SystemMessage(
                    content=(
                        "You are a helpful assistant with access to a search tool. "
                        "When you get the answer from the tool, STOP and write: 'The planets are [names]'. "
                        "DO NOT use the search tool more than once for the same question. "
                        "If you see the answer in the conversation history, just repeat it to the user."
                    )
                ),
                HumanMessage(
                    content="What are the names of all planets in solar system? Answer in plain text."
                ),
            ]
        },
        config={"recursion_limit": 10}
    )
    print(f"\nTools Response: ", result)


@tool
def search(query: str) -> str:
    """
    Search the internet. USE THIS TOOL TO GET DATA.
    After receiving the results, provide the final answer to the user immediately.
    """
    print(f"\nSearching for '{query}'")
    return tavily.search(query=query)
