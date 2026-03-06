import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  screenerService, 
  ScreenerFilters, 
  ScreenedStock, 
  AIPickStock 
} from '@/services/screenerService';
import { Button } from '@/components/ui/Button';

type ViewMode = 'screener' | 'trending' | 'ai-picks';
type SortField = 'price' | 'change_percent' | 'volume' | 'market_cap' | 'pe_ratio';
type SortOrder = 'asc' | 'desc';

// 快捷篩選模板
const QUICK_FILTERS = {
  highDividend: { name: '高殖利率股', filters: { min_dividend_yield: 4, limit: 50 } },
  lowPE: { name: '低本益比股', filters: { min_pe_ratio: 5, max_pe_ratio: 15, limit: 50 } },
  oversold: { name: 'RSI超賣股', filters: { rsi_min: 0, rsi_max: 30, limit: 50 } },
  overbought: { name: 'RSI超買股', filters: { rsi_min: 70, rsi_max: 100, limit: 50 } },
  highVolume: { name: '高成交量股', filters: { min_volume: 5000000, limit: 50 } },
  smallCap: { name: '小型股', filters: { min_market_cap: 10, max_market_cap: 100, limit: 50 } }
};

export const StockScreenerPage = () => {
  const navigate = useNavigate();
  
  // 狀態管理
  const [viewMode, setViewMode] = useState<ViewMode>('ai-picks');
  const [loading, setLoading] = useState(false);
  const [screenedStocks, setScreenedStocks] = useState<ScreenedStock[]>([]);
  const [aiPicks, setAIPicks] = useState<AIPickStock[]>([]);
  const [trendingStocks, setTrendingStocks] = useState<ScreenedStock[]>([]);
  const [sortField, setSortField] = useState<SortField>('change_percent');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');
  const [showFilters, setShowFilters] = useState(true);
  
  // 篩選條件
  const [filters, setFilters] = useState<ScreenerFilters>({
    limit: 50
  });
  const [error, setError] = useState<string | null>(null);
  const [abortController, setAbortController] = useState<AbortController | null>(null);

  useEffect(() => {
    // 取消之前的請求
    if (abortController) {
      abortController.abort();
    }
    
    // 創建新的 abort controller
    const controller = new AbortController();
    setAbortController(controller);
    
    loadData(controller);
    
    // 清理函數
    return () => {
      controller.abort();
    };
  }, [viewMode]);

  const loadData = async (controller?: AbortController) => {
    setLoading(true);
    setError(null);
    try {
      if (viewMode === 'screener') {
        const response = await screenerService.screenStocks(filters);
        if (!controller?.signal.aborted) {
          setScreenedStocks(response.stocks);
          console.log('Screener loaded:', response.stocks.length, 'stocks');
        }
      } else if (viewMode === 'trending') {
        const response = await screenerService.getTrendingStocks(20);
        if (!controller?.signal.aborted) {
          setTrendingStocks(response.stocks);
          console.log('Trending loaded:', response.stocks.length, 'stocks');
        }
      } else if (viewMode === 'ai-picks') {
        // 優化: 減少候選數避免 timeout (10 支股票，每批3支，約20秒)
        const response = await screenerService.getAIPicks(10, undefined, 10);
        if (!controller?.signal.aborted) {
          setAIPicks(response.stocks);
          console.log('AI picks loaded:', response.stocks.length, 'stocks');
        }
      }
    } catch (error: any) {
      if (error.name === 'CanceledError' || error.code === 'ERR_CANCELED') {
        console.log('Request cancelled');
        return;
      }
      const errorMsg = error?.response?.data?.detail || error?.message || '載入失敗';
      console.error('Failed to load data:', errorMsg, error);
      if (!controller?.signal.aborted) {
        setError(errorMsg);
      }
    } finally {
      if (!controller?.signal.aborted) {
        setLoading(false);
      }
    }
  };

  const handleFilterChange = (key: keyof ScreenerFilters, value: number | undefined) => {
    setFilters(prev => ({
      ...prev,
      [key]: value || undefined
    }));
  };

  const handleSearch = () => {
    loadData();
  };

  const handleReset = () => {
    setFilters({ limit: 50 });
    setScreenedStocks([]);
  };

  const applyQuickFilter = (filterKey: keyof typeof QUICK_FILTERS) => {
    const quickFilter = QUICK_FILTERS[filterKey];
    setFilters({ ...quickFilter.filters });
    setScreenedStocks([]);
  };

  const sortStocks = (stocks: ScreenedStock[], field: SortField, order: SortOrder) => {
    return [...stocks].sort((a, b) => {
      let aVal = a[field] || 0;
      let bVal = b[field] || 0;
      return order === 'asc' ? aVal - bVal : bVal - aVal;
    });
  };

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortOrder('desc');
    }
  };

  const getSortedStocks = () => {
    if (viewMode === 'screener') {
      return sortStocks(screenedStocks, sortField, sortOrder);
    } else if (viewMode === 'trending') {
      return sortStocks(trendingStocks, sortField, sortOrder);
    }
    return [];
  };

  const goToStockDetail = (symbol: string) => {
    navigate(`/stock/${symbol}`);
  };

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

        {/* 標題與視圖切換 */}
        <div className="bg-gradient-to-br from-indigo-500/20 to-purple-500/20 backdrop-blur-lg rounded-2xl p-8 border border-white/30 shadow-2xl">
          <h1 className="text-4xl font-bold text-white mb-6 flex items-center gap-3">
            <span className="text-5xl"></span>
            智能選股器
          </h1>
          <div className="flex gap-4 flex-wrap">
            <button
              onClick={() => setViewMode('screener')}
              className={`px-6 py-3 rounded-xl font-semibold transition-all duration-300 ${
                viewMode === 'screener'
                  ? 'bg-gradient-to-r from-indigo-500 to-purple-500 text-white shadow-lg scale-105'
                  : 'bg-white/10 text-gray-300 hover:bg-white/20 border border-white/20'
              }`}
            >
               條件篩選
            </button>
            <button
              onClick={() => setViewMode('trending')}
              className={`px-6 py-3 rounded-xl font-semibold transition-all duration-300 ${
                viewMode === 'trending'
                  ? 'bg-gradient-to-r from-indigo-500 to-purple-500 text-white shadow-lg scale-105'
                  : 'bg-white/10 text-gray-300 hover:bg-white/20 border border-white/20'
              }`}
            >
               熱門排行
            </button>
            <button
              onClick={() => setViewMode('ai-picks')}
              className={`px-6 py-3 rounded-xl font-semibold transition-all duration-300 ${
                viewMode === 'ai-picks'
                  ? 'bg-gradient-to-r from-indigo-500 to-purple-500 text-white shadow-lg scale-105'
                  : 'bg-white/10 text-gray-300 hover:bg-white/20 border border-white/20'
              }`}
            >
               AI 推薦
            </button>
          </div>
        </div>

        {/* 錯誤提示 */}
        {error && (
          <div className="mt-4 bg-red-500/20 border border-red-500/50 backdrop-blur-lg rounded-xl p-4">
            <div className="flex items-center gap-3">
              <svg className="w-6 h-6 text-red-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <p className="text-red-300 font-semibold">載入失敗</p>
                <p className="text-red-200 text-sm">{error}</p>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="max-w-7xl mx-auto">
        {/* 條件篩選模式 */}
        {viewMode === 'screener' && (
          <div className="space-y-6">
            {/* 篩選表單 */}
            <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20 shadow-xl">
              <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
                <span></span>
                篩選條件
              </h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {/* 價格範圍 */}
                <div className="space-y-2">
                  <label className="text-white font-semibold">價格範圍 ($)</label>
                  <div className="flex gap-2 items-center">
                    <input
                      type="number"
                      placeholder="最低"
                      value={filters.min_price || ''}
                      onChange={(e) => handleFilterChange('min_price', e.target.value ? parseFloat(e.target.value) : undefined)}
                      className="flex-1 px-4 py-2 rounded-lg bg-white/10 border border-white/20 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                    <span className="text-white">-</span>
                    <input
                      type="number"
                      placeholder="最高"
                      value={filters.max_price || ''}
                      onChange={(e) => handleFilterChange('max_price', e.target.value ? parseFloat(e.target.value) : undefined)}
                      className="flex-1 px-4 py-2 rounded-lg bg-white/10 border border-white/20 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                  </div>
                </div>

                {/* 市值範圍 */}
                <div className="space-y-2">
                  <label className="text-white font-semibold">市值範圍 (億)</label>
                  <div className="flex gap-2 items-center">
                    <input
                      type="number"
                      placeholder="最低"
                      value={filters.min_market_cap || ''}
                      onChange={(e) => handleFilterChange('min_market_cap', e.target.value ? parseFloat(e.target.value) : undefined)}
                      className="flex-1 px-4 py-2 rounded-lg bg-white/10 border border-white/20 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                    <span className="text-white">-</span>
                    <input
                      type="number"
                      placeholder="最高"
                      value={filters.max_market_cap || ''}
                      onChange={(e) => handleFilterChange('max_market_cap', e.target.value ? parseFloat(e.target.value) : undefined)}
                      className="flex-1 px-4 py-2 rounded-lg bg-white/10 border border-white/20 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                  </div>
                </div>

                {/* 本益比範圍 */}
                <div className="space-y-2">
                  <label className="text-white font-semibold">本益比 (P/E)</label>
                  <div className="flex gap-2 items-center">
                    <input
                      type="number"
                      placeholder="最低"
                      value={filters.min_pe_ratio || ''}
                      onChange={(e) => handleFilterChange('min_pe_ratio', e.target.value ? parseFloat(e.target.value) : undefined)}
                      className="flex-1 px-4 py-2 rounded-lg bg-white/10 border border-white/20 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                    <span className="text-white">-</span>
                    <input
                      type="number"
                      placeholder="最高"
                      value={filters.max_pe_ratio || ''}
                      onChange={(e) => handleFilterChange('max_pe_ratio', e.target.value ? parseFloat(e.target.value) : undefined)}
                      className="flex-1 px-4 py-2 rounded-lg bg-white/10 border border-white/20 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                  </div>
                </div>

                {/* 殖利率範圍 */}
                <div className="space-y-2">
                  <label className="text-white font-semibold">殖利率 (%)</label>
                  <div className="flex gap-2 items-center">
                    <input
                      type="number"
                      placeholder="最低"
                      value={filters.min_dividend_yield || ''}
                      onChange={(e) => handleFilterChange('min_dividend_yield', e.target.value ? parseFloat(e.target.value) : undefined)}
                      className="flex-1 px-4 py-2 rounded-lg bg-white/10 border border-white/20 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                    <span className="text-white">-</span>
                    <input
                      type="number"
                      placeholder="最高"
                      value={filters.max_dividend_yield || ''}
                      onChange={(e) => handleFilterChange('max_dividend_yield', e.target.value ? parseFloat(e.target.value) : undefined)}
                      className="flex-1 px-4 py-2 rounded-lg bg-white/10 border border-white/20 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                  </div>
                </div>

                {/* RSI 範圍 */}
                <div className="space-y-2">
                  <label className="text-white font-semibold">RSI 指標 (0-100)</label>
                  <div className="flex gap-2 items-center">
                    <input
                      type="number"
                      placeholder="最低"
                      min="0"
                      max="100"
                      value={filters.rsi_min || ''}
                      onChange={(e) => handleFilterChange('rsi_min', e.target.value ? parseFloat(e.target.value) : undefined)}
                      className="flex-1 px-4 py-2 rounded-lg bg-white/10 border border-white/20 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                    <span className="text-white">-</span>
                    <input
                      type="number"
                      placeholder="最高"
                      min="0"
                      max="100"
                      value={filters.rsi_max || ''}
                      onChange={(e) => handleFilterChange('rsi_max', e.target.value ? parseFloat(e.target.value) : undefined)}
                      className="flex-1 px-4 py-2 rounded-lg bg-white/10 border border-white/20 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                  </div>
                </div>

                {/* 成交量 */}
                <div className="space-y-2">
                  <label className="text-white font-semibold">最低成交量</label>
                  <input
                    type="number"
                    placeholder="例如：1000000"
                    value={filters.min_volume || ''}
                    onChange={(e) => handleFilterChange('min_volume', e.target.value ? parseInt(e.target.value) : undefined)}
                    className="w-full px-4 py-2 rounded-lg bg-white/10 border border-white/20 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
              </div>

              <div className="flex gap-4 mt-6">
                <Button onClick={handleSearch} disabled={loading}>
                  {loading ? '搜尋中...' : ' 開始篩選'}
                </Button>
                <Button onClick={handleReset} variant="secondary">
                   重置條件
                </Button>
              </div>
            </div>

            {/* 篩選結果 */}
            {screenedStocks.length > 0 && (
              <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20 shadow-xl">
                <h2 className="text-2xl font-bold text-white mb-4">
                  篩選結果 ({screenedStocks.length} 檔)
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {screenedStocks.map((stock) => (
                    <StockCard key={stock.symbol} stock={stock} onClick={() => goToStockDetail(stock.symbol)} />
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* 熱門排行模式 */}
        {viewMode === 'trending' && (
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20 shadow-xl">
            <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
              <span></span>
              熱門股票排行榜
            </h2>
            {loading ? (
              <div className="text-white text-center py-8">載入中...</div>
            ) : trendingStocks.length === 0 ? (
              <div className="text-center py-12">
                <div className="text-6xl mb-4">📊</div>
                <p className="text-gray-300 text-lg">暫無熱門股票數據</p>
                <Button onClick={loadData} className="mt-4">
                  重新載入
                </Button>
              </div>
            ) : (
              <div className="space-y-3">
                {trendingStocks.map((stock, index) => (
                  <div
                    key={stock.symbol}
                    onClick={() => goToStockDetail(stock.symbol)}
                    className="flex items-center gap-4 p-4 rounded-xl bg-white/5 hover:bg-white/10 border border-white/20 hover:border-orange-500/50 cursor-pointer transition-all hover:scale-[1.02] hover:shadow-xl hover:shadow-orange-500/10"
                  >
                    <div className={`text-xl font-bold w-10 h-10 flex items-center justify-center rounded-full ${
                      index === 0 ? 'bg-yellow-500/20 text-yellow-400 shadow-lg shadow-yellow-500/50' :
                      index === 1 ? 'bg-gray-400/20 text-gray-300 shadow-lg shadow-gray-400/50' :
                      index === 2 ? 'bg-orange-500/20 text-orange-400 shadow-lg shadow-orange-500/50' :
                      'bg-white/10 text-gray-400'
                    }`}>
                      {index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : index + 1}
                    </div>
                    <div className="flex-1">
                      <div className="font-bold text-white text-lg">{stock.name}</div>
                      <div className="text-sm text-gray-300">{stock.symbol}</div>
                    </div>
                    <div className="text-right">
                      <div className="text-xl font-bold text-white">${stock.price.toFixed(2)}</div>
                      <div className={`text-sm font-semibold ${stock.change >= 0 ? 'text-red-400' : 'text-green-400'}`}>
                        {stock.change >= 0 ? '' : ''} {stock.change_percent.toFixed(2)}%
                      </div>
                    </div>
                    <div className="text-right text-sm text-gray-400">
                      <div>成交量</div>
                      <div className="font-semibold text-white">{(stock.volume / 1000000).toFixed(2)}M</div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* AI 推薦模式 */}
        {viewMode === 'ai-picks' && (
          <div className="space-y-6">
            <div className="bg-gradient-to-br from-purple-500/10 to-pink-500/10 backdrop-blur-lg rounded-2xl p-6 border border-white/30 shadow-xl">
              <h2 className="text-2xl font-bold text-white mb-2 flex items-center gap-2">
                <span></span>
                AI 智能推薦
              </h2>
              <p className="text-gray-300 mb-6">
                綜合技術指標、基本面和市場動態，由 AI 為您推薦潛力股
              </p>
              {loading ? (
                <div className="text-white text-center py-8">AI 分析中...</div>
              ) : aiPicks.length === 0 ? (
                <div className="text-center py-12">
                  <div className="text-6xl mb-4">🤖</div>
                  <p className="text-gray-300 text-lg">暫無 AI 推薦數據</p>
                  <Button onClick={loadData} className="mt-4">
                    重新載入
                  </Button>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {aiPicks.map((stock) => (
                    <div
                      key={stock.symbol}
                      onClick={() => goToStockDetail(stock.symbol)}
                      className="p-6 rounded-xl bg-white/5 hover:bg-white/10 border border-white/20 cursor-pointer transition-all group"
                    >
                      <div className="flex items-start justify-between mb-4">
                        <div>
                          <div className="font-bold text-white text-xl group-hover:text-indigo-400 transition-colors">
                            {stock.name}
                          </div>
                          <div className="text-sm text-gray-300">{stock.symbol}</div>
                        </div>
                        <div className="text-right">
                          <div className="text-2xl font-bold text-white">${stock.price.toFixed(2)}</div>
                          <div className={`text-sm font-semibold ${stock.change >= 0 ? 'text-red-400' : 'text-green-400'}`}>
                            {stock.change >= 0 ? '' : ''} {stock.change_percent.toFixed(2)}%
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center gap-3 mb-4">
                        <div className="flex-1 h-2 bg-white/10 rounded-full overflow-hidden">
                          <div
                            className={`h-full rounded-full transition-all ${
                              stock.ai_score >= 70 ? 'bg-gradient-to-r from-green-500 to-emerald-500' :
                              stock.ai_score >= 50 ? 'bg-gradient-to-r from-yellow-500 to-amber-500' :
                              'bg-gradient-to-r from-red-500 to-rose-500'
                            }`}
                            style={{ width: `${stock.ai_score}%` }}
                          />
                        </div>
                        <div className="text-white font-bold text-lg">{stock.ai_score}</div>
                      </div>

                      <div className={`inline-flex px-3 py-1 rounded-lg text-sm font-semibold mb-4 ${
                        stock.recommendation === '買入' ? 'bg-red-500/20 text-red-400' :
                        stock.recommendation === '觀望' ? 'bg-yellow-500/20 text-yellow-400' :
                        'bg-green-500/20 text-green-400'
                      }`}>
                        {stock.recommendation}
                      </div>

                      <div className="space-y-2">
                        {stock.reasons.map((reason, idx) => (
                          <div key={idx} className="text-sm text-gray-300 flex items-start gap-2">
                            <span className="text-indigo-400"></span>
                            <span>{reason}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// 股票卡片組件
const StockCard = ({ stock, onClick }: { stock: ScreenedStock; onClick: () => void }) => {
  return (
    <div
      onClick={onClick}
      className="p-4 rounded-xl bg-gradient-to-br from-white/5 to-white/10 hover:from-white/10 hover:to-white/15 border border-white/20 hover:border-indigo-500/50 cursor-pointer transition-all group hover:scale-[1.02] hover:shadow-xl hover:shadow-indigo-500/10"
    >
      <div className="flex justify-between items-start mb-3">
        <div>
          <div className="font-bold text-white text-lg group-hover:text-indigo-400 transition-colors">
            {stock.name}
          </div>
          <div className="text-sm text-gray-300">{stock.symbol}</div>
        </div>
        <div className="text-right">
          <div className="text-xl font-bold text-white">${stock.price.toFixed(2)}</div>
          <div className={`text-sm font-semibold ${stock.change >= 0 ? 'text-red-400' : 'text-green-400'}`}>
            {stock.change >= 0 ? '' : ''} {stock.change_percent.toFixed(2)}%
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-2 text-sm">
        {stock.pe_ratio && (
          <div className="bg-white/5 rounded-lg p-2">
            <div className="text-gray-400">本益比</div>
            <div className="text-white font-semibold">{stock.pe_ratio.toFixed(2)}</div>
          </div>
        )}
        {stock.dividend_yield && (
          <div className="bg-white/5 rounded-lg p-2">
            <div className="text-gray-400">殖利率</div>
            <div className="text-white font-semibold">{stock.dividend_yield.toFixed(2)}%</div>
          </div>
        )}
        <div className="bg-white/5 rounded-lg p-2">
          <div className="text-gray-400">成交量</div>
          <div className="text-white font-semibold">{(stock.volume / 1000000).toFixed(1)}M</div>
        </div>
        <div className="bg-white/5 rounded-lg p-2">
          <div className="text-gray-400">市值</div>
          <div className="text-white font-semibold">{(stock.market_cap / 100000000).toFixed(0)}億</div>
        </div>
      </div>
    </div>
  );
};
