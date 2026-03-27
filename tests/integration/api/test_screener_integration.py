"""
Integration tests for screener-related APIs.

These tests monkeypatch external dependencies to keep the suite deterministic.
"""

import pytest


@pytest.mark.asyncio
async def test_screener_returns_filtered_stocks(client, monkeypatch):
    async def mock_get_all_stocks():
        return [
            {"symbol": "2330.TW", "market": "TWSE"},
            {"symbol": "AAPL", "market": "US"},
        ]

    async def mock_get_stock_info(symbol: str):
        return {
            "symbol": symbol,
            "name": "Mock Stock",
            "price": 100.0,
            "change": 1.0,
            "change_percent": 1.0,
            "volume": 100000,
            "market_cap": 10000000000,
            "pe_ratio": 15.0,
            "dividend_yield": 2.0,
        }

    monkeypatch.setattr(
        "apps.api.v1.routes.screener.stock_list_manager.get_all_stocks",
        mock_get_all_stocks,
    )
    monkeypatch.setattr(
        "apps.api.v1.routes.screener.YahooFinanceService.get_stock_info",
        mock_get_stock_info,
    )

    response = await client.get("/api/v1/screener", params={"limit": 5})

    assert response.status_code == 200
    payload = response.json()
    assert "total" in payload
    assert "stocks" in payload
    assert payload["total"] >= 1


@pytest.mark.asyncio
async def test_trending_returns_ranked_stocks(client, monkeypatch):
    async def mock_get_stock_info(symbol: str):
        return {
            "symbol": symbol,
            "name": f"Mock {symbol}",
            "price": 99.0,
            "change": 0.5,
            "change_percent": 0.5,
            "volume": 1000 if symbol == "AAPL" else 500,
            "market_cap": 5000000000,
        }

    monkeypatch.setattr(
        "apps.api.v1.routes.screener.YahooFinanceService.get_stock_info",
        mock_get_stock_info,
    )

    response = await client.get("/api/v1/stocks/trending", params={"limit": 3})

    assert response.status_code == 200
    payload = response.json()
    assert "stocks" in payload
    assert len(payload["stocks"]) <= 3


@pytest.mark.asyncio
async def test_ai_picks_returns_expected_shape(client, monkeypatch):
    async def mock_generate_recommendations(db, market=None, limit=10, min_score=60.0, max_candidates=20):
        return [
            {
                "symbol": "2330.TW",
                "stock_name": "台積電",
                "price": 650.0,
                "change_percent": 1.2,
                "ai_score": 82.5,
                "recommendation": "買入",
                "reasons": ["RSI 接近超賣", "多頭排列"],
                "market": "TW",
            }
        ]

    async def mock_get_stats(db, days=30):
        return {
            "total_recommendations": 1,
            "average_score": 82.5,
            "buy_count": 1,
            "hold_count": 0,
            "sell_count": 0,
            "period_days": days,
        }

    monkeypatch.setattr(
        "apps.api.v1.routes.screener.EnhancedAIRecommendationEngine.generate_recommendations",
        mock_generate_recommendations,
    )
    monkeypatch.setattr(
        "apps.api.v1.routes.screener.EnhancedAIRecommendationEngine.get_recommendation_statistics",
        mock_get_stats,
    )

    response = await client.get(
        "/api/v1/stocks/ai-picks",
        params={"limit": 5, "max_candidates": 5, "min_score": 50},
    )

    assert response.status_code == 200
    payload = response.json()
    assert "stocks" in payload
    assert "statistics" in payload
    assert payload["total"] == 1