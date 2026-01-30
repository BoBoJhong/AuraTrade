import requests

# 測試股票清單管理器
print(" 測試 1: 載入股票清單...")
from apps.core.services.stock_list_manager import stock_list_manager
import asyncio

async def test():
    stocks = await stock_list_manager.get_all_stocks(force_refresh=True)
    print(f" 總共: {len(stocks)} 檔")
    
    # 分類統計
    twse = [s for s in stocks if s['market'] == 'TWSE']
    tpex = [s for s in stocks if s['market'] == 'TPEX']
    us = [s for s in stocks if s['market'] == 'US']
    
    print(f" 台灣上市 (TWSE): {len(twse)} 檔")
    print(f" 台灣上櫃 (TPEX): {len(tpex)} 檔")
    print(f" 美股: {len(us)} 檔")
    
    # 測試搜尋
    print("\n 測試 2: 搜尋功能...")
    results = await stock_list_manager.search_stocks("2330")
    print(f"搜尋 '2330': {len(results)} 筆")
    for r in results[:3]:
        print(f"  - {r['symbol']}: {r['name']}")
    
    results = await stock_list_manager.search_stocks("台積電")
    print(f"搜尋 '台積電': {len(results)} 筆")
    for r in results[:3]:
        print(f"  - {r['symbol']}: {r['name']}")

asyncio.run(test())
