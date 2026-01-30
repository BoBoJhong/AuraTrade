import api from '@/lib/axios'

export interface Position {
  id: number
  user_id: string
  symbol: string
  quantity: number
  buy_price: number
  current_price?: number
  cost: number
  market_value?: number
  profit_loss?: number
  profit_loss_percent?: number
}

export interface PortfolioSummary {
  total_positions: number
  total_cost: number
  total_market_value: number
  total_profit_loss: number
  total_profit_loss_percent: number
  positions: Position[]
}

export const portfolioService = {
  // 獲取投資組合摘要
  getSummary: async (): Promise<PortfolioSummary> => {
    const response = await api.get('/portfolio/summary')
    return response.data
  },

  // 獲取所有持倉
  getPositions: async (): Promise<Position[]> => {
    const response = await api.get('/portfolio')
    return response.data
  }
}
