from datetime import datetime
from langchain_core.tools import tool
from langchain_tavily import TavilySearch
import config

@tool
def search_tool(query:str,limit:int):
    """This tool is used to search content from the internet."""
    print("CALLED SEARCH TOOL WITH QUERY:",query)
    search_agent=TavilySearch(api_key=config.config.tavily_api_key)
    res=search_agent.invoke({"query":query})["results"][:limit]
    response=""
    for data in res:
        response+=data["content"]+"\n"
    return response

@tool
def get_date_time():
    """This tool returns current date and time"""
    return datetime.now()



