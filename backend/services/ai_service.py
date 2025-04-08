from AI.processor import analyze_text
from fastapi import HTTPException

def process_with_langchain(text: str):
    try:
        if not text or len(text.strip()) < 10:
            raise ValueError("Text must be at least 10 characters long")
        return analyze_text(text)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"AI processing failed: {str(e)}"
        )
