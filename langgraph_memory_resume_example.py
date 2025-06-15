# LangGraph Memory Resume Example
# Based on: https://langchain-ai.github.io/langgraph/concepts/memory/#profile

from typing import TypedDict, Annotated, Union

# Simulate the manage_list reducer from the docs

def manage_list(existing: list, updates: Union[list, dict]):
    if isinstance(updates, list):
        return existing + updates
    elif isinstance(updates, dict) and updates.get("type") == "keep":
        return existing[updates["from"]:updates["to"]]
    return existing

class State(TypedDict):
    my_list: Annotated[list, manage_list]

def my_node(state: State):
    # Simulate a node that keeps only the last 2 messages
    return {
        "my_list": {"type": "keep", "from": -2, "to": None}
    }

# Simulate a conversation
conversation = [
    {"role": "user", "content": "Hello!"},
    {"role": "assistant", "content": "Hi, how can I help you?"},
    {"role": "user", "content": "Tell me a joke."},
    {"role": "assistant", "content": "Why did the chicken cross the road?"},
]

# Initial state
state = {"my_list": conversation}
print("Initial state:")
for msg in state["my_list"]:
    print(msg)

# Simulate saving (checkpointing) the state
import pickle
with open("tenx_ipersona/mock_memory.db", "wb") as f:
    pickle.dump(state, f)

# Simulate resuming (loading) the state
with open("tenx_ipersona/mock_memory.db", "rb") as f:
    loaded_state = pickle.load(f)

print("\nLoaded state (before node update):")
for msg in loaded_state["my_list"]:
    print(msg)

# Apply the node logic to trim the conversation
update = my_node(loaded_state)
loaded_state["my_list"] = manage_list(loaded_state["my_list"], update["my_list"])

print("\nState after applying node (keep last 2 messages):")
for msg in loaded_state["my_list"]:
    print(msg) 