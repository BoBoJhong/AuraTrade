import { stockService, Stock } from '../../services/stockService'
import { StockSearch } from '../../components/stocks/StockSearch'
import { WatchlistCard } from '../../components/stocks/WatchlistCard'
import { PositionCard } from '../../components/stocks/PositionCard'
import { RecommendedStocks } from '../../components/stocks/RecommendedStocks'
import { NewsPanel } from '../../components/stocks/NewsPanel'
import { AllNewsPage } from '../../components/stocks/AllNewsPage'
import { useAuthStore } from '../../stores/authStore'
import { NotificationBell } from '../../components/ui/NotificationBell'
import { useNavigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import axios from 'axios'

type ViewMode = 'watchlist' | 'recommended' | 'positions' | 'news';

interface WatchlistItem {
    id: number
    symbol: string
    name: string
    market: string
}

export const DashboardPage = () => {
    const { user, logout } = useAuthStore()
    const navigate = useNavigate()
    const [viewMode, setViewMode] = useState<ViewMode>('watchlist')
    const [watchlistStocks, setWatchlistStocks] = useState<WatchlistItem[]>([])
    const [selectedStock, setSelectedStock] = useState<string | null>(null)

    useEffect(() => {
        if (viewMode === 'watchlist') {
            fetchWatchlist()
        }
    }, [viewMode])

    const fetchWatchlist = async () => {
        try {
            const token = localStorage.getItem('access_token')
            if (!token) return

            const response = await axios.get('http://localhost:8000/api/v1/watchlist', {
                headers: { Authorization: `Bearer ${token}` }
            })
            
            const stocks = response.data.map((item: any) => ({
                id: item.id,
                symbol: item.stock.symbol,
                name: item.stock.name,
                market: item.stock.market
            }))
            
            setWatchlistStocks(stocks)
            if (stocks.length > 0 && !selectedStock) {
                setSelectedStock(stocks[0].symbol)
            }
        } catch (error) {
            console.error('Failed to fetch watchlist:', error)
        }
    }

    const handleLogout = () => {
        logout()
        navigate('/login')
    }

    const handleStockSelect = async (stock: Stock) => {
        try {
            await stockService.addToWatchlist(stock.symbol)
            window.location.reload()
        } catch (error: any) {
            console.error("Error adding to watchlist", error)
            
            // 解析後端錯誤訊息
            let errorMessage = "加入自選股失敗"
            
            if (error.response?.data?.detail) {
                const detail = error.response.data.detail
                if (typeof detail === 'string') {
                    errorMessage = detail
                } else if (detail.message) {
                    errorMessage = detail.message
                    if (detail.hint) {
                        errorMessage += `\n${detail.hint}`
                    }
                }
            } else if (error.response?.status === 404) {
                errorMessage = "找不到此股票代碼\n請確認代碼是否正確，或稍後再試（Yahoo Finance API 可能暫時限流）"
            } else if (error.response?.status === 400) {
                errorMessage = "此股票已在您的自選股中"
            }
            
            alert(errorMessage)
        }
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-950 via-indigo-950 to-purple-950 relative overflow-hidden">
            {/* Animated Background Elements */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
                <div className="absolute -top-40 -left-40 w-96 h-96 bg-indigo-600/20 rounded-full blur-3xl animate-pulse" />
                <div className="absolute top-1/3 -right-40 w-96 h-96 bg-purple-600/20 rounded-full blur-3xl animate-pulse" style={{animationDelay: '1s'}} />
                <div className="absolute -bottom-40 left-1/3 w-96 h-96 bg-blue-600/15 rounded-full blur-3xl animate-pulse" style={{animationDelay: '2s'}} />
            </div>

            {/* Glassmorphism Navbar */}
            <nav className="glass border-b border-white/10 sticky top-0 z-50 backdrop-blur-xl shadow-2xl safe-padding">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex items-center justify-between h-16 lg:h-20">
                        {/* Brand */}
                        <div className="flex items-center gap-2 lg:gap-3 group">
                            <div className="relative">
                                <div className="absolute -inset-1 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-xl blur opacity-50 group-hover:opacity-75 transition duration-300"></div>
                                <div className="relative w-10 h-10 lg:w-12 lg:h-12 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-xl">
                                    <svg className="w-6 h-6 lg:w-7 lg:h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                                    </svg>
                                </div>
                            </div>
                            <div className="hidden sm:block">
                                <span className="text-xl lg:text-2xl font-bold bg-gradient-to-r from-indigo-300 via-purple-300 to-pink-300 bg-clip-text text-transparent">
                                    AuraTrade
                                </span>
                                <p className="text-xs text-gray-400 font-medium hidden lg:block">AI-Powered Platform</p>
                            </div>
                        </div>

                        {/* View Mode Tabs */}
                        <div className="hidden md:flex items-center gap-2 bg-white/5 backdrop-blur-xl rounded-xl p-1.5 border border-white/10 shadow-lg">
                            <button
                                onClick={() => setViewMode('watchlist')}
                                className={`px-3 lg:px-5 py-2 lg:py-2.5 rounded-lg text-xs lg:text-sm font-semibold transition-all duration-200 ${
                                    viewMode === 'watchlist'
                                        ? 'bg-gradient-to-r from-indigo-500 to-purple-500 text-white shadow-lg shadow-indigo-500/50 scale-105'
                                        : 'text-gray-300 hover:text-white hover:bg-white/10'
                                }`}
                            >
                                <span className="flex items-center gap-1.5">
                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
                                    </svg>
                                    <span className="hidden sm:inline">自選股</span>
                                </span>
                            </button>
                            <button
                                onClick={() => setViewMode('recommended')}
                                className={`px-3 lg:px-5 py-2 lg:py-2.5 rounded-lg text-xs lg:text-sm font-semibold transition-all duration-200 ${
                                    viewMode === 'recommended'
                                        ? 'bg-gradient-to-r from-indigo-500 to-purple-500 text-white shadow-lg shadow-indigo-500/50 scale-105'
                                        : 'text-gray-300 hover:text-white hover:bg-white/10'
                                }`}
                            >
                                <span className="flex items-center gap-1.5">
                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                                    </svg>
                                    <span className="hidden sm:inline">推薦</span>
                                </span>
                            </button>
                            <button
                                onClick={() => setViewMode('positions')}
                                className={`px-3 lg:px-5 py-2 lg:py-2.5 rounded-lg text-xs lg:text-sm font-semibold transition-all duration-200 ${
                                    viewMode === 'positions'
                                        ? 'bg-gradient-to-r from-indigo-500 to-purple-500 text-white shadow-lg shadow-indigo-500/50 scale-105'
                                        : 'text-gray-300 hover:text-white hover:bg-white/10'
                                }`}
                            >
                                <span className="flex items-center gap-1.5">
                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                                    </svg>
                                    <span className="hidden sm:inline">持倉</span>
                                </span>
                            </button>
                            <button
                                onClick={() => setViewMode('news')}
                                className={`px-3 lg:px-5 py-2 lg:py-2.5 rounded-lg text-xs lg:text-sm font-semibold transition-all duration-200 ${
                                    viewMode === 'news'
                                        ? 'bg-gradient-to-r from-indigo-500 to-purple-500 text-white shadow-lg shadow-indigo-500/50 scale-105'
                                        : 'text-gray-300 hover:text-white hover:bg-white/10'
                                }`}
                            >
                                <span className="flex items-center gap-1.5">
                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
                                    </svg>
                                    <span className="hidden sm:inline">財經新聞</span>
                                </span>
                            </button>
                            <button
                                onClick={() => navigate('/screener')}
                                className="px-3 lg:px-5 py-2 lg:py-2.5 rounded-lg text-xs lg:text-sm font-semibold transition-all duration-200 bg-gradient-to-r from-yellow-500 to-orange-500 text-white shadow-lg shadow-yellow-500/50 hover:scale-105"
                            >
                                <span className="flex items-center gap-1.5">
                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                                    </svg>
                                    <span className="hidden sm:inline">選股器</span>
                                </span>
                            </button>
                        </div>

                        {/* User Menu */}
                        <div className="flex items-center gap-2 lg:gap-4">
                            {/* Notification Bell */}
                            <NotificationBell />
                            
                            {/* User Avatar - Show on mobile */}
                            <div className="md:hidden w-9 h-9 rounded-lg bg-gradient-to-br from-indigo-400 to-purple-500 flex items-center justify-center text-white font-bold text-sm shadow-lg">
                                {user?.username?.[0]?.toUpperCase()}
                            </div>
                            
                            {/* Full User Info - Hide on mobile */}
                            <div className="hidden md:flex items-center gap-3 px-3 lg:px-4 py-2 rounded-xl bg-white/5 border border-white/10">
                                <div className="w-9 h-9 lg:w-10 lg:h-10 rounded-lg bg-gradient-to-br from-indigo-400 to-purple-500 flex items-center justify-center text-white font-bold text-sm shadow-lg">
                                    {user?.username?.[0]?.toUpperCase()}
                                </div>
                                <div className="text-right hidden lg:block">
                                    <p className="text-sm font-semibold text-white">{user?.username}</p>
                                    <p className="text-xs text-indigo-300">{user?.role === 'admin' ? '👑 管理員' : '✨ 會員'}</p>
                                </div>
                            </div>
                            <button
                                onClick={handleLogout}
                                className="flex items-center gap-2 px-3 lg:px-4 py-2 lg:py-2.5 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 hover:bg-red-500/20 hover:border-red-500/50 transition-all font-medium min-w-[44px] min-h-[44px] justify-center"
                            >
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                                </svg>
                                <span className="hidden md:inline">登出</span>
                            </button>
                        </div>
                    </div>
                </div>
            </nav>

            {/* Main Content */}
            <main className="relative max-w-7xl mx-auto py-4 md:py-8 px-4 sm:px-6 lg:px-8 safe-padding">
                {/* Mobile View Tabs */}
                <div className="md:hidden mb-4 flex items-center gap-2 p-1 bg-white/5 backdrop-blur-xl rounded-xl border border-white/10 overflow-x-auto">
                    <button
                        onClick={() => setViewMode('watchlist')}
                        className={`flex-shrink-0 px-4 py-2.5 rounded-lg text-sm font-semibold transition-all duration-200 ${
                            viewMode === 'watchlist'
                                ? 'bg-gradient-to-r from-indigo-500 to-purple-500 text-white shadow-lg'
                                : 'text-gray-300 hover:text-white hover:bg-white/10'
                        }`}
                    >
                        📊 自選股
                    </button>
                    <button
                        onClick={() => setViewMode('recommended')}
                        className={`flex-shrink-0 px-4 py-2.5 rounded-lg text-sm font-semibold transition-all duration-200 ${
                            viewMode === 'recommended'
                                ? 'bg-gradient-to-r from-indigo-500 to-purple-500 text-white shadow-lg'
                                : 'text-gray-300 hover:text-white hover:bg-white/10'
                        }`}
                    >
                        ⚡ 推薦
                    </button>
                    <button
                        onClick={() => setViewMode('positions')}
                        className={`flex-shrink-0 px-4 py-2.5 rounded-lg text-sm font-semibold transition-all duration-200 ${
                            viewMode === 'positions'
                                ? 'bg-gradient-to-r from-indigo-500 to-purple-500 text-white shadow-lg'
                                : 'text-gray-300 hover:text-white hover:bg-white/10'
                        }`}
                    >
                        💼 持倉
                    </button>
                    <button
                        onClick={() => setViewMode('news')}
                        className={`flex-shrink-0 px-4 py-2.5 rounded-lg text-sm font-semibold transition-all duration-200 ${
                            viewMode === 'news'
                                ? 'bg-gradient-to-r from-indigo-500 to-purple-500 text-white shadow-lg'
                                : 'text-gray-300 hover:text-white hover:bg-white/10'
                        }`}
                    >
                        📰 財經新聞
                    </button>
                    <button
                        onClick={() => navigate('/screener')}
                        className="flex-shrink-0 px-4 py-2.5 rounded-lg text-sm font-semibold transition-all duration-200 bg-gradient-to-r from-yellow-500 to-orange-500 text-white shadow-lg"
                    >
                        🎯 選股器
                    </button>
                </div>

                {viewMode === 'watchlist' && (
                    <>
                        {/* Stock Search Section - 只在自選股視圖顯示 */}
                        <div className="mb-6 md:mb-8 animate-fadeIn relative z-50">
                            <div className="max-w-4xl mx-auto">
                                <div className="glass rounded-2xl p-4 md:p-6 border border-white/20 shadow-2xl overflow-visible">
                                    <div className="flex items-center gap-3 mb-3 md:mb-4">
                                        <div className="w-10 h-10 md:w-12 md:h-12 flex-shrink-0 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg">
                                            <svg className="w-5 h-5 md:w-6 md:h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                                            </svg>
                                        </div>
                                        <div>
                                            <h3 className="text-lg md:text-xl font-bold text-white">股票搜尋</h3>
                                            <p className="text-xs md:text-sm text-gray-400">搜尋並加入股票到自選清單</p>
                                        </div>
                                    </div>
                                    <StockSearch onSelect={handleStockSelect} />
                                </div>
                            </div>
                        </div>

                        <div className="mb-6 md:mb-8 animate-fadeIn">
                            <div className="flex items-center gap-3 md:gap-4 mb-4 md:mb-6">
                                <div className="flex items-center gap-2">
                                    <div className="w-1 md:w-1.5 h-8 md:h-10 bg-gradient-to-b from-indigo-400 via-purple-500 to-pink-500 rounded-full shadow-lg"></div>
                                    <h2 className="text-2xl md:text-4xl font-bold bg-gradient-to-r from-white via-indigo-100 to-purple-100 bg-clip-text text-transparent">我的自選股</h2>
                                </div>
                                <div className="flex-1 h-px bg-gradient-to-r from-indigo-500/50 to-transparent"></div>
                            </div>
                            <WatchlistCard />
                        </div>
                        
                        {/* Market News Section */}
                        <div className="mb-6 md:mb-8 animate-fadeIn">
                            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-4 md:mb-6">
                                <div className="flex items-center gap-3 md:gap-4">
                                    <div className="flex items-center gap-2">
                                        <div className="w-1 md:w-1.5 h-8 md:h-10 bg-gradient-to-b from-emerald-400 via-teal-500 to-cyan-500 rounded-full shadow-lg"></div>
                                        <h2 className="text-2xl md:text-4xl font-bold bg-gradient-to-r from-white via-emerald-100 to-teal-100 bg-clip-text text-transparent">市場快訊</h2>
                                    </div>
                                    <span className="hidden sm:inline-flex px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-sm text-emerald-300 font-medium">🤖 AI 分析</span>
                                </div>
                                
                                {/* Stock Selector */}
                                {watchlistStocks.length > 0 && (
                                    <select
                                        value={selectedStock || ''}
                                        onChange={(e) => setSelectedStock(e.target.value)}
                                        className="w-full sm:w-auto px-3 md:px-4 py-2 md:py-2.5 bg-white/5 backdrop-blur-xl border border-white/20 rounded-xl text-white text-sm md:text-base font-medium focus:outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-500/50 transition-all shadow-lg"
                                    >
                                        {watchlistStocks.map((stock) => (
                                            <option key={stock.symbol} value={stock.symbol} className="bg-gray-800">
                                                {stock.name} ({stock.symbol})
                                            </option>
                                        ))}
                                    </select>
                                )}
                            </div>
                            
                            {watchlistStocks.length > 0 && selectedStock ? (
                                <NewsPanel 
                                    symbol={selectedStock} 
                                    stockName={watchlistStocks.find(s => s.symbol === selectedStock)?.name}
                                />
                            ) : (
                                <div className="glass rounded-2xl p-12 text-center">
                                    <svg className="w-16 h-16 mx-auto text-gray-600 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
                                    </svg>
                                    <p className="text-gray-400 mb-2">尚未加入自選股</p>
                                    <p className="text-gray-600 text-sm">請先搜尋並加入股票到自選清單</p>
                                </div>
                            )}
                        </div>
                    </>
                )}
                
                {viewMode === 'recommended' && (
                    <div className="mb-6 md:mb-8 animate-fadeIn">
                        <div className="flex items-center gap-3 md:gap-4 mb-4 md:mb-6">
                            <div className="flex items-center gap-2">
                                <div className="w-1 md:w-1.5 h-8 md:h-10 bg-gradient-to-b from-yellow-400 via-orange-500 to-red-500 rounded-full shadow-lg"></div>
                                <h2 className="text-2xl md:text-4xl font-bold bg-gradient-to-r from-white via-yellow-100 to-orange-100 bg-clip-text text-transparent">AI 推薦</h2>
                            </div>
                            <div className="flex-1 h-px bg-gradient-to-r from-yellow-500/50 to-transparent"></div>
                        </div>
                        <RecommendedStocks />
                    </div>
                )}
                
                {viewMode === 'positions' && (
                    <div className="mb-6 md:mb-8 animate-fadeIn">
                        <div className="flex items-center gap-3 md:gap-4 mb-4 md:mb-6">
                            <div className="flex items-center gap-2">
                                <div className="w-1 md:w-1.5 h-8 md:h-10 bg-gradient-to-b from-purple-400 via-pink-500 to-rose-500 rounded-full shadow-lg"></div>
                                <h2 className="text-2xl md:text-4xl font-bold bg-gradient-to-r from-white via-purple-100 to-pink-100 bg-clip-text text-transparent">投資組合</h2>
                            </div>
                            <div className="flex-1 h-px bg-gradient-to-r from-purple-500/50 to-transparent"></div>
                        </div>
                        <PositionCard />
                    </div>
                )}

                {viewMode === 'news' && (
                    <div className="mb-6 md:mb-8 animate-fadeIn">
                        <AllNewsPage />
                    </div>
                )}
            </main>

            {/* Footer */}
            <footer className="relative border-t border-white/10 mt-8 md:mt-16 backdrop-blur-xl">
                <div className="max-w-7xl mx-auto py-6 md:py-8 px-4 sm:px-6 lg:px-8">
                    <div className="flex flex-col items-center gap-3 text-center">
                        <div className="flex items-center gap-2">
                            <div className="w-7 h-7 md:w-8 md:h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg">
                                <svg className="w-4 h-4 md:w-5 md:h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                                </svg>
                            </div>
                            <span className="text-base md:text-lg font-bold bg-gradient-to-r from-indigo-300 to-purple-300 bg-clip-text text-transparent">AuraTrade</span>
                        </div>
                        <p className="text-xs md:text-sm text-gray-400">
                            © 2026 AuraTrade · AI-Powered Investment Platform · All rights reserved
                        </p>
                        <div className="flex flex-wrap items-center justify-center gap-2 md:gap-4 text-xs text-gray-500">
                            <span>🔒 安全加密</span>
                            <span>·</span>
                            <span>🤖 AI 驅動</span>
                            <span>·</span>
                            <span>📊 即時數據</span>
                        </div>
                    </div>
                </div>
            </footer>
        </div>
    )
}

