import { useEffect, useState } from 'react'
import { stockService, WatchlistItem } from '../../services/stockService'
import AlertModal from './AlertModal'
import { WatchlistStockCard } from './WatchlistStockCard'

interface StockPriceCache {
    [symbol: string]: {
        price: number;
        change: number;
        changePercent: number;
        timestamp?: string;
    };
}

export const WatchlistCard = () => {
    const [watchlist, setWatchlist] = useState<WatchlistItem[]>([])
    const [isLoading, setIsLoading] = useState(true)
    const [expandedStock, setExpandedStock] = useState<string | null>(null)
    const [alertModalOpen, setAlertModalOpen] = useState<string | null>(null)
    const [priceData, setPriceData] = useState<StockPriceCache>({})

    const fetchWatchlist = async () => {
        try {
            const data = await stockService.getWatchlist()
            setWatchlist(data)
            
            // 並行獲取所有股票的歷史數據來計算漲跌
            const pricePromises = data.map(async (item) => {
                try {
                    const history = await stockService.getHistoricalData(item.stock.symbol, '5d')
                    
                    // 確保數據按日期排序（新→舊）
                    const sortedHistory = history?.sort((a, b) => 
                        new Date(b.date).getTime() - new Date(a.date).getTime()
                    ) || []
                    
                    console.log(`📊 ${item.stock.symbol} 歷史數據（排序後）:`, {
                        count: sortedHistory.length,
                        newest: sortedHistory[0],
                        secondNewest: sortedHistory[1]
                    })
                    
                    if (sortedHistory && sortedHistory.length >= 2) {
                        // 最新的在 [0]，前一天在 [1]
                        const newestData = sortedHistory[0]
                        const previousData = sortedHistory[1]
                        
                        const todayPrice = newestData?.close || newestData?.price || 0
                        const yesterdayPrice = previousData?.close || previousData?.price || todayPrice
                        const change = todayPrice - yesterdayPrice
                        const changePercent = yesterdayPrice > 0 ? (change / yesterdayPrice) * 100 : 0
                        
                        console.log(`💰 ${item.stock.symbol} 價格計算:`, { 
                            newestDate: newestData?.date,
                            todayPrice, 
                            yesterdayDate: previousData?.date,
                            yesterdayPrice, 
                            change, 
                            changePercent
                        })
                        
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
                } catch (err) {
                    console.error(`Failed to fetch ${item.stock.symbol} history:`, err)
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
            <div className="glass rounded-2xl p-12 border border-white/20 animate-fadeIn">
                <div className="flex flex-col items-center justify-center space-y-4">
                    {/* 優化的載入動畫 */}
                    <div className="relative">
                        <div className="w-16 h-16 border-4 border-indigo-500/20 border-t-indigo-500 rounded-full animate-spin"></div>
                        <div className="absolute inset-0 w-16 h-16 border-4 border-purple-500/20 border-b-purple-500 rounded-full animate-spin" style={{animationDirection: 'reverse', animationDuration: '1.5s'}}></div>
                    </div>
                    <div className="text-center">
                        <p className="text-slate-900 font-semibold">載入自選股中...</p>
                        <p className="text-slate-500 text-sm mt-1">正在獲取即時數據</p>
                    </div>
                    {/* 骨架屏預覽 */}
                    <div className="w-full space-y-3 mt-6">
                        {[1, 2, 3].map(i => (
                            <div key={i} className="animate-pulse">
                                <div className="h-24 bg-white/5 rounded-xl"></div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        )
    }

    if (watchlist.length === 0) {
        return (
            <div className="glass rounded-2xl p-12 border border-white/20 animate-fadeIn relative overflow-hidden">
                {/* 背景裝飾 */}
                <div className="absolute inset-0 opacity-5">
                    <div className="absolute top-0 left-0 w-32 h-32 bg-indigo-500 rounded-full filter blur-3xl"></div>
                    <div className="absolute bottom-0 right-0 w-40 h-40 bg-purple-500 rounded-full filter blur-3xl"></div>
                </div>
                
                <div className="relative text-center">
                    {/* 動畫圖標 */}
                    <div className="inline-block mb-6 relative">
                        <div className="absolute inset-0 bg-indigo-500/20 rounded-2xl blur-xl animate-pulse"></div>
                        <div className="relative bg-gradient-to-br from-indigo-500/20 to-purple-500/20 p-6 rounded-2xl border border-white/10">
                            <svg className="w-20 h-20 mx-auto text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                            </svg>
                        </div>
                    </div>
                    
                    <h3 className="text-2xl font-extrabold text-slate-900 mb-3 tracking-tight">開始建立您的投資組合</h3>
                    <p className="text-slate-700 text-base mb-2">目前尚未加入任何關注股票</p>
                    <p className="text-gray-500 text-sm mb-6">使用上方搜尋功能，開始追蹤您感興趣的股票</p>
                    
                    {/* 特色提示 */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
                        <div className="bg-white/5 rounded-xl p-4 border border-white/10 hover:border-indigo-500/50 transition-all">
                            <div className="text-3xl mb-2">📊</div>
                            <p className="text-sm text-slate-700 font-semibold">即時追蹤</p>
                            <p className="text-xs text-gray-500 mt-1">查看股價走勢圖表</p>
                        </div>
                        <div className="bg-white/5 rounded-xl p-4 border border-white/10 hover:border-purple-500/50 transition-all">
                            <div className="text-3xl mb-2">🔔</div>
                            <p className="text-sm text-slate-700 font-semibold">價格提醒</p>
                            <p className="text-xs text-gray-500 mt-1">設定漲跌通知</p>
                        </div>
                        <div className="bg-white/5 rounded-xl p-4 border border-white/10 hover:border-pink-500/50 transition-all">
                            <div className="text-3xl mb-2">🤖</div>
                            <p className="text-sm text-slate-700 font-semibold">AI 分析</p>
                            <p className="text-xs text-gray-500 mt-1">智能投資建議</p>
                        </div>
                    </div>
                </div>
            </div>
        )
    }

    return (
        <div className="space-y-4">
            {/* 統計摘要卡片 - 響應式設計 */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 lg:gap-4">
                <div className="glass rounded-xl p-4 border border-white/10 hover:border-indigo-500/50 transition-all group">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-gray-400 text-xs lg:text-sm">追蹤股票</span>
                        <div className="w-8 h-8 rounded-lg bg-indigo-500/10 flex items-center justify-center group-hover:scale-110 transition-transform">
                            <span className="text-lg">📊</span>
                        </div>
                    </div>
                    <p className="text-xl lg:text-2xl font-extrabold text-slate-900 tracking-tight">{watchlist.length}</p>
                    <p className="text-xs text-gray-500 mt-1">支股票</p>
                </div>
                
                <div className="glass rounded-xl p-4 border border-white/10 hover:border-green-500/50 transition-all group">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-gray-400 text-xs lg:text-sm">上漲數</span>
                        <div className="w-8 h-8 rounded-lg bg-green-500/10 flex items-center justify-center group-hover:scale-110 transition-transform">
                            <span className="text-lg">📈</span>
                        </div>
                    </div>
                    <p className="text-xl lg:text-2xl font-bold text-green-400">
                        {Object.values(priceData).filter(p => p.changePercent > 0).length}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">支上漲</p>
                </div>
                
                <div className="glass rounded-xl p-4 border border-white/10 hover:border-red-500/50 transition-all group">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-gray-400 text-xs lg:text-sm">下跌數</span>
                        <div className="w-8 h-8 rounded-lg bg-red-500/10 flex items-center justify-center group-hover:scale-110 transition-transform">
                            <span className="text-lg">📉</span>
                        </div>
                    </div>
                    <p className="text-xl lg:text-2xl font-bold text-red-400">
                        {Object.values(priceData).filter(p => p.changePercent < 0).length}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">支下跌</p>
                </div>
                
                <div className="glass rounded-xl p-4 border border-white/10 hover:border-purple-500/50 transition-all group">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-gray-400 text-xs lg:text-sm">平均漲跌</span>
                        <div className="w-8 h-8 rounded-lg bg-purple-500/10 flex items-center justify-center group-hover:scale-110 transition-transform">
                            <span className="text-lg">💹</span>
                        </div>
                    </div>
                    <p className={`text-xl lg:text-2xl font-bold ${
                        Object.values(priceData).reduce((sum, p) => sum + p.changePercent, 0) / watchlist.length >= 0 
                            ? 'text-green-400' 
                            : 'text-red-400'
                    }`}>
                        {(Object.values(priceData).reduce((sum, p) => sum + p.changePercent, 0) / watchlist.length).toFixed(2)}%
                    </p>
                    <p className="text-xs text-gray-500 mt-1">平均值</p>
                </div>
            </div>

            {/* 股票列表 - 響應式網格 */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                {watchlist.map((item, index) => {
                const { stock } = item
                const stockPrice = priceData[stock.symbol] || { price: stock.price || 0, change: 0, changePercent: 0 }

                return (
                    <WatchlistStockCard
                        key={item.id}
                        item={item}
                        index={index}
                        expandedStock={expandedStock}
                        onToggleExpand={setExpandedStock}
                        onRemove={handleRemove}
                        onOpenAlert={setAlertModalOpen}
                        initialPrice={stockPrice.price}
                        initialChange={stockPrice.change}
                        initialChangePercent={stockPrice.changePercent}
                    />
                )
            })}
            </div>
            
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


