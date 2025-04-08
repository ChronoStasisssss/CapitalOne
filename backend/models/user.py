from pydantic import BaseModel

class User(BaseModel):
    name: str
    email: str
    description: str  # Texto que analizará la IA
