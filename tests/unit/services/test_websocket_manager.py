import pytest

from apps.api.v1.routes.websocket import ConnectionManager


class FakeWebSocket:
    def __init__(self, should_fail_send: bool = False):
        self.accepted = False
        self.should_fail_send = should_fail_send
        self.messages = []

    async def accept(self):
        self.accepted = True

    async def send_json(self, data):
        if self.should_fail_send:
            raise RuntimeError("socket disconnected")
        self.messages.append(data)


@pytest.mark.asyncio
async def test_connection_manager_connect_and_disconnect():
    manager = ConnectionManager()
    ws = FakeWebSocket()

    await manager.connect(ws, "2330.TW")
    assert ws.accepted is True
    assert "2330.TW" in manager.active_connections
    assert ws in manager.active_connections["2330.TW"]

    manager.disconnect(ws, "2330.TW")
    assert "2330.TW" not in manager.active_connections


@pytest.mark.asyncio
async def test_connection_manager_broadcast_removes_disconnected_clients():
    manager = ConnectionManager()
    healthy_ws = FakeWebSocket()
    broken_ws = FakeWebSocket(should_fail_send=True)

    await manager.connect(healthy_ws, "AAPL")
    await manager.connect(broken_ws, "AAPL")

    payload = {"type": "price_update", "symbol": "AAPL", "price": 100}
    await manager.broadcast_price("AAPL", payload)

    assert healthy_ws.messages == [payload]
    assert broken_ws not in manager.active_connections.get("AAPL", [])