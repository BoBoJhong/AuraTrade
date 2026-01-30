import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { stockService, StockData } from '@/services/stockService';
import { getComprehensiveStockInfo, ComprehensiveStockInfo } from '@/services/marketService';
import { positionService, Position } from '@/services/positionService';
import { Button } from '@/components/ui/Button';
import { 
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, 
  Tooltip, Legend, ResponsiveContainer, ReferenceLine, ComposedChart 
} from 'recharts';

export const StockDetailPage = () => {
  const { symbol } = useParams<{ symbol: string }>();
  const navigate = useNavigate();
  
  const [stockData, setStockData] = useState<StockData | null>(null);
  const [marketInfo, setMarketInfo] = useState<ComprehensiveStockInfo | null>(null);
  const [userPosition, setUserPosition] = useState<Position | null>(null);
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
      // 並行獲取股價數據、市場資訊和持倉資訊
      const [priceData, info, positions] = await Promise.all([
        stockService.getStockData(symbol!, '1mo'),
        getComprehensiveStockInfo(symbol!).catch(() => null),
        positionService.getPositions().catch(() => [])
      ]);

      setStockData(priceData);
      setMarketInfo(info);
      
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

  // 從歷史數據計算漲跌
  const prices = stockData.prices;
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
        <Button onClick={() => navigate('/dashboard')} className="mb-4">
          ← 返回首頁
        </Button>
        
        {/* 股票標題區 */}
        <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-3xl font-bold text-white mb-2">
                {stockData.info.name} ({symbol})
              </h1>
              <div className="flex items-baseline gap-4">
                <span className="text-4xl font-bold text-white">
                  ${currentPrice.toFixed(2)}
                </span>
                {/* 漲跌顯示 - 直接從歷史數據計算 */}
                <div className="flex items-center gap-2">
                  <span className={`text-xl font-semibold ${
                    change >= 0 ? 'text-red-400' : 'text-green-400'
                  }`}>
                    {change >= 0 ? '↑' : '↓'}
                    {change >= 0 ? '+' : ''}{change.toFixed(2)}
                    <span className="text-sm ml-1">
                      ({change >= 0 ? '+' : ''}{changePercent.toFixed(2)}%)
                    </span>
                  </span>
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
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
              <h2 className="text-xl font-bold text-white mb-4 flex items-center">
                <span className="text-2xl mr-2">💰</span>
                股利資訊
              </h2>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-gray-300">現金股利</span>
                  <span className="text-white font-semibold text-lg">
                    ${dividend.cash_dividend.toFixed(2)}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-300">股票股利</span>
                  <span className="text-white font-semibold text-lg">
                    {dividend.stock_dividend.toFixed(2)}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-300">合計股利</span>
                  <span className="text-white font-semibold text-lg">
                    ${dividend.total_dividend.toFixed(2)}
                  </span>
                </div>
                {dividend.ex_dividend_date && (
                  <div className="flex justify-between items-center pt-2 border-t border-white/10">
                    <span className="text-gray-300">除息日</span>
                    <span className="text-white font-semibold">
                      {dividend.ex_dividend_date}
                    </span>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* 技術分析詳情 */}
          {stockData.recommendation && (
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
              <h2 className="text-xl font-bold text-white mb-4">技術指標詳情</h2>
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
          {/* K線圖 */}
          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
            <h2 className="text-xl font-bold text-white mb-4 flex items-center justify-between">
              <span>K 線圖</span>
              {userPosition && (
                <span className="text-sm text-blue-400 font-normal flex items-center gap-2">
                  <span className="w-3 h-0.5 bg-blue-400"></span>
                  持倉成本: ${userPosition.buy_price.toFixed(2)}
                </span>
              )}
            </h2>
            <ResponsiveContainer width="100%" height={300}>
              <ComposedChart data={stockData.prices}>
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
                <Line type="monotone" dataKey="close" stroke="#ef4444" name="收盤價" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="ma5" stroke="#fbbf24" name="MA5" strokeWidth={1} dot={false} />
                <Line type="monotone" dataKey="ma20" stroke="#a78bfa" name="MA20" strokeWidth={1} dot={false} />
              </ComposedChart>
            </ResponsiveContainer>
          </div>

          {/* 成交量 */}
          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
            <h2 className="text-xl font-bold text-white mb-4">成交量</h2>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={stockData.prices}>
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
          {stockData.prices[0]?.macd !== undefined && (
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
              <h2 className="text-xl font-bold text-white mb-4">MACD</h2>
              <ResponsiveContainer width="100%" height={200}>
                <ComposedChart data={stockData.prices}>
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
          {stockData.prices[0]?.rsi !== undefined && (
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
              <h2 className="text-xl font-bold text-white mb-4">RSI</h2>
              <ResponsiveContainer width="100%" height={200}>
                <LineChart data={stockData.prices}>
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
                  <ReferenceLine y={70} stroke="#ef4444" strokeDasharray="3 3" label="超買" />
                  <ReferenceLine y={30} stroke="#10b981" strokeDasharray="3 3" label="超賣" />
                  <Line type="monotone" dataKey="rsi" stroke="#a78bfa" name="RSI" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
