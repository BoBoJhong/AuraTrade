import { InputHTMLAttributes } from 'react'

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
    label: string
    error?: string
}

export const Input = ({ label, error, className = '', id, ...props }: InputProps) => {
    // Generate a unique id if not provided
    const inputId = id || `input-${label.replace(/\s+/g, '-').toLowerCase()}-${Math.random().toString(36).substr(2, 9)}`
    
    return (
        <div className="w-full group">
            <label 
                htmlFor={inputId}
                className="block text-sm font-semibold text-slate-700 mb-2.5 group-focus-within:text-indigo-700 transition-colors"
            >
                {label}
            </label>
            <div className="relative">
                <input
                    id={inputId}
                    name={inputId}
                    className={`
                        w-full px-4 py-3.5 rounded-xl
                        bg-white border-2 border-slate-200
                        text-slate-900 placeholder-slate-400
                        focus:outline-none focus:border-indigo-500 focus:bg-white
                        focus:ring-4 focus:ring-indigo-500/15
                        hover:border-slate-300
                        transition-all duration-300
                        ${error ? 'border-red-400 focus:border-red-500 focus:ring-red-500/15' : ''}
                        ${className}
                    `}
                    {...props}
                />
                {/* Focus Glow Effect */}
                <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-indigo-500/0 to-cyan-500/0 group-focus-within:from-indigo-500/5 group-focus-within:to-cyan-500/5 pointer-events-none transition-all duration-300" />
            </div>
            {error && (
                <p className="mt-2 text-sm text-red-600 flex items-center gap-1.5 animate-in fade-in slide-in-from-top-1 duration-300">
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                    </svg>
                    {error}
                </p>
            )}
        </div>
    )
}
