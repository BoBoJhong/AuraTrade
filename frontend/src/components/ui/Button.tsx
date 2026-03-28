import { ButtonHTMLAttributes, ReactNode } from 'react'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: 'primary' | 'secondary' | 'outline' | 'danger'
    isLoading?: boolean
    children: ReactNode
}

export const Button = ({
    variant = 'primary',
    isLoading,
    children,
    className = '',
    disabled,
    ...props
}: ButtonProps) => {
    const baseStyles = "relative w-full py-3.5 px-6 rounded-xl font-semibold transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 overflow-hidden group focus:outline-none focus:ring-4 focus:ring-indigo-500/20"

    const variants = {
        primary: "bg-gradient-to-r from-indigo-600 via-sky-600 to-cyan-600 text-white hover:shadow-lg hover:shadow-indigo-500/30 hover:scale-[1.01] active:scale-[0.98]",
        secondary: "bg-slate-100 text-slate-800 hover:bg-slate-200 border-2 border-slate-200 hover:border-slate-300",
        outline: "border-2 border-slate-300 text-slate-700 hover:bg-slate-50 hover:border-indigo-400",
        danger: "bg-gradient-to-r from-rose-600 to-red-600 text-white hover:shadow-lg hover:shadow-rose-500/30 hover:scale-[1.01] active:scale-[0.98]"
    }

    return (
        <button
            className={`${baseStyles} ${variants[variant]} ${className}`}
            disabled={disabled || isLoading}
            {...props}
        >
            {isLoading && (
                <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
            )}
            {isLoading ? '處理中...' : children}
        </button>
    )
}

