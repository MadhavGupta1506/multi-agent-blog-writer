from dotenv import load_dotenv
import os
class Config:
    def __init__(self):
        load_dotenv()
        self.serpapi_key = os.getenv("SERPAPI_KEY")
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.email_address = os.getenv("EMAIL_ADDRESS")
        self.email_password = os.getenv("EMAIL_PASSWORD")
        self.tavily_api_key = os.getenv("TAVILY_API_KEY")
config = Config()