"""
API Request/Response Schemas (Pydantic)
"""
from typing import Optional
from pydantic import BaseModel, Field


# ── Decision ──────────────────────────────────────────────────────────────

class DecisionRequest(BaseModel):
    """决策分析请求"""
    goal: str = Field(..., description="用户目标/问题描述")
    context: Optional[str] = Field(None, description="额外上下文信息")
    model_name: Optional[str] = Field("gpt-4o-mini", description="调用的LLM模型")
    api_key: Optional[str] = Field(None, description="LLM API Key（支持占位符）")
    max_depth: Optional[int] = Field(3, ge=1, le=10, description="最大递归深度")

    class Config:
        json_schema_extra = {
            "example": {
                "goal": "我应该在北京还是上海设立研发中心？",
                "context": "我们是AI创业公司，核心团队在北京",
                "model_name": "gpt-4o-mini",
                "max_depth": 3
            }
        }


class AtomicTaskSchema(BaseModel):
    """原子任务 schema"""
    task_id: str
    description: str
    estimated_hours: float
    dependencies: list[str] = Field(default_factory=list)
    risk_level: str = "medium"  # low / medium / high / critical
    assignee: Optional[str] = None


class MonteCarloResult(BaseModel):
    """蒙特卡洛仿真结果"""
    mean_hours: float
    min_hours: float
    max_hours: float
    p10_hours: float
    p50_hours: float
    p90_hours: float
    confidence: float = Field(..., description="置信度 0~1")
    simulation_count: int


class RiskItem(BaseModel):
    """风险项"""
    risk_id: str
    description: str
    severity: str  # low / medium / high / critical
    mitigation: str


class DecisionResponse(BaseModel):
    """决策分析完整响应"""
    session_id: str
    status: str  # processing / completed / failed
    goal: str
    atomic_tasks: list[AtomicTaskSchema]
    monte_carlo: Optional[MonteCarloResult] = None
    risks: list[RiskItem] = Field(default_factory=list)
    recommended_decision: Optional[str] = None
    reasoning: Optional[str] = None
    error: Optional[str] = None


# ── Session ────────────────────────────────────────────────────────────────

class SessionStatus(BaseModel):
    session_id: str
    status: str
    created_at: str
    updated_at: str
