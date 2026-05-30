from langchain_groq import ChatGroq
import config

model=ChatGroq(model="llama-3.1-8b-instant", groq_api_key=config.config.groq_api_key)
versatile_model=ChatGroq(model="llama-3.3-70b-versatile", groq_api_key=config.config.groq_api_key)