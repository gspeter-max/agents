"""from langchain.agents import create_agent
from langchain.agents.middleware import (
    HumanInTheLoopMiddleware,
    InterruptOnConfig,
)
from langchain_core.tools import tool
from langchain.messages import SystemMessage
from langgraph.checkpoint.memory import (
    InMemorySaver,
)


@tool
def write_tool():
    pass


@tool
def read_tool():
    pass


tools = [write_tool, read_tool]
agents = create_agent(
    model="gpt-4o",
    tools=tools,
    system_prompt=SystemMessage(
        content="here the systemPrompt"
    ),
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                "write_tool": True,
                "read_tool": InterruptOnConfig(
                    allowed_decisions=[
                        "approve",
                        "reject",
                    ]
                ),
            },
            description_prefix="here the description_prefix foor this tool",
        )
    ],
    checkpointer=InMemorySaver(),
)"""

from langgraph.graph import (
    StateGraph,
    START,
    END,
)
from langgraph.graph.state import (
    RetryPolicy,
    RunnableConfig,
)
from langgraph.runtime import Runtime
from langgraph.types import (
    Interrupt,
    Overwrite,
    Command,
)

from typing_extensions import (
    Annotated,
    TypedDict,
)
import operator
from pprint import pprint

from langgraph.checkpoint.memory import (
    InMemorySaver,
)
from pydantic import BaseModel


class context_class(BaseModel):
    message: str


class State(TypedDict):
    messages: Annotated[list, operator.add]


def add_message(state: State):
    return {"messages": ["first message"]}


def add_second_message(
    state: State,
    runtime: Runtime[context_class],
):
    interrupt_value = Interrupt(
        "hello whats oon your mind"
    )
    pprint(
        f"here the value : {interrupt_value}"
    )
    return {"messages": ["second message"]}


def replace_messages(
    state: State,
    runtime: Runtime[context_class],
):
    # Bypass the reducer and replace the entire messages list
    value = runtime
    pprint(f"values : {value}")
    return {
        "messages": Overwrite(
            ["third_message_here"]
        )
    }


# means they also added and also added ine edges
builder = StateGraph(
    State, context_schema=context_class
)
builder.add_node(
    "add_message",
    add_message,
    retry_policy=RetryPolicy(),
)
builder.add_sequence(
    nodes=[
        add_second_message,
        replace_messages,
    ]
)
builder.add_edge(START, "add_message")
builder.add_edge(
    "add_message", "add_second_message"
)
graph = builder.compile(
    checkpointer=InMemorySaver()
)
config: RunnableConfig = {
    "configurable": {"thread_id": "One"}
}
result = graph.invoke(
    {"messages": ["initial"]},
    context=context_class(message="env"),
    config=config,
)
print(result)
result = graph.invoke(
    Command(resume="here the things"),
    config=config,
)
print(f"second : result : {result}")
print(result)
