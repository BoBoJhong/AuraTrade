/// <reference types="vite/client" />
import { api } from '../lib/axios'

export interface Stock {
    symbol: string
    name: string
    market: string
    sector?: string
    price?: number
    change?: number
    change_percent?: number
}

export interface WatchlistItem {
    id: number
    stock: Stock
    target_price?: number
}

export interface HistoricalData {
    date: string
    price: number
    volume?: number
}

export interface TechnicalIndicators {
    ma: {
        ma5: (number | null)[]
        ma10: (number | null)[]
        ma20: (number | null)[]
        ma60: (number | null)[]
    }
    macd: {
        macd: (number | null)[]
        signal: (number | null)[]
        histogram: (number | null)[]
    }
    rsi: (number | null)[]
    kdj: {
        k: (number | null)[]
        d: (number | null)[]
        j: (number | null)[]
    }
}

export interface PriceData {
    date: string
    open: number
    high: number
    low: number
    close: number
    volume: number
    ma5?: number
    ma10?: number
    ma20?: number
    ma60?: number
    macd?: number
    signal?: number
    histogram?: number
    rsi?: number
    kdj_k?: number
    kdj_d?: number
    kdj_j?: number
}

export interface Recommendation {
    action: 'BUY' | 'SELL' | 'HOLD'
    score: number
    reasons: string[]
}

interface RecommendationApiStock {
    symbol: string
    stock_name?: string
    name?: string
    price: number
    change_percent: number
    ai_score?: number
    score?: number
    reasons: string[]
    market: string
}

interface RecommendationApiResponse {
    total: number
    stocks: RecommendationApiStock[]
}

export interface StockData {
    info: Stock
    prices: PriceData[]
    recommendation?: Recommendation
}

export const stockService = {
    search: async (query: string): Promise<Stock[]> => {
        const response = await api.get<Stock[]>(`/stocks/search`, {
            params: { q: query },
        })
        return response.data
    },

    getQuote: async (symbol: string): Promise<Stock> => {
        const response = await api.get<Stock>(`/stocks/${symbol}`)
        return response.data
    },

    getWatchlist: async (): Promise<WatchlistItem[]> => {
        const response = await api.get<WatchlistItem[]>('/watchlist')
        return response.data
    },

    addToWatchlist: async (symbol: string, targetPrice?: number): Promise<WatchlistItem> => {
        const response = await api.post<WatchlistItem>('/watchlist', {
            symbol,
            target_price: targetPrice,
        })
        return response.data
    },

    removeFromWatchlist: async (symbol: string): Promise<void> => {
        await api.delete(`/watchlist/${symbol}`)
    },

    getHistoricalData: async (
        symbol: string, 
        period: string = '1mo',
        interval: string = '1d'
    ): Promise<HistoricalData[]> => {
        const response = await api.get<any[]>(`/stocks/${symbol}/history`, {
            params: { period, interval },
        })
        // Transform backend format (close) to frontend format (price)
        return response.data.map((item: any) => ({
            date: item.date,
            price: item.close,
            volume: item.volume
        }))
    },

    getTechnicalIndicators: async (
        symbol: string,
        period: string = '1mo',
        interval: string = '1d'
    ): Promise<TechnicalIndicators> => {
        const response = await api.get<any>(`/stocks/${symbol}/indicators`, {
            params: { period, interval },
        })
        return response.data.indicators
    },

    getStockData: async (symbol: string, period: string = '1mo'): Promise<StockData> => {
        // 並行獲取股票資訊、歷史數據和技術指標
        const [quote, historyResponse, indicatorsResponse] = await Promise.all([
            api.get<Stock>(`/stocks/${symbol}`),
            api.get<any>(`/stocks/${symbol}/history`, { params: { period } }),
            api.get<any>(`/stocks/${symbol}/indicators`, { params: { period } })
        ])

        const stock = quote.data
        const history = historyResponse.data
        const indicators = indicatorsResponse.data

        // 合併歷史數據和技術指標
        const prices: PriceData[] = history.map((item: any, index: number) => ({
            date: item.date.split('T')[0], // 只取日期部分
            open: item.open || item.close * 0.995,
            high: item.high || item.close * 1.005,
            low: item.low || item.close * 0.995,
            close: item.close,
            volume: item.volume || 0,
            ma5: indicators.indicators?.ma?.ma5?.[index] || undefined,
            ma10: indicators.indicators?.ma?.ma10?.[index] || undefined,
            ma20: indicators.indicators?.ma?.ma20?.[index] || undefined,
            ma60: indicators.indicators?.ma?.ma60?.[index] || undefined,
            macd: indicators.indicators?.macd?.macd?.[index] || undefined,
            signal: indicators.indicators?.macd?.signal?.[index] || undefined,
            histogram: indicators.indicators?.macd?.histogram?.[index] || undefined,
            rsi: indicators.indicators?.rsi?.[index] || undefined,
            kdj_k: indicators.indicators?.kdj?.k?.[index] || undefined,
            kdj_d: indicators.indicators?.kdj?.d?.[index] || undefined,
            kdj_j: indicators.indicators?.kdj?.j?.[index] || undefined
        }))

        return {
            info: stock,
            prices,
            recommendation: indicators.recommendation
        }
    },

    getRecommendations: async (
        market?: string,
        limit: number = 10
    ): Promise<any[]> => {
        const response = await api.get<RecommendationApiResponse>('/recommendations', {
            params: { market, limit },
        })

        const stocks = response.data?.stocks || []
        return stocks.map((item) => ({
            symbol: item.symbol,
            name: item.stock_name || item.name || item.symbol,
            price: item.price,
            change_percent: item.change_percent,
            // Backend enhanced score is 0-100, UI card expects roughly 0-10 display.
            score: Number((((item.ai_score ?? item.score ?? 0) / 10)).toFixed(1)),
            reasons: item.reasons || [],
            market: item.market,
        }))
    }
}
