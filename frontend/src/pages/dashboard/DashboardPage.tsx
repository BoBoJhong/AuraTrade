import { stockService, Stock } from '../../services/stockService'
import { StockSearch } from '../../components/stocks/StockSearch'
import { WatchlistCard } from '../../components/stocks/WatchlistCard'
import { PositionCard } from '../../components/stocks/PositionCard'
import { RecommendedStocks } from '../../components/stocks/RecommendedStocks'
import { useAuthStore } from '../../stores/authStore'
import { Button } from '../../components/ui/Button'
import { NotificationBell } from '../../components/ui/NotificationBell'
import { useNavigate } from 'react-router-dom'
import { useState } from 'react'

type ViewMode = 'watchlist' | 'recommended' | 'positions';

export const DashboardPage = () => {
    const { user, logout } = useAuthStore()
    const navigate = useNavigate()
    const [viewMode, setViewMode] = useState<ViewMode>('watchlist')

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
        <div className="min-h-screen">
            {/* Glassmorphism Navbar */}
            <nav className="glass border-b border-gray-800/50 sticky top-0 z-50 backdrop-blur-xl">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex items-center justify-between h-20">
                        {/* Brand */}
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg">
                                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                                </svg>
                            </div>
                            <span className="text-2xl font-bold bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
                                AuraTrade
                            </span>
                        </div>

                        {/* Search Bar */}
                        <div className="flex-1 max-w-2xl mx-8">
                            <StockSearch onSelect={handleStockSelect} />
                        </div>

                        {/* View Mode Tabs */}
                        <div className="flex items-center gap-2 mr-6 bg-gray-800/50 rounded-xl p-1">
                            <button
                                onClick={() => setViewMode('watchlist')}
                                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                                    viewMode === 'watchlist'
                                        ? 'bg-indigo-500 text-white shadow-lg'
                                        : 'text-gray-400 hover:text-white hover:bg-gray-700/50'
                                }`}
                            >
                                <span className="flex items-center gap-2">
                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
                                    </svg>
                                    自選股
                                </span>
                            </button>
                            <button
                                onClick={() => setViewMode('recommended')}
                                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                                    viewMode === 'recommended'
                                        ? 'bg-indigo-500 text-white shadow-lg'
                                        : 'text-gray-400 hover:text-white hover:bg-gray-700/50'
                                }`}
                            >
                                <span className="flex items-center gap-2">
                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                                    </svg>
                                    推薦
                                </span>
                            </button>
                            <button
                                onClick={() => setViewMode('positions')}
                                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                                    viewMode === 'positions'
                                        ? 'bg-indigo-500 text-white shadow-lg'
                                        : 'text-gray-400 hover:text-white hover:bg-gray-700/50'
                                }`}
                            >
                                <span className="flex items-center gap-2">
                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                                    </svg>
                                    持倉
                                </span>
                            </button>
                        </div>

                        {/* User Menu */}
                        <div className="flex items-center gap-4">
                            {/* Notification Bell */}
                            <NotificationBell />
                            
                            <div className="text-right hidden md:block">
                                <p className="text-sm font-medium text-white">{user?.username}</p>
                                <p className="text-xs text-gray-400">{user?.role === 'admin' ? '管理員' : '用戶'}</p>
                            </div>
                            <Button
                                variant="outline"
                                className="w-auto py-2 px-4 hover:border-red-500 hover:text-red-400"
                                onClick={handleLogout}
                            >
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                                </svg>
                                登出
                            </Button>
                        </div>
                    </div>
                </div>
            </nav>

            {/* Main Content */}
            <main className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
                {viewMode === 'watchlist' && (
                    <div className="mb-8 animate-fadeIn">
                        <div className="flex items-center gap-3 mb-6">
                            <div className="w-1 h-8 bg-gradient-to-b from-indigo-500 to-purple-600 rounded-full"></div>
                            <h2 className="text-3xl font-bold text-white">我的自選股</h2>
                        </div>
                        <WatchlistCard />
                    </div>
                )}
                
                {viewMode === 'recommended' && (
                    <div className="mb-8 animate-fadeIn">
                        <RecommendedStocks />
                    </div>
                )}
                
                {viewMode === 'positions' && (
                    <div className="mb-8 animate-fadeIn">
                        <div className="flex items-center gap-3 mb-6">
                            <div className="w-1 h-8 bg-gradient-to-b from-purple-500 to-pink-600 rounded-full"></div>
                            <h2 className="text-3xl font-bold text-white">投資組合</h2>
                        </div>
                        <PositionCard />
                    </div>
                )}
            </main>

            {/* Footer */}
            <footer className="border-t border-gray-800/50 mt-16">
                <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
                    <p className="text-center text-sm text-gray-500">
                        © 2026 AuraTrade. AI-Powered Investment Platform. All rights reserved.
                    </p>
                </div>
            </footer>
        </div>
    )
}

