import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../../stores/authStore'
import { AuthLayout } from '../../components/layouts/AuthLayout'
import { Input } from '../../components/ui/Input'
import { Button } from '../../components/ui/Button'

export const RegisterPage = () => {
    const navigate = useNavigate()
    const register = useAuthStore((state) => state.register)
    const isLoading = useAuthStore((state) => state.isLoading)
    const error = useAuthStore((state) => state.error)

    const [formData, setFormData] = useState({
        username: '',
        email: '',
        password: '',
        confirmPassword: '',
    })

    const [formError, setFormError] = useState<string | null>(null)

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setFormError(null)

        if (formData.password !== formData.confirmPassword) {
            setFormError('密碼不一致')
            return
        }

        if (formData.password.length < 8) {
            setFormError('密碼必須至少 8 個字元')
            return
        }

        try {
            await register({
                username: formData.username,
                email: formData.email,
                password: formData.password,
            })
            navigate('/dashboard')
        } catch (err) {
            // Error is handled by store
        }
    }

    return (
        <AuthLayout
            title="加入 AuraTrade"
            subtitle="開啟您的智能投資之旅"
        >
            <form className="space-y-6" onSubmit={handleSubmit}>
                {(error || formError) && (
                    <div className="relative overflow-hidden bg-red-500/10 border-2 border-red-500/30 text-red-400 rounded-xl p-4 text-sm flex items-start gap-3 backdrop-blur-sm animate-in fade-in slide-in-from-top-2 duration-300">
                        <div className="absolute inset-0 bg-gradient-to-r from-red-500/5 to-transparent" />
                        <svg className="w-5 h-5 flex-shrink-0 mt-0.5 relative z-10" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                        </svg>
                        <span className="relative z-10">{error || formError}</span>
                    </div>
                )}

                <Input
                    id="register-username"
                    label="用戶名稱"
                    type="text"
                    required
                    placeholder="您的暱稱"
                    value={formData.username}
                    onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                />

                <Input
                    id="register-email"
                    label="Email"
                    type="email"
                    required
                    placeholder="your@email.com"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                />

                <Input
                    id="register-password"
                    label="密碼"
                    type="password"
                    required
                    minLength={8}
                    placeholder="至少 8 個字元"
                    value={formData.password}
                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                />

                <Input
                    id="register-confirm-password"
                    label="確認密碼"
                    type="password"
                    required
                    placeholder="再次輸入密碼"
                    value={formData.confirmPassword}
                    onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                />

                <div className="relative overflow-hidden flex items-start gap-3 text-xs text-gray-400 bg-gray-800/40 border border-gray-700/50 p-3.5 rounded-xl">
                    <div className="absolute inset-0 bg-gradient-to-r from-indigo-500/5 to-transparent" />
                    <svg className="w-4 h-4 flex-shrink-0 mt-0.5 text-indigo-400 relative z-10" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                    </svg>
                    <span className="relative z-10">密碼需包含至少 8 個字元，並包含大小寫字母與數字</span>
                </div>

                <Button type="submit" isLoading={isLoading} className="mt-6">
                    {isLoading ? '註冊中...' : '立即註冊'}
                </Button>

                <div className="text-center text-sm pt-4 border-t border-gray-800">
                    <span className="text-gray-500">已經有帳號了？</span>{' '}
                    <Link to="/login" className="font-semibold text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-purple-400 hover:from-indigo-300 hover:to-purple-300 transition-all">
                        直接登入 →
                    </Link>
                </div>
            </form>

            {/* Benefits */}
            <div className="mt-8 pt-6 border-t border-gray-800/50">
                <p className="text-xs text-gray-500 text-center mb-6">註冊即表示您同意我們的服務條款與隱私政策</p>
                <div className="grid grid-cols-3 gap-6">
                    <div className="text-center space-y-2 group">
                        <div className="relative inline-flex items-center justify-center w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-500/10 to-purple-500/10 border border-indigo-500/20 group-hover:scale-110 transition-transform duration-300">
                            <div className="text-xl font-bold bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">∞</div>
                        </div>
                        <p className="text-xs text-gray-500 font-medium">永久免費</p>
                    </div>
                    <div className="text-center space-y-2 group">
                        <div className="relative inline-flex items-center justify-center w-12 h-12 rounded-xl bg-gradient-to-br from-green-500/10 to-teal-500/10 border border-green-500/20 group-hover:scale-110 transition-transform duration-300">
                            <div className="text-xl font-bold bg-gradient-to-r from-green-400 to-teal-400 bg-clip-text text-transparent">AI</div>
                        </div>
                        <p className="text-xs text-gray-500 font-medium">智能分析</p>
                    </div>
                    <div className="text-center space-y-2 group">
                        <div className="relative inline-flex items-center justify-center w-12 h-12 rounded-xl bg-gradient-to-br from-orange-500/10 to-pink-500/10 border border-orange-500/20 group-hover:scale-110 transition-transform duration-300">
                            <div className="text-sm font-bold bg-gradient-to-r from-orange-400 to-pink-400 bg-clip-text text-transparent">24/7</div>
                        </div>
                        <p className="text-xs text-gray-500 font-medium">即時監控</p>
                    </div>
                </div>
            </div>
        </AuthLayout>
    )
}

