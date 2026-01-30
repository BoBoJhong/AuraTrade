import React, { useState, useEffect } from 'react';
import { positionService, UpdatePositionRequest, Position } from '@/services/positionService';
import { Button } from '@/components/ui/Button';

interface EditPositionModalProps {
  position: Position | null;
  isOpen: boolean;
  onClose: () => void;
  onPositionUpdated?: () => void;
}

const EditPositionModal: React.FC<EditPositionModalProps> = ({
  position,
  isOpen,
  onClose,
  onPositionUpdated
}) => {
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState<UpdatePositionRequest>({
    quantity: 0,
    buy_price: 0,
    buy_date: '',
    notes: ''
  });

  // 當 position 變化時更新表單
  useEffect(() => {
    if (position) {
      setFormData({
        quantity: position.quantity,
        buy_price: position.buy_price,
        buy_date: position.buy_date,
        notes: position.notes || ''
      });
    }
  }, [position]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!position) return;
    
    // 驗證
    if (formData.quantity && formData.quantity <= 0) {
      alert('請輸入有效的股數（大於 0）');
      return;
    }
    
    if (formData.buy_price && formData.buy_price <= 0) {
      alert('請輸入有效的買入價格（大於 0）');
      return;
    }

    setLoading(true);

    try {
      await positionService.updatePosition(position.id, formData);
      
      alert('持倉更新成功！');
      onPositionUpdated?.();
      onClose();
    } catch (error: any) {
      console.error('更新持倉失敗:', error);
      alert(error.response?.data?.detail || '更新持倉失敗');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen || !position) return null;

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-gradient-to-br from-gray-900 via-indigo-900/20 to-gray-900 rounded-2xl shadow-2xl max-w-md w-full border border-white/10 animate-fadeIn">
        {/* 標題列 */}
        <div className="flex justify-between items-center p-6 border-b border-white/10">
          <h2 className="text-2xl font-bold text-white flex items-center">
            <span className="text-3xl mr-3">✏️</span>
            編輯持倉 - {position.symbol}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* 表單內容 */}
        <form onSubmit={handleSubmit} className="p-6 space-y-5">
          {/* 股數 */}
          <div>
            <label htmlFor="position-quantity" className="block text-sm font-medium text-gray-300 mb-2">
              股數
            </label>
            <input
              id="position-quantity"
              name="position-quantity"
              type="number"
              value={formData.quantity || ''}
              onChange={(e) => setFormData({ ...formData, quantity: parseInt(e.target.value) || 0 })}
              placeholder="例如：1000"
              min="1"
              step="1"
              className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
            />
          </div>

          {/* 買入價格 */}
          <div>
            <label htmlFor="position-buy-price" className="block text-sm font-medium text-gray-300 mb-2">
              買入價格
            </label>
            <input
              id="position-buy-price"
              name="position-buy-price"
              type="number"
              value={formData.buy_price || ''}
              onChange={(e) => setFormData({ ...formData, buy_price: parseFloat(e.target.value) || 0 })}
              placeholder="例如：625.00"
              min="0.01"
              step="0.01"
              className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
            />
          </div>

          {/* 買入日期 */}
          <div>
            <label htmlFor="position-buy-date" className="block text-sm font-medium text-gray-300 mb-2">
              買入日期
            </label>
            <input
              id="position-buy-date"
              name="position-buy-date"
              type="date"
              value={formData.buy_date}
              onChange={(e) => setFormData({ ...formData, buy_date: e.target.value })}
              max={new Date().toISOString().split('T')[0]}
              className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
            />
          </div>

          {/* 備註 */}
          <div>
            <label htmlFor="position-notes" className="block text-sm font-medium text-gray-300 mb-2">
              備註
            </label>
            <textarea
              id="position-notes"
              name="position-notes"
              value={formData.notes}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
              placeholder="記錄買入原因或策略..."
              rows={3}
              className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all resize-none"
            />
          </div>

          {/* 當前持倉成本資訊 */}
          <div className="bg-indigo-500/10 border border-indigo-500/30 rounded-lg p-4">
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div>
                <p className="text-gray-400">當前成本</p>
                <p className="text-white font-semibold">${position.cost.toFixed(2)}</p>
              </div>
              <div>
                <p className="text-gray-400">市值</p>
                <p className="text-white font-semibold">${position.market_value.toFixed(2)}</p>
              </div>
              <div className="col-span-2">
                <p className="text-gray-400">損益</p>
                <p className={`font-bold ${position.profit_loss >= 0 ? 'text-red-400' : 'text-green-400'}`}>
                  {position.profit_loss >= 0 ? '+' : ''}${position.profit_loss.toFixed(2)}
                  <span className="text-xs ml-2">
                    ({position.profit_loss >= 0 ? '+' : ''}{position.profit_loss_percent.toFixed(2)}%)
                  </span>
                </p>
              </div>
            </div>
          </div>

          {/* 按鈕組 */}
          <div className="flex gap-3 pt-4">
            <Button
              type="button"
              onClick={onClose}
              className="flex-1 bg-gray-700 hover:bg-gray-600"
              disabled={loading}
            >
              取消
            </Button>
            <Button
              type="submit"
              className="flex-1 bg-gradient-to-r from-indigo-500 to-purple-500 hover:from-indigo-600 hover:to-purple-600"
              disabled={loading}
            >
              {loading ? '儲存中...' : '儲存變更'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default EditPositionModal;
