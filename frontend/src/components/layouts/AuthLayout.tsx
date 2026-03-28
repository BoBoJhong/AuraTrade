import { ReactNode } from 'react'

interface AuthLayoutProps {
    children: ReactNode
    title: string
    subtitle?: string
}

export const AuthLayout = ({ children, title, subtitle }: AuthLayoutProps) => {
    return (
        <div className="light-auth min-h-screen flex items-center justify-center px-4 relative overflow-hidden bg-gradient-to-br from-slate-50 via-indigo-50 to-cyan-50">
            {/* Enhanced Animated Background */}
            <div className="absolute inset-0 overflow-hidden">
                <div className="absolute -top-40 -left-40 w-96 h-96 bg-indigo-300/25 rounded-full blur-3xl animate-pulse" />
                <div className="absolute top-1/3 -right-40 w-96 h-96 bg-sky-300/25 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }} />
                <div className="absolute -bottom-40 left-1/3 w-96 h-96 bg-cyan-300/20 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '2s' }} />
                {/* Grid Pattern */}
                <div className="absolute inset-0 bg-[linear-gradient(rgba(99,102,241,0.04)_1px,transparent_1px),linear-gradient(to_right,rgba(99,102,241,0.04)_1px,transparent_1px)] bg-[size:4rem_4rem]" />
            </div>

            <div className="max-w-md w-full relative z-10">
                {/* Premium Glass Card */}
                <div className="relative group">
                    {/* Glow Effect */}
                    <div className="absolute -inset-0.5 bg-gradient-to-r from-indigo-500/35 to-cyan-500/35 rounded-3xl blur opacity-40 group-hover:opacity-60 transition duration-1000" />
                    
                    <div className="relative bg-white/95 backdrop-blur-2xl border border-slate-200 rounded-3xl shadow-xl p-8">
                        {/* Logo/Brand */}
                        <div className="text-center mb-8">
                            <div className="relative inline-flex items-center justify-center mb-6">
                                <div className="absolute inset-0 bg-gradient-to-r from-indigo-500 to-cyan-500 rounded-2xl blur-xl opacity-35" />
                                <div className="relative flex items-center justify-center w-20 h-20 rounded-2xl bg-gradient-to-br from-indigo-500 via-sky-500 to-cyan-500 shadow-lg">
                                    <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                                    </svg>
                                </div>
                            </div>
                            <h1 className="text-4xl font-bold mb-2">
                                <span className="bg-gradient-to-r from-indigo-700 via-sky-700 to-cyan-700 bg-clip-text text-transparent">
                                    {title}
                                </span>
                            </h1>
                            {subtitle && (
                                <p className="text-slate-600 text-base">
                                    {subtitle}
                                </p>
                            )}
                        </div>

                        <div>
                            {children}
                        </div>
                    </div>
                </div>

                {/* Footer */}
                <p className="text-center text-sm text-slate-500 mt-8">
                    © 2026 AuraTrade · AI 驅動的投資平台
                </p>
            </div>
        </div>
    )
}
