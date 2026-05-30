from pydantic import BaseModel
from typing import Literal
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.types import Command
from models import versatile_model
from state import ContentState
from writer_team import writers
from research_tools import get_date_time
from research_team import researchers
from langgraph.prebuilt import ToolNode
from langgraph.graph import END, StateGraph, START

class SupervisorRouter(BaseModel):
    next: Literal["research_team", "writer_team", "FINISH"]
    instruction:str
    
    
def supervisor_node(state:ContentState):
    system_prompt="""
    You are the Workflow Supervisor managing a Content Creation Process.
        You have access to two teams:
        1. 'research_team': Search the web and gather information from web.It can also Identify current date and time for you.
        2. 'writer_team': Write the gathered facts into an article file.\n
        
        WORKFLOW RULES:
        1. If there are no search results in the conversation history, route to 'research_team'.
        2. If 'research_team' has already provided the search facts/summary, you MUST route to 'writer_team'. Do NOT route back to 'research_team'.
        3. If 'writer_team' has confirmed the file is saved, route to 'FINISH'.
        4. Do not review files unnecessarily, once file is written by the writer team just go to finish 
        
        Do not get stuck in a loop. Moving forward to the next team is strictly required.
        Also write the complete instruction so that the team could understand what it needs to do
    """
    
    print("CALLED SUPERVISOR NODE",)

    messages=[SystemMessage(system_prompt),HumanMessage(content="topic:"+state["topic"])]+state["messages"]
    supervisor_model=versatile_model.with_structured_output(SupervisorRouter)

    res=supervisor_model.invoke(messages)
    print(f"\n📌 [Supervisor Decision] Routing to 👉 {res.next}")
    print(f"💬 [Supervisor Context] {res.instruction}\n")
    
    if(res.next=="FINISH"):
        return Command(goto=END)
    return Command(goto=res.next,update={"messages":SystemMessage("Supervisor says:"+res.instruction)})

supervisor_graph=StateGraph(ContentState)
supervisor_graph.add_node("supervisor_node",supervisor_node)
supervisor_graph.add_node("research_team",researchers)
supervisor_graph.add_node("writer_team",writers)
supervisor_graph.add_node("tool",ToolNode([get_date_time]))


supervisor_graph.add_edge(START,"supervisor_node")
supervisor_graph.add_edge("research_team","supervisor_node")
supervisor_graph.add_edge("writer_team","supervisor_node")

workflow=supervisor_graph.compile()
