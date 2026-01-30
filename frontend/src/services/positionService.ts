import axios from '@/lib/axios';

export interface Position {
  id: number;
  user_id: string;
  symbol: string;
  quantity: number;
  buy_price: number;
  buy_date: string;
  notes: string | null;
  created_at: string;
  updated_at: string;
  
  // 計算欄位
  current_price: number | null;
  market_value: number | null;
  cost: number;
  profit_loss: number;
  profit_loss_percent: number;
}

export interface CreatePositionRequest {
  symbol: string;
  quantity: number;
  buy_price: number;
  buy_date: string;
  notes?: string;
}

export interface UpdatePositionRequest {
  quantity?: number;
  buy_price?: number;
  buy_date?: string;
  notes?: string;
}

export interface PortfolioSummary {
  total_positions: number;
  total_cost: number;
  total_market_value: number;
  total_profit_loss: number;
  total_profit_loss_percent: number;
}

export const positionService = {
  // 查詢所有持倉
  async getPositions(): Promise<Position[]> {
    const response = await axios.get('/positions');
    return response.data;
  },

  // 建立持倉
  async createPosition(data: CreatePositionRequest): Promise<Position> {
    const response = await axios.post('/positions', data);
    return response.data;
  },

  // 更新持倉
  async updatePosition(positionId: number, data: UpdatePositionRequest): Promise<Position> {
    const response = await axios.patch(`/positions/${positionId}`, data);
    return response.data;
  },

  // 刪除持倉
  async deletePosition(positionId: number): Promise<void> {
    await axios.delete(`/positions/${positionId}`);
  },

  // 取得投資組合總覽
  async getPortfolioSummary(): Promise<PortfolioSummary> {
    const response = await axios.get('/positions/summary');
    return response.data;
  }
};
