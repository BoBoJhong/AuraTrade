import React, { useState } from 'react';
import { positionService, CreatePositionRequest } from '@/services/positionService';
import { Button } from '@/components/ui/Button';

interface AddPositionModalProps {
  isOpen: boolean;
  onClose: () => void;
  onPositionAdded?: () => void;
}

const AddPositionModal: React.FC<AddPositionModalProps> = ({
  isOpen,
  onClose,
  onPositionAdded
}) => {
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState<CreatePositionRequest>({
    symbol: '',
    quantity: 0,
    buy_price: 0,
    buy_date: new Date().toISOString().split('T')[0], // 預設今天
    notes: ''
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // 驗證
    if (!formData.symbol.trim()) {
      alert('請輸入股票代碼');
      return;
    }
    
    if (formData.quantity <= 0) {
      alert('請輸入有效的股數（大於 0）');
      return;
    }
    
    if (formData.buy_price <= 0) {
      alert('請輸入有效的買入價格（大於 0）');
      return;
    }

    setLoading(true);

    try {
      // 確保股票代碼格式正確（台股自動加 .TW）
      let symbol = formData.symbol.trim().toUpperCase();
      if (!symbol.includes('.') && /^\d{4}$/.test(symbol)) {
        symbol = `${symbol}.TW`;
      }

      await positionService.createPosition({
        ...formData,
        symbol
      });
      
      alert('持倉新增成功！');
      
      // 重置表單
      setFormData({
        symbol: '',
        quantity: 0,
        buy_price: 0,
        buy_date: new Date().toISOString().split('T')[0],
        notes: ''
      });

      onPositionAdded?.();
      onClose();
    } catch (error: any) {
      console.error('新增持倉失敗:', error);
      alert(error.response?.data?.detail || '新增持倉失敗');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-gradient-to-br from-gray-900 via-purple-900/20 to-gray-900 rounded-2xl shadow-2xl max-w-md w-full border border-white/10 animate-fadeIn">
        {/* 標題列 */}
        <div className="flex justify-between items-center p-6 border-b border-white/10">
          <h2 className="text-2xl font-bold text-white flex items-center">
            <span className="text-3xl mr-3">📊</span>
            新增持倉
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
          {/* 股票代碼 */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              股票代碼 <span className="text-red-400">*</span>
            </label>
            <input
              type="text"
              value={formData.symbol}
              onChange={(e) => setFormData({ ...formData, symbol: e.target.value })}
              placeholder="例如：2330 或 AAPL"
              className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
              required
            />
            <p className="text-xs text-gray-500 mt-1">
              台股代碼會自動加上 .TW 後綴
            </p>
          </div>

          {/* 股數 */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              股數 <span className="text-red-400">*</span>
            </label>
            <input
              type="number"
              value={formData.quantity || ''}
              onChange={(e) => setFormData({ ...formData, quantity: parseInt(e.target.value) || 0 })}
              placeholder="例如：1000"
              min="1"
              step="1"
              className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
              required
            />
          </div>

          {/* 買入價格 */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              買入價格 <span className="text-red-400">*</span>
            </label>
            <input
              type="number"
              value={formData.buy_price || ''}
              onChange={(e) => setFormData({ ...formData, buy_price: parseFloat(e.target.value) || 0 })}
              placeholder="例如：625.00"
              min="0.01"
              step="0.01"
              className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
              required
            />
          </div>

          {/* 買入日期 */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              買入日期 <span className="text-red-400">*</span>
            </label>
            <input
              type="date"
              value={formData.buy_date}
              onChange={(e) => setFormData({ ...formData, buy_date: e.target.value })}
              max={new Date().toISOString().split('T')[0]} // 不能選未來日期
              className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
              required
            />
          </div>

          {/* 備註 */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              備註（選填）
            </label>
            <textarea
              value={formData.notes}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
              placeholder="記錄買入原因或策略..."
              rows={3}
              className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all resize-none"
            />
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
              className="flex-1 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600"
              disabled={loading}
            >
              {loading ? '新增中...' : '新增持倉'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AddPositionModal;
