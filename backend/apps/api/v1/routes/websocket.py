from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List, Dict
import asyncio
import json
from apps.core.services.yahoo_finance import YahooFinanceService

router = APIRouter(tags=["websocket"])

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.finance_service = YahooFinanceService()

    async def connect(self, websocket: WebSocket, symbol: str):
        await websocket.accept()
        if symbol not in self.active_connections:
            self.active_connections[symbol] = []
        self.active_connections[symbol].append(websocket)

    def disconnect(self, websocket: WebSocket, symbol: str):
        if symbol in self.active_connections:
            self.active_connections[symbol].remove(websocket)
            if not self.active_connections[symbol]:
                del self.active_connections[symbol]

    async def broadcast_price(self, symbol: str, data: dict):
        """Broadcast price updates to all subscribers"""
        if symbol in self.active_connections:
            disconnected = []
            for connection in self.active_connections[symbol]:
                try:
                    await connection.send_json(data)
                except:
                    disconnected.append(connection)
            
            # Remove disconnected clients
            for conn in disconnected:
                self.disconnect(conn, symbol)

    async def start_price_updates(self, symbol: str):
        """Start sending periodic price updates"""
        while symbol in self.active_connections and self.active_connections[symbol]:
            try:
                # Fetch latest price
                quote = await self.finance_service.get_stock_quote(symbol)
                if quote:
                    data = {
                        'type': 'price_update',
                        'symbol': symbol,
                        'price': quote.get('price'),
                        'change': quote.get('change'),
                        'change_percent': quote.get('change_percent'),
                        'timestamp': quote.get('timestamp')
                    }
                    await self.broadcast_price(symbol, data)
                
                # Wait 5 seconds before next update
                await asyncio.sleep(5)
            except Exception as e:
                print(f"Error in price updates for {symbol}: {e}")
                await asyncio.sleep(5)

manager = ConnectionManager()

@router.websocket("/ws/stocks/{symbol}")
async def websocket_stock_endpoint(websocket: WebSocket, symbol: str):
    """WebSocket endpoint for real-time stock price updates"""
    await manager.connect(websocket, symbol)
    
    # Start background task for price updates
    update_task = asyncio.create_task(manager.start_price_updates(symbol))
    
    try:
        while True:
            # Keep connection alive and receive client messages
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle client commands
            if message.get('type') == 'ping':
                await websocket.send_json({'type': 'pong'})
            elif message.get('type') == 'subscribe':
                # Already subscribed
                await websocket.send_json({
                    'type': 'subscribed',
                    'symbol': symbol
                })
    except WebSocketDisconnect:
        manager.disconnect(websocket, symbol)
        print(f"Client disconnected from {symbol}")
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket, symbol)
    finally:
        update_task.cancel()


@router.websocket("/ws/market")
async def websocket_market_endpoint(websocket: WebSocket):
    """WebSocket endpoint for market-wide updates"""
    await websocket.accept()
    
    try:
        # Send market summary every 10 seconds
        while True:
            market_data = {
                'type': 'market_update',
                'indices': {
                    'TSEC': {'name': '加權指數', 'change': 0.5},
                    'OTC': {'name': '櫃買指數', 'change': -0.2}
                },
                'timestamp': asyncio.get_event_loop().time()
            }
            await websocket.send_json(market_data)
            await asyncio.sleep(10)
    except WebSocketDisconnect:
        print("Market websocket disconnected")
    except Exception as e:
        print(f"Market websocket error: {e}")