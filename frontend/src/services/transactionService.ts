import api from '@/lib/axios'

export interface Transaction {
  id: number
  user_id: string
  stock_symbol: string
  transaction_type: 'buy' | 'sell'
  quantity: number
  price: number
  commission: number
  tax: number
  total_amount: number
  transaction_date: string
  notes?: string
  created_at: string
}

export interface TransactionStats {
  total_transactions: number
  total_buy_amount: number
  total_sell_amount: number
  total_commission: number
  total_tax: number
  net_profit_loss: number
  net_profit: number
}

export interface TransactionCreate {
  stock_symbol: string
  transaction_type: 'buy' | 'sell'
  quantity: number
  price: number
  commission?: number
  tax?: number
  transaction_date: string
  notes?: string
}

export const transactionService = {
  // 獲取所有交易記錄
  getTransactions: async (skip: number = 0, limit: number = 100): Promise<Transaction[]> => {
    const response = await api.get('/transactions', {
      params: { skip, limit }
    })
    return response.data
  },

  // 獲取交易統計
  getStats: async (): Promise<TransactionStats> => {
    const response = await api.get('/transactions/summary/stats')
    const data = response.data
    return {
      ...data,
      net_profit: data.net_profit_loss,
    }
  },

  // 建立交易記錄
  createTransaction: async (data: TransactionCreate): Promise<Transaction> => {
    const response = await api.post('/transactions', data)
    return response.data
  },

  // 刪除交易記錄
  deleteTransaction: async (id: number): Promise<void> => {
    await api.delete(`/transactions/${id}`)
  }
}
