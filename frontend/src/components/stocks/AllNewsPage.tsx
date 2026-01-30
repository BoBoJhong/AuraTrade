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

export const AllNewsPage = () => {
    const [news, setNews] = useState<NewsItem[]>([])
    const [isLoading, setIsLoading] = useState(true)
    const [searchQuery, setSearchQuery] = useState('')
    const [selectedSymbol, setSelectedSymbol] = useState<string>('all')
    const [symbols, setSymbols] = useState<string[]>([])

    useEffect(() => {
        fetchAllNews()
    }, [])

    const fetchAllNews = async () => {
        try {
            setIsLoading(true)
            // 獲取所有新聞（從多個熱門股票）
            const popularSymbols = ['2330.TW', 'AAPL', 'TSLA', 'NVDA', '2317.TW', 'GOOGL', 'MSFT']
            
            const newsPromises = popularSymbols.map(async (symbol) => {
                try {
                    const response = await api.get(`/stocks/${symbol}/news`, {
                        params: { limit: 10, days: 7 }
                    })
                    return response.data.news || []
                } catch (error) {
                    console.error(`Failed to fetch news for ${symbol}:`, error)
                    return []
                }
            })

            const newsResults = await Promise.all(newsPromises)
            const allNews = newsResults.flat()
            
            // 按發布時間排序（最新的在前）
            allNews.sort((a, b) => 
                new Date(b.published_at).getTime() - new Date(a.published_at).getTime()
            )

            setNews(allNews)
            
            // 提取所有股票代碼
            const uniqueSymbols = Array.from(new Set(allNews.map(n => n.symbol)))
            setSymbols(uniqueSymbols)
        } catch (error) {
            console.error('Failed to fetch news:', error)
        } finally {
            setIsLoading(false)
        }
    }

    const getSentimentColor = (sentiment: string | null) => {
        switch (sentiment) {
            case 'positive':
                return 'bg-green-500/10 text-green-400 border-green-500/30'
            case 'negative':
                return 'bg-red-500/10 text-red-400 border-red-500/30'
            default:
                return 'bg-gray-500/10 text-gray-400 border-gray-500/30'
        }
    }

    const getSentimentIcon = (sentiment: string | null) => {
        switch (sentiment) {
            case 'positive':
                return ''
            case 'negative':
                return ''
            default:
                return ''
        }
    }

    const filteredNews = news.filter(item => {
        const matchesSearch = !searchQuery || 
            item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
            item.summary?.toLowerCase().includes(searchQuery.toLowerCase()) ||
            item.source.toLowerCase().includes(searchQuery.toLowerCase())
        
        const matchesSymbol = selectedSymbol === 'all' || item.symbol === selectedSymbol

        return matchesSearch && matchesSymbol
    })

    if (isLoading) {
        return (
            <div className="glass rounded-2xl p-12 border border-white/20 animate-fadeIn">
                <div className="text-center">
                    <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500 mb-4"></div>
                    <p className="text-white font-medium">載入財經新聞...</p>
                    <p className="text-gray-400 text-sm mt-2">正在彙整最新資訊</p>
                </div>
            </div>
        )
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="glass rounded-2xl p-6 border border-white/20">
                <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                    <div>
                        <h2 className="text-3xl font-bold text-white mb-2"> 財經新聞專區</h2>
                        <p className="text-gray-400">彙整全球財經動態，掌握市場脈動</p>
                    </div>
                    <button
                        onClick={fetchAllNews}
                        className="px-4 py-2 rounded-lg bg-indigo-500/20 text-indigo-400 hover:bg-indigo-500/30 border border-indigo-500/30 transition-all"
                    >
                         重新載入
                    </button>
                </div>

                {/* Search and Filter */}
                <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
                    {/* Search Bar */}
                    <div className="relative">
                        <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                        </svg>
                        <input
                            type="text"
                            placeholder="搜尋新聞標題、內容、來源..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="w-full pl-10 pr-4 py-3 bg-white/5 border border-white/20 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-500/50 transition-all"
                        />
                    </div>

                    {/* Symbol Filter */}
                    <select
                        value={selectedSymbol}
                        onChange={(e) => setSelectedSymbol(e.target.value)}
                        className="px-4 py-3 bg-white/5 border border-white/20 rounded-xl text-white focus:outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-500/50 transition-all"
                    >
                        <option value="all" className="bg-gray-800">所有股票</option>
                        {symbols.map(symbol => (
                            <option key={symbol} value={symbol} className="bg-gray-800">
                                {symbol}
                            </option>
                        ))}
                    </select>
                </div>

                {/* Stats */}
                <div className="mt-4 flex items-center gap-4 text-sm text-gray-400">
                    <span> 共 {news.length} 則新聞</span>
                    <span></span>
                    <span> 顯示 {filteredNews.length} 則</span>
                </div>
            </div>

            {/* News List */}
            {filteredNews.length === 0 ? (
                <div className="glass rounded-2xl p-12 border border-white/20 text-center">
                    <svg className="w-16 h-16 mx-auto text-gray-600 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
                    </svg>
                    <p className="text-gray-400 mb-2">找不到符合條件的新聞</p>
                    <p className="text-gray-600 text-sm">嘗試更改搜尋條件或篩選選項</p>
                </div>
            ) : (
                <div className="space-y-4">
                    {filteredNews.map((item) => (
                        <a
                            key={item.id}
                            href={item.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="block glass rounded-xl p-6 border border-white/20 hover:border-indigo-500/50 transition-all group"
                        >
                            <div className="flex items-start gap-4">
                                {/* Sentiment Badge */}
                                <div className={`flex-shrink-0 px-3 py-1.5 rounded-lg text-xs font-medium border ${getSentimentColor(item.sentiment)}`}>
                                    <span className="mr-1">{getSentimentIcon(item.sentiment)}</span>
                                    {item.sentiment === 'positive' ? '利多' : item.sentiment === 'negative' ? '利空' : '中性'}
                                </div>

                                {/* Content */}
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center gap-2 mb-2">
                                        <span className="px-2 py-1 rounded text-xs font-medium bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                                            {item.symbol}
                                        </span>
                                        <span className="text-gray-500 text-xs"></span>
                                        <span className="text-gray-400 text-xs">
                                            {new Date(item.published_at).toLocaleDateString('zh-TW', {
                                                year: 'numeric',
                                                month: '2-digit',
                                                day: '2-digit',
                                                hour: '2-digit',
                                                minute: '2-digit'
                                            })}
                                        </span>
                                    </div>

                                    <h4 className="text-white font-semibold text-lg mb-2 group-hover:text-indigo-400 transition-colors line-clamp-2">
                                        {item.title}
                                    </h4>
                                    
                                    {item.summary && (
                                        <p className="text-gray-400 text-sm mb-3 line-clamp-2">
                                            {item.summary}
                                        </p>
                                    )}
                                    
                                    <div className="flex items-center gap-2 text-xs text-gray-500">
                                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
                                        </svg>
                                        {item.source}
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
