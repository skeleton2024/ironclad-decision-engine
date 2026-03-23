# PRD: Ironclad-Decision-Engine

## 1. Overview
A deterministic, adversarial rational decision engine designed to test and validate strategic plans through recursive task decomposition, adversarial audit, and Monte Carlo risk simulations.

## 2. Objectives
- Provide a rigorous framework for decision planning with quantifiable metrics.
- Enable modular development with clear interfaces across Architect, Inquisitor, and Quant Engine.
- Support real-world data verification via integrated search APIs.

## 3. Key Features
- Recursive task decomposition using PERT weighted averages: Te = (O + 4M + P) / 6
- Red Team Inquisitor to challenge plans with counter-evidence and failure modes
- Monte Carlo simulations to estimate project success probability based on task risk
- Modular API surface for extensibility
- Visual dashboard for topology and risk visualization (front-end stack TBD)

## 4. Scope
- In scope: core engine (Architect, Inquisitor, Quant Engine), API endpoints, and data schemas.
- Out of scope: production-grade UI polish, external audit certifications, and full-scale data provenance systems for now.

## 5. Tech Stack (Proposed)
- Frontend: Next.js 14 (App Router), Tailwind CSS, Lucide React, Recharts
- Backend: FastAPI (Python)
- Orchestration: LangGraph
- Search/API: Tavily or Perplexity
- Simulation: NumPy/SciPy
- Data Modeling: Pydantic / TypeScript types

## 6. API Surface (Initial)
- POST /core/plan: Create a Plan with atomic tasks
- GET /core/plan/{id}: Retrieve plan state
- POST /modules/architect/decompose: Trigger recursive decomposition
- POST /modules/inquisitor/audit: Run adversarial audit
- POST /shared/quant-engine/simulate: Run Monte Carlo simulations

## 7. Data Models (Core)
- AtomicTask
- RiskProfile
- FeasibilityReport
- Plan (root schema)

## 8. Milestones
- M1: Scaffold repository structure and core schemas
- M2: Implement Architect recursion and PERT
- M3: Implement Inquisitor red-teaming flow
- M4: Implement Monte Carlo engine and basic API
- M5: End-to-end demo with sample data

## 9. Risks & Mitigations
- Misinterpretation of metrics: add validation and tests
- Data quality issues: integrate external verification with fallback

## 10. Assumptions
- Data sources are accessible; API keys managed securely
- Team adopts the same formalism for tasks

## 11. Deliverables
- Code scaffolding in workspace/ebrain skill
- Tests, docs, and basic demo data
