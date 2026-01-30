import asyncio
from apps.core.services.stock_list_manager import stock_list_manager

async def test_search():
    print(" 測試搜尋功能\n")
    
    test_cases = [
        "2330",      # 台積電
        "2454",      # 聯發科  
        "006208",    # 富邦台50
        "日月光",    # 名稱搜尋
        "國泰金",    # 名稱搜尋
        "聯電",      # 名稱搜尋
    ]
    
    for query in test_cases:
        results = await stock_list_manager.search_stocks(query, limit=3)
        print(f"【{query}】  找到 {len(results)} 筆")
        for r in results[:3]:
            print(f"  {r['symbol']:12} {r['name']:20} ({r['market']})")
        print()

asyncio.run(test_search())
