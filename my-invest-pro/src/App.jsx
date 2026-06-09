import React, { useMemo, useState } from 'react';

const marketSnapshot = [
  { name: '上证指数', value: '3,284.21', change: '+0.62%', turnover: '4,680亿', state: '修复' },
  { name: '深成指', value: '10,214.37', change: '+0.91%', turnover: '5,940亿', state: '放量' },
  { name: '创业板指', value: '2,087.44', change: '+1.18%', turnover: '2,310亿', state: '强于主板' },
  { name: '科创50', value: '867.12', change: '+1.53%', turnover: '846亿', state: '科技领涨' },
];

const sectors = [
  {
    id: 'ai',
    name: 'AI算力',
    score: 92,
    heat: 88,
    fund: '+86.4亿',
    trend: '主升',
    verify: '订单与价格双验证',
    color: '#38bdf8',
    chain: ['大模型迭代', '训练/推理需求', 'GPU服务器', '光模块/PCB/液冷', '算力租赁'],
    catalysts: ['海外云厂商资本开支上修', '国产算力替代加速', '800G/1.6T光模块放量'],
    risks: ['一致预期过高', '海外订单波动', '上游芯片供给扰动'],
    stocks: [
      {
        code: '300308.SZ',
        name: '中际旭创',
        role: '光模块龙头',
        price: 178.62,
        change: '+4.82%',
        core: 96,
        proof: 93,
        valuation: 62,
        trend: 91,
        capital: 88,
        mcap: '约1800亿',
        pe: '38x',
        revenue: '+122%',
        margin: '31.8%',
        roe: '22.5%',
        logic: '800G/1.6T光模块直接承接AI算力扩张，是算力链中业绩弹性最清晰的核心环节。',
      },
      {
        code: '300502.SZ',
        name: '新易盛',
        role: '高速光模块',
        price: 116.41,
        change: '+3.76%',
        core: 92,
        proof: 89,
        valuation: 66,
        trend: 87,
        capital: 82,
        mcap: '约800亿',
        pe: '35x',
        revenue: '+96%',
        margin: '29.4%',
        roe: '19.7%',
        logic: '高速光模块持续放量，受益海外AI集群建设，利润弹性强于传统通信链。',
      },
      {
        code: '002463.SZ',
        name: '沪电股份',
        role: 'AI服务器PCB',
        price: 42.35,
        change: '+2.18%',
        core: 84,
        proof: 81,
        valuation: 70,
        trend: 78,
        capital: 76,
        mcap: '约800亿',
        pe: '31x',
        revenue: '+48%',
        margin: '27.1%',
        roe: '18.1%',
        logic: 'AI服务器带来高多层PCB价值量提升，属于算力基础设施扩张的材料型受益环节。',
      },
    ],
  },
  {
    id: 'semi',
    name: '半导体国产替代',
    score: 86,
    heat: 82,
    fund: '+51.8亿',
    trend: '趋势修复',
    verify: '设备订单验证',
    color: '#a78bfa',
    chain: ['出口管制', '国产替代', '晶圆厂扩产', '设备/材料导入', '良率提升'],
    catalysts: ['先进制程自主可控', '存储扩产周期', '设备国产化率提升'],
    risks: ['估值敏感', '验证周期长', '订单节奏不均衡'],
    stocks: [
      {
        code: '002371.SZ',
        name: '北方华创',
        role: '平台型设备',
        price: 326.18,
        change: '+2.44%',
        core: 94,
        proof: 88,
        valuation: 58,
        trend: 78,
        capital: 79,
        mcap: '约2800亿',
        pe: '46x',
        revenue: '+42%',
        margin: '43.5%',
        roe: '17.8%',
        logic: '刻蚀、薄膜、清洗等设备平台化布局，直接受益晶圆厂扩产和国产化率提升。',
      },
      {
        code: '688012.SH',
        name: '中微公司',
        role: '刻蚀设备',
        price: 184.77,
        change: '+1.96%',
        core: 91,
        proof: 86,
        valuation: 60,
        trend: 75,
        capital: 73,
        mcap: '约1500亿',
        pe: '53x',
        revenue: '+37%',
        margin: '45.2%',
        roe: '14.6%',
        logic: '刻蚀设备是先进制程核心瓶颈，技术壁垒高，国产替代逻辑强。',
      },
      {
        code: '688019.SH',
        name: '安集科技',
        role: 'CMP材料',
        price: 157.28,
        change: '+1.42%',
        core: 79,
        proof: 74,
        valuation: 67,
        trend: 68,
        capital: 64,
        mcap: '约250亿',
        pe: '39x',
        revenue: '+28%',
        margin: '55.7%',
        roe: '13.2%',
        logic: '抛光液和功能湿电子化学品导入加速，属于材料国产替代的高壁垒环节。',
      },
    ],
  },
  {
    id: 'robot',
    name: '人形机器人',
    score: 81,
    heat: 86,
    fund: '+38.6亿',
    trend: '高波动上行',
    verify: '样机到订单过渡',
    color: '#f472b6',
    chain: ['整机量产预期', '关节价值量提升', '减速器/丝杠', '传感器', '执行器集成'],
    catalysts: ['头部厂商迭代加速', '执行器定点', '传感器送样验证'],
    risks: ['量产节奏不确定', '主题交易拥挤', '短期业绩贡献有限'],
    stocks: [
      {
        code: '601689.SH',
        name: '拓普集团',
        role: '执行器平台',
        price: 63.51,
        change: '+3.12%',
        core: 88,
        proof: 74,
        valuation: 61,
        trend: 80,
        capital: 76,
        mcap: '约800亿',
        pe: '32x',
        revenue: '+25%',
        margin: '21.9%',
        roe: '16.3%',
        logic: '汽车零部件平台延伸到机器人执行器，若量产兑现，单机价值量弹性较大。',
      },
      {
        code: '688017.SH',
        name: '绿的谐波',
        role: '谐波减速器',
        price: 112.06,
        change: '+2.77%',
        core: 86,
        proof: 68,
        valuation: 52,
        trend: 79,
        capital: 70,
        mcap: '约250亿',
        pe: '68x',
        revenue: '+18%',
        margin: '48.1%',
        roe: '10.5%',
        logic: '谐波减速器是机器人关节核心零部件，产业趋势强，但估值对订单兑现敏感。',
      },
      {
        code: '603662.SH',
        name: '柯力传感',
        role: '力传感器',
        price: 38.95,
        change: '+1.51%',
        core: 76,
        proof: 62,
        valuation: 64,
        trend: 71,
        capital: 58,
        mcap: '约120亿',
        pe: '41x',
        revenue: '+16%',
        margin: '38.6%',
        roe: '11.7%',
        logic: '力矩和触觉传感器提升机器人感知能力，是从样机到量产需要验证的关键方向。',
      },
    ],
  },
  {
    id: 'low',
    name: '低空经济',
    score: 77,
    heat: 79,
    fund: '+24.9亿',
    trend: '政策驱动',
    verify: '基建招标验证',
    color: '#22d3ee',
    chain: ['政策放开', '空域管理', 'eVTOL取证', '低空基建', '运营场景'],
    catalysts: ['地方低空规划密集落地', '空管系统建设', '低空物流与文旅试点'],
    risks: ['商业化周期长', '订单分散', '估值先于业绩'],
    stocks: [
      {
        code: '688631.SH',
        name: '莱斯信息',
        role: '空管系统',
        price: 79.48,
        change: '+2.69%',
        core: 87,
        proof: 72,
        valuation: 54,
        trend: 75,
        capital: 69,
        mcap: '约100亿',
        pe: '58x',
        revenue: '+22%',
        margin: '36.5%',
        roe: '9.4%',
        logic: '低空经济要商业化，空域管理和空管系统必须先行，是政策落地后的关键基建。',
      },
      {
        code: '002085.SZ',
        name: '万丰奥威',
        role: 'eVTOL整机',
        price: 18.37,
        change: '+1.94%',
        core: 80,
        proof: 58,
        valuation: 49,
        trend: 78,
        capital: 72,
        mcap: '约300亿',
        pe: '65x',
        revenue: '+12%',
        margin: '19.6%',
        roe: '8.9%',
        logic: '通航制造基础叠加eVTOL预期，弹性较大，但需要持续跟踪适航和订单兑现。',
      },
      {
        code: '000099.SZ',
        name: '中信海直',
        role: '通航运营',
        price: 19.12,
        change: '+0.84%',
        core: 68,
        proof: 61,
        valuation: 70,
        trend: 62,
        capital: 55,
        mcap: '约100亿',
        pe: '35x',
        revenue: '+10%',
        margin: '18.3%',
        roe: '7.2%',
        logic: '运营端有稀缺性，但短期更偏主题扩散，核心程度弱于空管和核心装备。',
      },
    ],
  },
  {
    id: 'medicine',
    name: '创新药出海',
    score: 74,
    heat: 66,
    fund: '+18.3亿',
    trend: '中期修复',
    verify: 'License-out验证',
    color: '#34d399',
    chain: ['研发管线', '临床数据', '海外授权', '商业化放量', '利润兑现'],
    catalysts: ['创新药出海交易', '医保谈判温和', 'GLP-1和ADC景气'],
    risks: ['临床失败', '海外监管', '商业化节奏'],
    stocks: [
      {
        code: '600276.SH',
        name: '恒瑞医药',
        role: '创新药龙头',
        price: 48.31,
        change: '+1.36%',
        core: 83,
        proof: 78,
        valuation: 68,
        trend: 66,
        capital: 63,
        mcap: '约3500亿',
        pe: '44x',
        revenue: '+18%',
        margin: '86.2%',
        roe: '13.8%',
        logic: '创新药管线持续推进，出海和国内商业化共同驱动估值修复。',
      },
      {
        code: '688235.SH',
        name: '百济神州',
        role: '全球化创新药',
        price: 151.2,
        change: '+2.11%',
        core: 86,
        proof: 84,
        valuation: 55,
        trend: 69,
        capital: 61,
        mcap: '约2500亿',
        pe: '亏损收窄',
        revenue: '+73%',
        margin: '84.6%',
        roe: '-',
        logic: '全球商业化能力已被验证，是中国创新药出海的标杆型公司。',
      },
      {
        code: '300760.SZ',
        name: '迈瑞医疗',
        role: '高端器械',
        price: 287.54,
        change: '+0.48%',
        core: 75,
        proof: 80,
        valuation: 72,
        trend: 58,
        capital: 52,
        mcap: '约3500亿',
        pe: '30x',
        revenue: '+15%',
        margin: '66.8%',
        roe: '29.2%',
        logic: '器械国产替代和海外扩张更偏稳健成长，弹性弱于创新药但质量较高。',
      },
    ],
  },
  {
    id: 'ev',
    name: '智能电动车',
    score: 72,
    heat: 69,
    fund: '+12.7亿',
    trend: '分化修复',
    verify: '销量与毛利验证',
    color: '#f59e0b',
    chain: ['新能源渗透', '电池成本', '智能驾驶', '热管理/线控', '整车竞争'],
    catalysts: ['智能驾驶下沉', '电池技术迭代', '出海销量增长'],
    risks: ['价格战', '库存周期', '整车利润承压'],
    stocks: [
      {
        code: '300750.SZ',
        name: '宁德时代',
        role: '动力电池',
        price: 218.49,
        change: '+1.05%',
        core: 84,
        proof: 82,
        valuation: 74,
        trend: 63,
        capital: 60,
        mcap: '约11000亿',
        pe: '24x',
        revenue: '+9%',
        margin: '24.8%',
        roe: '20.1%',
        logic: '全球动力电池龙头，受益电动化和储能，但行业价格竞争压制弹性。',
      },
      {
        code: '002920.SZ',
        name: '德赛西威',
        role: '智能座舱/智驾',
        price: 112.8,
        change: '+2.25%',
        core: 78,
        proof: 76,
        valuation: 65,
        trend: 72,
        capital: 66,
        mcap: '约700亿',
        pe: '37x',
        revenue: '+31%',
        margin: '21.3%',
        roe: '18.6%',
        logic: '智能座舱和域控制器持续渗透，受益汽车智能化升级。',
      },
      {
        code: '002050.SZ',
        name: '三花智控',
        role: '热管理',
        price: 27.46,
        change: '+0.76%',
        core: 73,
        proof: 75,
        valuation: 73,
        trend: 57,
        capital: 51,
        mcap: '约700亿',
        pe: '28x',
        revenue: '+19%',
        margin: '28.6%',
        roe: '17.1%',
        logic: '热管理单车价值量提升，属于电动车供应链中确定性较强的稳健环节。',
      },
    ],
  },
];

const tabs = [
  { id: 'overview', label: '市场总览' },
  { id: 'research', label: '产业链研究' },
  { id: 'stock', label: '个股深度' },
  { id: 'compare', label: '对比筛选' },
  { id: 'plan', label: '交易计划' },
];

function allStocks() {
  return sectors.flatMap((sector) =>
    sector.stocks.map((stock) => ({ ...stock, sectorId: sector.id, sectorName: sector.name, sectorColor: sector.color }))
  );
}

function getCompositeScore(stock) {
  return Math.round(stock.core * 0.28 + stock.proof * 0.24 + stock.trend * 0.2 + stock.capital * 0.16 + stock.valuation * 0.12);
}

function buildIntraday(seed, basePrice) {
  let value = basePrice * 0.992;
  return Array.from({ length: 72 }, (_, index) => {
    const drift = Math.sin((index + seed) / 7) * 0.22 + Math.cos((index + seed) / 13) * 0.16 + (index > 42 ? 0.08 : -0.02);
    value = Math.max(basePrice * 0.955, value + drift);
    return {
      time: index < 36 ? `09:${String(30 + index * 3).padStart(2, '0')}` : `13:${String((index - 36) * 3).padStart(2, '0')}`,
      price: Number(value.toFixed(2)),
      volume: Math.round(800 + Math.abs(Math.sin(index / 3 + seed)) * 2600 + index * 18),
    };
  });
}

function buildKline(seed, basePrice) {
  let close = basePrice * 0.82;
  return Array.from({ length: 46 }, (_, index) => {
    const open = close + Math.sin((index + seed) / 3) * 1.2;
    close = open + Math.sin((index + seed) / 4) * 1.8 + 0.34;
    const high = Math.max(open, close) + 1.6 + Math.abs(Math.cos(index + seed));
    const low = Math.min(open, close) - 1.5 - Math.abs(Math.sin(index + seed));
    return {
      open: Number(open.toFixed(2)),
      close: Number(close.toFixed(2)),
      high: Number(high.toFixed(2)),
      low: Number(low.toFixed(2)),
      volume: Math.round(1200 + Math.abs(Math.cos(index / 4 + seed)) * 4200),
    };
  });
}

function MiniBar({ value, color = '#38bdf8' }) {
  return (
    <div className="mini-bar">
      <span style={{ width: `${Math.max(3, Math.min(100, value))}%`, background: color }} />
    </div>
  );
}

function IntradayChart({ data, color }) {
  const width = 620;
  const height = 238;
  const pad = 26;
  const prices = data.map((d) => d.price);
  const min = Math.min(...prices);
  const max = Math.max(...prices);
  const range = max - min || 1;
  const points = data.map((d, index) => {
    const x = pad + (index / (data.length - 1)) * (width - pad * 2);
    const y = pad + ((max - d.price) / range) * (height - pad * 2 - 38);
    return `${x},${y}`;
  });
  const last = data[data.length - 1];

  return (
    <svg className="chart" viewBox={`0 0 ${width} ${height}`} role="img" aria-label="分时图">
      {[0, 1, 2, 3].map((line) => (
        <line key={line} x1={pad} x2={width - pad} y1={pad + line * 42} y2={pad + line * 42} className="grid-line" />
      ))}
      <polyline points={points.join(' ')} fill="none" stroke={color} strokeWidth="2.6" />
      <polygon points={`${pad},${height - 54} ${points.join(' ')} ${width - pad},${height - 54}`} fill={color} opacity="0.1" />
      {data.map((d, index) => {
        if (index % 4 !== 0) return null;
        const x = pad + (index / (data.length - 1)) * (width - pad * 2);
        const barHeight = Math.min(34, d.volume / 120);
        return <rect key={d.time} x={x - 2} y={height - 24 - barHeight} width="3" height={barHeight} fill="#475569" opacity="0.65" />;
      })}
      <text x={pad} y={18} className="chart-label">
        分时 {last.price}
      </text>
      <text x={width - pad - 92} y={18} className="chart-label">
        量能模拟
      </text>
    </svg>
  );
}

function KLineChart({ data }) {
  const width = 620;
  const height = 238;
  const pad = 26;
  const highs = data.map((d) => d.high);
  const lows = data.map((d) => d.low);
  const max = Math.max(...highs);
  const min = Math.min(...lows);
  const range = max - min || 1;
  const candleWidth = (width - pad * 2) / data.length * 0.56;
  const y = (price) => pad + ((max - price) / range) * (height - pad * 2 - 34);

  return (
    <svg className="chart" viewBox={`0 0 ${width} ${height}`} role="img" aria-label="K线图">
      {[0, 1, 2, 3].map((line) => (
        <line key={line} x1={pad} x2={width - pad} y1={pad + line * 42} y2={pad + line * 42} className="grid-line" />
      ))}
      {data.map((d, index) => {
        const x = pad + (index / (data.length - 1)) * (width - pad * 2);
        const up = d.close >= d.open;
        const top = y(Math.max(d.open, d.close));
        const bottom = y(Math.min(d.open, d.close));
        return (
          <g key={index}>
            <line x1={x} x2={x} y1={y(d.high)} y2={y(d.low)} stroke={up ? '#ef4444' : '#22c55e'} strokeWidth="1.2" />
            <rect
              x={x - candleWidth / 2}
              y={top}
              width={candleWidth}
              height={Math.max(2, bottom - top)}
              fill={up ? '#ef4444' : '#22c55e'}
              opacity="0.92"
            />
          </g>
        );
      })}
      <text x={pad} y={18} className="chart-label">
        日K模拟
      </text>
      <text x={width - pad - 118} y={18} className="chart-label">
        趋势与量价结构
      </text>
    </svg>
  );
}

function ScoreBadge({ score }) {
  const label = score >= 85 ? '核心龙头' : score >= 75 ? '重点跟踪' : score >= 65 ? '观察标的' : '谨慎';
  return <span className={`score-badge ${score >= 85 ? 'hot' : score >= 75 ? 'warm' : ''}`}>{score} · {label}</span>;
}

export default function App() {
  const stocks = useMemo(() => allStocks(), []);
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedSectorId, setSelectedSectorId] = useState('ai');
  const [selectedStockCode, setSelectedStockCode] = useState('300308.SZ');
  const [compareCodes, setCompareCodes] = useState(['300308.SZ', '002371.SZ', '601689.SH']);
  const [search, setSearch] = useState('');
  const [plan, setPlan] = useState({ capital: 200000, riskPct: 1, entry: 50, stop: 47.5, target: 58 });

  const selectedSector = sectors.find((sector) => sector.id === selectedSectorId) || sectors[0];
  const selectedStock = stocks.find((stock) => stock.code === selectedStockCode) || stocks[0];
  const filteredStocks = stocks.filter((stock) => `${stock.name}${stock.code}${stock.role}${stock.sectorName}`.toLowerCase().includes(search.toLowerCase()));
  const intraday = useMemo(() => buildIntraday(selectedStock.code.charCodeAt(0), selectedStock.price), [selectedStock]);
  const kline = useMemo(() => buildKline(selectedStock.code.charCodeAt(1), selectedStock.price), [selectedStock]);
  const compareStocks = compareCodes.map((code) => stocks.find((stock) => stock.code === code)).filter(Boolean);
  const riskAmount = plan.capital * plan.riskPct / 100;
  const singleRisk = Math.max(0, plan.entry - plan.stop);
  const shares = singleRisk > 0 ? Math.floor(riskAmount / singleRisk / 100) * 100 : 0;
  const position = shares * plan.entry;
  const rewardRisk = singleRisk > 0 ? ((plan.target - plan.entry) / singleRisk).toFixed(2) : '0.00';

  const selectStock = (stock) => {
    setSelectedStockCode(stock.code);
    setSelectedSectorId(stock.sectorId);
    setActiveTab('stock');
  };

  const toggleCompare = (code) => {
    setCompareCodes((current) => {
      if (current.includes(code)) return current.filter((item) => item !== code);
      return [...current, code].slice(-3);
    });
  };

  return (
    <div className="terminal">
      <style>{styles}</style>
      <header className="topbar">
        <div>
          <div className="eyebrow">A股产业链趋势研究终端</div>
          <h1>核心受益决策工作台</h1>
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
          <>
            <section className="market-strip">
              {marketSnapshot.map((item) => (
                <button key={item.name} className="market-card">
                  <span>{item.name}</span>
                  <strong>{item.value}</strong>
                  <em>{item.change}</em>
                  <small>{item.turnover} · {item.state}</small>
                </button>
              ))}
            </section>

            <section className="grid overview-grid">
              <div className="panel wide">
                <div className="panel-head">
                  <h2>主线强度排行</h2>
                  <span>按资金、趋势、验证、核心环节综合排序</span>
                </div>
                <div className="sector-rank">
                  {[...sectors].sort((a, b) => b.score - a.score).map((sector) => (
                    <button
                      key={sector.id}
                      className={`rank-row ${selectedSectorId === sector.id ? 'selected' : ''}`}
                      onClick={() => {
                        setSelectedSectorId(sector.id);
                        setActiveTab('research');
                      }}
                    >
                      <strong>{sector.name}</strong>
                      <MiniBar value={sector.score} color={sector.color} />
                      <span>{sector.score}</span>
                      <small>{sector.fund} · {sector.trend}</small>
                    </button>
                  ))}
                </div>
              </div>

              <div className="panel">
                <div className="panel-head">
                  <h2>市场情绪</h2>
                  <span>演示模型</span>
                </div>
                <div className="gauge">
                  <strong>76</strong>
                  <span>修复转强</span>
                </div>
                <div className="stat-list">
                  <p><b>涨停</b><span>78</span></p>
                  <p><b>跌停</b><span>6</span></p>
                  <p><b>连板高度</b><span>5板</span></p>
                  <p><b>全市场成交</b><span>10,620亿</span></p>
                </div>
              </div>

              <div className="panel">
                <div className="panel-head">
                  <h2>产业链热力图</h2>
                  <span>点击切换研究对象</span>
                </div>
                <div className="heatmap">
                  {sectors.map((sector) => (
                    <button
                      key={sector.id}
                      style={{ background: `linear-gradient(135deg, ${sector.color}55, #111827)` }}
                      onClick={() => setSelectedSectorId(sector.id)}
                    >
                      <strong>{sector.name}</strong>
                      <span>{sector.heat}</span>
                    </button>
                  ))}
                </div>
              </div>

              <div className="panel wide">
                <div className="panel-head">
                  <h2>核心候选池</h2>
                  <span>机构视角先看验证，再看价格</span>
                </div>
                <StockTable stocks={stocks.slice().sort((a, b) => getCompositeScore(b) - getCompositeScore(a)).slice(0, 9)} onSelect={selectStock} onCompare={toggleCompare} compareCodes={compareCodes} />
              </div>
            </section>
          </>
        )}

        {activeTab === 'research' && (
          <section className="grid research-grid">
            <div className="panel">
              <div className="panel-head">
                <h2>板块列表</h2>
                <span>趋势强度</span>
              </div>
              <div className="sector-list">
                {sectors.map((sector) => (
                  <button key={sector.id} className={selectedSectorId === sector.id ? 'active' : ''} onClick={() => setSelectedSectorId(sector.id)}>
                    <strong>{sector.name}</strong>
                    <span>{sector.verify}</span>
                    <MiniBar value={sector.score} color={sector.color} />
                  </button>
                ))}
              </div>
            </div>

            <div className="panel span-2">
              <div className="panel-head">
                <h2>{selectedSector.name}产业链拆解</h2>
                <span>{selectedSector.trend} · {selectedSector.fund}</span>
              </div>
              <div className="chain-flow">
                {selectedSector.chain.map((node, index) => (
                  <React.Fragment key={node}>
                    <div className={index >= 2 ? 'core-node' : ''}>
                      <small>{index + 1}</small>
                      <strong>{node}</strong>
                    </div>
                    {index < selectedSector.chain.length - 1 && <span className="connector">→</span>}
                  </React.Fragment>
                ))}
              </div>
              <div className="research-notes">
                <div>
                  <h3>催化</h3>
                  {selectedSector.catalysts.map((item) => <p key={item}>{item}</p>)}
                </div>
                <div>
                  <h3>风险</h3>
                  {selectedSector.risks.map((item) => <p key={item}>{item}</p>)}
                </div>
                <div>
                  <h3>机构判断</h3>
                  <p>优先确认核心环节是否出现订单、价格、毛利率或产能利用率改善。</p>
                  <p>若龙头强于板块平均，说明资金认可主线；若只有边缘标的活跃，要降低权重。</p>
                </div>
              </div>
            </div>

            <div className="panel span-3">
              <div className="panel-head">
                <h2>{selectedSector.name}核心公司</h2>
                <span>点击进入个股深度</span>
              </div>
              <StockTable stocks={selectedSector.stocks.map((stock) => ({ ...stock, sectorId: selectedSector.id, sectorName: selectedSector.name, sectorColor: selectedSector.color }))} onSelect={selectStock} onCompare={toggleCompare} compareCodes={compareCodes} />
            </div>
          </section>
        )}

        {activeTab === 'stock' && (
          <section className="grid stock-grid">
            <div className="panel span-2">
              <div className="panel-head">
                <h2>{selectedStock.name} · {selectedStock.code}</h2>
                <span>{selectedStock.sectorName} · {selectedStock.role}</span>
              </div>
              <div className="quote-line">
                <strong>{selectedStock.price.toFixed(2)}</strong>
                <span>{selectedStock.change}</span>
                <ScoreBadge score={getCompositeScore(selectedStock)} />
              </div>
              <div className="chart-grid">
                <IntradayChart data={intraday} color={selectedStock.sectorColor} />
                <KLineChart data={kline} />
              </div>
            </div>

            <div className="panel">
              <div className="panel-head">
                <h2>机构评分</h2>
                <span>五维模型</span>
              </div>
              {[
                ['核心受益', selectedStock.core],
                ['业绩验证', selectedStock.proof],
                ['估值安全', selectedStock.valuation],
                ['趋势强度', selectedStock.trend],
                ['资金关注', selectedStock.capital],
              ].map(([label, value]) => (
                <div className="factor" key={label}>
                  <span>{label}</span>
                  <MiniBar value={value} color={selectedStock.sectorColor} />
                  <b>{value}</b>
                </div>
              ))}
            </div>

            <div className="panel">
              <div className="panel-head">
                <h2>核心逻辑</h2>
                <span>产业链位置</span>
              </div>
              <p className="logic-text">{selectedStock.logic}</p>
              <div className="data-grid">
                <div><span>市值</span><strong>{selectedStock.mcap}</strong></div>
                <div><span>PE</span><strong>{selectedStock.pe}</strong></div>
                <div><span>营收增速</span><strong>{selectedStock.revenue}</strong></div>
                <div><span>毛利率</span><strong>{selectedStock.margin}</strong></div>
                <div><span>ROE</span><strong>{selectedStock.roe}</strong></div>
                <div><span>板块</span><strong>{selectedStock.sectorName}</strong></div>
              </div>
            </div>

            <div className="panel span-2">
              <div className="panel-head">
                <h2>验证清单</h2>
                <span>决定是否继续跟踪</span>
              </div>
              <div className="check-grid">
                <label><input type="checkbox" /> 核心环节出现订单、涨价、扩产或客户认证</label>
                <label><input type="checkbox" /> 龙头走势强于同板块平均水平</label>
                <label><input type="checkbox" /> 财报数据能验证产业链逻辑</label>
                <label><input type="checkbox" /> 估值和拥挤度尚未明显透支</label>
              </div>
            </div>
          </section>
        )}

        {activeTab === 'compare' && (
          <section className="grid compare-grid">
            <div className="panel span-3">
              <div className="panel-head">
                <h2>三股横向对比</h2>
                <span>核心、业绩、估值、趋势、资金</span>
              </div>
              <div className="compare-cards">
                {compareStocks.map((stock) => (
                  <div className="compare-card" key={stock.code}>
                    <button onClick={() => toggleCompare(stock.code)}>移除</button>
                    <h3>{stock.name}</h3>
                    <p>{stock.sectorName} · {stock.role}</p>
                    <ScoreBadge score={getCompositeScore(stock)} />
                    <div className="factor compact"><span>核心</span><MiniBar value={stock.core} color={stock.sectorColor} /><b>{stock.core}</b></div>
                    <div className="factor compact"><span>验证</span><MiniBar value={stock.proof} color={stock.sectorColor} /><b>{stock.proof}</b></div>
                    <div className="factor compact"><span>趋势</span><MiniBar value={stock.trend} color={stock.sectorColor} /><b>{stock.trend}</b></div>
                  </div>
                ))}
              </div>
            </div>
            <div className="panel span-3">
              <div className="panel-head">
                <h2>全市场候选筛选</h2>
                <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="搜索公司、代码、板块、产业环节" />
              </div>
              <StockTable stocks={filteredStocks} onSelect={selectStock} onCompare={toggleCompare} compareCodes={compareCodes} />
            </div>
          </section>
        )}

        {activeTab === 'plan' && (
          <section className="grid plan-grid">
            <div className="panel">
              <div className="panel-head">
                <h2>仓位与止损</h2>
                <span>先定义亏损边界</span>
              </div>
              <div className="form-grid">
                {[
                  ['capital', '账户资金'],
                  ['riskPct', '单笔风险%'],
                  ['entry', '计划买入价'],
                  ['stop', '止损价'],
                  ['target', '目标价'],
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
                <h2>交易结果</h2>
                <span>按计划价测算</span>
              </div>
              <div className="result-grid">
                <div><span>最大亏损</span><strong>{riskAmount.toFixed(0)}</strong></div>
                <div><span>建议股数</span><strong>{shares}</strong></div>
                <div><span>占用仓位</span><strong>{plan.capital ? (position / plan.capital * 100).toFixed(1) : '0.0'}%</strong></div>
                <div><span>盈亏比</span><strong>{rewardRisk}</strong></div>
              </div>
              <p className="logic-text">纪律建议：盈亏比低于 2 时，不急于交易；核心分不足 75 时，只保留观察，不进入计划。</p>
            </div>

            <div className="panel span-3">
              <div className="panel-head">
                <h2>交易计划模板</h2>
                <span>复盘时填写</span>
              </div>
              <div className="journal">
                <textarea placeholder="买入理由：核心受益环节、验证信号、资金行为、价格位置" />
                <textarea placeholder="失效条件：订单不及预期、板块龙头走弱、放量破位、估值透支" />
                <textarea placeholder="复盘记录：是否按计划执行，错误来自逻辑、价格还是情绪" />
              </div>
            </div>
          </section>
        )}
      </main>

      <footer>
        演示数据仅用于页面与研究框架展示，不构成投资建议。真实使用时建议接入行情、财报、公告、研报和资金流接口。
      </footer>
    </div>
  );
}

function StockTable({ stocks, onSelect, onCompare, compareCodes }) {
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>公司</th>
            <th>产业链位置</th>
            <th>价格</th>
            <th>核心分</th>
            <th>验证</th>
            <th>趋势</th>
            <th>综合</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          {stocks.map((stock) => (
            <tr key={stock.code}>
              <td onClick={() => onSelect(stock)}>
                <strong>{stock.name}</strong>
                <span>{stock.code}</span>
              </td>
              <td>{stock.sectorName || ''} · {stock.role}</td>
              <td>
                <strong>{stock.price.toFixed(2)}</strong>
                <span className="red">{stock.change}</span>
              </td>
              <td>{stock.core}</td>
              <td>{stock.proof}</td>
              <td>{stock.trend}</td>
              <td><ScoreBadge score={getCompositeScore(stock)} /></td>
              <td>
                <button className="text-btn" onClick={() => onSelect(stock)}>深度</button>
                <button className={`text-btn ${compareCodes.includes(stock.code) ? 'on' : ''}`} onClick={() => onCompare(stock.code)}>
                  {compareCodes.includes(stock.code) ? '已对比' : '对比'}
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

const styles = `
* { box-sizing: border-box; }
body { margin: 0; background: #080b12; }
button, input, textarea { font: inherit; }
.terminal {
  min-height: 100vh;
  background: #080b12;
  color: #e5edf6;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
}
.topbar {
  position: sticky;
  top: 0;
  z-index: 20;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  padding: 16px 22px;
  border-bottom: 1px solid #202939;
  background: rgba(8, 11, 18, 0.94);
  backdrop-filter: blur(16px);
}
.eyebrow { color: #7dd3fc; font-size: 12px; margin-bottom: 4px; }
h1, h2, h3, p { margin: 0; }
h1 { font-size: 24px; letter-spacing: 0; }
.tabs { display: flex; gap: 8px; flex-wrap: wrap; }
.tabs button, .text-btn, .market-card, .rank-row, .sector-list button, .heatmap button {
  border: 1px solid #263244;
  background: #111827;
  color: #cbd5e1;
  border-radius: 8px;
  cursor: pointer;
}
.tabs button { padding: 9px 13px; }
.tabs button.active, .text-btn.on { border-color: #38bdf8; color: #e0f2fe; background: rgba(56, 189, 248, 0.12); }
main { padding: 18px 22px 30px; }
.market-strip { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; margin-bottom: 16px; }
.market-card { text-align: left; padding: 14px; min-height: 104px; }
.market-card span, .market-card small, .panel-head span, table span, .result-grid span, .data-grid span { display: block; color: #94a3b8; font-size: 12px; }
.market-card strong { display: block; font-size: 22px; margin: 7px 0 2px; }
.market-card em, .red { color: #ef4444; font-style: normal; }
.grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16px; }
.overview-grid { grid-template-columns: 1.2fr 0.8fr 1fr; }
.research-grid { grid-template-columns: 300px 1fr 1fr; }
.stock-grid { grid-template-columns: 1fr 1fr 360px; }
.compare-grid, .plan-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
.panel {
  min-width: 0;
  background: #111827;
  border: 1px solid #202939;
  border-radius: 8px;
  padding: 16px;
}
.wide { grid-column: span 2; }
.span-2 { grid-column: span 2; }
.span-3 { grid-column: span 3; }
.panel-head {
  display: flex;
  justify-content: space-between;
  gap: 14px;
  align-items: center;
  margin-bottom: 14px;
}
.panel-head h2 { font-size: 16px; }
.panel-head input {
  width: min(360px, 100%);
  background: #0b1220;
  border: 1px solid #263244;
  color: #e5edf6;
  border-radius: 8px;
  padding: 9px 11px;
}
.sector-rank, .sector-list, .stat-list { display: grid; gap: 10px; }
.rank-row {
  display: grid;
  grid-template-columns: 140px 1fr 44px 150px;
  gap: 12px;
  align-items: center;
  padding: 10px;
  text-align: left;
}
.rank-row.selected, .sector-list button.active { border-color: #38bdf8; background: rgba(56, 189, 248, 0.08); }
.mini-bar { height: 8px; background: #0b1220; border-radius: 999px; overflow: hidden; }
.mini-bar span { display: block; height: 100%; border-radius: 999px; }
.gauge {
  min-height: 170px;
  border: 1px solid #263244;
  border-radius: 8px;
  display: grid;
  place-content: center;
  text-align: center;
  background: radial-gradient(circle, rgba(56, 189, 248, 0.22), rgba(17, 24, 39, 0.4) 56%);
}
.gauge strong { font-size: 54px; line-height: 1; }
.gauge span { color: #bae6fd; }
.stat-list p { display: flex; justify-content: space-between; border-bottom: 1px solid #202939; padding: 9px 0; color: #cbd5e1; }
.stat-list b { font-weight: 500; color: #94a3b8; }
.heatmap { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }
.heatmap button { min-height: 86px; padding: 12px; text-align: left; }
.heatmap strong, .heatmap span { display: block; }
.heatmap span { font-size: 26px; margin-top: 8px; color: #fff; }
.table-wrap { overflow-x: auto; }
table { width: 100%; min-width: 860px; border-collapse: collapse; }
th, td { border-bottom: 1px solid #202939; padding: 11px 9px; text-align: left; font-size: 13px; }
th { color: #94a3b8; font-weight: 500; }
td:first-child { cursor: pointer; }
td strong { display: block; }
.text-btn { padding: 6px 9px; margin-right: 6px; }
.score-badge {
  display: inline-flex;
  border-radius: 999px;
  padding: 3px 9px;
  background: #1f2937;
  color: #cbd5e1;
  font-size: 12px;
}
.score-badge.warm { background: rgba(245, 158, 11, 0.16); color: #fcd34d; }
.score-badge.hot { background: rgba(239, 68, 68, 0.16); color: #fca5a5; }
.sector-list button {
  padding: 12px;
  text-align: left;
}
.sector-list strong, .sector-list span { display: block; margin-bottom: 7px; }
.sector-list span { color: #94a3b8; font-size: 12px; }
.chain-flow { display: flex; align-items: stretch; gap: 8px; overflow-x: auto; padding-bottom: 10px; }
.chain-flow div {
  min-width: 138px;
  border: 1px solid #263244;
  border-radius: 8px;
  padding: 12px;
  background: #0b1220;
}
.chain-flow .core-node { border-color: rgba(245, 158, 11, 0.65); background: rgba(245, 158, 11, 0.1); }
.chain-flow small { color: #94a3b8; display: block; margin-bottom: 7px; }
.connector { color: #64748b; align-self: center; }
.research-notes { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; margin-top: 14px; }
.research-notes div, .compare-card, .result-grid div, .data-grid div {
  border: 1px solid #263244;
  border-radius: 8px;
  background: #0b1220;
  padding: 12px;
}
.research-notes h3 { font-size: 14px; margin-bottom: 8px; }
.research-notes p, .logic-text { color: #cbd5e1; line-height: 1.7; font-size: 13px; }
.quote-line { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
.quote-line > strong { font-size: 34px; }
.quote-line > span { color: #ef4444; }
.chart-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.chart { width: 100%; min-height: 220px; background: #0b1220; border: 1px solid #263244; border-radius: 8px; }
.grid-line { stroke: #202939; stroke-width: 1; }
.chart-label { fill: #94a3b8; font-size: 12px; }
.factor { display: grid; grid-template-columns: 76px 1fr 34px; gap: 9px; align-items: center; margin-bottom: 12px; color: #cbd5e1; font-size: 13px; }
.factor.compact { grid-template-columns: 48px 1fr 30px; margin-top: 12px; }
.data-grid, .result-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; margin-top: 12px; }
.data-grid strong, .result-grid strong { display: block; margin-top: 5px; }
.check-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }
.check-grid label { border: 1px solid #263244; border-radius: 8px; padding: 12px; color: #cbd5e1; background: #0b1220; }
.check-grid input { accent-color: #38bdf8; margin-right: 8px; }
.compare-cards { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; }
.compare-card button { float: right; border: 1px solid #263244; background: transparent; color: #94a3b8; border-radius: 6px; cursor: pointer; }
.compare-card h3 { margin: 2px 0 4px; }
.compare-card p { color: #94a3b8; margin-bottom: 10px; }
.form-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
.form-grid label { color: #94a3b8; font-size: 12px; }
.form-grid input {
  display: block;
  width: 100%;
  margin-top: 6px;
  background: #0b1220;
  border: 1px solid #263244;
  color: #e5edf6;
  border-radius: 8px;
  padding: 10px;
}
.journal { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; }
.journal textarea {
  min-height: 160px;
  resize: vertical;
  background: #0b1220;
  border: 1px solid #263244;
  color: #e5edf6;
  border-radius: 8px;
  padding: 12px;
}
footer { color: #64748b; font-size: 12px; text-align: center; padding: 20px; border-top: 1px solid #202939; }
@media (max-width: 1100px) {
  .topbar { align-items: flex-start; flex-direction: column; }
  .market-strip, .grid, .overview-grid, .research-grid, .stock-grid, .compare-grid, .plan-grid { grid-template-columns: 1fr; }
  .wide, .span-2, .span-3 { grid-column: auto; }
  .chart-grid, .research-notes, .compare-cards, .journal { grid-template-columns: 1fr; }
  .rank-row { grid-template-columns: 120px 1fr 40px; }
  .rank-row small { grid-column: 1 / -1; }
}
@media (max-width: 640px) {
  main { padding: 12px; }
  .topbar { padding: 14px; }
  .market-strip, .data-grid, .result-grid, .check-grid, .form-grid, .heatmap { grid-template-columns: 1fr; }
  h1 { font-size: 20px; }
}
`;
