import React, { useEffect, useMemo, useState } from 'react';

// 模拟大盘氛围（因各大指数代码特殊，此处暂留静态做氛围展示）
const marketSnapshot = [
  { name: '上证指数', value: '3,284.21', change: '+0.62%', turnover: '4,680亿', state: '主板防守' },
  { name: '深成指', value: '10,214.37', change: '+0.91%', turnover: '5,940亿', state: '放量修复' },
  { name: '创业板指', value: '2,087.44', change: '+1.18%', turnover: '2,310亿', state: '弹性领涨' },
  { name: '科创50', value: '867.12', change: '+1.53%', turnover: '846亿', state: '硬科技爆发' },
];

// 三大核心赛道硬核数据库
const sectors = [
  {
    id: 'robot',
    name: '人形机器人量产',
    score: 94,
    heat: 95,
    fund: '+68.4亿',
    trend: '跨越拐点',
    color: '#f472b6',
    stocks: [
      { code: '688017.SH', name: '绿的谐波', role: '谐波减速器', price: 112.06, change: '+4.82%', core: 98, proof: 95, valuation: 60, trend: 92, capital: 88, mcap: '约300亿', pe: '85x', revenue: '+45%', margin: '42.1%', logic: '占据全球约15%份额，打破海外垄断，财报已明确兑现具身智能利润。' },
      { code: '002472.SZ', name: '双环传动', role: 'RV减速器/齿轮', price: 28.45, change: '+2.18%', core: 92, proof: 98, valuation: 75, trend: 85, capital: 82, mcap: '约240亿', pe: '28x', revenue: '+22%', margin: '22.4%', logic: '新能源汽车齿轮业务是印钞机，明牌切入海外人形机器人，主板完美替代。' },
      { code: '603009.SH', name: '北特科技', role: '行星滚柱丝杠', price: 18.65, change: '+6.11%', core: 95, proof: 80, valuation: 65, trend: 88, capital: 85, mcap: '约67亿', pe: '55x', revenue: '+18%', margin: '19.8%', logic: '主板“含螺量”极高。利用汽车底盘高精长轴工艺降维打击，送样进度领先。' },
      { code: '603662.SH', name: '柯力传感', role: '六维力传感器', price: 38.95, change: '+1.51%', core: 90, proof: 85, valuation: 64, trend: 71, capital: 70, mcap: '约120亿', pe: '41x', revenue: '+16%', margin: '38.6%', logic: '机器人的触觉神经，已向超70家整机厂送样测试，传统物联网提供稳定现金流。' },
    ],
  },
  {
    id: 'ai-hardware',
    name: 'AI算力底座与端侧',
    score: 92,
    heat: 88,
    fund: '+86.4亿',
    trend: '主升浪',
    color: '#38bdf8',
    stocks: [
      { code: '300308.SZ', name: '中际旭创', role: '800G/1.6T光模块', price: 178.62, change: '+3.76%', core: 99, proof: 98, valuation: 65, trend: 94, capital: 90, mcap: '约1800亿', pe: '38x', revenue: '+122%', margin: '31.8%', logic: '算力集群的数据高速公路，绑定北美大厂，业绩兑现最残暴的卖铲人。' },
      { code: '601138.SH', name: '工业富联', role: 'AI服务器/液冷', price: 25.12, change: '+1.15%', core: 85, proof: 95, valuation: 80, trend: 75, capital: 88, mcap: '约5000亿', pe: '15x', revenue: '+25%', margin: '8.2%', logic: '掌握核心液冷技术，承接海量代工订单。智能手机和网络设备提供千亿安全垫。' },
      { code: '000657.SZ', name: '中钨高新', role: '高阶PCB微钻耗材', price: 11.24, change: '+2.44%', core: 88, proof: 82, valuation: 72, trend: 78, capital: 75, mcap: '约150亿', pe: '35x', revenue: '+12%', margin: '18.5%', logic: '打孔耗材极度消耗，且手握优质大钨矿资产注入预期，极易形成戴维斯双击。' },
      { code: '688041.SH', name: '海光信息', role: '国产算力芯片', price: 82.50, change: '+1.88%', core: 95, proof: 88, valuation: 55, trend: 85, capital: 80, mcap: '约1900亿', pe: '62x', revenue: '+45%', margin: '58.2%', logic: '国内极少数量产X86架构的企业。政企信创和超算中心集采大单提供极强支撑。' },
    ],
  },
  {
    id: 'solid-low',
    name: '固态电池与低空',
    score: 85,
    heat: 82,
    fund: '+45.8亿',
    trend: '共振起爆',
    color: '#a78bfa',
    stocks: [
      { code: '603659.SH', name: '璞泰来', role: '硅基负极升级', price: 21.45, change: '+1.42%', core: 90, proof: 85, valuation: 75, trend: 70, capital: 65, mcap: '约450亿', pe: '22x', revenue: '+15%', margin: '32.5%', logic: '配合固态电解质，传统石墨负极必须升级硅基。全球负极巨头，主业极其赚钱。' },
      { code: '002085.SZ', name: '万丰奥威', role: '碳纤维骨架/eVTOL', price: 18.37, change: '+2.94%', core: 88, proof: 78, valuation: 65, trend: 82, capital: 78, mcap: '约300亿', pe: '38x', revenue: '+12%', margin: '19.6%', logic: '全球汽车轮毂龙头，旗下钻石飞机具备顶尖航空碳纤维量产能力。' },
      { code: '688631.SH', name: '莱斯信息', role: '低空空管系统', price: 79.48, change: '+3.69%', core: 92, proof: 72, valuation: 54, trend: 85, capital: 70, mcap: '约100亿', pe: '58x', revenue: '+22%', margin: '36.5%', logic: '未动车先修路，中国电科旗下国家队主导民航空管，护城河深不见底。' },
    ],
  },
];

const tabs = [
  { id: 'overview', label: '市场总览' },
  { id: 'alpha-beta', label: 'α-β周期推演' },
  { id: 'stock', label: '个股深度' },
  { id: 'plan', label: '实战交易计划' },
];

function allStocks() {
  return sectors.flatMap((sector) =>
    sector.stocks.map((stock) => ({ ...stock, sectorId: sector.id, sectorName: sector.name, sectorColor: sector.color }))
  );
}

function getCompositeScore(stock) {
  return Math.round(stock.core * 0.28 + stock.proof * 0.24 + stock.trend * 0.2 + stock.capital * 0.16 + stock.valuation * 0.12);
}

function MiniBar({ value, color = '#38bdf8' }) {
  return (
    <div className="mini-bar">
      <span style={{ width: `${Math.max(3, Math.min(100, value))}%`, background: color }} />
    </div>
  );
}

function ScoreBadge({ score }) {
  const label = score >= 85 ? '核心卡脖子' : score >= 75 ? '重点跟踪' : score >= 65 ? '观察期权' : '边缘化';
  return <span className={`score-badge ${score >= 85 ? 'hot' : score >= 75 ? 'warm' : ''}`}>{score} · {label}</span>;
}

export default function App() {
  const stocks = useMemo(() => allStocks(), []);
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedSectorId, setSelectedSectorId] = useState('robot');
  const [selectedStockCode, setSelectedStockCode] = useState('688017.SH');
  
  // 实时行情状态
  const [realTimeData, setRealTimeData] = useState({});

  // 交易计划计算器状态
  const [plan, setPlan] = useState({ capital: 200000, riskPct: 1, entry: 50, stop: 47.5, target: 58 });

  // α-β 沙盘状态
  const [betaScore, setBetaScore] = useState(85);
  const [alphaScore, setAlphaScore] = useState(80);
  const alphaBetaResult = ((betaScore * alphaScore) / 100).toFixed(1);

  const selectedSector = sectors.find((sector) => sector.id === selectedSectorId) || sectors[0];
  const selectedStock = stocks.find((stock) => stock.code === selectedStockCode) || stocks[0];

  // 交易计划计算逻辑
  const riskAmount = plan.capital * (plan.riskPct / 100);
  const singleRisk = Math.max(0, plan.entry - plan.stop);
  const shares = singleRisk > 0 ? Math.floor(riskAmount / singleRisk / 100) * 100 : 0;
  const position = shares * plan.entry;
  const rewardRisk = singleRisk > 0 ? ((plan.target - plan.entry) / singleRisk).toFixed(2) : '0.00';

  // 核心：腾讯财经 API 轮询引擎 (动态注入 script 绕过跨域)
  useEffect(() => {
    const fetchPrices = () => {
      // 转换代码格式：688017.SH -> sh688017, 002472.SZ -> sz002472
      const queryCodes = stocks.map(s => {
        const [num, market] = s.code.split('.');
        return market.toLowerCase() + num;
      }).join(',');

      const scriptId = 'tencent-finance-api';
      const oldScript = document.getElementById(scriptId);
      if (oldScript) document.body.removeChild(oldScript);

      const script = document.createElement('script');
      script.id = scriptId;
      script.src = `https://qt.gtimg.cn/q=${queryCodes}`;
      
      script.onload = () => {
        const newData = {};
        stocks.forEach(s => {
          const [num, market] = s.code.split('.');
          const qCode = market.toLowerCase() + num;
          const res = window[`v_${qCode}`];
          if (res) {
            const parts = res.split('~');
            if (parts.length > 32) {
              const currentPrice = parseFloat(parts[3]);
              const changePercent = parseFloat(parts[32]);
              newData[s.code] = {
                price: currentPrice,
                change: `${changePercent > 0 ? '+' : ''}${changePercent}%`,
                isUp: changePercent > 0
              };
            }
          }
        });
        setRealTimeData(newData);
      };
      document.body.appendChild(script);
    };

    fetchPrices(); // 初始拉取
    const interval = setInterval(fetchPrices, 10000); // 每 10 秒刷新一次实时数据
    return () => clearInterval(interval);
  }, [stocks]);

  const selectStock = (stock) => {
    setSelectedStockCode(stock.code);
    setSelectedSectorId(stock.sectorId);
    // 自动将当前价格填入交易计划的买入价
    const currentPrice = realTimeData[stock.code]?.price || stock.price;
    setPlan(prev => ({ ...prev, entry: currentPrice }));
    setActiveTab('stock');
  };

  return (
    <div className="terminal">
      <style>{styles}</style>
      <header className="topbar">
        <div>
          <div className="eyebrow">A股产业链趋势研究终端 V2.1</div>
          <h1>核心受益量化决策工作台 <span className="live-badge">● 实时行情接通</span></h1>
        </div>
        <nav className="tabs">
          {tabs.map((tab) => (
            <button key={tab.id} className={activeTab === tab.id ? 'active' : ''} onClick={() => setActiveTab(tab.id)}>
              {tab.label}
            </button>
          ))}
        </nav>
      </header>

      <main>
        {activeTab === 'overview' && (
           <section className="grid overview-grid">
            <div className="panel wide">
              <div className="panel-head">
                <h2>主线强度排行</h2>
                <span>按资金、趋势、验证、核心环节综合排序</span>
              </div>
              <div className="sector-rank">
                {[...sectors].sort((a, b) => b.score - a.score).map((sector) => (
                  <button key={sector.id} className={`rank-row ${selectedSectorId === sector.id ? 'selected' : ''}`} onClick={() => setSelectedSectorId(sector.id)}>
                    <strong>{sector.name}</strong>
                    <MiniBar value={sector.score} color={sector.color} />
                    <span>{sector.score}</span>
                    <small>{sector.trend}</small>
                  </button>
                ))}
              </div>
            </div>
            <div className="panel">
              <div className="panel-head">
                <h2>核心候选池 (实时)</h2>
                <span>机构视角先看验证，再看价格</span>
              </div>
              <StockTable stocks={stocks.slice().sort((a, b) => getCompositeScore(b) - getCompositeScore(a)).slice(0, 6)} realTimeData={realTimeData} onSelect={selectStock} compact />
            </div>
          </section>
        )}

        {activeTab === 'alpha-beta' && (
          <section className="grid alpha-beta-grid">
            <div className="panel span-2">
              <div className="panel-head">
                <h2>α-β 周期共振推演沙盘</h2>
                <span>机构价值流向追踪法</span>
              </div>
              <div className="formula-box">
                <p>机构量化核心公式：</p>
                <strong>核心受益估值 = 需求弹性（暴增 β） ÷ 供给弹性（极难 α）</strong>
              </div>
              <div className="slider-group">
                <label>
                  <span>β 周期：该赛道的需求爆发度 / 渗透率 (0-100)</span>
                  <input type="range" min="1" max="100" value={betaScore} onChange={(e) => setBetaScore(e.target.value)} />
                  <b>{betaScore}</b>
                </label>
                <p className="logic-text">如：小龙虾爆火带来的算力租赁需求，或特斯拉Optimus万台级量产。</p>
                
                <label style={{marginTop: '20px'}}>
                  <span>α 周期：该环节的扩产难度 / 技术壁垒 (0-100)</span>
                  <input type="range" min="1" max="100" value={alphaScore} onChange={(e) => setAlphaScore(e.target.value)} />
                  <b>{alphaScore}</b>
                </label>
                <p className="logic-text">如：谐波减速器长达12-24个月的扩产周期，或光模块DSP芯片的技术垄断。</p>
              </div>
              
              <div className="resonance-result">
                <h3>当前共振指数：<span style={{ color: alphaBetaResult >= 65 ? '#ef4444' : '#38bdf8' }}>{alphaBetaResult}</span></h3>
                <p>{alphaBetaResult >= 80 ? '🔥🔥 极度稀缺！处于“戴维斯双击”的绝佳主升浪，重点锁定龙头！' : alphaBetaResult >= 60 ? '🔥 稳步放量期，适合寻找有传统业绩安全垫的主板标的。' : '⚠️ 供给过剩或需求伪命题，警惕杀估值风险！'}</p>
              </div>
            </div>

            <div className="panel">
              <div className="panel-head">
                <h2>动态推荐标的</h2>
                <span>基于当前指数自动筛选</span>
              </div>
              <div className="check-grid">
                {stocks.filter(s => getCompositeScore(s) >= alphaBetaResult).slice(0, 5).map(stock => (
                  <label key={stock.code} onClick={() => selectStock(stock)} style={{cursor: 'pointer'}}>
                    <strong>{stock.name}</strong> ({stock.role})
                  </label>
                ))}
              </div>
            </div>
          </section>
        )}

        {/* 恢复纯净的战术级实战交易计划面板 */}
        {activeTab === 'plan' && (
          <section className="grid plan-grid">
            <div className="panel">
              <div className="panel-head">
                <h2>仓位与止损计算器</h2>
                <span>先定义亏损边界</span>
              </div>
              <div className="form-grid">
                {[
                  ['capital', '账户总资金 (元)'],
                  ['riskPct', '单笔最大风险敞口 (%)'],
                  ['entry', '计划买入价 (元)'],
                  ['stop', '止损价 (元)'],
                  ['target', '第一目标价 (元)'],
                ].map(([key, label]) => (
                  <label key={key}>
                    {label}
                    <input
                      type="number"
                      value={plan[key]}
                      onChange={(event) => setPlan((current) => ({ ...current, [key]: Number(event.target.value) }))}
                    />
                  </label>
                ))}
              </div>
            </div>

            <div className="panel">
              <div className="panel-head">
                <h2>风控测算结果</h2>
                <span>基于固定风险模型</span>
              </div>
              <div className="result-grid">
                <div><span>此单若止损将亏损</span><strong className="red">¥{riskAmount.toFixed(0)}</strong></div>
                <div><span>建议买入股数</span><strong>{shares} 股</strong></div>
                <div><span>实际占用资金</span><strong>¥{position.toFixed(0)}</strong></div>
                <div><span>仓位占比</span><strong>{plan.capital ? (position / plan.capital * 100).toFixed(1) : '0.0'}%</strong></div>
                <div><span>潜在盈亏比</span><strong style={{color: rewardRisk >= 2 ? '#22c55e' : '#f59e0b'}}>{rewardRisk} : 1</strong></div>
              </div>
              <p className="logic-text" style={{marginTop: '16px'}}>纪律建议：机构资金极其看重赔率，盈亏比低于 2:1 时，即使逻辑再好也不急于扣动扳机；若核心分不足 75，仅保留观察。</p>
            </div>

            <div className="panel span-3">
              <div className="panel-head">
                <h2>核心推演交易日志 (Journal)</h2>
                <span>复盘比预测更重要</span>
              </div>
              <div className="journal">
                <textarea placeholder="【进攻理由】填写 α-β 共振逻辑：它是哪个环节的卖铲人？需求爆发点在哪？扩产壁垒在哪？" />
                <textarea placeholder="【防守底线】填写财务护城河：如果是主板公司，它的传统主业市盈率是否安全？是否是行业龙头？" />
                <textarea placeholder="【离场条件】如果跌破止损位，或者财报披露订单不及预期、行业发生价格战，无条件离场。" />
              </div>
            </div>
          </section>
        )}
        
        {activeTab === 'stock' && (
           <section className="grid stock-grid">
            <div className="panel span-3">
              <div className="panel-head">
                <h2>{selectedStock.name} · {selectedStock.code}</h2>
                <span>{selectedStock.sectorName} · {selectedStock.role}</span>
              </div>
              <div style={{display: 'flex', alignItems: 'baseline', gap: '12px', marginBottom: '16px'}}>
                <strong style={{fontSize: '40px'}}>
                  {realTimeData[selectedStock.code]?.price || selectedStock.price.toFixed(2)}
                </strong>
                <span className={realTimeData[selectedStock.code]?.isUp === false ? 'green' : 'red'} style={{fontSize: '20px', fontWeight: 'bold'}}>
                  {realTimeData[selectedStock.code]?.change || selectedStock.change}
                </span>
                <ScoreBadge score={getCompositeScore(selectedStock)} />
              </div>
              <p className="logic-text" style={{fontSize: '15px', color: '#fff'}}>{selectedStock.logic}</p>
              <div className="data-grid" style={{marginTop: '20px'}}>
                <div><span>总市值</span><strong>{selectedStock.mcap}</strong></div>
                <div><span>动态PE</span><strong>{selectedStock.pe}</strong></div>
                <div><span>营收增速</span><strong>{selectedStock.revenue}</strong></div>
                <div><span>毛利率 (壁垒验证)</span><strong>{selectedStock.margin}</strong></div>
              </div>
              <button 
                style={{marginTop: '20px', padding: '10px 20px', background: '#38bdf8', color: '#000', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold'}}
                onClick={() => setActiveTab('plan')}
              >
                带入当前价格并制定交易计划 ➔
              </button>
            </div>
          </section>
        )}

      </main>
    </div>
  );
}

function StockTable({ stocks, realTimeData, onSelect, compact = false }) {
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>公司与代码</th>
            {!compact && <th>产业链角色</th>}
            <th>现价 (实时)</th>
            <th>综合分</th>
          </tr>
        </thead>
        <tbody>
          {stocks.map((stock) => {
            const liveData = realTimeData[stock.code];
            const displayPrice = liveData?.price || stock.price.toFixed(2);
            const displayChange = liveData?.change || stock.change;
            const isUp = liveData ? liveData.isUp : displayChange.includes('+');
            return (
              <tr key={stock.code} onClick={() => onSelect(stock)} style={{cursor: 'pointer'}}>
                <td>
                  <strong>{stock.name}</strong>
                  <span>{stock.code}</span>
                </td>
                {!compact && <td>{stock.sectorName} · {stock.role}</td>}
                <td>
                  <strong>{displayPrice}</strong>
                  <span className={isUp ? 'red' : 'green'}>{displayChange}</span>
                </td>
                <td><ScoreBadge score={getCompositeScore(stock)} /></td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

const styles = `
* { box-sizing: border-box; }
body { margin: 0; background: #080b12; color: #e5edf6; font-family: -apple-system, sans-serif; }
button, input, textarea { font: inherit; }
.terminal { min-height: 100vh; padding-bottom: 40px; }
.topbar { position: sticky; top: 0; z-index: 20; display: flex; align-items: center; justify-content: space-between; padding: 16px 22px; border-bottom: 1px solid #202939; background: rgba(8, 11, 18, 0.94); backdrop-filter: blur(16px); }
.eyebrow { color: #7dd3fc; font-size: 12px; margin-bottom: 4px; }
h1, h2, h3, p { margin: 0; } h1 { font-size: 24px; }
.live-badge { font-size: 12px; color: #ef4444; vertical-align: middle; margin-left: 8px; animation: blink 2s infinite; }
@keyframes blink { 0% { opacity: 1; } 50% { opacity: 0.4; } 100% { opacity: 1; } }
.tabs { display: flex; gap: 8px; flex-wrap: wrap; }
.tabs button { border: 1px solid #263244; background: #111827; color: #cbd5e1; border-radius: 8px; padding: 9px 13px; cursor: pointer; }
.tabs button.active { border-color: #38bdf8; color: #e0f2fe; background: rgba(56, 189, 248, 0.12); }
main { padding: 18px 22px; }
.grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16px; }
.overview-grid, .alpha-beta-grid { grid-template-columns: 2fr 1fr; }
.plan-grid { grid-template-columns: 1fr 1fr; }
.panel { background: #111827; border: 1px solid #202939; border-radius: 8px; padding: 16px; }
.span-2 { grid-column: span 2; } .span-3 { grid-column: span 3; }
.panel-head { display: flex; justify-content: space-between; margin-bottom: 14px; }
.panel-head span { color: #94a3b8; font-size: 12px; }
.sector-rank { display: grid; gap: 10px; }
.rank-row { display: grid; grid-template-columns: 140px 1fr 44px 150px; gap: 12px; align-items: center; padding: 10px; background: transparent; border: 1px solid #263244; color: #cbd5e1; border-radius: 8px; text-align: left; cursor: pointer; }
.mini-bar { height: 8px; background: #0b1220; border-radius: 99px; overflow: hidden; width: 100%; }
.mini-bar span { display: block; height: 100%; }
table { width: 100%; border-collapse: collapse; }
th, td { border-bottom: 1px solid #202939; padding: 11px 9px; text-align: left; font-size: 13px; }
th { color: #94a3b8; font-weight: 500; }
.red { color: #ef4444 !important; } .green { color: #22c55e !important; }
.score-badge { border-radius: 99px; padding: 3px 9px; background: #1f2937; font-size: 12px; }
.score-badge.warm { background: rgba(245, 158, 11, 0.16); color: #fcd34d; }
.score-badge.hot { background: rgba(239, 68, 68, 0.16); color: #fca5a5; }
.formula-box { background: rgba(56, 189, 248, 0.1); border: 1px dashed #38bdf8; padding: 16px; border-radius: 8px; text-align: center; margin-bottom: 24px; }
.formula-box strong { font-size: 20px; color: #38bdf8; }
.slider-group label { display: flex; flex-direction: column; gap: 8px; }
.slider-group input[type=range] { width: 100%; accent-color: #38bdf8; }
.logic-text { color: #94a3b8; font-size: 13px; margin-top: 6px; line-height: 1.6; }
.resonance-result { margin-top: 24px; padding-top: 16px; border-top: 1px solid #202939; }
.form-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
.form-grid label { color: #94a3b8; font-size: 12px; }
.form-grid input { display: block; width: 100%; margin-top: 6px; background: #0b1220; border: 1px solid #263244; color: #e5edf6; border-radius: 8px; padding: 10px; }
.result-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
.result-grid div { background: #0b1220; border: 1px solid #202939; border-radius: 8px; padding: 12px; }
.result-grid span { display: block; color: #94a3b8; font-size: 12px; margin-bottom: 4px; }
.result-grid strong { font-size: 18px; }
.journal { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
.journal textarea { min-height: 160px; resize: vertical; background: #0b1220; border: 1px solid #263244; color: #e5edf6; border-radius: 8px; padding: 12px; }
.data-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
.data-grid div { background: #0b1220; padding: 16px; border-radius: 8px; border: 1px solid #202939; }
.data-grid span { color: #94a3b8; font-size: 12px; display: block; margin-bottom: 4px; }
.data-grid strong { font-size: 18px; }
`;