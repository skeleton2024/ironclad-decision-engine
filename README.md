# 🛡️ Ironclad Decision Engine

> 对抗式理性决策引擎：通过递归拆解、红队审计、蒙特卡洛仿真输出可验证的决策方案。

[![CI](https://github.com/skeleton2024/ironclad-decision-engine/actions/workflows/ci.yml/badge.svg)](https://github.com/skeleton2024/ironclad-decision-engine/actions)

## 架构

```
用户输入 Goal
    ↓
┌─────────────────────────────────────────────┐
│  Architect（递归拆解 + PERT 估算 Te）        │
│  te = (O + 4M + P) / 6                      │
└─────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────┐
│  Inquisitor（红队审计）                      │
│  检测高耗时 / 依赖缺失 / 深层嵌套风险        │
└─────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────┐
│  Quant Engine（蒙特卡洛仿真）                │
│  输出 mean / min / max / P10 / P50 / P90    │
└─────────────────────────────────────────────┘
    ↓
  推荐决策 + 完整推理链
```

## 核心模块

| 模块 | 路径 | 说明 |
|------|------|------|
| **Architect** | `modules/architect/` | 递归任务拆解 + PERT 估算 |
| **Inquisitor** | `modules/inquisitor/` | 红队审计，依赖与风险检测 |
| **Quant Engine** | `shared/quant-engine/` | 蒙特卡洛仿真引擎 |
| **API** | `api/` | FastAPI 端点 |
| **Orchestration** | `orchestration/` | LangGraph 工作流编排 |

## 快速启动

### Docker Compose（一键启动）

```bash
cp .env.example .env
# 编辑 .env，填入真实 API Key
docker-compose up
```

- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- 前端: http://localhost:3000

### 本地开发

```bash
# 后端
pip install -r requirements.txt
PYTHONPATH=. uvicorn api.main:app --reload --port 8000

# 前端（新终端）
cd frontend && npm install && npm run dev
```

## 项目里程碑

| 里程碑 | 状态 | 说明 |
|--------|------|------|
| M1: 仓库骨架 + 核心 Schema | ✅ | `core/schemas/atomic_task.py` |
| M2: Architect 递归拆解 + PERT | ✅ | `modules/architect/decompose.py` |
| M3: Inquisitor 红队审计 | ✅ | `modules/inquisitor/` |
| M4: Monte Carlo 引擎 | ✅ | `shared/quant-engine/sim.py` |
| M5: 端到端 Demo | ✅ | FastAPI + Next.js + LangGraph + Docker |

## 测试

```bash
PYTHONPATH=. python3 tests/test_progress.py
```

## API 使用示例

```bash
curl -X POST http://localhost:8000/api/decide \
  -H "Content-Type: application/json" \
  -d '{
    "goal": "我应该在北京还是上海设立研发中心？",
    "context": "我们是AI创业公司，核心团队在北京",
    "max_depth": 3
  }'
```

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `OPENAI_API_KEY` | `<YOUR_OPENAI_API_KEY>` | OpenAI API 密钥 |
| `ANTHROPIC_API_KEY` | `<YOUR_ANTHROPIC_API_KEY>` | Anthropic API 密钥 |
| `LOG_LEVEL` | `INFO` | 日志级别 |

> ⚠️ 部署时请将 `.env.example` 复制为 `.env` 并填入真实密钥

## 技术栈

- **后端**: FastAPI · LangGraph · Pydantic · NumPy
- **前端**: Next.js 14 · Tailwind CSS · TypeScript
- **容器化**: Docker · Docker Compose

## License

MIT
