# Minimal LangGraph Memory Resume Example
# Demonstrates starting a conversation, saving state, and resuming from checkpoint
# Requires: langgraph, langchain, sqlite3

from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import HumanMessage, AIMessage
import sqlite3
import os

# --- State schema ---
class MyState(TypedDict):
    messages: Annotated[List, "add_messages"]

# --- Node functions ---
def user_node(state: MyState) -> MyState:
    # Add a user message
    return {"messages": state["messages"] + [HumanMessage(content="Hello!")]}

def ai_node(state: MyState) -> MyState:
    # Add an AI message
    return {"messages": state["messages"] + [AIMessage(content="Hi, how can I help you?")]}

def joke_node(state: MyState) -> MyState:
    # Add a user and AI message for the joke
    return {"messages": state["messages"] + [HumanMessage(content="Tell me a joke."), AIMessage(content="Why did the chicken cross the road?")]}

# --- Setup checkpointing ---
ckpt_path = "langgraph_test_resume.db"
if os.path.exists(ckpt_path):
    os.remove(ckpt_path)
conn = sqlite3.connect(ckpt_path, check_same_thread=False)
checkpointer = SqliteSaver(conn)

# --- Build the graph ---
builder = StateGraph(MyState)
builder.add_node("user", user_node)
builder.add_node("ai", ai_node)
builder.add_node("joke", joke_node)
builder.set_entry_point("user")
builder.add_edge("user", "ai")
builder.add_edge("ai", END)
builder.add_edge("joke", END)
graph = builder.compile(checkpointer=checkpointer)

# --- Phase 1: Start conversation and checkpoint ---
print("\n--- PHASE 1: Start conversation and checkpoint ---")
thread_id = "thread-1"
config = {"configurable": {"thread_id": thread_id}}
initial_state = {"messages": []}
for event in graph.stream(initial_state, config, stream_mode="values"):
    print(f"Event: {event}")

# --- Show state after phase 1 ---
checkpoint = checkpointer.get(config)
if checkpoint and checkpoint["channel_values"]:
    state_key = list(checkpoint["channel_values"].keys())[0]
    saved_state = checkpoint["channel_values"][state_key]
else:
    saved_state = {"messages": []}
print("\nState after phase 1 (should have 2 messages):")
for msg in saved_state["messages"]:
    print(msg)

# --- PHASE 2: Simulate script exit and resume ---
print("\n--- PHASE 2: Resume from checkpoint and continue conversation ---")
# (In a real scenario, you would reload the checkpointer and graph here)
# We'll just use the same objects for demo
for event in graph.stream(saved_state, config, stream_mode="values", entry_point="joke"):
    print(f"Event: {event}")

# --- Show state after phase 2 ---
checkpoint2 = checkpointer.get(config)
if checkpoint2 and checkpoint2["channel_values"]:
    state_key2 = list(checkpoint2["channel_values"].keys())[0]
    resumed_state = checkpoint2["channel_values"][state_key2]
else:
    resumed_state = {"messages": []}
print("\nState after phase 2 (should have 4 messages):")
for msg in resumed_state["messages"]:
    print(msg) 