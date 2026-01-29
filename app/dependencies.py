from functools import lru_cache
from langchain_groq import ChatGroq
from app.config import settings

@lru_cache()
def get_llm():
    return ChatGroq(
        temperature=0.0,
        model_name="llama-3.3-70b-versatile",
        api_key=settings.groq_api_key
    )
