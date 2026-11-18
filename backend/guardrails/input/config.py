from langchain_groq import ChatGroq
from nemoguardrails.llm.providers import register_chat_provider


register_chat_provider("groq", ChatGroq)
