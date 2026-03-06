"""
Locust Performance Testing Suite
AuraTrade API Performance & Load Testing

執行方式:
  本地執行:
    locust -f tests/performance/locustfile.py --host=http://localhost:8000
  
  Headless 模式 (CI):
    locust -f tests/performance/locustfile.py --host=http://localhost:8000 \
           --users 100 --spawn-rate 10 --run-time 1m --headless
  
  產出報告:
    locust -f tests/performance/locustfile.py --host=http://localhost:8000 \
           --users 100 --spawn-rate 10 --run-time 1m --headless \
           --html tests/reports/performance/load-test-report.html

測試場景:
  1. AuthLoadTest - 認證流程壓測
  2. StockAPILoadTest - 股票查詢壓測
  3. PortfolioLoadTest - 投資組合壓測
  4. MixedWorkload - 混合負載測試
"""

from locust import HttpUser, task, between, events
import random
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


# === 測試數據 ===

TEST_USERS = [
    {"email": f"loadtest{i}@example.com", "password": "LoadTest123", "username": f"loaduser{i}"}
    for i in range(1, 51)  # 50 個測試用戶
]

TEST_STOCKS = [
    "2330.TW",  # 台積電
    "2317.TW",  # 鴻海
    "2454.TW",  # 聯發科
    "0050.TW",  # 元大台灣50
    "AAPL",     # Apple
    "TSLA",     # Tesla
    "MSFT",     # Microsoft
    "NVDA",     # NVIDIA
]


# === 基礎用戶類 ===

class AuraTradeUser(HttpUser):
    """基礎用戶類 - 提供共用方法"""
    
    wait_time = between(1, 3)  # 用戶操作間隔 1-3 秒
    
    def on_start(self):
        """用戶開始時執行 - 登入獲取 Token"""
        self.token = None
        self.user_data = random.choice(TEST_USERS)
        self.login()
    
    def login(self):
        """用戶登入"""
        response = self.client.post(
            "/api/v1/auth/login",
            json={
                "email": self.user_data["email"],
                "password": self.user_data["password"]
            },
            catch_response=True
        )
        
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
            response.success()
        elif response.status_code == 401:
            # 用戶不存在，嘗試註冊
            self.register()
        else:
            response.failure(f"Login failed: {response.status_code}")
    
    def register(self):
        """用戶註冊"""
        response = self.client.post(
            "/api/v1/auth/register",
            json={
                "email": self.user_data["email"],
                "password": self.user_data["password"],
                "username": self.user_data["username"]
            },
            catch_response=True
        )
        
        if response.status_code == 200 or response.status_code == 201:
            data = response.json()
            self.token = data.get("access_token")
            response.success()
        else:
            response.failure(f"Register failed: {response.status_code}")
    
    def get_headers(self):
        """獲取認證 Header"""
        if self.token:
            return {"Authorization": f"Bearer {self.token}"}
        return {}


# === 場景 1: 認證流程壓測 ===

class AuthLoadTest(AuraTradeUser):
    """認證流程負載測試"""
    
    weight = 2  # 權重 (相對於其他場景)
    
    @task(3)
    def login_flow(self):
        """登入流程測試"""
        user = random.choice(TEST_USERS)
        self.client.post(
            "/api/v1/auth/login",
            json={"email": user["email"], "password": user["password"]},
            name="POST /api/v1/auth/login"
        )
    
    @task(1)
    def register_flow(self):
        """註冊流程測試"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        self.client.post(
            "/api/v1/auth/register",
            json={
                "email": f"perf{timestamp}@test.com",
                "password": "PerfTest123",
                "username": f"perfuser{timestamp}"
            },
            name="POST /api/v1/auth/register"
        )
    
    @task(2)
    def get_current_user(self):
        """獲取當前用戶信息"""
        self.client.get(
            "/api/v1/auth/me",
            headers=self.get_headers(),
            name="GET /api/v1/auth/me"
        )


# === 場景 2: 股票 API 壓測 ===

class StockAPILoadTest(AuraTradeUser):
    """股票 API 負載測試"""
    
    weight = 5  # 最高權重 (核心功能)
    
    @task(5)
    def search_stock(self):
        """搜尋股票"""
        keywords = ["台積電", "鴻海", "Apple", "Tesla", "2330"]
        keyword = random.choice(keywords)
        self.client.get(
            f"/api/v1/stocks/search?keyword={keyword}",
            headers=self.get_headers(),
            name="GET /api/v1/stocks/search"
        )
    
    @task(10)
    def get_stock_detail(self):
        """獲取股票詳情"""
        symbol = random.choice(TEST_STOCKS)
        self.client.get(
            f"/api/v1/stocks/{symbol}",
            headers=self.get_headers(),
            name="GET /api/v1/stocks/:symbol"
        )
    
    @task(3)
    def get_stock_history(self):
        """獲取歷史數據"""
        symbol = random.choice(TEST_STOCKS)
        period = random.choice(["1d", "5d", "1mo", "3mo"])
        self.client.get(
            f"/api/v1/stocks/{symbol}/history?period={period}",
            headers=self.get_headers(),
            name="GET /api/v1/stocks/:symbol/history"
        )
    
    @task(2)
    def get_technical_indicators(self):
        """獲取技術指標"""
        symbol = random.choice(TEST_STOCKS)
        self.client.get(
            f"/api/v1/stocks/{symbol}/indicators",
            headers=self.get_headers(),
            name="GET /api/v1/stocks/:symbol/indicators"
        )
    
    @task(1)
    def get_stock_news(self):
        """獲取股票新聞"""
        symbol = random.choice(TEST_STOCKS)
        self.client.get(
            f"/api/v1/stocks/{symbol}/news",
            headers=self.get_headers(),
            name="GET /api/v1/stocks/:symbol/news"
        )


# === 場景 3: 投資組合壓測 ===

class PortfolioLoadTest(AuraTradeUser):
    """投資組合負載測試"""
    
    weight = 3
    
    @task(5)
    def get_portfolio(self):
        """獲取投資組合"""
        self.client.get(
            "/api/v1/portfolio",
            headers=self.get_headers(),
            name="GET /api/v1/portfolio"
        )
    
    @task(2)
    def add_position(self):
        """新增持倉"""
        symbol = random.choice(TEST_STOCKS)
        self.client.post(
            "/api/v1/portfolio/positions",
            headers=self.get_headers(),
            json={
                "symbol": symbol,
                "quantity": random.randint(10, 100),
                "average_cost": random.uniform(50, 500)
            },
            name="POST /api/v1/portfolio/positions"
        )
    
    @task(3)
    def get_performance(self):
        """獲取績效分析"""
        self.client.get(
            "/api/v1/portfolio/performance",
            headers=self.get_headers(),
            name="GET /api/v1/portfolio/performance"
        )
    
    @task(1)
    def add_transaction(self):
        """新增交易記錄"""
        symbol = random.choice(TEST_STOCKS)
        self.client.post(
            "/api/v1/portfolio/transactions",
            headers=self.get_headers(),
            json={
                "symbol": symbol,
                "transaction_type": random.choice(["buy", "sell"]),
                "quantity": random.randint(10, 50),
                "price": random.uniform(50, 500),
                "transaction_date": datetime.now().isoformat()
            },
            name="POST /api/v1/portfolio/transactions"
        )


# === 場景 4: 混合負載測試 ===

class MixedWorkload(AuraTradeUser):
    """模擬真實用戶行為的混合負載"""
    
    weight = 10  # 最常見的用戶行為
    
    @task(10)
    def typical_user_flow(self):
        """典型用戶流程：登入 → 查股票 → 看新聞 → 查看組合"""
        
        # 1. 搜尋股票
        symbol = random.choice(TEST_STOCKS)
        self.client.get(
            f"/api/v1/stocks/search?keyword={symbol[:4]}",
            headers=self.get_headers(),
            name="Flow: Search Stock"
        )
        
        # 2. 查看股票詳情
        self.client.get(
            f"/api/v1/stocks/{symbol}",
            headers=self.get_headers(),
            name="Flow: Get Stock Detail"
        )
        
        # 3. 查看技術指標
        self.client.get(
            f"/api/v1/stocks/{symbol}/indicators",
            headers=self.get_headers(),
            name="Flow: Get Indicators"
        )
        
        # 4. 查看投資組合
        self.client.get(
            "/api/v1/portfolio",
            headers=self.get_headers(),
            name="Flow: Get Portfolio"
        )


# === 自定義事件監聽器 (報告增強) ===

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """測試開始時執行"""
    logger.info("🚀 Performance Test Started")
    logger.info(f"Target Host: {environment.host}")
    logger.info(f"Test Users: {len(TEST_USERS)}")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """測試結束時執行"""
    logger.info("✅ Performance Test Completed")
    
    # 產出簡易摘要
    stats = environment.stats
    logger.info(f"Total Requests: {stats.total.num_requests}")
    logger.info(f"Total Failures: {stats.total.num_failures}")
    logger.info(f"Average Response Time: {stats.total.avg_response_time:.2f}ms")
    logger.info(f"Requests/sec: {stats.total.total_rps:.2f}")


# === 自定義用戶場景 (可選) ===

class StressTest(AuraTradeUser):
    """壓力測試 - 高並發場景"""
    
    weight = 0  # 預設不啟用，需手動指定
    wait_time = between(0.1, 0.5)  # 極短等待時間
    
    @task
    def stress_api(self):
        """高頻率 API 請求"""
        symbol = random.choice(TEST_STOCKS)
        self.client.get(
            f"/api/v1/stocks/{symbol}",
            headers=self.get_headers(),
            name="Stress: Get Stock"
        )
