import api from '@/lib/axios';

export interface ScreenerFilters {
  min_price?: number;
  max_price?: number;
  min_market_cap?: number;
  max_market_cap?: number;
  min_pe_ratio?: number;
  max_pe_ratio?: number;
  min_dividend_yield?: number;
  max_dividend_yield?: number;
  min_volume?: number;
  rsi_min?: number;
  rsi_max?: number;
  limit?: number;
}

export interface ScreenedStock {
  symbol: string;
  name: string;
  price: number;
  change: number;
  change_percent: number;
  volume: number;
  market_cap: number;
  pe_ratio?: number;
  dividend_yield?: number;
}

export interface AIPickStock extends ScreenedStock {
  ai_score: number;
  reasons: string[];
  recommendation: string;
}

export interface ScreenerResponse {
  total: number;
  stocks: ScreenedStock[];
  filters_applied: any;
}

export interface TrendingResponse {
  total: number;
  stocks: ScreenedStock[];
}

export interface AIPicksResponse {
  total: number;
  stocks: AIPickStock[];
  note: string;
}

export const screenerService = {
  // 智能選股器
  screenStocks: async (filters: ScreenerFilters): Promise<ScreenerResponse> => {
    const response = await api.get<ScreenerResponse>('/screener', {
      params: filters
    });
    return response.data;
  },

  // 熱門股票排行榜
  getTrendingStocks: async (limit: number = 10): Promise<TrendingResponse> => {
    const response = await api.get<TrendingResponse>('/stocks/trending', {
      params: { limit }
    });
    return response.data;
  },

  // AI 推薦股票
  getAIPicks: async (limit: number = 10): Promise<AIPicksResponse> => {
    const response = await api.get<AIPicksResponse>('/stocks/ai-picks', {
      params: { limit }
    });
    return response.data;
  }
};
