import React, { useState, useMemo } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function InvestPlatform() {
  const [demand, setDemand] = useState(80);
  const [supplyDifficulty, setSupplyDifficulty] = useState(90);

  // 动态生成未来5年的推演数据
  const chartData = useMemo(() => {
    const data = [];
    const baseValue = 10; 
    for (let year = 2024; year <= 2028; year++) {
      // 机构核心公式：估值 = 需求弹性 / 供给弹性
      const multiplier = (demand / 100) / ((100 - supplyDifficulty + 1) / 100);
      const coreValue = baseValue * Math.pow(1 + (multiplier * 0.1), year - 2024);
      
      data.push({
        year: year.toString(),
        "核心卡脖子标的估值(亿)": parseFloat(coreValue.toFixed(2)),
        "普通蹭概念股(亿)": parseFloat((baseValue * Math.pow(1.05, year - 2024)).toFixed(2))
      });
    }
    return data;
  }, [demand, supplyDifficulty]);

  return (
    <div className="min-h-screen bg-slate-50 p-6 md:p-12 font-sans text-slate-800">
      <div className="max-w-5xl mx-auto space-y-8">
        
        <header className="text-center space-y-3">
          <h1 className="text-4xl font-extrabold text-slate-900">产业链趋势推演终端 Pro</h1>
          <p className="text-slate-500 font-medium">机构级底层逻辑：寻找“需求暴增 × 供给锁死”的卖铲人</p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* 左侧控制台 */}
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 space-y-8">
            <h2 className="text-xl font-bold border-b pb-3">⚙️ 赛道弹性参数调节</h2>
            
            <div className="space-y-4">
              <label className="block text-sm font-bold text-slate-700">
                🚀 新赛道需求爆发度 (如: AI推理量激增)
              </label>
              <input 
                type="range" min="10" max="100" value={demand}
                onChange={(e) => setDemand(e.target.value)}
                className="w-full accent-blue-600 cursor-pointer"
              />
              <div className="text-right text-blue-600 font-bold">{demand}%</div>
            </div>

            <div className="space-y-4">
              <label className="block text-sm font-bold text-slate-700">
                🧱 环节扩产难度 (如: 高端磨床卡脖子)
              </label>
              <input 
                type="range" min="10" max="99" value={supplyDifficulty}
                onChange={(e) => setSupplyDifficulty(e.target.value)}
                className="w-full accent-red-600 cursor-pointer"
              />
              <div className="text-right text-red-600 font-bold">{supplyDifficulty}%</div>
            </div>

            <div className="p-5 bg-slate-900 rounded-xl text-white shadow-inner">
              <div className="text-sm text-slate-400 mb-2">系统智能评级</div>
              <div className="text-2xl font-bold">
                {demand > 70 && supplyDifficulty > 80 ? '🔥🔥 极度稀缺 (重点跟踪)' : 
                 demand > 50 && supplyDifficulty > 50 ? '⭐ 景气向上 (标配观察)' : '⚠️ 陷入红海 (立即规避)'}
              </div>
            </div>
          </div>

          {/* 右侧可视化图表 */}
          <div className="lg:col-span-2 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
            <h2 className="text-xl font-bold mb-6">📈 5年期估值分化推演曲线</h2>
            <div className="h-80 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                  <XAxis dataKey="year" stroke="#94a3b8" tick={{fill: '#64748b'}} />
                  <YAxis stroke="#94a3b8" tick={{fill: '#64748b'}} />
                  <Tooltip contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)' }} />
                  <Legend wrapperStyle={{ paddingTop: '20px' }}/>
                  <Line type="monotone" dataKey="核心卡脖子标的估值(亿)" stroke="#ef4444" strokeWidth={4} activeDot={{ r: 8 }} />
                  <Line type="monotone" dataKey="普通蹭概念股(亿)" stroke="#cbd5e1" strokeWidth={2} strokeDasharray="5 5" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}