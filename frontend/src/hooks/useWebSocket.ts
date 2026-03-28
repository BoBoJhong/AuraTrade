import { useEffect, useRef, useState } from 'react'

interface PriceUpdate {
    type: 'price_update'
    symbol: string
    price: number
    change: number
    change_percent: number
    timestamp: string
}

export const useStockWebSocket = (symbol: string, enabled: boolean = true) => {
    const [priceData, setPriceData] = useState<PriceUpdate | null>(null)
    const [isConnected, setIsConnected] = useState(false)
    const wsRef = useRef<WebSocket | null>(null)
    const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null)

    useEffect(() => {
        if (!enabled || !symbol) return

        const connectWebSocket = () => {
            try {
                const ws = new WebSocket(`ws://localhost:8000/api/v1/ws/stocks/${symbol}`)
                wsRef.current = ws

                ws.onopen = () => {
                    console.log(`WebSocket connected for ${symbol}`)
                    setIsConnected(true)
                    
                    // Send subscribe message
                    ws.send(JSON.stringify({
                        type: 'subscribe',
                        symbol
                    }))
                }

                ws.onmessage = (event) => {
                    try {
                        const data = JSON.parse(event.data)
                        if (data.type === 'price_update') {
                            setPriceData(data)
                        }
                    } catch (error) {
                        console.error('Error parsing WebSocket message:', error)
                    }
                }

                ws.onerror = (error) => {
                    console.error('WebSocket error:', error)
                }

                ws.onclose = () => {
                    console.log(`WebSocket disconnected for ${symbol}`)
                    setIsConnected(false)
                    
                    // Attempt to reconnect after 5 seconds
                    reconnectTimeoutRef.current = setTimeout(() => {
                        if (enabled) {
                            console.log(`Reconnecting WebSocket for ${symbol}...`)
                            connectWebSocket()
                        }
                    }, 5000)
                }
            } catch (error) {
                console.error('Error creating WebSocket:', error)
            }
        }

        connectWebSocket()

        // Cleanup function
        return () => {
            if (reconnectTimeoutRef.current) {
                clearTimeout(reconnectTimeoutRef.current)
            }
            if (wsRef.current) {
                wsRef.current.close()
                wsRef.current = null
            }
        }
    }, [symbol, enabled])

    return { priceData, isConnected }
}

export const useMarketWebSocket = (enabled: boolean = true) => {
    const [marketData, setMarketData] = useState<any>(null)
    const [isConnected, setIsConnected] = useState(false)
    const wsRef = useRef<WebSocket | null>(null)

    useEffect(() => {
        if (!enabled) return

        try {
            const ws = new WebSocket('ws://localhost:8000/api/v1/ws/market')
            wsRef.current = ws

            ws.onopen = () => {
                console.log('Market WebSocket connected')
                setIsConnected(true)
            }

            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data)
                    setMarketData(data)
                } catch (error) {
                    console.error('Error parsing market data:', error)
                }
            }

            ws.onerror = (error) => {
                console.error('Market WebSocket error:', error)
            }

            ws.onclose = () => {
                console.log('Market WebSocket disconnected')
                setIsConnected(false)
            }
        } catch (error) {
            console.error('Error creating market WebSocket:', error)
        }

        return () => {
            if (wsRef.current) {
                wsRef.current.close()
                wsRef.current = null
            }
        }
    }, [enabled])

    return { marketData, isConnected }
}