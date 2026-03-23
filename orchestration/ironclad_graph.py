"""
Ironclad Decision Graph — LangGraph 编排层

流程：
  decide → architect → inquisitor → quant_engine → synthesizer → response

节点说明：
  - architect: 递归拆解任务（Architect）
  - inquisitor: 红队审计风险（Inquisitor）
  - quant_engine: 蒙特卡洛仿真（Quant Engine）
  - synthesizer: 综合输出推荐决策（Synthesizer）
"""
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END


class IroncladState(TypedDict, total=False):
    """共享状态"""
    goal: str
    context: Optional[str]
    max_depth: int
    api_key: Optional[str]

    # Architect 输出
    root_task: dict
    atomic_tasks: list[dict]

    # Inquisitor 输出
    risks: list[dict]

    # Quant Engine 输出
    monte_carlo: dict

    # Synthesizer 输出
    recommended_decision: str
    reasoning: str

    # 元数据
    error: Optional[str]


def architect_node(state: IroncladState) -> IroncladState:
    """任务拆解节点"""
    from modules.architect.decompose import recursive_decompose
    root = recursive_decompose(
        goal=state["goal"],
        context=state.get("context"),
        max_depth=state["max_depth"],
    )
    # 扁平化
    atomic = _flatten(root, [])
    return {**state, "root_task": root, "atomic_tasks": atomic}


def inquisitor_node(state: IroncladState) -> IroncladState:
    """红队审计节点"""
    from modules.inquisitor import audit
    risks = audit(state["atomic_tasks"])
    return {**state, "risks": risks}


def quant_engine_node(state: IroncladState) -> IroncladState:
    """蒙特卡洛仿真节点"""
    from shared.quant-engine.sim import monte_carlo
    hours = [t["estimated_hours"] for t in state["atomic_tasks"] if t.get("estimated_hours", 0) > 0]
    mc = monte_carlo(hours, n_simulations=1000)
    return {**state, "monte_carlo": mc}


def synthesizer_node(state: IroncladState) -> IroncladState:
    """综合决策节点（Stub — 正式版接入 LLM）"""
    from modules.inquisitor import audit
    risks = state.get("risks", [])
    mc = state.get("monte_carlo", {})
    high_risk = [r for r in risks if r.get("severity") in ("high", "critical")]

    if high_risk:
        rec = f"⚠️ {len(high_risk)} 项高风险，建议推迟: {high_risk[0]['description']}"
    elif mc.get("p90_hours", 0) > 1000:
        rec = f"⏱️ 预计 {mc['p90_hours']:.0f}h，建议分阶段执行"
    else:
        rec = "✅ 方案可行，建议推进"

    reasoning = (
        f"共 {len(state['atomic_tasks'])} 个原子任务，"
        f"均值 {mc.get('mean_hours', 0):.1f}h，"
        f"P90={mc.get('p90_hours', 0):.1f}h，"
        f"高风险 {len(high_risk)} 项。"
    )
    return {**state, "recommended_decision": rec, "reasoning": reasoning}


def _flatten(task: dict, result: list) -> list:
    if not task.get("children"):
        result.append(task)
    else:
        for child in task["children"]:
            _flatten(child, result)
    return result


# 构建图
builder = StateGraph(IroncladState)
builder.add_node("architect", architect_node)
builder.add_node("inquisitor", inquisitor_node)
builder.add_node("quant_engine", quant_engine_node)
builder.add_node("synthesizer", synthesizer_node)

builder.set_entry_point("architect")
builder.add_edge("architect", "inquisitor")
builder.add_edge("inquisitor", "quant_engine")
builder.add_edge("quant_engine", "synthesizer")
builder.add_edge("synthesizer", END)

ironclad_graph = builder.compile()


def run_ironclad(goal: str, context: Optional[str] = None, max_depth: int = 3,
                  api_key: Optional[str] = None) -> IroncladState:
    """同步入口"""
    return ironclad_graph.invoke({
        "goal": goal,
        "context": context,
        "max_depth": max_depth,
        "api_key": api_key,
    })
