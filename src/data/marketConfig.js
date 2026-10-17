export const CHART_CONFIGS = [
  { label: '金价 + 均线', keys: ['gold', 'goldMA50', 'goldMA200'], colors: ['#f0c040', '#22c55e', '#ef4444'], singleAxis: true },
  { label: '实际利率 vs 金价', keys: ['realYield', 'gold'], colors: ['#3b82f6', '#f0c040'], invertLeft: true },
  { label: '美元指数 vs 金价', keys: ['dxy', 'gold'], colors: ['#a78bfa', '#f0c040'] },
  { label: '通胀预期', keys: ['breakeven'], colors: ['#f97316'] },
  { label: '美联储资产 vs 金价', keys: ['fedAssets', 'gold'], colors: ['#14b8a6', '#f0c040'] },
  { label: 'VIX 恐慌指数', keys: ['vix'], colors: ['#ef4444'] },
  { label: '金银比', keys: ['silverGoldRatio'], colors: ['#a78bfa'] },
  { label: 'GDX vs 金价', keys: ['gdx', 'gold'], colors: ['#14b8a6', '#f0c040'] },
  { label: '收益率曲线', keys: ['yieldCurve'], colors: ['#f97316'] }
]
export const TIME_RANGES = [{ label: '1M', days: 30 }, { label: '3M', days: 90 }, { label: '6M', days: 180 }, { label: '1Y', days: 365 }, { label: '3Y', days: 1095 }]
export const KEY_LABELS = { realYield: '10Y实际利率(%)', gold: '黄金价格($)', goldMA50: 'MA50', goldMA200: 'MA200', dxy: '美元指数', breakeven: '通胀预期(%)', fedAssets: '美联储总资产(百万$)', vix: 'VIX', fwdInflation: '5Y5Y远期通胀(%)', silverGoldRatio: '金银比', gdx: 'GDX金矿ETF($)', yieldCurve: '10Y-2Y利差(%)' }
export const fmt = (n, decimals = 2) => n == null || !Number.isFinite(Number(n)) ? 'N/A' : Number(n).toLocaleString('en-US', { minimumFractionDigits: decimals, maximumFractionDigits: decimals })
