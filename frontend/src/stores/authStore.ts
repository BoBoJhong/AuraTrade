import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { api } from '../lib/axios'
import type { User, LoginRequest, RegisterRequest, AuthResponse } from '../types/auth'

interface AuthState {
    user: User | null
    accessToken: string | null
    refreshToken: string | null
    isLoading: boolean
    error: string | null

    // Actions
    login: (credentials: LoginRequest) => Promise<void>
    register: (data: RegisterRequest) => Promise<void>
    logout: () => void
    clearError: () => void
}

export const useAuthStore = create<AuthState>()(
    persist(
        (set) => ({
            user: null,
            accessToken: null,
            refreshToken: null,
            isLoading: false,
            error: null,

            login: async (credentials: LoginRequest) => {
                set({ isLoading: true, error: null })
                try {
                    const response = await api.post<any>('/auth/login', credentials)
                    const { access_token, refresh_token, user_id, email, username } = response.data

                    // Construct user object from flat response
                    const user: User = {
                        user_id,
                        email,
                        username,
                        role: 'user', // Default role
                        created_at: new Date().toISOString()
                    }

                    // Store tokens
                    localStorage.setItem('access_token', access_token)
                    localStorage.setItem('refresh_token', refresh_token)

                    set({
                        user,
                        accessToken: access_token,
                        refreshToken: refresh_token,
                        isLoading: false,
                    })
                } catch (error: any) {
                    const errorMessage = error.response?.data?.detail?.message || error.response?.data?.message || '登入失敗'
                    set({ error: errorMessage, isLoading: false })
                    throw error
                }
            },

            register: async (data: RegisterRequest) => {
                set({ isLoading: true, error: null })
                try {
                    const response = await api.post<any>('/auth/register', data)
                    const { access_token, refresh_token, user_id, email, username } = response.data

                    // Construct user object from flat response
                    const user: User = {
                        user_id,
                        email,
                        username,
                        role: 'user', // Default role
                        created_at: new Date().toISOString()
                    }

                    // Store tokens
                    localStorage.setItem('access_token', access_token)
                    localStorage.setItem('refresh_token', refresh_token)

                    set({
                        user,
                        accessToken: access_token,
                        refreshToken: refresh_token,
                        isLoading: false,
                    })
                } catch (error: any) {
                    const errorMessage = error.response?.data?.detail?.message || error.response?.data?.message || '註冊失敗'
                    set({ error: errorMessage, isLoading: false })
                    throw error
                }
            },

            logout: () => {
                localStorage.removeItem('access_token')
                localStorage.removeItem('refresh_token')
                set({
                    user: null,
                    accessToken: null,
                    refreshToken: null,
                    error: null,
                })
            },

            clearError: () => set({ error: null }),
        }),
        {
            name: 'auth-storage',
            partialize: (state) => ({
                user: state.user,
                accessToken: state.accessToken,
                refreshToken: state.refreshToken,
            }),
        }
    )
)
