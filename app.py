import streamlit as st
import os
from supervisor import workflow

st.set_page_config(page_title="My Streamlit App", page_icon=":smiley:", layout="centered")
topic = st.text_input("Write a topic to research")

if st.button("Generate Content") and topic:
    with st.spinner(f"Agents are creating content about {topic}..."):
        res = workflow.invoke({"topic": topic, "messages": []})
        
        # Traverse messages backwards to find the tool call that wrote the file
        written_content = None
        saved_file_name = None
        
        for message in reversed(res.get("messages", [])):
            if hasattr(message, "tool_calls") and message.tool_calls:
                for tool_call in message.tool_calls:
                    if tool_call["name"] == "write_file_tool":
                        saved_file_name = tool_call["args"].get("file_name")
                        written_content = tool_call["args"].get("content")
                        break
            if written_content:
                break
        
        if written_content:
            st.success(f"Content successfully generated and saved to `{saved_file_name}`!")
            
            # Displaying the content in Streamlit
            st.markdown("### Generated Article")
            st.write(written_content)
            
            # Allow user to download the file directly from Streamlit
            st.download_button(
                label="Download Article",
                data=written_content,
                file_name=saved_file_name or "article.txt",
                mime="text/plain"
            )
        else:
            st.warning("The workflow completed, but the write_file_tool wasn't called. Check your prompt logic!")