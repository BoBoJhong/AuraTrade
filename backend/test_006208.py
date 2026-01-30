import asyncio
from apps.core.services.stock_list_manager import stock_list_manager

async def test():
    # 強制刷新
    print(" 強制更新股票清單...")
    stocks = await stock_list_manager.get_all_stocks(force_refresh=True)
    
    # 檢查 006208
    found = [s for s in stocks if '006208' in s['symbol'] or '006208' in s['name']]
    print(f"\n 搜尋包含 '006208' 的股票:")
    if found:
        for s in found:
            print(f"  {s['symbol']:15} {s['name']:20} ({s['market']})")
    else:
        print("   未找到")
    
    # 測試搜尋
    print("\n 測試搜尋 API:")
    results = await stock_list_manager.search_stocks("006208")
    print(f"結果: {len(results)} 筆")
    for r in results[:3]:
        print(f"  {r['symbol']:15} {r['name']:20}")

asyncio.run(test())
