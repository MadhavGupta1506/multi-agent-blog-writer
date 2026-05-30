from state import ContentState
from langchain_core.messages import SystemMessage, HumanMessage
from writer_tools import writer_tools
from models import versatile_model
from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import ToolNode

def writer_node(state:ContentState):
    system_prompt="""You are the Writer Agent. Use the facts provided by the Research team in the conversation history
        to write an engaging, well-formatted blog post or article. Researcher team search the content for you
        RULES:
        1. Write the final article by fully invoking the `write_file_tool` ONCE.
        2. Do NOT write line-by-line.
        3. You must provide a valid `file_name` taking inspiration from the topic with .txt extension eg.: `topic.txt`, `news.txt`, `updates.txt`, etc.
        4. You are given with `write_file_tool`, `read_file_tool` and `edit_file_tool` to make changes in the file.
        5. You are also given `send_email_tool` to send an email to the email mentioned. If user did not mention in its query skip the email. Send email only when the file is saved .
        6. Do not use `send_email_tool` if user did not mention about email in its query. Only use `send_email_tool` when the file is saved and user mentioned about email in its query. Always make sure you have the right email address before sending email. Do not send mail to any random email address. If you are not sure about the email address then do not use the `send_email_tool`
        
        You only have these tools:
        `write_file_tool`: Create and make changes in the file
        `read_file_tool`: Read content of the file
        `edit_file_tool`: Make changes in the specific content in the file
        `send_email_tool`: To send an email to the person's mail id.
        
        RULES:
        Avoid excessive quotation marks.
        Summarize instead of copying exact sentences.
        Do not include escaped quotes, backslashes, or complex escape characters that break JSON encoding.
        DO NOT CALL ANY OTHER TOOL THAN PROVIDED.
        Make sure the file is properly saved.
        Do not use `send_email_tool` if user did not mention about email in its query. Only use `send_email_tool` when the file is saved and user mentioned about email in its query.
        """
    
    print("CALLED WRITER NODE",)

    messages=[SystemMessage(system_prompt),HumanMessage(f"topic:{state['topic']}. Please draft the file based on the previous context.")]+state['messages']
    writer_model=versatile_model.bind_tools(writer_tools)
    res=writer_model.invoke(messages)
    return{"messages":[res]}
def check_writer_tool(state:ContentState):
    """Determine whether to use a tool or end the subgraph."""
    last_message=state['messages'][-1]
    if(last_message.tool_calls):
        return "tool_node"
    return END

writer_state_graph=StateGraph(ContentState)
writer_state_graph.add_node("writer_node",writer_node)
writer_state_graph.add_node("tool_node",ToolNode(writer_tools))

writer_state_graph.add_edge(START,'writer_node')
writer_state_graph.add_conditional_edges("writer_node",check_writer_tool,{"tool_node":"tool_node",END:END})
writer_state_graph.add_edge("tool_node","writer_node")

writers=writer_state_graph.compile()