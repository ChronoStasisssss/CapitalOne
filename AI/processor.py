from langchain.llms import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

def analyze_text(text):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("Missing OPENAI_API_KEY in environment variables")
    
    llm = OpenAI(openai_api_key=api_key)
    return llm(text)
