import { useState, useEffect } from 'react';
import { alertService, PriceAlert } from '@/services/alertService';

export const NotificationBell = () => {
  const [notifications, setNotifications] = useState<PriceAlert[]>([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);

  // 定期檢查觸發的提醒
  useEffect(() => {
    const checkAlerts = async () => {
      try {
        // 先調用後端檢查並觸發提醒
        await alertService.checkAlerts();
        
        // 然後獲取觸發的提醒
        const alerts = await alertService.getAlerts(true);
        const triggered = alerts.filter(alert => alert.is_triggered && alert.is_active);
        setNotifications(triggered);
        setUnreadCount(triggered.length);
      } catch (error) {
        console.error('獲取提醒失敗:', error);
      }
    };

    checkAlerts();
    // 每 30 秒檢查一次
    const interval = setInterval(checkAlerts, 30000);

    return () => clearInterval(interval);
  }, []);

  const handleMarkAsRead = async (alertId: number) => {
    try {
      // 停用該提醒以標記為已讀
      await alertService.updateAlert(alertId, { is_active: false });
      
      // 更新本地狀態
      setNotifications(prev => prev.filter(n => n.id !== alertId));
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (error) {
      console.error('標記為已讀失敗:', error);
    }
  };

  const formatAlertMessage = (alert: PriceAlert) => {
    const typeText = {
      'price_above': '達到目標價',
      'price_below': '跌破目標價',
      'percent_up': '上漲',
      'percent_down': '下跌'
    }[alert.alert_type] || '提醒';

    const value = alert.alert_type.includes('percent') 
      ? `${alert.target_value}%` 
      : `$${alert.target_value}`;

    return `${alert.symbol} ${typeText} ${value}`;
  };

  return (
    <div className="relative">
      {/* 鈴鐺圖示 */}
      <button
        onClick={() => setShowDropdown(!showDropdown)}
        className="relative p-2 rounded-lg text-gray-300 hover:text-white hover:bg-gray-800/50 transition-all"
      >
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
        </svg>
        
        {/* 未讀數量徽章 */}
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs font-bold rounded-full w-5 h-5 flex items-center justify-center animate-pulse">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {/* 通知下拉選單 */}
      {showDropdown && (
        <>
          {/* 遮罩層 */}
          <div 
            className="fixed inset-0 z-40" 
            onClick={() => setShowDropdown(false)}
          />
          
          {/* 下拉內容 */}
          <div className="absolute right-0 mt-2 w-80 bg-gray-900 border border-gray-800 rounded-xl shadow-2xl z-50 overflow-hidden">
            {/* 標題 */}
            <div className="bg-gradient-to-r from-indigo-600 to-purple-600 px-4 py-3">
              <h3 className="text-white font-bold">價格提醒 ({unreadCount})</h3>
            </div>

            {/* 通知列表 */}
            <div className="max-h-96 overflow-y-auto">
              {notifications.length === 0 ? (
                <div className="p-8 text-center text-gray-500">
                  <svg className="w-12 h-12 mx-auto mb-3 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                  </svg>
                  <p className="text-sm">暫無新通知</p>
                </div>
              ) : (
                notifications.map((alert) => (
                  <div
                    key={alert.id}
                    className="border-b border-gray-800 hover:bg-gray-800/50 transition-colors"
                  >
                    <div className="p-4">
                      <div className="flex items-start justify-between gap-3">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-yellow-400">🔔</span>
                            <span className="text-white font-medium text-sm">
                              {formatAlertMessage(alert)}
                            </span>
                          </div>
                          
                          {alert.message && (
                            <p className="text-gray-400 text-xs mb-2">{alert.message}</p>
                          )}
                          
                          <p className="text-gray-500 text-xs">
                            {alert.triggered_at && new Date(alert.triggered_at).toLocaleString('zh-TW', {
                              month: 'short',
                              day: 'numeric',
                              hour: '2-digit',
                              minute: '2-digit'
                            })}
                          </p>
                        </div>

                        <button
                          onClick={() => handleMarkAsRead(alert.id)}
                          className="text-gray-500 hover:text-white text-xs px-2 py-1 rounded hover:bg-gray-700 transition-colors"
                          title="標記為已讀"
                        >
                          ✕
                        </button>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>

            {/* 底部操作 */}
            {notifications.length > 0 && (
              <div className="border-t border-gray-800 p-2">
                <button
                  onClick={async () => {
                    // 全部標記為已讀
                    for (const alert of notifications) {
                      await handleMarkAsRead(alert.id);
                    }
                  }}
                  className="w-full text-center text-sm text-gray-400 hover:text-white py-2 rounded hover:bg-gray-800 transition-colors"
                >
                  全部標記為已讀
                </button>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
};
