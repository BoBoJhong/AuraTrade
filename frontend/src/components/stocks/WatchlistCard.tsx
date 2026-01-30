import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { stockService, WatchlistItem } from '../../services/stockService'
import { StockChart } from './StockChart'
import AlertModal from './AlertModal'

interface StockPriceCache {
    [symbol: string]: {
        price: number;
        change: number;
        changePercent: number;
    };
}

export const WatchlistCard = () => {
    const [watchlist, setWatchlist] = useState<WatchlistItem[]>([])
    const [isLoading, setIsLoading] = useState(true)
    const [expandedStock, setExpandedStock] = useState<string | null>(null)
    const [alertModalOpen, setAlertModalOpen] = useState<string | null>(null)
    const [priceData, setPriceData] = useState<StockPriceCache>({})
    const navigate = useNavigate()

    const fetchWatchlist = async () => {
        try {
            const data = await stockService.getWatchlist()
            setWatchlist(data)
            
            // 並行獲取所有股票的歷史數據來計算漲跌
            const pricePromises = data.map(async (item) => {
                try {
                    const history = await stockService.getHistoricalData(item.stock.symbol, '5d')
                    
                    if (history && history.length >= 2) {
                        const todayPrice = history[history.length - 1]?.price || 0
                        const yesterdayPrice = history[history.length - 2]?.price || todayPrice
                        const change = todayPrice - yesterdayPrice
                        const changePercent = yesterdayPrice > 0 ? (change / yesterdayPrice) * 100 : 0
                        
                        return { 
                            symbol: item.stock.symbol, 
                            price: todayPrice,
                            change,
                            changePercent
                        }
                    }
                    return { 
                        symbol: item.stock.symbol, 
                        price: item.stock.price || 0,
                        change: 0,
                        changePercent: 0
                    }
                } catch {
                    return { 
                        symbol: item.stock.symbol, 
                        price: item.stock.price || 0,
                        change: 0,
                        changePercent: 0
                    }
                }
            })
            
            const prices = await Promise.all(pricePromises)
            const priceMap: StockPriceCache = {}
            prices.forEach(({ symbol, price, change, changePercent }) => {
                priceMap[symbol] = { price, change, changePercent }
            })
            setPriceData(priceMap)
        } catch (error) {
            console.error('Failed to fetch watchlist', error)
        } finally {
            setIsLoading(false)
        }
    }

    useEffect(() => {
        fetchWatchlist()
    }, [])

    const handleRemove = async (symbol: string) => {
        try {
            await stockService.removeFromWatchlist(symbol)
            setWatchlist(prev => prev.filter(item => item.stock.symbol !== symbol))
        } catch (error) {
            console.error('Failed to remove stock', error)
        }
    }

    if (isLoading) {
        return (
            <div className="text-center text-gray-400 py-8">
                <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500"></div>
                <p className="mt-2">載入自選股...</p>
            </div>
        )
    }

    if (watchlist.length === 0) {
        return (
            <div className="glass rounded-2xl p-12 text-center animate-fadeIn">
                <svg className="w-16 h-16 mx-auto text-gray-600 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                <p className="text-gray-400 text-lg mb-2">目前沒有關注的股票</p>
                <p className="text-gray-600 text-sm">使用上方搜尋功能開始追蹤您的投資組合</p>
                <p className="text-indigo-400/70 text-xs mt-4">💡 加入後點擊卡片即可查看歷史圖表</p>
            </div>
        )
    }

    return (
        <div className="space-y-6">
            {watchlist.map((item, index) => {
                const { stock } = item
                const stockPrice = priceData[stock.symbol] || { price: stock.price || 0, change: 0, changePercent: 0 }
                const currentPrice = stockPrice.price
                const change = stockPrice.change
                const changePercent = stockPrice.changePercent
                const isPositive = change >= 0
                const changeColor = isPositive ? 'text-red-400' : 'text-green-400'
                const bgGradient = isPositive
                    ? 'from-red-500/10 to-transparent'
                    : 'from-green-500/10 to-transparent'
                const isExpanded = expandedStock === stock.symbol

                return (
                    <div
                        key={item.id}
                        className="glass rounded-2xl shadow-lg hover:shadow-xl animate-fadeIn transition-all duration-300"
                        style={{ animationDelay: `${index * 0.1}s` }}
                    >
                        {/* Stock Summary Card */}
                        <div
                            className="p-6 cursor-pointer relative overflow-hidden group"
                            onClick={() => setExpandedStock(isExpanded ? null : stock.symbol)}
                        >
                            {/* Gradient Background */}
                            <div className={`absolute inset-0 bg-gradient-to-br ${bgGradient} opacity-0 group-hover:opacity-100 transition-opacity duration-300`} />

                            <div className="relative z-10">
                                <div className="flex justify-between items-start mb-4">
                                    <div className="flex-1">
                                        <div className="flex items-center gap-3 mb-1">
                                            <h4 className="text-xl font-bold text-white">{stock.symbol}</h4>
                                            {stock.market && (
                                                <span className={`text-xs px-2 py-0.5 rounded-full ${
                                                    stock.market === 'TW' 
                                                        ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30' 
                                                        : 'bg-purple-500/20 text-purple-400 border border-purple-500/30'
                                                }`}>
                                                    {stock.market === 'TW' ? '台股' : stock.market}
                                                </span>
                                            )}
                                        </div>
                                        <p className="text-sm text-gray-400 mb-1">{stock.name}</p>
                                        {stock.sector && (
                                            <p className="text-xs text-gray-500">{stock.sector}</p>
                                        )}
                                    </div>
                                    
                                    <div className="flex items-center gap-2">
                                        <button
                                            onClick={(e) => {
                                                e.stopPropagation()
                                                navigate(`/stock/${stock.symbol}`)
                                            }}
                                            className="p-2 rounded-lg text-gray-500 hover:text-blue-400 hover:bg-blue-500/10 transition-all"
                                            title="查看完整分析"
                                        >
                                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                            </svg>
                                        </button>
                                        <button
                                            onClick={(e) => {
                                                e.stopPropagation()
                                                setAlertModalOpen(stock.symbol)
                                            }}
                                            className="p-2 rounded-lg text-gray-500 hover:text-yellow-400 hover:bg-yellow-500/10 transition-all"
                                            title="設定價格提醒"
                                        >
                                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                                            </svg>
                                        </button>
                                        <button
                                            onClick={(e) => {
                                                e.stopPropagation()
                                                handleRemove(stock.symbol)
                                            }}
                                            className="p-2 rounded-lg text-gray-500 hover:text-red-400 hover:bg-red-500/10 transition-all"
                                        >
                                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                            </svg>
                                        </button>
                                        <button
                                            className={`p-2 rounded-lg text-gray-400 hover:text-indigo-400 hover:bg-indigo-500/10 transition-all ${
                                                isExpanded ? 'rotate-180' : ''
                                            }`}
                                        >
                                            <svg className="w-5 h-5 transition-transform duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                                            </svg>
                                        </button>
                                    </div>
                                </div>

                                <div className="flex justify-between items-end">
                                    <div>
                                        <span className="text-3xl font-bold text-white">
                                            ${currentPrice.toFixed(2)}
                                        </span>
                                        {item.target_price && (
                                            <p className="text-xs text-gray-500 mt-1">
                                                目標價: ${item.target_price.toFixed(2)}
                                            </p>
                                        )}
                                        {!isExpanded && (
                                            <p className="text-xs text-indigo-400/70 mt-2 flex items-center gap-1 animate-pulse">
                                                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                                                </svg>
                                                點擊查看圖表
                                            </p>
                                        )}
                                    </div>
                                    <div className={`text-right ${changeColor}`}>
                                        <div className="flex items-center gap-1 justify-end">
                                            {isPositive ? (
                                                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                                                    <path fillRule="evenodd" d="M5.293 9.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 7.414V15a1 1 0 11-2 0V7.414L6.707 9.707a1 1 0 01-1.414 0z" clipRule="evenodd" />
                                                </svg>
                                            ) : (
                                                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                                                    <path fillRule="evenodd" d="M14.707 10.293a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 111.414-1.414L9 12.586V5a1 1 0 012 0v7.586l2.293-2.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                                </svg>
                                            )}
                                            <span className="text-lg font-bold">
                                                {isPositive ? '+' : ''}{change.toFixed(2)}
                                            </span>
                                        </div>
                                        <div className="text-sm font-medium">
                                            ({isPositive ? '+' : ''}{changePercent.toFixed(2)}%)
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Expanded Chart Section */}
                        {isExpanded && (
                            <div className="px-6 pb-6 border-t border-gray-800/50 animate-in slide-in-from-top-4 duration-300">
                                <div className="mt-6">
                                    <StockChart symbol={stock.symbol} />
                                </div>
                            </div>
                        )}
                    </div>
                )
            })}
            
            {/* Alert Modal */}
            {alertModalOpen && (
                <AlertModal
                    symbol={alertModalOpen}
                    stockName={watchlist.find(item => item.stock.symbol === alertModalOpen)?.stock.name || ''}
                    currentPrice={priceData[alertModalOpen]?.price || watchlist.find(item => item.stock.symbol === alertModalOpen)?.stock.price || 0}
                    isOpen={!!alertModalOpen}
                    onClose={() => setAlertModalOpen(null)}
                    onAlertCreated={() => {
                        // 可以在這裡重新載入 watchlist 或顯示通知
                    }}
                />
            )}
        </div>
    )
}


