import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../../stores/authStore'
import { AuthLayout } from '../../components/layouts/AuthLayout'
import { Input } from '../../components/ui/Input'
import { Button } from '../../components/ui/Button'

export const LoginPage = () => {
    const navigate = useNavigate()
    const login = useAuthStore((state) => state.login)
    const isLoading = useAuthStore((state) => state.isLoading)
    const error = useAuthStore((state) => state.error)

    const [formData, setFormData] = useState({
        email: '',
        password: '',
    })

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        try {
            await login(formData)
            navigate('/dashboard')
        } catch (err) {
            // Error is handled by store
        }
    }

    return (
        <AuthLayout
            title="歡迎回到 AuraTrade"
            subtitle="智能投資決策，從這裡開始"
        >
            <form className="space-y-6" onSubmit={handleSubmit}>
                {error && (
                    <div className="relative overflow-hidden bg-red-50 border border-red-200 text-red-700 rounded-xl p-4 text-sm flex items-center gap-3 backdrop-blur-sm animate-in fade-in slide-in-from-top-2 duration-300">
                        <div className="absolute inset-0 bg-gradient-to-r from-red-500/5 to-transparent" />
                        <svg className="w-5 h-5 flex-shrink-0 relative z-10" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                        </svg>
                        <span className="relative z-10">{error}</span>
                    </div>
                )}

                <Input
                    id="login-email"
                    label="Email"
                    type="email"
                    required
                    placeholder="your@email.com"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                />

                <Input
                    id="login-password"
                    label="密碼"
                    type="password"
                    required
                    placeholder="••••••••"
                    value={formData.password}
                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                />

                <div className="flex items-center justify-between text-sm pt-1">
                    <label className="flex items-center gap-2.5 text-slate-600 cursor-pointer hover:text-slate-800 transition-colors group">
                        <input 
                            id="remember-me"
                            name="remember-me"
                            type="checkbox" 
                            className="w-4 h-4 rounded border-slate-300 bg-white text-indigo-600 focus:ring-2 focus:ring-indigo-500/20 focus:ring-offset-0 transition-all" 
                        />
                        <span className="select-none">記住我</span>
                    </label>
                    <a href="#" className="font-medium text-indigo-700 hover:text-indigo-800 transition-colors relative group">
                        忘記密碼？
                        <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-indigo-700 group-hover:w-full transition-all duration-300" />
                    </a>
                </div>

                <Button type="submit" isLoading={isLoading} className="mt-6">
                    {isLoading ? '登入中...' : '立即登入'}
                </Button>

                <div className="relative my-8">
                    <div className="absolute inset-0 flex items-center">
                        <div className="w-full border-t border-slate-200"></div>
                    </div>
                    <div className="relative flex justify-center text-sm">
                        <span className="px-4 bg-white/90 text-slate-500 font-medium">或使用以下方式</span>
                    </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                    <button type="button" className="group relative flex items-center justify-center gap-2.5 px-4 py-3.5 border-2 border-slate-200 rounded-xl text-slate-700 hover:border-slate-300 hover:bg-slate-50 transition-all duration-300 overflow-hidden">
                        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-slate-100 to-transparent translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000" />
                        <svg className="w-5 h-5 relative z-10" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M12.545,10.239v3.821h5.445c-0.712,2.315-2.647,3.972-5.445,3.972c-3.332,0-6.033-2.701-6.033-6.032s2.701-6.032,6.033-6.032c1.498,0,2.866,0.549,3.921,1.453l2.814-2.814C17.503,2.988,15.139,2,12.545,2C7.021,2,2.543,6.477,2.543,12s4.478,10,10.002,10c8.396,0,10.249-7.85,9.426-11.748L12.545,10.239z" />
                        </svg>
                        <span className="font-medium relative z-10">Google</span>
                    </button>
                    <button type="button" className="group relative flex items-center justify-center gap-2.5 px-4 py-3.5 border-2 border-slate-200 rounded-xl text-slate-700 hover:border-slate-300 hover:bg-slate-50 transition-all duration-300 overflow-hidden">
                        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-slate-100 to-transparent translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000" />
                        <svg className="w-5 h-5 relative z-10" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M12 2C6.477 2 2 6.477 2 12c0 4.42 2.865 8.17 6.839 9.49.5.092.682-.217.682-.482 0-.237-.008-.866-.013-1.7-2.782.603-3.369-1.34-3.369-1.34-.454-1.156-1.11-1.463-1.11-1.463-.908-.62.069-.608.069-.608 1.003.07 1.531 1.03 1.531 1.03.892 1.529 2.341 1.087 2.91.831.092-.646.35-1.086.636-1.336-2.22-.253-4.555-1.11-4.555-4.943 0-1.091.39-1.984 1.029-2.683-.103-.253-.446-1.27.098-2.647 0 0 .84-.269 2.75 1.025A9.578 9.578 0 0112 6.836c.85.004 1.705.114 2.504.336 1.909-1.294 2.747-1.025 2.747-1.025.546 1.377.203 2.394.1 2.647.64.699 1.028 1.592 1.028 2.683 0 3.842-2.339 4.687-4.566 4.935.359.309.678.919.678 1.852 0 1.336-.012 2.415-.012 2.743 0 .267.18.578.688.48C19.138 20.167 22 16.418 22 12c0-5.523-4.477-10-10-10z" />
                        </svg>
                        <span className="font-medium relative z-10">GitHub</span>
                    </button>
                </div>

                <div className="text-center text-sm pt-4 border-t border-slate-200">
                    <span className="text-slate-500">還沒有帳號？</span>{' '}
                    <Link to="/register" className="font-semibold text-transparent bg-clip-text bg-gradient-to-r from-indigo-700 to-cyan-700 hover:from-indigo-800 hover:to-cyan-800 transition-all">
                        立即註冊，開始您的投資之旅 →
                    </Link>
                </div>
            </form>

            {/* Trust Indicators */}
            <div className="mt-8 pt-6 border-t border-slate-200">
                <div className="flex items-center justify-center gap-8 text-xs text-slate-500">
                    <div className="flex items-center gap-1">
                        <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm11.541 3.708a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>256位元加密</span>
                    </div>
                    <div className="flex items-center gap-1">
                        <svg className="w-4 h-4 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M10 2a6 6 0 00-6 6v3.586l-.707.707A1 1 0 004 14h12a1 1 0 00.707-1.707L16 11.586V8a6 6 0 00-6-6zM10 18a3 3 0 01-3-3h6a3 3 0 01-3 3z" />
                        </svg>
                        <span>即時通知</span>
                    </div>
                    <div className="flex items-center gap-1">
                        <svg className="w-4 h-4 text-purple-500" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clipRule="evenodd" />
                        </svg>
                        <span>AI 驅動分析</span>
                    </div>
                </div>
            </div>
        </AuthLayout>
    )
}

