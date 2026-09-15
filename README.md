# Ironclad Decision Engine

**计划拆解、风险规则与工时模拟原型**

我把任务树、依赖和三点估时组织成一条计算流程：递归拆解，检查高耗时与缺失依赖，再模拟总工时分布。FastAPI 返回结构化任务、风险和计算摘要，Next.js 提供交互入口。

## 运行

Python 3.10–3.12，建议独立虚拟环境。

~~~bash
python -m pip install -r requirements.txt
python tests/test_progress.py
python -m pip install pytest
python -m pytest tests/test_api_contract.py -q
python -m uvicorn api.main:app --port 8000
~~~

打开 http://localhost:8000/docs ，向 POST /api/decide 输入目标。省略 plan 时使用明确标记的内置示例估时；提供 plan 可分析自己的任务树。接口示例见 [examples/request.json](examples/request.json)。

前端在独立终端执行：

~~~bash
cd frontend
npm install
npm run dev
~~~

访问 http://localhost:3000 。本地计算流程无需 API Key。

## 计算约定

- 所有估时统一为小时。
- PERT 展示值为 (O + 4M + P) / 6。
- 模拟独立采样三角分布 Triangular(O, P, M)，其均值为 (O + M + P) / 3，与 PERT 展示值分别计算。
- 各任务工时相加得到串行总工时；依赖关系用于规则检查。
- P10/P50/P90 是模拟分位数，需结合输入估时理解。

## 结构与本次修复

- modules/architect/：递归拆解并保留 O/M/P，避免模拟退化为固定值。
- modules/inquisitor/：高耗时、缺失依赖和深层嵌套检查。
- shared/quant-engine/sim.py：独立随机数生成器、输入约束、工时分布。
- orchestration/pipeline.py：API 共用的本地计算流程。
- 修复了 API 导入、字段衔接和会话查询；示例估时单独标记。
- orchestration/ironclad_graph.py 提供可选 LangGraph 包装。

## 许可

沿用项目原有 MIT 声明，见 [LICENSE](LICENSE)。
