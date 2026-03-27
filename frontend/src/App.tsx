import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './stores/authStore'

import { LoginPage } from './pages/auth/LoginPage'
import { RegisterPage } from './pages/auth/RegisterPage'
import { DashboardPage } from './pages/dashboard/DashboardPage'
import { StockDetailPage } from './pages/stock/StockDetailPage'
import { StockScreenerPage } from './pages/screener/StockScreenerPage'
import TransactionsPage from './pages/transactions/TransactionsPage'

// Protected Route Component
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
    const { user, isLoading } = useAuthStore()

    if (isLoading) {
        return <div className="min-h-screen bg-gray-900 flex items-center justify-center text-white">Loading...</div>
    }

    if (!user) {
        return <Navigate to="/login" replace />
    }

    return <>{children}</>
}

function App() {
    return (
        <Router>
            <Routes>
                <Route path="/login" element={<LoginPage />} />
                <Route path="/register" element={<RegisterPage />} />
                <Route
                    path="/dashboard"
                    element={
                        <ProtectedRoute>
                            <DashboardPage />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/stock/:symbol"
                    element={
                        <ProtectedRoute>
                            <StockDetailPage />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/screener"
                    element={
                        <ProtectedRoute>
                            <StockScreenerPage />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/transactions"
                    element={
                        <ProtectedRoute>
                            <TransactionsPage />
                        </ProtectedRoute>
                    }
                />
                <Route path="/" element={<Navigate to="/dashboard" replace />} />
            </Routes>
        </Router>
    )
}

export default App
