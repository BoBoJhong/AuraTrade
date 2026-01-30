import axios from '@/lib/axios';

export enum AlertType {
  PRICE_ABOVE = 'price_above',
  PRICE_BELOW = 'price_below',
  PERCENT_UP = 'percent_up',
  PERCENT_DOWN = 'percent_down',
}

export interface PriceAlert {
  id: number;
  user_id: string;
  symbol: string;
  alert_type: AlertType;
  target_value: number;
  base_price: number | null;
  is_active: boolean;
  is_triggered: boolean;
  triggered_at: string | null;
  message: string | null;
  created_at: string;
  updated_at: string;
}

export interface CreateAlertRequest {
  symbol: string;
  alert_type: AlertType;
  target_value: number;
  base_price?: number;
  message?: string;
}

export interface UpdateAlertRequest {
  is_active?: boolean;
  target_value?: number;
  message?: string;
}

export const alertService = {
  // 查詢所有提醒
  async getAlerts(activeOnly: boolean = true): Promise<PriceAlert[]> {
    const response = await axios.get('/alerts', {
      params: { active_only: activeOnly }
    });
    return response.data;
  },

  // 查詢特定股票的提醒
  async getAlertsByStock(symbol: string): Promise<PriceAlert[]> {
    const response = await axios.get(`/alerts/stock/${symbol}`);
    return response.data;
  },

  // 建立提醒
  async createAlert(data: CreateAlertRequest): Promise<PriceAlert> {
    const response = await axios.post('/alerts', data);
    return response.data;
  },

  // 更新提醒
  async updateAlert(alertId: number, data: UpdateAlertRequest): Promise<PriceAlert> {
    const response = await axios.patch(`/alerts/${alertId}`, data);
    return response.data;
  },

  // 刪除提醒
  async deleteAlert(alertId: number): Promise<void> {
    await axios.delete(`/alerts/${alertId}`);
  },

  // 切換提醒啟用狀態
  async toggleAlert(alertId: number, isActive: boolean): Promise<PriceAlert> {
    return this.updateAlert(alertId, { is_active: isActive });
  },

  // 檢查並觸發提醒
  async checkAlerts(): Promise<{ checked: number; triggered: number; message: string }> {
    const response = await axios.post('/alerts/check');
    return response.data;
  }
};
