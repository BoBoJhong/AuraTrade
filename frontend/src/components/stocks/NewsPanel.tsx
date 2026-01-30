import { useState, useEffect } from 'react'
import api from '@/lib/axios'

interface NewsItem {
    id: number
    symbol: string
    title: string
    summary: string
    source: string
    url: string
    published_at: string
    sentiment: 'positive' | 'negative' | 'neutral' | null
    sentiment_score: number | null
}

interface SentimentStats {
    symbol: string
    days: number
    total_news: number
    positive_count: number
    negative_count: number
    neutral_count: number
    positive_ratio: number
    negative_ratio: number
    avg_sentiment_score: number
    sentiment_index: number
    sentiment_label: string
    positive_reasons: string[]
    negative_reasons: string[]
}

interface NewsPanelProps {
    symbol: string
    stockName?: string
}

export const NewsPanel = ({ symbol, stockName }: NewsPanelProps) => {
    const [news, setNews] = useState<NewsItem[]>([])
    const [stats, setStats] = useState<SentimentStats | null>(null)
    const [isLoading, setIsLoading] = useState(true)
    const [timeRange, setTimeRange] = useState<'1d' | '7d' | '30d'>('7d')
    const [isFetching, setIsFetching] = useState(false)

    const timeRangeDays = {
        '1d': 1,
        '7d': 7,
        '30d': 30
    }

    useEffect(() => {
        if (!symbol) return
        fetchNews()
        fetchStats()
    }, [symbol, timeRange])

    const fetchNews = async () => {
        try {
            setIsLoading(true)
            const response = await api.get(
                `/stocks/${symbol}/news`,
                {
                    params: {
                        days: timeRangeDays[timeRange],
                        limit: 20
                    }
                }
            )
            setNews(response.data.news || [])
        } catch (error) {
            console.error('Failed to fetch news:', error)
            setNews([])
        } finally {
            setIsLoading(false)
        }
    }

    const fetchStats = async () => {
        try {
            const response = await api.get(
                `/stocks/${symbol}/news/sentiment-stats`,
                {
                    params: {
                        days: timeRangeDays[timeRange]
                    }
                }
            )
            setStats(response.data)
        } catch (error) {
            console.error('Failed to fetch sentiment stats:', error)
        }
    }

    const handleFetchNews = async () => {
        try {
            setIsFetching(true)
            await api.post(`/stocks/${symbol}/news/fetch`)
            await fetchNews()
        } catch (error) {
            console.error('Failed to fetch new news:', error)
        } finally {
            setIsFetching(false)
        }
    }

    const getSentimentColor = (sentiment: string | null) => {
        switch (sentiment) {
            case 'positive':
                return 'bg-green-500/20 text-green-400 border-green-500/30'
            case 'negative':
                return 'bg-red-500/20 text-red-400 border-red-500/30'
            case 'neutral':
                return 'bg-gray-500/20 text-gray-400 border-gray-500/30'
            default:
                return 'bg-gray-500/20 text-gray-400 border-gray-500/30'
        }
    }

    const getSentimentIcon = (sentiment: string | null) => {
        switch (sentiment) {
            case 'positive':
                return '📈'
            case 'negative':
                return '📉'
            case 'neutral':
                return '➡️'
            default:
                return '❓'
        }
    }

    const formatDate = (dateStr: string) => {
        const date = new Date(dateStr)
        const now = new Date()
        const diffMs = now.getTime() - date.getTime()
        const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
        
        if (diffHours < 1) {
            const diffMins = Math.floor(diffMs / (1000 * 60))
            return `${diffMins} 分鐘前`
        } else if (diffHours < 24) {
            return `${diffHours} 小時前`
        } else {
            const diffDays = Math.floor(diffHours / 24)
            return `${diffDays} 天前`
        }
    }

    if (isLoading) {
        return (
            <div className="glass rounded-2xl p-4 md:p-8 animate-fadeIn">
                <div className="text-center text-gray-400">
                    <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500 mb-4"></div>
                    <p className="text-sm md:text-base">載入新聞中...</p>
                </div>
            </div>
        )
    }

    return (
        <div className="glass rounded-2xl p-4 md:p-6 animate-fadeIn">
            {/* Header with Sentiment Stats */}
            <div className="flex flex-col md:flex-row md:justify-between md:items-start gap-4 mb-4 md:mb-6">
                <div className="flex flex-col gap-3">
                    <div className="flex items-center gap-2 md:gap-3">
                        <svg className="w-5 h-5 md:w-6 md:h-6 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
                        </svg>
                        <h3 className="text-lg md:text-xl font-bold text-white">{stockName || symbol}</h3>
                        <span className="text-xs md:text-sm text-gray-500">({news.length} 則)</span>
                    </div>
                    
                    {/* Sentiment Index */}
                    {stats && stats.total_news > 0 && (
                        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-2 md:gap-3">
                            <div className={`px-3 md:px-4 py-2 rounded-lg border ${
                                stats.sentiment_index >= 65 ? 'bg-green-500/20 text-green-400 border-green-500/30' :
                                stats.sentiment_index >= 55 ? 'bg-green-500/10 text-green-300 border-green-500/20' :
                                stats.sentiment_index <= 35 ? 'bg-red-500/20 text-red-400 border-red-500/30' :
                                stats.sentiment_index <= 45 ? 'bg-red-500/10 text-red-300 border-red-500/20' :
                                'bg-gray-500/20 text-gray-400 border-gray-500/30'
                            }`}>
                                <div className="flex items-center gap-2">
                                    <span className="text-xl md:text-2xl font-bold">{stats.sentiment_index}</span>
                                    <div className="flex flex-col">
                                        <span className="text-xs">{stats.sentiment_label}</span>
                                        <span className="text-xs opacity-70">情緒指數</span>
                                    </div>
                                </div>
                            </div>
                            
                            <div className="flex items-center gap-2 text-xs md:text-sm flex-wrap">
                                <span className="text-green-400">📈 {stats.positive_count} ({stats.positive_ratio}%)</span>
                                <span className="text-red-400">📉 {stats.negative_count} ({stats.negative_ratio}%)</span>
                            </div>
                        </div>
                    )}
                </div>
                
                <button
                    onClick={handleFetchNews}
                    disabled={isFetching}
                    className="px-3 md:px-4 py-2 rounded-lg bg-indigo-500/20 text-indigo-400 hover:bg-indigo-500/30 border border-indigo-500/30 transition-all disabled:opacity-50 text-sm md:text-base tap-target flex-shrink-0"
                >
                    {isFetching ? '抓取中...' : '更新新聞'}
                </button>
            </div>

            {/* Time Range Filter */}
            <div className="flex gap-2 mb-4 md:mb-6 overflow-x-auto pb-2">
                {(['1d', '7d', '30d'] as const).map((range) => (
                    <button
                        key={range}
                        onClick={() => setTimeRange(range)}
                        className={`px-3 md:px-4 py-1.5 md:py-2 rounded-lg transition-all text-sm md:text-base whitespace-nowrap tap-target ${
                            timeRange === range
                                ? 'bg-indigo-500 text-white'
                                : 'bg-gray-800/50 text-gray-400 hover:bg-gray-700/50'
                        }`}
                    >
                        {range === '1d' ? '1天' : range === '7d' ? '7天' : '30天'}
                    </button>
                ))}
            </div>

            {/* Sentiment Reasons */}
            {stats && (stats.positive_reasons.length > 0 || stats.negative_reasons.length > 0) && (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-3 md:gap-4 mb-4 md:mb-6">
                    {/* Positive Reasons */}
                    {stats.positive_reasons.length > 0 && (
                        <div className="bg-green-500/10 border border-green-500/30 rounded-xl p-3 md:p-4">
                            <div className="flex items-center gap-2 mb-2 md:mb-3">
                                <span className="text-green-400 text-base md:text-lg">📈</span>
                                <h4 className="text-green-400 font-semibold text-sm md:text-base">利多原因</h4>
                            </div>
                            <ul className="space-y-1.5 md:space-y-2">
                                {stats.positive_reasons.map((reason, idx) => (
                                    <li key={idx} className="text-xs md:text-sm text-green-300 flex items-start gap-2">
                                        <span className="text-green-500 mt-1 flex-shrink-0">•</span>
                                        <span className="flex-1">{reason}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}
                    
                    {/* Negative Reasons */}
                    {stats.negative_reasons.length > 0 && (
                        <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-3 md:p-4">
                            <div className="flex items-center gap-2 mb-2 md:mb-3">
                                <span className="text-red-400 text-base md:text-lg">📉</span>
                                <h4 className="text-red-400 font-semibold text-sm md:text-base">利空原因</h4>
                            </div>
                            <ul className="space-y-1.5 md:space-y-2">
                                {stats.negative_reasons.map((reason, idx) => (
                                    <li key={idx} className="text-xs md:text-sm text-red-300 flex items-start gap-2">
                                        <span className="text-red-500 mt-1 flex-shrink-0">•</span>
                                        <span className="flex-1">{reason}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}
                </div>
            )}

            {/* News List */}
            {news.length === 0 ? (
                <div className="text-center py-8 md:py-12">
                    <svg className="w-12 h-12 md:w-16 md:h-16 mx-auto text-gray-600 mb-3 md:mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
                    </svg>
                    <p className="text-gray-400 mb-2 text-sm md:text-base">目前沒有新聞</p>
                    <p className="text-gray-600 text-xs md:text-sm">點擊上方「更新新聞」按鈕抓取最新消息</p>
                </div>
            ) : (
                <div className="space-y-3 md:space-y-4">
                    {news.map((item) => (
                        <a
                            key={item.id}
                            href={item.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="block p-3 md:p-4 rounded-xl bg-gray-800/30 hover:bg-gray-800/50 border border-gray-700/50 hover:border-indigo-500/50 transition-all group tap-target"
                        >
                            <div className="flex items-start gap-2 md:gap-3">
                                {/* Sentiment Badge */}
                                <div className={`flex-shrink-0 px-2 md:px-3 py-1 rounded-lg text-xs font-medium border whitespace-nowrap ${getSentimentColor(item.sentiment)}`}>
                                    <span className="mr-1">{getSentimentIcon(item.sentiment)}</span>
                                    <span className="hidden sm:inline">{item.sentiment === 'positive' ? '利多' : item.sentiment === 'negative' ? '利空' : '中性'}</span>
                                </div>

                                {/* Content */}
                                <div className="flex-1 min-w-0">
                                    <h4 className="text-white font-medium text-sm md:text-base mb-1.5 md:mb-2 group-hover:text-indigo-400 transition-colors line-clamp-2">
                                        {item.title}
                                    </h4>
                                    
                                    {item.summary && (
                                        <p className="text-gray-400 text-xs md:text-sm mb-1.5 md:mb-2 line-clamp-2">
                                            {item.summary}
                                        </p>
                                    )}
                                    
                                    <div className="flex flex-wrap items-center gap-2 md:gap-4 text-xs text-gray-500">
                                        <span className="flex items-center gap-1">
                                            <svg className="w-3.5 h-3.5 md:w-4 md:h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9.a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
                                            </svg>
                                            <span className="truncate max-w-[120px] md:max-w-none">{item.source}</span>
                                        </span>
                                        <span className="flex items-center gap-1">
                                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                                            </svg>
                                            {formatDate(item.published_at)}
                                        </span>
                                    </div>
                                </div>

                                {/* External Link Icon */}
                                <svg className="w-5 h-5 text-gray-500 group-hover:text-indigo-400 transition-colors flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                                </svg>
                            </div>
                        </a>
                    ))}
                </div>
            )}
        </div>
    )
}