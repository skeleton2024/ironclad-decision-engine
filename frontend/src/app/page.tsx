'use client';

import { useState } from 'react';

interface AtomicTask {
  task_id: string;
  description: string;
  estimated_hours: number;
  dependencies: string[];
  risk_level: string;
}

interface MonteCarlo {
  mean_hours: number;
  min_hours: number;
  max_hours: number;
  p10_hours: number;
  p50_hours: number;
  p90_hours: number;
  confidence: number;
  simulation_count: number;
}

interface Risk {
  risk_id: string;
  description: string;
  severity: string;
  mitigation: string;
}

export default function Home() {
  const [goal, setGoal] = useState('');
  const [context, setContext] = useState('');
  const [maxDepth, setMaxDepth] = useState(3);
  const [apiKey, setApiKey] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{
    session_id: string;
    atomic_tasks: AtomicTask[];
    monte_carlo: MonteCarlo;
    risks: Risk[];
    recommended_decision: string;
    reasoning: string;
  } | null>(null);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!goal.trim()) return;
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const res = await fetch('/api/decide', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          goal,
          context: context || null,
          max_depth: maxDepth,
          api_key: apiKey || null,
        }),
      });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      setResult(data);
    } catch (err: any) {
      setError(err.message || '请求失败');
    } finally {
      setLoading(false);
    }
  };

  const severityColor = (s: string) => {
    switch (s) {
      case 'critical': return 'text-white bg-red-600';
      case 'high': return 'text-white bg-orange-500';
      case 'medium': return 'text-white bg-yellow-500';
      default: return 'text-white bg-green-500';
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 text-white p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold mb-2">🛡️ Ironclad Decision Engine</h1>
        <p className="text-slate-400 mb-8">对抗式理性决策引擎 · 递归拆解 × 红队审计 × 蒙特卡洛仿真</p>

        <form onSubmit={handleSubmit} className="space-y-4 mb-8">
          <div>
            <label className="block text-sm text-slate-300 mb-1">决策目标</label>
            <textarea
              className="w-full bg-slate-800 border border-slate-600 rounded p-3 text-white resize-none"
              rows={3}
              placeholder="例如：我应该在北京还是上海设立研发中心？"
              value={goal}
              onChange={e => setGoal(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-sm text-slate-300 mb-1">上下文（可选）</label>
            <textarea
              className="w-full bg-slate-800 border border-slate-600 rounded p-3 text-white resize-none"
              rows={2}
              placeholder="补充背景信息..."
              value={context}
              onChange={e => setContext(e.target.value)}
            />
          </div>
          <div className="flex gap-4">
            <div className="flex-1">
              <label className="block text-sm text-slate-300 mb-1">最大递归深度</label>
              <input
                type="number"
                className="w-full bg-slate-800 border border-slate-600 rounded p-3 text-white"
                min={1} max={10}
                value={maxDepth}
                onChange={e => setMaxDepth(Number(e.target.value))}
              />
            </div>
            <div className="flex-1">
              <label className="block text-sm text-slate-300 mb-1">API Key（可选，占位符也行）</label>
              <input
                type="password"
                className="w-full bg-slate-800 border border-slate-600 rounded p-3 text-white"
                placeholder="sk-... 或 <YOUR_KEY>"
                value={apiKey}
                onChange={e => setApiKey(e.target.value)}
              />
            </div>
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 text-white font-bold py-3 rounded transition"
          >
            {loading ? '⚙️ 分析中...' : '🚀 启动决策分析'}
          </button>
        </form>

        {error && (
          <div className="bg-red-900/50 border border-red-500 rounded p-4 mb-6 text-red-200">
            ❌ {error}
          </div>
        )}

        {result && (
          <div className="space-y-6">
            {/* 推荐决策 */}
            <div className="bg-emerald-900/40 border border-emerald-600 rounded-lg p-6">
              <h2 className="text-lg font-bold text-emerald-300 mb-2">💡 推荐决策</h2>
              <p className="text-xl font-semibold">{result.recommended_decision}</p>
              <p className="text-slate-300 mt-2">{result.reasoning}</p>
              <p className="text-xs text-slate-500 mt-1">Session: {result.session_id}</p>
            </div>

            {/* 蒙特卡洛结果 */}
            <div className="bg-slate-800 border border-slate-600 rounded-lg p-6">
              <h2 className="text-lg font-bold mb-3">📊 蒙特卡洛仿真（n=1000）</h2>
              <div className="grid grid-cols-3 gap-4 text-sm">
                {[
                  ['均值', result.monte_carlo.mean_hours, 'h'],
                  ['P50', result.monte_carlo.p50_hours, 'h'],
                  ['P90', result.monte_carlo.p90_hours, 'h'],
                  ['最小', result.monte_carlo.min_hours, 'h'],
                  ['最大', result.monte_carlo.max_hours, 'h'],
                  ['P10', result.monte_carlo.p10_hours, 'h'],
                ].map(([label, val, unit]) => (
                  <div key={label as string} className="bg-slate-700 rounded p-3 text-center">
                    <div className="text-slate-400 text-xs">{label}</div>
                    <div className="text-xl font-mono text-blue-300">{val.toFixed(1)}{unit}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* 风险项 */}
            {result.risks.length > 0 && (
              <div className="bg-slate-800 border border-slate-600 rounded-lg p-6">
                <h2 className="text-lg font-bold mb-3">🚨 红队审计风险（{result.risks.length} 项）</h2>
                <div className="space-y-2">
                  {result.risks.map((r) => (
                    <div key={r.risk_id} className="flex items-center gap-3 bg-slate-700 rounded p-3">
                      <span className={`text-xs px-2 py-0.5 rounded font-bold ${severityColor(r.severity)}`}>
                        {r.severity.toUpperCase()}
                      </span>
                      <span className="flex-1">{r.description}</span>
                      <span className="text-xs text-slate-400">→ {r.mitigation}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* 原子任务 */}
            <div className="bg-slate-800 border border-slate-600 rounded-lg p-6">
              <h2 className="text-lg font-bold mb-3">
                📋 原子任务（{result.atomic_tasks.length} 个）
              </h2>
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {result.atomic_tasks.map((t) => (
                  <div key={t.task_id} className="flex items-center gap-3 bg-slate-700 rounded p-2 text-sm">
                    <span className="text-xs text-slate-400 font-mono">{t.task_id}</span>
                    <span className="flex-1">{t.description}</span>
                    <span className="text-blue-300">{t.estimated_hours}h</span>
                    <span className={`text-xs px-1.5 rounded ${
                      t.risk_level === 'critical' ? 'bg-red-600' :
                      t.risk_level === 'high' ? 'bg-orange-500' :
                      t.risk_level === 'medium' ? 'bg-yellow-500' : 'bg-green-600'
                    }`}>{t.risk_level}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
