import React, { useState, useMemo } from 'react';
// 👇 自动引入你用 Python 引擎跑出来的最新数据罐头
import quantData from './quant_output.json';

// ==========================================
// 1. 底层静态数据底座（基本面与研报数据）
// ==========================================
const marketSnapshot = [
  { name: '上证指数', value: '3,284.21', change: '+0.62%', turnover: '4,680亿', state: '主板防守' },
  { name: '深成指', value: '10,214.37', change: '+0.91%', turnover: '5,940亿', state: '放量修复' },
  { name: '创业板指', value: '2,087.44', change: '+1.18%', turnover: '2,310亿', state: '弹性领涨' },
  { name: '科创50', value: '867.12', change: '+1.53%', turnover: '846亿', state: '硬科技爆发' },
];

const initialSectors = [
  {
    id: 'robot',
    name: '人形机器人量产',
    score: 94,
    heat: 95,
    fund: '+68.4亿',
    trend: '跨越拐点',
    color: 'text-pink-400',
    bg: 'bg-pink-500/10',
    border: 'border-pink-500/20',
    stocks: [
      { code: '688017.SH', name: '绿的谐波', role: '谐波减速器', core: 98, pe: '85x', revenue: '+45%', margin: '42.1%' },
      { code: '002472.SZ', name: '双环传动', role: '新能源与机器人齿轮', core: 95, pe: '30x', revenue: '+22%', margin: '22.5%' },
      { code: '603728.SH', name: '鸣志电器', role: '空心杯电机', core: 92, pe: '70x', revenue: '+15%', margin: '38.2%' },
      { code: '603009.SH', name: '北特科技', role: '行星滚柱丝杠', core: 88, pe: '65x', revenue: '+30%', margin: '18.4%' }
    ]
  },
  {
    id: 'ai',
    name: 'AI算力底座',
    score: 98,
    heat: 99,
    fund: '+125.6亿',
    trend: '业绩主升浪',
    color: 'text-blue-400',
    bg: 'bg-blue-500/10',
    border: 'border-blue-500/20',
    stocks: [
      { code: '300308.SZ', name: '中际旭创', role: '800G/1.6T光模块', core: 99, pe: '45x', revenue: '+85%', margin: '33.5%' },
      { code: '601138.SH', name: '工业富联', role: 'AI服务器与液冷', core: 90, pe: '20x', revenue: '+35%', margin: '8.5%' },
      { code: '688041.SH', name: '海光信息', role: '国产算力芯片', core: 95, pe: '60x', revenue: '+55%', margin: '58.2%' }
    ]
  },
  {
    id: 'solid_state',
    name: '固态电池与低空',
    score: 88,
    heat: 82,
    fund: '+32.1亿',
    trend: '概念验证期',
    color: 'text-emerald-400',
    bg: 'bg-emerald-500/10',
    border: 'border-emerald-500/20',
    stocks: [
      { code: '603659.SH', name: '璞泰来', role: '固态电池负极材料', core: 85, pe: '25x', revenue: '+12%', margin: '35.1%' },
      { code: '002025.SZ', name: '航天电器', role: '航空航天连接器', core: 88, pe: '35x', revenue: '+18%', margin: '32.4%' }
    ]
  }
];

// ==========================================
// 2. 主组件渲染
// ==========================================
export default function App() {
  const [activeTab, setActiveTab] = useState('robot');
  
  // α-β 沙盘状态管理
  const [demandBeta, setDemandBeta] = useState(80);
  const [supplyAlpha, setSupplyAlpha] = useState(90);

  // 核心逻辑：数据缝合引擎 (将 Python 数据注入静态面板)
  const mergedSectors = useMemo(() => {
    // 确保 quantData 是数组，防止 JSON 格式错误导致崩溃
    const safeQuantData = Array.isArray(quantData) ? quantData : [];

    return initialSectors.map(sector => ({
      ...sector,
      stocks: sector.stocks.map(stock => {
        // 去罐头里找这只股票
        const liveData = safeQuantData.find(q => q.stock_name === stock.name);
        
        if (liveData) {
          return {
            ...stock,
            price: liveData.current_price,
            // 处理涨跌幅格式
            change: liveData.change_pct > 0 ? `+${liveData.change_pct}%` : `${liveData.change_pct}%`,
            isPositive: liveData.change_pct > 0,
            quantAction: liveData.action || '智能评级中'
          };
        }
        // 如果没在 Python 列表里找到，用兜底数据
        return { 
          ...stock, 
          price: '模拟数据', 
          change: '--', 
          isPositive: true,
          quantAction: '未纳入战略池' 
        };
      })
    }));
  }, []);

  const activeSectorData = mergedSectors.find(s => s.id === activeTab);

  // 动态计算核心受益评分
  const resonanceScore = useMemo(() => {
    return Math.min(100, Math.round((demandBeta * 1.5) / (101 - supplyAlpha) * 10));
  }, [demandBeta, supplyAlpha]);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-200 p-6 font-sans">
      <div className="max-w-6xl mx-auto space-y-6">
        
        {/* 顶部标题区 */}
        <header className="flex items-center justify-between border-b border-slate-800 pb-4">
          <div>
            <h1 className="text-3xl font-bold text-white tracking-tight flex items-center gap-3">
              🦅 舟哥推演：机构级产业链沙盘 <span className="text-sm font-normal bg-indigo-500/20 text-indigo-400 px-2 py-1 rounded">V2.0 量化融合版</span>
            </h1>
            <p className="text-slate-400 mt-2 text-sm">Python 引擎实时数据接入 | α-β 共振模型 | 资产防守配置</p>
          </div>
        </header>

        {/* 市场环境快照 */}
        <div className="grid grid-cols-4 gap-4">
          {marketSnapshot.map((item, idx) => (
            <div key={idx} className="bg-slate-900 border border-slate-800 p-4 rounded-xl shadow-lg">
              <div className="text-slate-400 text-xs mb-1">{item.name}</div>
              <div className="flex items-end justify-between">
                <div className="text-xl font-semibold text-white">{item.value}</div>
                <div className="text-red-500 text-sm font-medium">{item.change}</div>
              </div>
              <div className="mt-3 flex items-center justify-between text-xs">
                <span className="text-slate-500">成交: {item.turnover}</span>
                <span className="bg-slate-800 text-slate-300 px-2 py-0.5 rounded">{item.state}</span>
              </div>
            </div>
          ))}
        </div>

        {/* 核心功能区：左右分栏 */}
        <div className="grid grid-cols-3 gap-6">
          
          {/* 左侧：α-β 推演沙盘 */}
          <div className="col-span-1 bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
            <h2 className="text-lg font-bold text-white mb-4 border-b border-slate-800 pb-2">🧠 α-β 共振推演模型</h2>
            
            <div className="space-y-6">
              <div>
                <label className="flex justify-between text-sm text-slate-400 mb-2">
                  <span>需求弹性 (β周期)</span>
                  <span className="text-blue-400 font-bold">{demandBeta}%</span>
                </label>
                <input 
                  type="range" min="10" max="100" value={demandBeta} 
                  onChange={(e) => setDemandBeta(e.target.value)}
                  className="w-full accent-blue-500" 
                />
                <p className="text-xs text-slate-500 mt-1">评估行业爆发红利 (如: AI需求暴增)</p>
              </div>

              <div>
                <label className="flex justify-between text-sm text-slate-400 mb-2">
                  <span>供给难度 (α周期)</span>
                  <span className="text-pink-400 font-bold">{supplyAlpha}%</span>
                </label>
                <input 
                  type="range" min="10" max="99" value={supplyAlpha} 
                  onChange={(e) => setSupplyAlpha(e.target.value)}
                  className="w-full accent-pink-500" 
                />
                <p className="text-xs text-slate-500 mt-1">评估卡脖子壁垒 (如: 产能极难扩张)</p>
              </div>

              <div className="pt-6 border-t border-slate-800">
                <div className="text-center">
                  <div className="text-sm text-slate-400 mb-1">核心受益爆发指数</div>
                  <div className={`text-5xl font-black ${resonanceScore > 80 ? 'text-red-500' : 'text-yellow-500'}`}>
                    {resonanceScore}
                  </div>
                  <p className="text-xs text-slate-500 mt-2">公式: 核心受益 = 需求弹性 ÷ 供给弹性</p>
                </div>
              </div>
            </div>
          </div>

          {/* 右侧：量化标的库 */}
          <div className="col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
            {/* 赛道切换 Tabs */}
            <div className="flex space-x-2 mb-6">
              {mergedSectors.map(sector => (
                <button
                  key={sector.id}
                  onClick={() => setActiveTab(sector.id)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                    activeTab === sector.id 
                    ? `${sector.bg} ${sector.color} border ${sector.border}` 
                    : 'bg-slate-800/50 text-slate-400 hover:bg-slate-800 border border-transparent'
                  }`}
                >
                  {sector.name}
                </button>
              ))}
            </div>

            {/* 标的表格 */}
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="text-slate-500 border-b border-slate-800">
                    <th className="pb-3 font-medium">核心标的</th>
                    <th className="pb-3 font-medium">卡脖子环节</th>
                    <th className="pb-3 font-medium">最新价</th>
                    <th className="pb-3 font-medium">今日涨幅</th>
                    <th className="pb-3 font-medium">Python 量化评级</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/50">
                  {activeSectorData.stocks.map((stock, idx) => (
                    <tr key={idx} className="hover:bg-slate-800/30 transition-colors">
                      <td className="py-4">
                        <div className="font-bold text-slate-200">{stock.name}</div>
                        <div className="text-xs text-slate-500">{stock.code}</div>
                      </td>
                      <td className="py-4 text-slate-300">{stock.role}</td>
                      <td className="py-4 font-mono text-white">{stock.price}</td>
                      <td className={`py-4 font-mono font-medium ${stock.isPositive ? 'text-red-500' : 'text-green-500'}`}>
                        {stock.change}
                      </td>
                      <td className="py-4">
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          stock.quantAction.includes('核心重仓') ? 'bg-red-500/20 text-red-400' : 
                          stock.quantAction.includes('谨慎观察') ? 'bg-yellow-500/20 text-yellow-400' :
                          'bg-slate-800 text-slate-400'
                        }`}>
                          {stock.quantAction}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* 底部：稳健现金流防守堡垒 */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
          <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
            🛡️ 资产防守堡垒 <span className="text-xs font-normal text-slate-400">大资金的底线：切断本金归零风险</span>
          </h2>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-slate-950 border border-slate-800 p-4 rounded-lg">
              <div className="flex justify-between items-center mb-2">
                <h3 className="font-semibold text-emerald-400">招银/建信 固收+理财</h3>
                <span className="bg-emerald-500/20 text-emerald-400 text-xs px-2 py-1 rounded">预期年化 3.0%-3.5%</span>
              </div>
              <p className="text-sm text-slate-400 leading-relaxed">
                <span className="text-slate-200">资金去向：</span> 80%打底高评级信用债，20%追求弹性打新。容量极大，适合一笔买入大额本金作为“现金防守垫”，手机银行直购。
              </p>
            </div>
            <div className="bg-slate-950 border border-slate-800 p-4 rounded-lg">
              <div className="flex justify-between items-center mb-2">
                <h3 className="font-semibold text-blue-400">短债公募基金</h3>
                <span className="bg-blue-500/20 text-blue-400 text-xs px-2 py-1 rounded">预期年化 2.5%-3.0%</span>
              </div>
              <p className="text-sm text-slate-400 leading-relaxed">
                <span className="text-slate-200">资金去向：</span> 纯粹持有久期小于1年的短期债券。随存随取流动性极佳，机构资金做避险的终极停泊处，用来平替活期存款。
              </p>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}