import { useEffect, useState } from 'react';
import { positionService, Position, PortfolioSummary } from '@/services/positionService';
import { stockService } from '@/services/stockService';
import { Button } from '@/components/ui/Button';
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
          const history = await stockService.getHistoricalData(pos.symbol, '1d');
          const latestPrice = history[history.length - 1]?.price || pos.current_price || 0;
          return { symbol: pos.symbol, price: latestPrice };
        } catch {
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
      <div className="text-center text-gray-400 py-8">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500"></div>
        <p className="mt-2">載入持倉...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 投資組合總覽 */}
      {summary && (
        <div className="glass rounded-2xl p-6 border border-indigo-500/30">
          <h3 className="text-xl font-bold text-white mb-4">📊 投資組合總覽</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-gray-400 text-sm mb-1">持倉數量</p>
              <p className="text-2xl font-bold text-white">{summary.total_positions}</p>
            </div>
            <div>
              <p className="text-gray-400 text-sm mb-1">總成本</p>
              <p className="text-2xl font-bold text-white">${summary.total_cost.toFixed(2)}</p>
            </div>
            <div>
              <p className="text-gray-400 text-sm mb-1">市值</p>
              <p className="text-2xl font-bold text-white">
                ${(() => {
                  const totalMarketValue = positions.reduce((sum, pos) => {
                    const currentPrice = latestPrices[pos.symbol] || pos.current_price || 0;
                    return sum + (pos.quantity * currentPrice);
                  }, 0);
                  return totalMarketValue.toFixed(2);
                })()}
              </p>
            </div>
            <div>
              <p className="text-gray-400 text-sm mb-1">損益</p>
              <p className={`text-2xl font-bold ${(() => {
                const totalMarketValue = positions.reduce((sum, pos) => {
                  const currentPrice = latestPrices[pos.symbol] || pos.current_price || 0;
                  return sum + (pos.quantity * currentPrice);
                }, 0);
                const profitLoss = totalMarketValue - summary.total_cost;
                return profitLoss >= 0 ? 'text-red-400' : 'text-green-400';
              })()}`}>
                {(() => {
                  const totalMarketValue = positions.reduce((sum, pos) => {
                    const currentPrice = latestPrices[pos.symbol] || pos.current_price || 0;
                    return sum + (pos.quantity * currentPrice);
                  }, 0);
                  const profitLoss = totalMarketValue - summary.total_cost;
                  return `${profitLoss >= 0 ? '+' : ''}$${profitLoss.toFixed(2)}`;
                })()}
              </p>
              <p className={`text-sm ${(() => {
                const totalMarketValue = positions.reduce((sum, pos) => {
                  const currentPrice = latestPrices[pos.symbol] || pos.current_price || 0;
                  return sum + (pos.quantity * currentPrice);
                }, 0);
                const profitLoss = totalMarketValue - summary.total_cost;
                return profitLoss >= 0 ? 'text-red-400' : 'text-green-400';
              })()}`}>
                {(() => {
                  const totalMarketValue = positions.reduce((sum, pos) => {
                    const currentPrice = latestPrices[pos.symbol] || pos.current_price || 0;
                    return sum + (pos.quantity * currentPrice);
                  }, 0);
                  const profitLoss = totalMarketValue - summary.total_cost;
                  const profitLossPercent = summary.total_cost > 0 ? (profitLoss / summary.total_cost * 100) : 0;
                  return `(${profitLoss >= 0 ? '+' : ''}${profitLossPercent.toFixed(2)}%)`;
                })()}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* 持倉列表 */}
      <div className="glass rounded-2xl p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-xl font-bold text-white">📈 持倉明細</h3>
          <Button
            onClick={() => setShowAddModal(true)}
            className="w-auto px-4 py-2"
          >
            + 新增持倉
          </Button>
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
                      <h4 className="text-lg font-bold text-white">{pos.symbol}</h4>
                      <span className="text-sm text-gray-400">x {pos.quantity}</span>
                    </div>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                      <div>
                        <p className="text-gray-500">買入均價</p>
                        <p className="text-white font-medium">${pos.buy_price.toFixed(2)}</p>
                      </div>
                      <div>
                        <p className="text-gray-500">當前價</p>
                        <p className="text-white font-medium">
                          ${currentPrice.toFixed(2)}
                        </p>
                      </div>
                      <div>
                        <p className="text-gray-500">成本</p>
                        <p className="text-white font-medium">${pos.cost.toFixed(2)}</p>
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
