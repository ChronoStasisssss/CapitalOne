from langchain.llms import OpenAI

def analyze_text(text):
    llm = OpenAI()
    return llm(text)
