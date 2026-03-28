import { useEffect, useState } from 'react';
import { positionService, Position, PortfolioSummary } from '@/services/positionService';
import { stockService } from '@/services/stockService';
import AddPositionModal from './AddPositionModal';
import EditPositionModal from './EditPositionModal';

interface LatestPrices {
  [symbol: string]: number;
}

export const PositionCard = () => {
  const [positions, setPositions] = useState<Position[]>([]);
  const [summary, setSummary] = useState<PortfolioSummary | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingPosition, setEditingPosition] = useState<Position | null>(null);
  const [latestPrices, setLatestPrices] = useState<LatestPrices>({});

  const loadPositions = async () => {
    try {
      const [posData, summaryData] = await Promise.all([
        positionService.getPositions(),
        positionService.getPortfolioSummary()
      ]);
      setPositions(posData);
      setSummary(summaryData);
      
      // 並行獲取所有持倉的最新價格
      const pricePromises = posData.map(async (pos) => {
        try {
          const history = await stockService.getHistoricalData(pos.symbol, '5d');
          if (history && history.length > 0) {
            // 按日期排序，確保最新的在最後
            const sortedHistory = [...history].sort((a, b) => 
              new Date(a.date).getTime() - new Date(b.date).getTime()
            );
            const latestPrice = sortedHistory[sortedHistory.length - 1]?.price;
            return { symbol: pos.symbol, price: latestPrice || pos.current_price || 0 };
          }
          return { symbol: pos.symbol, price: pos.current_price || 0 };
        } catch (error) {
          console.error(`獲取 ${pos.symbol} 價格失敗:`, error);
          return { symbol: pos.symbol, price: pos.current_price || 0 };
        }
      });
      
      const prices = await Promise.all(pricePromises);
      const priceMap: LatestPrices = {};
      prices.forEach(({ symbol, price }) => {
        priceMap[symbol] = price;
      });
      setLatestPrices(priceMap);
    } catch (error) {
      console.error('載入持倉失敗:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadPositions();
  }, []);

  const handleDelete = async (id: number) => {
    if (!confirm('確定要刪除此持倉記錄嗎？')) return;
    
    try {
      await positionService.deletePosition(id);
      await loadPositions();
    } catch (error) {
      console.error('刪除失敗:', error);
    }
  };

  if (isLoading) {
    return (
      <div className="glass rounded-2xl p-12 border border-white/20 animate-fadeIn">
        <div className="flex flex-col items-center justify-center space-y-4">
          {/* 雙圈載入動畫 */}
          <div className="relative">
            <div className="w-16 h-16 border-4 border-purple-500/20 border-t-purple-500 rounded-full animate-spin"></div>
            <div className="absolute inset-0 w-16 h-16 border-4 border-pink-500/20 border-b-pink-500 rounded-full animate-spin" style={{animationDirection: 'reverse', animationDuration: '1.5s'}}></div>
          </div>
          <div className="text-center">
            <p className="text-slate-900 font-semibold">載入投資組合...</p>
            <p className="text-slate-500 text-sm mt-1">正在計算收益</p>
          </div>
          {/* 骨架屏 */}
          <div className="w-full space-y-3 mt-6">
            <div className="animate-pulse">
              <div className="h-32 bg-white/5 rounded-xl mb-3"></div>
              {[1, 2].map(i => (
                <div key={i} className="h-24 bg-white/5 rounded-xl mb-3"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 投資組合總覽 - 優化數據視覺化 */}
      {summary && (
        <div className="glass rounded-2xl p-6 lg:p-8 border border-purple-500/30 relative overflow-hidden">
          {/* 背景裝飾 */}
          <div className="absolute top-0 right-0 w-64 h-64 bg-purple-500/5 rounded-full filter blur-3xl"></div>
          
          <div className="relative">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-2xl font-extrabold text-slate-900 tracking-tight flex items-center gap-2">
                <span>📊</span> 投資組合總覽
              </h3>
              <div className="px-3 py-1 rounded-full bg-purple-500/10 border border-purple-500/30 text-purple-300 text-sm font-medium">
                即時數據
              </div>
            </div>
            
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-6">
              <div className="bg-white/5 rounded-xl p-4 lg:p-5 border border-white/10 hover:border-indigo-500/50 transition-all group">
                <div className="flex items-center justify-between mb-3">
                  <p className="text-gray-400 text-xs lg:text-sm">持倉數量</p>
                  <div className="w-8 h-8 rounded-lg bg-indigo-500/10 flex items-center justify-center group-hover:scale-110 transition-transform">
                    <span className="text-base">💼</span>
                  </div>
                </div>
                <p className="text-2xl lg:text-3xl font-extrabold text-slate-900 tracking-tight">{summary.total_positions}</p>
                <p className="text-xs text-gray-500 mt-1">支股票</p>
              </div>
              
              <div className="bg-white/5 rounded-xl p-4 lg:p-5 border border-white/10 hover:border-blue-500/50 transition-all group">
                <div className="flex items-center justify-between mb-3">
                  <p className="text-gray-400 text-xs lg:text-sm">總成本</p>
                  <div className="w-8 h-8 rounded-lg bg-blue-500/10 flex items-center justify-center group-hover:scale-110 transition-transform">
                    <span className="text-base">💰</span>
                  </div>
                </div>
                <p className="text-2xl lg:text-3xl font-extrabold text-slate-900 tracking-tight">${summary.total_cost.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</p>
                <p className="text-xs text-gray-500 mt-1">投入資金</p>
              </div>
              
              <div className="bg-white/5 rounded-xl p-4 lg:p-5 border border-white/10 hover:border-cyan-500/50 transition-all group">
                <div className="flex items-center justify-between mb-3">
                  <p className="text-gray-400 text-xs lg:text-sm">目前市值</p>
                  <div className="w-8 h-8 rounded-lg bg-cyan-500/10 flex items-center justify-center group-hover:scale-110 transition-transform">
                    <span className="text-base">💵</span>
                  </div>
                </div>
                <p className="text-2xl lg:text-3xl font-extrabold text-slate-900 tracking-tight">
                  ${(() => {
                    const totalMarketValue = positions.reduce((sum, pos) => {
                      const currentPrice = latestPrices[pos.symbol] || pos.current_price || 0;
                      return sum + (pos.quantity * currentPrice);
                    }, 0);
                    return totalMarketValue.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
                  })()}
                </p>
                <p className="text-xs text-gray-500 mt-1">即時估值</p>
              </div>
              
              <div className="bg-white/5 rounded-xl p-4 lg:p-5 border border-white/10 hover:border-purple-500/50 transition-all group">
                <div className="flex items-center justify-between mb-3">
                  <p className="text-gray-400 text-xs lg:text-sm">總損益</p>
                  <div className={`w-8 h-8 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform ${
                    (() => {
                      const totalMarketValue = positions.reduce((sum, pos) => {
                        const currentPrice = latestPrices[pos.symbol] || pos.current_price || 0;
                        return sum + (pos.quantity * currentPrice);
                      }, 0);
                      const profitLoss = totalMarketValue - summary.total_cost;
                      return profitLoss >= 0 ? 'bg-green-500/10' : 'bg-red-500/10';
                    })()
                  }`}>
                    <span className="text-base">{(() => {
                      const totalMarketValue = positions.reduce((sum, pos) => {
                        const currentPrice = latestPrices[pos.symbol] || pos.current_price || 0;
                        return sum + (pos.quantity * currentPrice);
                      }, 0);
                      const profitLoss = totalMarketValue - summary.total_cost;
                      return profitLoss >= 0 ? '📈' : '📉';
                    })()}</span>
                  </div>
                </div>
                <p className={`text-2xl lg:text-3xl font-bold ${(() => {
                  const totalMarketValue = positions.reduce((sum, pos) => {
                    const currentPrice = latestPrices[pos.symbol] || pos.current_price || 0;
                    return sum + (pos.quantity * currentPrice);
                  }, 0);
                  const profitLoss = totalMarketValue - summary.total_cost;
                  return profitLoss >= 0 ? 'text-green-400' : 'text-red-400';
                })()}`}>
                  {(() => {
                    const totalMarketValue = positions.reduce((sum, pos) => {
                      const currentPrice = latestPrices[pos.symbol] || pos.current_price || 0;
                      return sum + (pos.quantity * currentPrice);
                    }, 0);
                    const profitLoss = totalMarketValue - summary.total_cost;
                    return `${profitLoss >= 0 ? '+' : ''}$${Math.abs(profitLoss).toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
                  })()}
                </p>
                <p className={`text-sm font-medium mt-1 ${(() => {
                  const totalMarketValue = positions.reduce((sum, pos) => {
                    const currentPrice = latestPrices[pos.symbol] || pos.current_price || 0;
                    return sum + (pos.quantity * currentPrice);
                  }, 0);
                  const profitLoss = totalMarketValue - summary.total_cost;
                  return profitLoss >= 0 ? 'text-green-400' : 'text-red-400';
                })()}`}>
                  {(() => {
                    const totalMarketValue = positions.reduce((sum, pos) => {
                      const currentPrice = latestPrices[pos.symbol] || pos.current_price || 0;
                      return sum + (pos.quantity * currentPrice);
                    }, 0);
                    const profitLoss = totalMarketValue - summary.total_cost;
                    const profitLossPercent = summary.total_cost > 0 ? (profitLoss / summary.total_cost * 100) : 0;
                    return `${profitLoss >= 0 ? '▲' : '▼'} ${Math.abs(profitLossPercent).toFixed(2)}%`;
                  })()}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 持倉列表 */}
      <div className="glass rounded-2xl p-6 lg:p-8 border border-white/20">
        <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4 mb-6">
          <div>
            <h3 className="text-2xl font-extrabold text-slate-900 tracking-tight flex items-center gap-2">
              <span>📈</span> 持倉明細
            </h3>
            <p className="text-sm text-gray-400 mt-1">共 {positions.length} 筆持倉記錄</p>
          </div>
          <button
            onClick={() => setShowAddModal(true)}
            className="px-6 py-3 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-500 text-white font-medium hover:shadow-lg hover:shadow-indigo-500/50 transition-all hover:scale-105 active:scale-95 flex items-center gap-2 justify-center"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            新增持倉
          </button>
        </div>

        {positions.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <svg className="w-16 h-16 mx-auto mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            <p>尚無持倉記錄</p>
            <p className="text-sm mt-2">點擊上方按鈕新增您的第一筆持倉</p>
          </div>
        ) : (
          <div className="space-y-3">
            {positions.map((pos) => {
              const currentPrice = latestPrices[pos.symbol] || pos.current_price || 0;
              const marketValue = pos.quantity * currentPrice;
              const profitLoss = marketValue - pos.cost;
              const profitLossPercent = pos.cost > 0 ? (profitLoss / pos.cost * 100) : 0;
              
              return (
              <div
                key={pos.id}
                className="border border-gray-800 rounded-xl p-4 hover:border-indigo-500/50 transition-colors"
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h4 className="text-lg font-bold text-slate-900">{pos.symbol}</h4>
                      <span className="text-sm text-gray-400">x {pos.quantity}</span>
                    </div>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                      <div>
                        <p className="text-gray-500">買入均價</p>
                        <p className="text-slate-800 font-semibold">${pos.buy_price.toFixed(2)}</p>
                      </div>
                      <div>
                        <p className="text-gray-500">當前價</p>
                        <p className="text-slate-800 font-semibold">
                          ${currentPrice.toFixed(2)}
                        </p>
                      </div>
                      <div>
                        <p className="text-gray-500">成本</p>
                        <p className="text-slate-800 font-semibold">${pos.cost.toFixed(2)}</p>
                      </div>
                      <div>
                        <p className="text-gray-500">損益</p>
                        <p className={`font-bold ${profitLoss >= 0 ? 'text-red-400' : 'text-green-400'}`}>
                          {profitLoss >= 0 ? '+' : ''}${profitLoss.toFixed(2)}
                          <span className="text-xs ml-1">
                            ({profitLoss >= 0 ? '+' : ''}{profitLossPercent.toFixed(2)}%)
                          </span>
                        </p>
                      </div>
                    </div>
                    
                    {pos.notes && (
                      <p className="text-gray-400 text-xs mt-2 italic">💬 {pos.notes}</p>
                    )}
                  </div>

                  <div className="flex gap-2">
                    <button
                      onClick={() => setEditingPosition(pos)}
                      className="p-2 text-gray-500 hover:text-blue-400 hover:bg-blue-500/10 rounded-lg transition-colors"
                      title="編輯持倉"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                    </button>
                    <button
                      onClick={() => handleDelete(pos.id)}
                      className="p-2 text-gray-500 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-colors"
                      title="刪除持倉"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            );
            })}
          </div>
        )}
      </div>

      {/* 新增持倉 Modal */}
      <AddPositionModal
        isOpen={showAddModal}
        onClose={() => setShowAddModal(false)}
        onPositionAdded={loadPositions}
      />

      {/* 編輯持倉 Modal */}
      <EditPositionModal
        position={editingPosition}
        isOpen={!!editingPosition}
        onClose={() => setEditingPosition(null)}
        onPositionUpdated={loadPositions}
      />
    </div>
  );
};
