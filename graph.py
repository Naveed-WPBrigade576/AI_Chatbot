from typing import TypedDict, Annotated

from langgraph.graph import StateGraph, END
from langgraph.graph.message import AnyMessage, add_messages
from langchain_groq import ChatGroq

from dotenv import load_dotenv
load_dotenv()

# Instantiate the LLM; it will read GROQ_API_KEY from environment
llm = ChatGroq(model="groq/compound-mini")


class ChatState(TypedDict):
    # Accumulates message history; add_messages appends returned messages
    messages: Annotated[list[AnyMessage], add_messages]


def chatbot_node(state: ChatState) -> ChatState:
    messages = state.get("messages", [])
    # Invoke the model with the conversation so far
    response = llm.invoke(messages)
    # Return only new messages; aggregator will append
    return {"messages": [response]}


def create_chat_graph():
    builder = StateGraph(ChatState)
    builder.add_node("chat", chatbot_node)
    builder.set_entry_point("chat")
    builder.add_edge("chat", END)
    return builder.compile()
