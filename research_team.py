from state import ContentState
from langchain_core.messages import SystemMessage, HumanMessage
from research_tools import search_tool, get_date_time
from models import model
from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import ToolNode
def research_node(state:ContentState):
    system_prompt="""You are the Research Agent. Use the `search_tool` strictly ONCE to gather relevant information 
        about the given topic. Call the tool, analyze the results, and provide a clear, 
        synthesized summary of facts for the Writer team. Do NOT make multiple parallel tool calls.
        while calling the `search_tool` remember to pass limit in int and query as a string. You are also given with the `get_date_time` tool to find current date and time. DO not assume any dates on your own use tool to get current date and time"""
    print("CALLED RESEARCH NODE",)
    researcher_model=model.bind_tools([search_tool,get_date_time])
    messages=[SystemMessage(system_prompt),HumanMessage("topic:",state['topic'])]+state['messages']
    res=researcher_model.invoke(messages)
    return {"messages":[res]}

def check_tool(state:ContentState):
    """Determine whether to use a tool or end the subgraph."""

    last_message=state['messages'][-1]  
    if(last_message.tool_calls):
        return "tool_node"
    return END

research_graph=StateGraph(ContentState)
research_graph.add_node("research_node",research_node)
research_graph.add_node("tool_node",ToolNode([search_tool,get_date_time]))

research_graph.add_edge(START,"research_node")
research_graph.add_conditional_edges("research_node",check_tool,{"tool_node":"tool_node",END:END})
research_graph.add_edge("tool_node","research_node")

researchers=research_graph.compile()
