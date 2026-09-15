"""Optional LangGraph wrapper around the shared local pipeline."""
from typing import TypedDict
from langgraph.graph import StateGraph, END
from orchestration.pipeline import analyze_plan

class IroncladState(TypedDict, total=False):
    goal: str
    plan: dict
    max_depth: int
    result: dict

def analyze(state):
    return {"result": analyze_plan(state['goal'], state.get('plan'), state.get('max_depth',3))}

builder = StateGraph(IroncladState)
builder.add_node('analyze', analyze)
builder.set_entry_point('analyze')
builder.add_edge('analyze', END)
ironclad_graph = builder.compile()

def run_ironclad(goal, context=None, max_depth=3, api_key=None, plan=None):
    return ironclad_graph.invoke(dict(goal=goal, plan=plan, max_depth=max_depth))
