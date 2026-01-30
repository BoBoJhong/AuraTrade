import { useState, useEffect } from 'react'
import { transactionService, Transaction, TransactionStats, TransactionCreate } from '@/services/transactionService'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'

export default function TransactionsPage() {
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [stats, setStats] = useState<TransactionStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState<TransactionCreate>({
    stock_symbol: '',
    transaction_type: 'buy',
    quantity: 0,
    price: 0,
    commission: 0,
    tax: 0,
    transaction_date: new Date().toISOString().split('T')[0],
    notes: ''
  })

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      setLoading(true)
      const [txData, statsData] = await Promise.all([
        transactionService.getTransactions(),
        transactionService.getStats()
      ])
      setTransactions(txData)
      setStats(statsData)
    } catch (error) {
      console.error('載入失敗:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await transactionService.createTransaction(formData)
      setShowForm(false)
      fetchData()
      setFormData({
        stock_symbol: '',
        transaction_type: 'buy',
        quantity: 0,
        price: 0,
        commission: 0,
        tax: 0,
        transaction_date: new Date().toISOString().split('T')[0],
        notes: ''
      })
    } catch (error) {
      console.error('建立失敗:', error)
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm('確定要刪除此交易記錄嗎？')) return
    try {
      await transactionService.deleteTransaction(id)
      fetchData()
    } catch (error) {
      console.error('刪除失敗:', error)
    }
  }

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen"><div className="text-xl">載入中...</div></div>
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold text-white">交易紀錄管理</h1>
          <Button onClick={() => setShowForm(!showForm)}>{showForm ? '取消' : '新增交易'}</Button>
        </div>

        {/* 統計卡片 */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-white/10 backdrop-blur-md rounded-xl p-4 border border-white/20">
              <div className="text-gray-300 text-sm">總交易數</div>
              <div className="text-2xl font-bold text-white">{stats.total_transactions}</div>
            </div>
            <div className="bg-white/10 backdrop-blur-md rounded-xl p-4 border border-white/20">
              <div className="text-gray-300 text-sm">總買入金額</div>
              <div className="text-2xl font-bold text-white">${stats.total_buy_amount.toFixed(2)}</div>
            </div>
            <div className="bg-white/10 backdrop-blur-md rounded-xl p-4 border border-white/20">
              <div className="text-gray-300 text-sm">總賣出金額</div>
              <div className="text-2xl font-bold text-white">${stats.total_sell_amount.toFixed(2)}</div>
            </div>
            <div className={`bg-white/10 backdrop-blur-md rounded-xl p-4 border border-white/20`}>
              <div className="text-gray-300 text-sm">淨損益</div>
              <div className={`text-2xl font-bold ${stats.net_profit >= 0 ? 'text-red-400' : 'text-green-400'}`}>
                ${stats.net_profit.toFixed(2)}
              </div>
            </div>
          </div>
        )}

        {/* 新增表單 */}
        {showForm && (
          <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 mb-6 border border-white/20">
            <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input
                id="transaction-stock-symbol"
                label="股票代碼"
                value={formData.stock_symbol}
                onChange={(e) => setFormData({ ...formData, stock_symbol: e.target.value })}
                required
              />
              <div>
                <label htmlFor="transaction-type" className="block text-sm font-medium text-gray-300 mb-2">類型</label>
                <select
                  id="transaction-type"
                  name="transaction-type"
                  value={formData.transaction_type}
                  onChange={(e) => setFormData({ ...formData, transaction_type: e.target.value as 'buy' | 'sell' })}
                  className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-white"
                >
                  <option value="buy">買入</option>
                  <option value="sell">賣出</option>
                </select>
              </div>
              <Input
                id="transaction-quantity"
                label="數量"
                type="number"
                step="0.01"
                value={formData.quantity}
                onChange={(e) => setFormData({ ...formData, quantity: parseFloat(e.target.value) })}
                required
              />
              <Input
                id="transaction-price"
                label="價格"
                type="number"
                step="0.01"
                value={formData.price}
                onChange={(e) => setFormData({ ...formData, price: parseFloat(e.target.value) })}
                required
              />
              <Input
                id="transaction-commission"
                label="手續費"
                type="number"
                step="0.01"
                value={formData.commission}
                onChange={(e) => setFormData({ ...formData, commission: parseFloat(e.target.value) })}
              />
              <Input
                id="transaction-tax"
                label="交易稅"
                type="number"
                step="0.01"
                value={formData.tax}
                onChange={(e) => setFormData({ ...formData, tax: parseFloat(e.target.value) })}
              />
              <Input
                id="transaction-date"
                label="交易日期"
                type="date"
                value={formData.transaction_date}
                onChange={(e) => setFormData({ ...formData, transaction_date: e.target.value })}
                required
              />
              <Input
                id="transaction-notes"
                label="備註"
                value={formData.notes || ''}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
              />
              <div className="md:col-span-2">
                <Button type="submit" className="w-full">建立交易記錄</Button>
              </div>
            </form>
          </div>
        )}

        {/* 交易列表 */}
        <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
          <h2 className="text-xl font-bold text-white mb-4">交易歷史</h2>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="text-left border-b border-white/20">
                  <th className="pb-3 text-gray-300">日期</th>
                  <th className="pb-3 text-gray-300">股票</th>
                  <th className="pb-3 text-gray-300">類型</th>
                  <th className="pb-3 text-gray-300">數量</th>
                  <th className="pb-3 text-gray-300">價格</th>
                  <th className="pb-3 text-gray-300">總金額</th>
                  <th className="pb-3 text-gray-300">操作</th>
                </tr>
              </thead>
              <tbody>
                {transactions.map((tx) => (
                  <tr key={tx.id} className="border-b border-white/10">
                    <td className="py-3 text-white">{tx.transaction_date}</td>
                    <td className="py-3 text-white font-medium">{tx.stock_symbol}</td>
                    <td className="py-3">
                      <span className={`px-2 py-1 rounded text-sm ${tx.transaction_type === 'buy' ? 'bg-red-500/20 text-red-400' : 'bg-green-500/20 text-green-400'}`}>
                        {tx.transaction_type === 'buy' ? '買入' : '賣出'}
                      </span>
                    </td>
                    <td className="py-3 text-white">{tx.quantity}</td>
                    <td className="py-3 text-white">${tx.price.toFixed(2)}</td>
                    <td className="py-3 text-white font-medium">${tx.total_amount.toFixed(2)}</td>
                    <td className="py-3">
                      <button
                        onClick={() => handleDelete(tx.id)}
                        className="text-red-400 hover:text-red-300 transition-colors"
                      >
                        刪除
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {transactions.length === 0 && (
              <div className="text-center py-8 text-gray-400">尚無交易記錄</div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
