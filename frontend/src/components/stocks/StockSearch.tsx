import { useState, useEffect } from 'react'
import { stockService, Stock } from '../../services/stockService'
import { Input } from '../ui/Input'

interface StockSearchProps {
    onSelect: (stock: Stock) => void
}

export const StockSearch = ({ onSelect }: StockSearchProps) => {
    const [query, setQuery] = useState('')
    const [results, setResults] = useState<Stock[]>([])
    const [isLoading, setIsLoading] = useState(false)
    const [showResults, setShowResults] = useState(false)

    // Auto search when user types (with debounce)
    useEffect(() => {
        const timer = setTimeout(() => {
            if (query.trim().length > 0) {
                handleSearch()
            } else {
                setResults([])
                setShowResults(false)
            }
        }, 500)

        return () => clearTimeout(timer)
    }, [query])

    const handleSearch = async () => {
        if (!query.trim()) return
        
        setIsLoading(true)
        try {
            const data = await stockService.search(query.trim())
            setResults(data)
            setShowResults(true)
        } catch (error) {
            console.error('Search error:', error)
            setResults([])
        } finally {
            setIsLoading(false)
        }
    }

    const handleSelect = (stock: Stock) => {
        onSelect(stock)
        setResults([])
        setQuery('')
        setShowResults(false)
    }

    return (
        <div className="relative">
            <div className="relative">
                <div className="relative">
                    <input
                        id="stock-search-input"
                        type="text"
                        placeholder="輸入股票代碼或名稱 (例如: 2330 或 AAPL)"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        onFocus={() => results.length > 0 && setShowResults(true)}
                        className="w-full px-4 md:px-5 py-3 md:py-4 pl-10 md:pl-12 bg-white/5 backdrop-blur-xl border border-white/20 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-500/50 transition-all text-sm md:text-lg shadow-lg"
                        aria-label="搜尋股票代碼或名稱"
                    />
                    <svg className="absolute left-3 md:left-4 top-1/2 -translate-y-1/2 w-5 h-5 md:w-6 md:h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                </div>
                {isLoading && (
                    <div className="absolute right-4 top-1/2 -translate-y-1/2">
                        <svg className="animate-spin h-5 w-5 text-indigo-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                    </div>
                )}
                {!isLoading && query && (
                    <button
                        onClick={() => {
                            setQuery('')
                            setResults([])
                            setShowResults(false)
                        }}
                        className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white transition-colors p-1 rounded-lg hover:bg-white/10"
                    >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                )}
            </div>

            {/* Search Tips */}
            {query.length === 0 && (
                <div className="mt-3 flex items-center gap-2 text-sm text-gray-400 bg-indigo-500/5 border border-indigo-500/20 rounded-lg p-3">
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                    </svg>
                    <span>提示：台股直接輸入代碼（如 2330），美股輸入代號（如 AAPL）</span>
                </div>
            )}

            {/* Results Dropdown */}
            {showResults && results.length > 0 && (
                <div className="absolute z-[9999] w-full mt-3 glass border border-indigo-500/30 rounded-2xl shadow-2xl max-h-[70vh] md:max-h-96 overflow-y-auto backdrop-blur-xl">
                    <div className="p-2 md:p-3">
                        <div className="flex items-center justify-between px-3 md:px-4 py-2 md:py-3 bg-indigo-500/10 rounded-xl mb-2">
                            <div className="flex items-center gap-2 text-xs md:text-sm font-medium text-indigo-300">
                                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                                    <path fillRule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clipRule="evenodd" />
                                </svg>
                                找到 {results.length} 個結果
                            </div>
                            <button
                                onClick={() => {
                                    setShowResults(false)
                                    setQuery('')
                                    setResults([])
                                }}
                                className="text-gray-400 hover:text-white transition-colors tap-target"
                            >
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                </svg>
                            </button>
                        </div>
                        {results.map((stock) => (
                            <div
                                key={stock.symbol}
                                className="group p-3 md:p-4 hover:bg-indigo-500/10 cursor-pointer rounded-xl flex justify-between items-center transition-all duration-200 border border-transparent hover:border-indigo-500/50 hover:shadow-lg tap-target"
                                onClick={() => handleSelect(stock)}
                            >
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center gap-2 md:gap-3 flex-wrap">
                                        <span className="font-bold text-white text-base md:text-lg group-hover:text-indigo-300 transition-colors">
                                            {stock.symbol}
                                        </span>
                                        {stock.market && (
                                            <span className={`text-xs px-2 md:px-2.5 py-0.5 md:py-1 rounded-full font-medium whitespace-nowrap ${
                                                stock.market === 'TW' 
                                                    ? 'bg-blue-500/20 text-blue-300 border border-blue-400/40' 
                                                    : 'bg-purple-500/20 text-purple-300 border border-purple-400/40'
                                            }`}>
                                                {stock.market === 'TW' ? '🇹🇼 台股' : stock.market}
                                            </span>
                                        )}
                                    </div>
                                    <div className="text-gray-300 text-xs md:text-sm mt-1 md:mt-1.5 font-medium truncate">{stock.name}</div>
                                    {stock.sector && (
                                        <div className="text-gray-500 text-xs mt-1 truncate">{stock.sector}</div>
                                    )}
                                </div>
                                <div className="text-right ml-2 md:ml-4 flex flex-col sm:flex-row items-end sm:items-center gap-2 md:gap-3 flex-shrink-0">
                                    <div className="hidden sm:block">
                                        {stock.price && (
                                            <div className="text-white font-bold text-lg md:text-xl">
                                                ${typeof stock.price === 'number' ? stock.price.toFixed(2) : stock.price}
                                            </div>
                                        )}
                                        {stock.change_percent !== undefined && (
                                            <div className={`text-xs md:text-sm font-semibold ${
                                                stock.change_percent >= 0 ? 'text-green-400' : 'text-red-400'
                                            }`}>
                                                {stock.change_percent >= 0 ? '▲' : '▼'} {Math.abs(stock.change_percent).toFixed(2)}%
                                            </div>
                                        )}
                                    </div>
                                    <button className="px-3 md:px-4 py-1.5 md:py-2 rounded-lg bg-indigo-500/20 text-indigo-300 border border-indigo-500/40 hover:bg-indigo-500/30 hover:border-indigo-400 transition-all font-medium text-xs md:text-sm whitespace-nowrap tap-target">
                                        加入
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* No Results */}
            {showResults && results.length === 0 && !isLoading && query.trim().length > 0 && (
                <div className="absolute z-50 w-full mt-2 glass border border-gray-700/50 rounded-xl p-4 backdrop-blur-xl">
                    <div className="text-center text-gray-400">
                        <svg className="w-12 h-12 mx-auto mb-2 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <p className="text-sm">找不到「{query}」相關股票</p>
                        <p className="text-xs text-gray-500 mt-1">請確認股票代碼是否正確</p>
                    </div>
                </div>
            )}
        </div>
    )
}
