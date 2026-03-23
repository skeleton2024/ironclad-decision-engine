"""
Ironclad Decision Engine — FastAPI Entry Point
端到端决策分析服务
"""
import uuid
import asyncio
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from api.schemas import (
    DecisionRequest,
    DecisionResponse,
    SessionStatus,
    AtomicTaskSchema,
    MonteCarloResult,
    RiskItem,
)

app = FastAPI(
    title="Ironclad Decision Engine",
    description="对抗式理性决策引擎：递归拆解 + 红队审计 + 蒙特卡洛仿真",
    version="1.0.0",
)

# CORS — 允许前端本地开发
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session store（生产环境换 Redis）
_sessions: dict[str, dict] = {}


# ── 健康检查 ──────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "ok", "service": "ironclad-decision-engine", "version": "1.0.0"}


# ── 决策分析 ──────────────────────────────────────────────────────────────

@app.post("/api/decide", response_model=DecisionResponse)
async def decide(request: DecisionRequest):
    """
    接收决策目标，返回完整分析结果。

    流程：goal → Architect(递归拆解) → Inquisitor(红队审计)
        → Quant Engine(蒙特卡洛仿真) → 推荐决策
    """
    session_id = str(uuid.uuid4())[:8]

    # 检查 API Key 是否为占位符
    if request.api_key and ("<" in request.api_key or "YOUR_" in request.api_key):
        api_key = None  # 使用占位符，降级为模拟模式
    else:
        api_key = request.api_key

    try:
        # 启动异步决策流程
        result = await _run_ironclad(session_id, request, api_key)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def _run_ironclad(session_id: str, request: DecisionRequest, api_key: Optional[str]):
    """
    核心编排流程（LangGraph 编排层 stub，实际接入见 orchestration/）
    当前为顺序执行演示版
    """
    from modules.architect.decompose import recursive_decompose
    from modules.inquisitor import audit
    from shared.quant-engine.sim import monte_carlo

    # ① Architect: 递归拆解
    root_task = recursive_decompose(
        goal=request.goal,
        context=request.context,
        max_depth=request.max_depth,
    )

    # 收集所有原子任务
    atomic_tasks = _flatten_tasks(root_task, [])

    # ② Inquisitor: 红队审计
    risks = audit(atomic_tasks)

    # ③ Quant Engine: 蒙特卡洛仿真
    hours_list = [t.estimated_hours for t in atomic_tasks if t.estimated_hours > 0]
    mc_result = monte_carlo(hours_list, n_simulations=1000)

    # ④ 生成推荐决策
    recommended = _generate_recommendation(request.goal, atomic_tasks, risks, mc_result)

    return DecisionResponse(
        session_id=session_id,
        status="completed",
        goal=request.goal,
        atomic_tasks=[AtomicTaskSchema(**t) for t in atomic_tasks],
        monte_carlo=MonteCarloResult(**mc_result),
        risks=[RiskItem(**r) for r in risks],
        recommended_decision=recommended,
        reasoning=_build_reasoning(atomic_tasks, mc_result, risks),
    )


def _flatten_tasks(task: dict, result: list) -> list:
    """将任务树扁平化为原子任务列表"""
    if not task.get("children"):
        result.append(task)
    else:
        for child in task["children"]:
            _flatten_tasks(child, result)
    return result


def _generate_recommendation(goal: str, tasks: list, risks: list, mc: dict) -> str:
    """生成决策建议（规则版，正式版由 LLM 生成）"""
    high_risk = [r for r in risks if r.get("severity") in ("high", "critical")]
    if high_risk:
        return f"⚠️ 检测到 {len(high_risk)} 项高风险，建议推迟决策，先解决: {high_risk[0]['description']}"
    if mc.get("p90_hours", 0) > 1000:
        return f"⏱️ 项目预计耗时 {mc['p90_hours']:.0f}h，建议分阶段执行"
    return "✅ 方案可行，建议推进"


def _build_reasoning(tasks: list, mc: dict, risks: list) -> str:
    """构建推理说明"""
    total = len(tasks)
    total_hours = mc.get("mean_hours", 0)
    high_risk = len([r for r in risks if r.get("severity") in ("high", "critical")])
    return (
        f"共拆解出 {total} 个原子任务，"
        f"预计总工时 {total_hours:.1f}h（P90={mc.get('p90_hours', 0):.1f}h），"
        f"高风险项 {high_risk} 个。"
        f"建议结合业务优先级筛选执行。"
    )


# ── Session 查询 ──────────────────────────────────────────────────────────

@app.get("/api/session/{session_id}", response_model=SessionStatus)
async def get_session(session_id: str):
    if session_id not in _sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return SessionStatus(**_sessions[session_id])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
