import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { stockService } from '@/services/stockService';

interface RecommendedStock {
  symbol: string;
  name: string;
  price: number;
  change_percent: number;
  score: number;
  reasons: string[];
  market: string;
}

export const RecommendedStocks = () => {
  const [recommendations, setRecommendations] = useState<RecommendedStock[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchRecommendations();
  }, []);

  const fetchRecommendations = async () => {
    try {
      setIsLoading(true);
      setError(null);
      // 調用後端 AI 推薦 API
      const data = await stockService.getRecommendations(undefined, 10);
      setRecommendations(data);
    } catch (err: any) {
      console.error('Failed to fetch recommendations:', err);
      setError(err.message || '無法載入推薦股票');
      // 使用備援 Mock 數據
      const fallbackRecommendations: RecommendedStock[] = [
        {
          symbol: '2330.TW',
          name: '台積電',
          price: 625.0,
          change_percent: 2.5,
          score: 8.5,
          reasons: ['多頭排列', 'MACD 金叉', 'RSI 強勢'],
          market: 'TW'
        },
        {
          symbol: 'NVDA',
          name: 'NVIDIA',
          price: 875.3,
          change_percent: 4.2,
          score: 9.0,
          reasons: ['強勢上漲', 'AI 題材', 'MACD 多頭'],
          market: 'US'
        }
      ];
      setRecommendations(fallbackRecommendations);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="text-center text-gray-400 py-12">
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500"></div>
        <p className="mt-4 text-lg">AI 分析市場數據中...</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <span className="text-3xl">🎯</span>
            AI 推薦股票
          </h2>
          <p className="text-sm text-gray-400 mt-1">基於技術分析與市場趨勢的智能推薦</p>
        </div>
        <div className="flex items-center gap-2 text-sm text-gray-400">
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
          </svg>
          <span>更新時間: {new Date().toLocaleTimeString('zh-TW')}</span>
        </div>
      </div>

      {/* Recommendation Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {recommendations.map((stock, index) => {
          const isPositive = stock.change_percent >= 0;
          
          return (
            <div
              key={stock.symbol}
              className="glass rounded-2xl p-6 border border-indigo-500/30 hover:border-indigo-500/60 transition-all duration-300 cursor-pointer group animate-fadeIn"
              style={{ animationDelay: `${index * 0.1}s` }}
              onClick={() => navigate(`/stock/${stock.symbol}`)}
            >
              {/* Stock Header */}
              <div className="flex justify-between items-start mb-4">
                <div>
                  <div className="flex items-center gap-3 mb-1">
                    <h3 className="text-xl font-bold text-white">{stock.symbol}</h3>
                    <span className={`text-xs px-2 py-0.5 rounded-full ${
                      stock.market === 'TW' 
                        ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30' 
                        : 'bg-purple-500/20 text-purple-400 border border-purple-500/30'
                    }`}>
                      {stock.market === 'TW' ? '台股' : stock.market}
                    </span>
                  </div>
                  <p className="text-sm text-gray-400">{stock.name}</p>
                </div>

                {/* Score Badge */}
                <div className="text-center">
                  <div className={`inline-flex items-center justify-center w-14 h-14 rounded-full ${
                    stock.score >= 8.5 ? 'bg-gradient-to-br from-red-500 to-pink-500' :
                    stock.score >= 7.5 ? 'bg-gradient-to-br from-orange-500 to-yellow-500' :
                    'bg-gradient-to-br from-green-500 to-emerald-500'
                  } shadow-lg`}>
                    <span className="text-white font-bold text-lg">{stock.score}</span>
                  </div>
                  <p className="text-xs text-gray-400 mt-1">評分</p>
                </div>
              </div>

              {/* Price Info */}
              <div className="flex items-baseline gap-3 mb-4">
                <span className="text-3xl font-bold text-white">
                  ${stock.price.toFixed(2)}
                </span>
                <span className={`text-lg font-semibold ${
                  isPositive ? 'text-red-400' : 'text-green-400'
                }`}>
                  {isPositive ? '+' : ''}{stock.change_percent.toFixed(2)}%
                </span>
              </div>

              {/* Reasons */}
              <div className="space-y-2">
                <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider">推薦理由:</p>
                <div className="flex flex-wrap gap-2">
                  {stock.reasons.map((reason, idx) => (
                    <span
                      key={idx}
                      className="text-xs px-3 py-1.5 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30"
                    >
                      ✓ {reason}
                    </span>
                  ))}
                </div>
              </div>

              {/* View Details Button */}
              <div className="mt-4 pt-4 border-t border-gray-700/50">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-400">點擊查看完整分析</span>
                  <svg className="w-5 h-5 text-indigo-400 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Disclaimer */}
      <div className="mt-6 p-4 rounded-xl bg-yellow-500/10 border border-yellow-500/30">
        <div className="flex items-start gap-3">
          <svg className="w-5 h-5 text-yellow-400 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
          <div className="flex-1">
            <p className="text-sm font-medium text-yellow-300">投資風險提醒</p>
            <p className="text-xs text-yellow-200/80 mt-1">
              本推薦僅供參考，不構成投資建議。投資有風險，請根據自身財務狀況謹慎決策。
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};