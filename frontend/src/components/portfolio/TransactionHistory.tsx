import { useState, useEffect } from 'react'
import axios from 'axios'

interface Transaction {
    id: number
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

interface TransactionSummary {
    total_buy_amount: number
    total_sell_amount: number
    total_commission: number
    total_tax: number
    net_profit_loss: number
    total_transactions: number
}

export const TransactionHistory = () => {
    const [transactions, setTransactions] = useState<Transaction[]>([])
    const [summary, setSummary] = useState<TransactionSummary | null>(null)
    const [isLoading, setIsLoading] = useState(true)
    const [showAddModal, setShowAddModal] = useState(false)
    const [filterSymbol, setFilterSymbol] = useState('')
    const [filterType, setFilterType] = useState<'' | 'buy' | 'sell'>('')

    useEffect(() => {
        fetchTransactions()
        fetchSummary()
    }, [filterSymbol, filterType])

    const fetchTransactions = async () => {
        try {
            setIsLoading(true)
            const params: any = { limit: 100 }
            if (filterSymbol) params.symbol = filterSymbol
            if (filterType) params.transaction_type = filterType

            const response = await axios.get('http://localhost:8000/api/v1/transactions', {
                params,
                headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
            })
            setTransactions(response.data)
        } catch (error) {
            console.error('Failed to fetch transactions:', error)
        } finally {
            setIsLoading(false)
        }
    }

    const fetchSummary = async () => {
        try {
            const response = await axios.get('http://localhost:8000/api/v1/transactions/summary/stats', {
                headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
            })
            setSummary(response.data)
        } catch (error) {
            console.error('Failed to fetch summary:', error)
        }
    }

    const handleDelete = async (id: number) => {
        if (!confirm('確定要刪除這筆交易記錄嗎？')) return

        try {
            await axios.delete(`http://localhost:8000/api/v1/transactions/${id}`, {
                headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
            })
            fetchTransactions()
            fetchSummary()
        } catch (error) {
            console.error('Failed to delete transaction:', error)
            alert('刪除失敗')
        }
    }

    const formatDate = (dateStr: string) => {
        return new Date(dateStr).toLocaleDateString('zh-TW')
    }

    const formatCurrency = (amount: number) => {
        return new Intl.NumberFormat('zh-TW', {
            style: 'currency',
            currency: 'TWD',
            minimumFractionDigits: 0
        }).format(amount)
    }

    return (
        <div className="space-y-6">
            {/* Summary Cards */}
            {summary && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="glass rounded-2xl p-6">
                        <div className="flex items-center gap-3 mb-2">
                            <div className="w-10 h-10 rounded-lg bg-green-500/20 flex items-center justify-center">
                                <svg className="w-6 h-6 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                                </svg>
                            </div>
                            <div>
                                <p className="text-sm text-gray-400">總買入</p>
                                <p className="text-xl font-bold text-white">{formatCurrency(summary.total_buy_amount)}</p>
                            </div>
                        </div>
                    </div>

                    <div className="glass rounded-2xl p-6">
                        <div className="flex items-center gap-3 mb-2">
                            <div className="w-10 h-10 rounded-lg bg-blue-500/20 flex items-center justify-center">
                                <svg className="w-6 h-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />
                                </svg>
                            </div>
                            <div>
                                <p className="text-sm text-gray-400">總賣出</p>
                                <p className="text-xl font-bold text-white">{formatCurrency(summary.total_sell_amount)}</p>
                            </div>
                        </div>
                    </div>

                    <div className="glass rounded-2xl p-6">
                        <div className="flex items-center gap-3 mb-2">
                            <div className={`w-10 h-10 rounded-lg ${summary.net_profit_loss >= 0 ? 'bg-green-500/20' : 'bg-red-500/20'} flex items-center justify-center`}>
                                <svg className={`w-6 h-6 ${summary.net_profit_loss >= 0 ? 'text-green-400' : 'text-red-400'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                            </div>
                            <div>
                                <p className="text-sm text-gray-400">淨損益</p>
                                <p className={`text-xl font-bold ${summary.net_profit_loss >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                                    {formatCurrency(summary.net_profit_loss)}
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Transaction List */}
            <div className="glass rounded-2xl p-6">
                <div className="flex justify-between items-center mb-6">
                    <h3 className="text-xl font-bold text-white">交易記錄</h3>
                    <div className="flex gap-3">
                        <input
                            type="text"
                            placeholder="篩選股票代號"
                            value={filterSymbol}
                            onChange={(e) => setFilterSymbol(e.target.value)}
                            className="px-4 py-2 rounded-lg bg-gray-800 border border-gray-700 text-white focus:border-indigo-500 focus:outline-none"
                        />
                        <select
                            value={filterType}
                            onChange={(e) => setFilterType(e.target.value as '' | 'buy' | 'sell')}
                            className="px-4 py-2 rounded-lg bg-gray-800 border border-gray-700 text-white focus:border-indigo-500 focus:outline-none"
                        >
                            <option value="">全部類型</option>
                            <option value="buy">買入</option>
                            <option value="sell">賣出</option>
                        </select>
                    </div>
                </div>

                {isLoading ? (
                    <div className="text-center py-12">
                        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500"></div>
                    </div>
                ) : transactions.length === 0 ? (
                    <div className="text-center py-12">
                        <p className="text-gray-400">尚無交易記錄</p>
                    </div>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead>
                                <tr className="border-b border-gray-700">
                                    <th className="text-left py-3 px-4 text-gray-400 font-medium">日期</th>
                                    <th className="text-left py-3 px-4 text-gray-400 font-medium">股票</th>
                                    <th className="text-center py-3 px-4 text-gray-400 font-medium">類型</th>
                                    <th className="text-right py-3 px-4 text-gray-400 font-medium">數量</th>
                                    <th className="text-right py-3 px-4 text-gray-400 font-medium">價格</th>
                                    <th className="text-right py-3 px-4 text-gray-400 font-medium">總額</th>
                                    <th className="text-center py-3 px-4 text-gray-400 font-medium">操作</th>
                                </tr>
                            </thead>
                            <tbody>
                                {transactions.map((tx) => (
                                    <tr key={tx.id} className="border-b border-gray-800 hover:bg-gray-800/30 transition-colors">
                                        <td className="py-3 px-4 text-gray-300">{formatDate(tx.transaction_date)}</td>
                                        <td className="py-3 px-4 text-white font-medium">{tx.stock_symbol}</td>
                                        <td className="py-3 px-4 text-center">
                                            <span className={`px-3 py-1 rounded-lg text-xs font-medium ${
                                                tx.transaction_type === 'buy'
                                                    ? 'bg-green-500/20 text-green-400'
                                                    : 'bg-red-500/20 text-red-400'
                                            }`}>
                                                {tx.transaction_type === 'buy' ? '買入' : '賣出'}
                                            </span>
                                        </td>
                                        <td className="py-3 px-4 text-right text-gray-300">{tx.quantity}</td>
                                        <td className="py-3 px-4 text-right text-gray-300">{formatCurrency(tx.price)}</td>
                                        <td className="py-3 px-4 text-right text-white font-medium">{formatCurrency(tx.total_amount)}</td>
                                        <td className="py-3 px-4 text-center">
                                            <button
                                                onClick={() => handleDelete(tx.id)}
                                                className="p-2 rounded-lg text-red-400 hover:bg-red-500/20 transition-all"
                                            >
                                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                                </svg>
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </div>
    )
}