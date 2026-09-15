"""Local plan-analysis API."""
from datetime import datetime, timezone
from uuid import uuid4
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from api.schemas import DecisionRequest, DecisionResponse, SessionStatus
from orchestration.pipeline import analyze_plan

app = FastAPI(title="Ironclad Decision Engine", version="0.2.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
                   allow_methods=["GET", "POST"], allow_headers=["Content-Type"])
_sessions = {}

@app.get("/health")
async def health():
    return {"status": "ok", "service": "ironclad-decision-engine"}

@app.post("/api/decide", response_model=DecisionResponse)
async def decide(request: DecisionRequest):
    try:
        result = analyze_plan(request.goal, request.plan, request.max_depth or 3)
    except (ValueError, KeyError, TypeError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    session_id = uuid4().hex[:12]
    now = datetime.now(timezone.utc).isoformat()
    _sessions[session_id] = dict(session_id=session_id, status="completed", created_at=now, updated_at=now)
    return DecisionResponse(session_id=session_id, status="completed", goal=request.goal, **result)

@app.get("/api/session/{session_id}", response_model=SessionStatus)
async def get_session(session_id: str):
    if session_id not in _sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return _sessions[session_id]
