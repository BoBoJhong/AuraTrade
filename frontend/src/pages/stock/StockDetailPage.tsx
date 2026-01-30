import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { stockService, StockData, TechnicalIndicators } from '@/services/stockService';
import { getComprehensiveStockInfo, ComprehensiveStockInfo } from '@/services/marketService';
import { positionService, Position } from '@/services/positionService';
import { Button } from '@/components/ui/Button';
import { NewsPanel } from '@/components/stocks/NewsPanel';
import { 
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, 
  Tooltip, Legend, ResponsiveContainer, ReferenceLine, ComposedChart, Area, AreaChart
} from 'recharts';

type IndicatorType = 'MA' | 'EMA' | 'MACD' | 'RSI' | 'KDJ' | 'BB';

export const StockDetailPage = () => {
  const { symbol } = useParams<{ symbol: string }>();
  const navigate = useNavigate();
  
  const [stockData, setStockData] = useState<StockData | null>(null);
  const [marketInfo, setMarketInfo] = useState<ComprehensiveStockInfo | null>(null);
  const [userPosition, setUserPosition] = useState<Position | null>(null);
  const [indicators, setIndicators] = useState<TechnicalIndicators | null>(null);
  const [selectedIndicators, setSelectedIndicators] = useState<Set<IndicatorType>>(new Set(['MA', 'MACD', 'RSI']));
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (symbol) {
      fetchAllData();
    }
  }, [symbol]);

  const fetchAllData = async () => {
    setLoading(true);
    setError(null);

    try {
      // 並行獲取股價數據、市場資訊、持倉資訊和技術指標
      const [priceData, info, positions, techIndicators] = await Promise.all([
        stockService.getStockData(symbol!, '1mo'),
        getComprehensiveStockInfo(symbol!).catch(() => null),
        positionService.getPositions().catch(() => []),
        stockService.getTechnicalIndicators(symbol!, '1mo', '1d').catch(() => null)
      ]);

      setStockData(priceData);
      setMarketInfo(info);
      setIndicators(techIndicators);
      
      // 查找該股票的持倉
      const position = positions.find(p => p.symbol === symbol);
      setUserPosition(position || null);
    } catch (err: any) {
      console.error('Failed to fetch stock data:', err);
      setError(err.message || '無法載入股票資料');
    } finally {
      setLoading(false);
    }
  };

  const toggleIndicator = (indicator: IndicatorType) => {
    setSelectedIndicators(prev => {
      const newSet = new Set(prev);
      if (newSet.has(indicator)) {
        newSet.delete(indicator);
      } else {
        newSet.add(indicator);
      }
      return newSet;
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 flex items-center justify-center">
        <div className="text-white text-xl">載入中...</div>
      </div>
    );
  }

  if (error || !stockData) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-400 text-xl mb-4">{error || '無法載入股票資料'}</div>
          <Button onClick={() => navigate('/dashboard')}>返回首頁</Button>
        </div>
      </div>
    );
  }

  // 確保價格數據按日期升序排列（舊→新）
  const sortedPrices = [...stockData.prices].sort((a, b) => 
    new Date(a.date).getTime() - new Date(b.date).getTime()
  );
  
  // 從歷史數據計算漲跌 (最新數據在最後)
  const prices = sortedPrices;
  const currentPrice = prices[prices.length - 1]?.close || 0;
  const previousPrice = prices.length >= 2 ? prices[prices.length - 2]?.close : currentPrice;
  
  const change = currentPrice - previousPrice;
  const changePercent = previousPrice > 0 ? (change / previousPrice) * 100 : 0;
  
  const fundamental = marketInfo?.fundamental;
  const dividend = marketInfo?.dividend;

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 p-6">
      {/* 頂部導航 */}
      <div className="max-w-7xl mx-auto mb-6">
        <button 
          onClick={() => navigate('/dashboard')} 
          className="mb-4 flex items-center gap-2 px-4 py-2 rounded-lg bg-white/10 hover:bg-white/20 border border-white/20 text-white transition-all"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          返回首頁
        </button>
        
        {/* 股票標題區 */}
        <div className="bg-gradient-to-br from-indigo-500/20 to-purple-500/20 backdrop-blur-lg rounded-2xl p-8 border border-white/30 shadow-2xl">
          <div className="flex justify-between items-start">
            <div>
              <div className="flex items-center gap-3 mb-3">
                <h1 className="text-4xl font-bold text-white">
                  {stockData.info.name}
                </h1>
                <span className="text-2xl font-semibold text-gray-300">({symbol})</span>
              </div>
              <div className="flex items-baseline gap-6">
                <span className="text-5xl font-bold text-white">
                  ${currentPrice.toFixed(2)}
                </span>
                {/* 漲跌顯示 */}
                <div className="flex items-center gap-3">
                  <div className={`flex items-center gap-2 px-4 py-2 rounded-xl ${
                    change >= 0 ? 'bg-red-500/20 border border-red-500/30' : 'bg-green-500/20 border border-green-500/30'
                  }`}>
                    <span className={`text-2xl font-bold ${
                      change >= 0 ? 'text-red-400' : 'text-green-400'
                    }`}>
                      {change >= 0 ? '↑' : '↓'}
                    </span>
                    <div>
                      <div className={`text-xl font-semibold ${
                        change >= 0 ? 'text-red-400' : 'text-green-400'
                      }`}>
                        {change >= 0 ? '+' : ''}{change.toFixed(2)}
                      </div>
                      <div className={`text-sm ${
                        change >= 0 ? 'text-red-300' : 'text-green-300'
                      }`}>
                        {change >= 0 ? '+' : ''}{changePercent.toFixed(2)}%
                      </div>
                    </div>
                  </div>
                </div>
                {stockData.recommendation && (
                  <span className={`text-lg font-semibold ${
                    stockData.recommendation.action === 'BUY' 
                      ? 'text-red-400' 
                      : stockData.recommendation.action === 'SELL'
                      ? 'text-green-400'
                      : 'text-gray-400'
                  }`}>
                    {stockData.recommendation.action === 'BUY' && '📈 建議買入'}
                    {stockData.recommendation.action === 'SELL' && '📉 建議賣出'}
                    {stockData.recommendation.action === 'HOLD' && '⏸️ 觀望'}
                  </span>
                )}
              </div>
            </div>
            
            {/* 推薦分數 */}
            {stockData.recommendation && (
              <div className="text-right">
                <div className="text-sm text-gray-300 mb-1">技術分析評分</div>
                <div className={`text-3xl font-bold ${
                  stockData.recommendation.score >= 6 
                    ? 'text-red-400' 
                    : stockData.recommendation.score <= 3
                    ? 'text-green-400'
                    : 'text-yellow-400'
                }`}>
                  {stockData.recommendation.score}/9
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 左側：基本面資訊 + 股利資訊 */}
        <div className="space-y-6">
          {/* 基本面分析 */}
          {fundamental && (
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
              <h2 className="text-xl font-bold text-white mb-4 flex items-center">
                <span className="text-2xl mr-2">📊</span>
                基本面分析
              </h2>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-gray-300">本益比 (P/E)</span>
                  <span className="text-white font-semibold text-lg">
                    {fundamental.pe_ratio !== null ? fundamental.pe_ratio.toFixed(2) : 'N/A'}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-300">殖利率</span>
                  <span className="text-white font-semibold text-lg">
                    {fundamental.dividend_yield !== null ? `${fundamental.dividend_yield.toFixed(2)}%` : 'N/A'}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-300">股價淨值比 (P/B)</span>
                  <span className="text-white font-semibold text-lg">
                    {fundamental.pb_ratio !== null ? fundamental.pb_ratio.toFixed(2) : 'N/A'}
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* 股利資訊 */}
          {dividend && (
            <div className="bg-gradient-to-br from-green-500/10 to-emerald-500/10 backdrop-blur-lg rounded-2xl p-6 border border-white/30 shadow-xl">
              <h2 className="text-2xl font-bold text-white mb-4 flex items-center">
                <span className="text-2xl mr-2">💰</span>
                股利資訊
              </h2>
              <div className="space-y-4">
                <div className="flex justify-between items-center p-3 bg-white/5 rounded-lg">
                  <span className="text-gray-200">現金股利</span>
                  <span className="text-white font-bold text-xl">
                    ${dividend.cash_dividend.toFixed(2)}
                  </span>
                </div>
                <div className="flex justify-between items-center p-3 bg-white/5 rounded-lg">
                  <span className="text-gray-200">股票股利</span>
                  <span className="text-white font-bold text-xl">
                    {dividend.stock_dividend.toFixed(2)}
                  </span>
                </div>
                <div className="flex justify-between items-center p-3 bg-white/5 rounded-lg">
                  <span className="text-gray-200">合計股利</span>
                  <span className="text-white font-bold text-xl">
                    ${dividend.total_dividend.toFixed(2)}
                  </span>
                </div>
                {dividend.ex_dividend_date && (
                  <div className="flex justify-between items-center pt-3 border-t border-white/20">
                    <span className="text-gray-200">除息日</span>
                    <span className="text-white font-bold">
                      {dividend.ex_dividend_date}
                    </span>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* 技術分析詳情 */}
          {stockData.recommendation && (
            <div className="bg-gradient-to-br from-purple-500/10 to-pink-500/10 backdrop-blur-lg rounded-2xl p-6 border border-white/30 shadow-xl">
              <h2 className="text-2xl font-bold text-white mb-4 flex items-center">
                <span className="text-2xl mr-2">🎯</span>
                技術指標詳情
              </h2>
              <div className="space-y-2 text-sm">
                {stockData.recommendation.reasons.map((reason, idx) => (
                  <div key={idx} className="text-gray-300">
                    • {reason}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* 右側：圖表區 */}
        <div className="lg:col-span-2 space-y-6">
          {/* 技術指標選擇器 */}
          <div className="bg-gradient-to-br from-indigo-500/10 to-purple-500/10 backdrop-blur-lg rounded-2xl p-6 border border-white/30 shadow-xl">
            <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <span className="text-2xl">🎛️</span>
              技術指標選擇
            </h3>
            <div className="flex flex-wrap gap-3">
              {[
                { id: 'MA' as IndicatorType, label: '移動平均線 (MA)', icon: '📊' },
                { id: 'EMA' as IndicatorType, label: '指數移動平均 (EMA)', icon: '📈' },
                { id: 'MACD' as IndicatorType, label: 'MACD', icon: '🔄' },
                { id: 'RSI' as IndicatorType, label: 'RSI 相對強弱', icon: '💪' },
                { id: 'KDJ' as IndicatorType, label: 'KDJ 隨機指標', icon: '🎯' },
                { id: 'BB' as IndicatorType, label: '布林通道 (BB)', icon: '🌊' }
              ].map(({ id, label, icon }) => (
                <button
                  key={id}
                  onClick={() => toggleIndicator(id)}
                  className={`px-4 py-2 rounded-xl font-semibold transition-all duration-300 flex items-center gap-2 ${
                    selectedIndicators.has(id)
                      ? 'bg-gradient-to-r from-indigo-500 to-purple-500 text-white shadow-lg scale-105'
                      : 'bg-white/10 text-gray-300 hover:bg-white/20 border border-white/20'
                  }`}
                >
                  <span>{icon}</span>
                  <span>{label}</span>
                </button>
              ))}
            </div>
          </div>

          {/* K線圖 */}
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20 shadow-xl">
            <h2 className="text-2xl font-bold text-white mb-6 flex items-center justify-between">
              <span className="flex items-center gap-2">
                <span className="text-2xl">📈</span>
                價格走勢
              </span>
              {userPosition && (
                <span className="text-sm text-blue-400 font-normal flex items-center gap-2">
                  <span className="w-3 h-0.5 bg-blue-400"></span>
                  持倉成本: ${userPosition.buy_price.toFixed(2)}
                </span>
              )}
            </h2>
            <ResponsiveContainer width="100%" height={400}>
              <ComposedChart data={sortedPrices}>
                <CartesianGrid strokeDasharray="3 3" stroke="#ffffff20" />
                <XAxis 
                  dataKey="date" 
                  stroke="#ffffff80"
                  tick={{ fill: '#ffffff80' }}
                />
                <YAxis 
                  stroke="#ffffff80"
                  tick={{ fill: '#ffffff80' }}
                  domain={['dataMin - 5', 'dataMax + 5']}
                />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'rgba(0,0,0,0.8)', 
                    border: '1px solid rgba(255,255,255,0.2)',
                    borderRadius: '8px',
                    color: '#fff'
                  }}
                />
                <Legend />
                {/* 持倉成本線 */}
                {userPosition && (
                  <ReferenceLine 
                    y={userPosition.buy_price} 
                    stroke="#60a5fa" 
                    strokeWidth={2}
                    strokeDasharray="5 5"
                    label={{ 
                      value: `成本 $${userPosition.buy_price.toFixed(2)}`, 
                      fill: '#60a5fa', 
                      fontSize: 12,
                      position: 'right'
                    }}
                  />
                )}
                {/* 布林通道 */}
                {selectedIndicators.has('BB') && indicators?.ma && (
                  <>
                    <Area 
                      type="monotone" 
                      dataKey={(entry: any) => {
                        const idx = sortedPrices.indexOf(entry);
                        const ma20 = indicators.ma.ma20[idx];
                        if (!ma20) return null;
                        // 計算標準差作為布林帶寬
                        const std = Math.sqrt(sortedPrices.slice(Math.max(0, idx-19), idx+1)
                          .reduce((sum, p) => sum + Math.pow(p.close - ma20, 2), 0) / 20);
                        return ma20 + 2 * std;
                      }}
                      stroke="#fbbf24" 
                      fill="#fbbf24" 
                      fillOpacity={0.1}
                      name="布林上軌"
                      strokeWidth={1}
                      dot={false}
                    />
                    <Area 
                      type="monotone" 
                      dataKey={(entry: any) => {
                        const idx = sortedPrices.indexOf(entry);
                        const ma20 = indicators.ma.ma20[idx];
                        if (!ma20) return null;
                        const std = Math.sqrt(sortedPrices.slice(Math.max(0, idx-19), idx+1)
                          .reduce((sum, p) => sum + Math.pow(p.close - ma20, 2), 0) / 20);
                        return ma20 - 2 * std;
                      }}
                      stroke="#fbbf24" 
                      fill="#fbbf24" 
                      fillOpacity={0.1}
                      name="布林下軌"
                      strokeWidth={1}
                      dot={false}
                    />
                  </>
                )}
                <Line type="monotone" dataKey="close" stroke="#ef4444" name="收盤價" strokeWidth={3} dot={false} />
                {selectedIndicators.has('MA') && (
                  <>
                    <Line type="monotone" dataKey="ma5" stroke="#fbbf24" name="MA5" strokeWidth={2} dot={false} strokeDasharray="5 5" />
                    <Line type="monotone" dataKey="ma20" stroke="#a78bfa" name="MA20" strokeWidth={2} dot={false} strokeDasharray="5 5" />
                    <Line type="monotone" dataKey="ma60" stroke="#10b981" name="MA60" strokeWidth={2} dot={false} strokeDasharray="3 3" />
                  </>
                )}
              </ComposedChart>
            </ResponsiveContainer>
          </div>

          {/* 成交量 */}
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20 shadow-xl">
            <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
              <span className="text-2xl">📉</span>
              成交量
            </h2>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={sortedPrices}>
                <CartesianGrid strokeDasharray="3 3" stroke="#ffffff20" />
                <XAxis 
                  dataKey="date" 
                  stroke="#ffffff80"
                  tick={{ fill: '#ffffff80' }}
                />
                <YAxis 
                  stroke="#ffffff80"
                  tick={{ fill: '#ffffff80' }}
                />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'rgba(0,0,0,0.8)', 
                    border: '1px solid rgba(255,255,255,0.2)',
                    borderRadius: '8px',
                    color: '#fff'
                  }}
                />
                <Bar dataKey="volume" fill="#60a5fa" name="成交量" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* MACD */}
          {selectedIndicators.has('MACD') && sortedPrices[0]?.macd !== undefined && (
            <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20 shadow-xl">
              <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
                <span className="text-2xl">🔄</span>
                MACD 指標
                <span className="text-sm font-normal text-gray-400">
                  (快慢線交叉判斷趨勢)
                </span>
              </h2>
              <ResponsiveContainer width="100%" height={250}>
                <ComposedChart data={sortedPrices}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#ffffff20" />
                  <XAxis 
                    dataKey="date" 
                    stroke="#ffffff80"
                    tick={{ fill: '#ffffff80' }}
                  />
                  <YAxis 
                    stroke="#ffffff80"
                    tick={{ fill: '#ffffff80' }}
                  />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: 'rgba(0,0,0,0.8)', 
                      border: '1px solid rgba(255,255,255,0.2)',
                      borderRadius: '8px',
                      color: '#fff'
                    }}
                  />
                  <Legend />
                  <ReferenceLine y={0} stroke="#ffffff40" />
                  <Line type="monotone" dataKey="macd" stroke="#ef4444" name="MACD" strokeWidth={2} dot={false} />
                  <Line type="monotone" dataKey="signal" stroke="#fbbf24" name="Signal" strokeWidth={2} dot={false} />
                  <Bar dataKey="histogram" fill="#60a5fa" name="Histogram" />
                </ComposedChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* RSI */}
          {selectedIndicators.has('RSI') && sortedPrices[0]?.rsi !== undefined && (
            <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20 shadow-xl">
              <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
                <span className="text-2xl">💪</span>
                RSI 相對強弱指標
                <span className="text-sm font-normal text-gray-400">
                  (超買 &gt;70, 超賣 &lt;30)
                </span>
              </h2>
              <ResponsiveContainer width="100%" height={250}>
                <LineChart data={sortedPrices}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#ffffff20" />
                  <XAxis 
                    dataKey="date" 
                    stroke="#ffffff80"
                    tick={{ fill: '#ffffff80' }}
                  />
                  <YAxis 
                    domain={[0, 100]}
                    stroke="#ffffff80"
                    tick={{ fill: '#ffffff80' }}
                  />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: 'rgba(0,0,0,0.8)', 
                      border: '1px solid rgba(255,255,255,0.2)',
                      borderRadius: '8px',
                      color: '#fff'
                    }}
                  />
                  <Legend />
                  <ReferenceLine y={70} stroke="#ef4444" strokeDasharray="3 3" label={{ value: "超買", fill: "#ef4444", position: "right" }} />
                  <ReferenceLine y={50} stroke="#ffffff40" strokeDasharray="1 1" />
                  <ReferenceLine y={30} stroke="#10b981" strokeDasharray="3 3" label={{ value: "超賣", fill: "#10b981", position: "right" }} />
                  <Line type="monotone" dataKey="rsi" stroke="#a78bfa" name="RSI" strokeWidth={3} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* KDJ */}
          {selectedIndicators.has('KDJ') && indicators?.kdj && (
            <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20 shadow-xl">
              <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
                <span className="text-2xl">🎯</span>
                KDJ 隨機指標
                <span className="text-sm font-normal text-gray-400">
                  (K線與D線交叉判斷買賣點)
                </span>
              </h2>
              <ResponsiveContainer width="100%" height={250}>
                <LineChart 
                  data={sortedPrices.map((price, idx) => ({
                    ...price,
                    k: indicators.kdj.k[idx],
                    d: indicators.kdj.d[idx],
                    j: indicators.kdj.j[idx]
                  }))}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#ffffff20" />
                  <XAxis 
                    dataKey="date" 
                    stroke="#ffffff80"
                    tick={{ fill: '#ffffff80' }}
                  />
                  <YAxis 
                    domain={[0, 100]}
                    stroke="#ffffff80"
                    tick={{ fill: '#ffffff80' }}
                  />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: 'rgba(0,0,0,0.8)', 
                      border: '1px solid rgba(255,255,255,0.2)',
                      borderRadius: '8px',
                      color: '#fff'
                    }}
                  />
                  <Legend />
                  <ReferenceLine y={80} stroke="#ef4444" strokeDasharray="3 3" label={{ value: "超買", fill: "#ef4444" }} />
                  <ReferenceLine y={20} stroke="#10b981" strokeDasharray="3 3" label={{ value: "超賣", fill: "#10b981" }} />
                  <Line type="monotone" dataKey="k" stroke="#fbbf24" name="K值" strokeWidth={2} dot={false} />
                  <Line type="monotone" dataKey="d" stroke="#a78bfa" name="D值" strokeWidth={2} dot={false} />
                  <Line type="monotone" dataKey="j" stroke="#ef4444" name="J值" strokeWidth={2} dot={false} strokeDasharray="3 3" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* 新聞模組 */}
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20 shadow-xl">
            <NewsPanel symbol={symbol!} stockName={stockData.info.name} />
          </div>
        </div>
      </div>
    </div>
  );
};
