import React, { useState, useEffect } from 'react';
import { alertService, AlertType, PriceAlert, CreateAlertRequest } from '@/services/alertService';
import { Button } from '@/components/ui/Button';

interface AlertModalProps {
  symbol: string;
  stockName: string;
  currentPrice: number;
  isOpen: boolean;
  onClose: () => void;
  onAlertCreated?: () => void;
}

const AlertModal: React.FC<AlertModalProps> = ({
  symbol,
  stockName,
  currentPrice,
  isOpen,
  onClose,
  onAlertCreated
}) => {
  const [alerts, setAlerts] = useState<PriceAlert[]>([]);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState<CreateAlertRequest>({
    symbol,
    alert_type: AlertType.PRICE_ABOVE,
    target_value: currentPrice * 1.05,
    base_price: currentPrice,
    message: ''
  });

  // 載入該股票的提醒
  useEffect(() => {
    if (isOpen) {
      loadAlerts();
    }
  }, [isOpen, symbol]);

  const loadAlerts = async () => {
    try {
      const data = await alertService.getAlertsByStock(symbol);
      setAlerts(data);
    } catch (error) {
      console.error('載入提醒失敗:', error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      await alertService.createAlert(formData);
      
      // 重置表單
      setFormData({
        symbol,
        alert_type: AlertType.PRICE_ABOVE,
        target_value: currentPrice * 1.05,
        base_price: currentPrice,
        message: ''
      });

      await loadAlerts();
      onAlertCreated?.();
      
      alert('提醒建立成功！');
    } catch (error: any) {
      console.error('建立提醒失敗:', error);
      alert(error.response?.data?.detail || '建立提醒失敗');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (alertId: number) => {
    if (!confirm('確定要刪除此提醒嗎？')) return;

    try {
      await alertService.deleteAlert(alertId);
      await loadAlerts();
      alert('提醒已刪除');
    } catch (error) {
      console.error('刪除提醒失敗:', error);
      alert('刪除失敗');
    }
  };

  const handleToggle = async (alertId: number, isActive: boolean) => {
    try {
      await alertService.toggleAlert(alertId, !isActive);
      await loadAlerts();
    } catch (error) {
      console.error('切換提醒狀態失敗:', error);
    }
  };

  const getAlertTypeLabel = (type: AlertType) => {
    switch (type) {
      case AlertType.PRICE_ABOVE: return '價格達到或超過';
      case AlertType.PRICE_BELOW: return '價格達到或低於';
      case AlertType.PERCENT_UP: return '上漲';
      case AlertType.PERCENT_DOWN: return '下跌';
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-500 to-purple-600 text-white p-6">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-2xl font-bold">{stockName}</h2>
              <p className="text-blue-100 mt-1">{symbol} · 當前價格: ${currentPrice.toFixed(2)}</p>
            </div>
            <button onClick={onClose} className="text-white/80 hover:text-white text-2xl">
              ✕
            </button>
          </div>
        </div>

        <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
          {/* 建立提醒表單 */}
          <form onSubmit={handleSubmit} className="mb-8">
            <h3 className="text-lg font-bold mb-4 text-gray-900">🔔 建立新提醒</h3>
            
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <label htmlFor="alert-type" className="block text-sm font-medium mb-2 text-gray-700">提醒類型</label>
                <select
                  id="alert-type"
                  name="alert-type"
                  value={formData.alert_type}
                  onChange={(e) => setFormData({ 
                    ...formData, 
                    alert_type: e.target.value as AlertType,
                    base_price: e.target.value.includes('percent') ? currentPrice : undefined
                  })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white text-gray-900"
                >
                  <option value={AlertType.PRICE_ABOVE}>價格達到或超過</option>
                  <option value={AlertType.PRICE_BELOW}>價格達到或低於</option>
                  <option value={AlertType.PERCENT_UP}>上漲百分比</option>
                  <option value={AlertType.PERCENT_DOWN}>下跌百分比</option>
                </select>
              </div>

              <div>
                <label htmlFor="alert-type" className="block text-sm font-medium mb-2 text-gray-700">
                  {formData.alert_type.includes('percent') ? '百分比 (%)' : '目標價格 ($)'}
                </label>
                <input
                  id="target-value"
                  name="target-value"
                  type="number"
                  step="0.01"
                  value={formData.target_value}
                  onChange={(e) => setFormData({ ...formData, target_value: parseFloat(e.target.value) })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white text-gray-900"
                  required
                />
              </div>
            </div>

            {formData.alert_type.includes('percent') && (
              <div className="mb-4">
                <label htmlFor="base-price" className="block text-sm font-medium mb-2 text-gray-700">基準價格 ($)</label>
                <input
                  id="base-price"
                  name="base-price"
                  type="number"
                  step="0.01"
                  value={formData.base_price || currentPrice}
                  onChange={(e) => setFormData({ ...formData, base_price: parseFloat(e.target.value) })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white text-gray-900"
                />
              </div>
            )}

            <div className="mb-4">
              <label htmlFor="alert-message" className="block text-sm font-medium mb-2 text-gray-700">提醒訊息（選填）</label>
              <input
                id="alert-message"
                name="alert-message"
                type="text"
                value={formData.message || ''}
                onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                placeholder="例如：達到目標價，考慮獲利了結"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white text-gray-900 placeholder-gray-400"
              />
            </div>

            <Button type="submit" disabled={loading} className="w-full">
              {loading ? '建立中...' : '建立提醒'}
            </Button>
          </form>

          {/* 現有提醒列表 */}
          <div>
            <h3 className="text-lg font-bold mb-4 text-gray-900">📋 現有提醒 ({alerts.length})</h3>
            {alerts.length === 0 ? (
              <p className="text-gray-500 text-center py-8">尚無提醒</p>
            ) : (
              <div className="space-y-3">
                {alerts.map((alert) => (
                  <div
                    key={alert.id}
                    className={`border rounded-lg p-4 ${
                      alert.is_triggered ? 'bg-yellow-50 border-yellow-300' :
                      alert.is_active ? 'bg-white border-gray-200' : 'bg-gray-50 border-gray-300'
                    }`}
                  >
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <span className={`px-2 py-1 rounded text-xs font-medium ${
                            alert.is_triggered ? 'bg-yellow-200 text-yellow-800' :
                            alert.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-200 text-gray-600'
                          }`}>
                            {alert.is_triggered ? '✓ 已觸發' : alert.is_active ? '● 啟用中' : '○ 已停用'}
                          </span>
                        </div>
                        
                        <p className="font-medium">
                          {getAlertTypeLabel(alert.alert_type)} {' '}
                          {alert.alert_type.includes('percent') 
                            ? `${alert.target_value}%` 
                            : `$${alert.target_value.toFixed(2)}`
                          }
                        </p>
                        
                        {alert.base_price && (
                          <p className="text-sm text-gray-600 mt-1">
                            基準價格: ${alert.base_price.toFixed(2)}
                          </p>
                        )}
                        
                        {alert.message && (
                          <p className="text-sm text-gray-600 mt-1 italic">"{alert.message}"</p>
                        )}
                        
                        {alert.triggered_at && (
                          <p className="text-xs text-gray-500 mt-2">
                            觸發時間: {new Date(alert.triggered_at).toLocaleString('zh-TW')}
                          </p>
                        )}
                      </div>

                      <div className="flex gap-2 ml-4">
                        {!alert.is_triggered && (
                          <button
                            onClick={() => handleToggle(alert.id, alert.is_active)}
                            className="px-3 py-1 text-sm rounded bg-blue-50 text-blue-600 hover:bg-blue-100"
                          >
                            {alert.is_active ? '停用' : '啟用'}
                          </button>
                        )}
                        <button
                          onClick={() => handleDelete(alert.id)}
                          className="px-3 py-1 text-sm rounded bg-red-50 text-red-600 hover:bg-red-100"
                        >
                          刪除
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AlertModal;
