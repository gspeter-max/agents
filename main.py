from typing import Annotated

from langgraph import StateGraph, START, RUNTIME
from pydantic import BaseModel


class state_class(BaseModel):
    message: Annotated(str, add_message)


state = StateGraph(state_class, context_variable=temp_class)


def node1(state: StateGraph, runtime: Runtime):
    print(f"runtime config ; {runtime.context.variable_name}")


def condition_edage(state: StateGraph):
    pass


state.add_node("node1", node1)
state.add_edage(START, "node1")
state.add_condition_edage("node1", condition_edage, ["possible_nodes"])

graph = state.build(state_class("values"), context={"key", "value"})
