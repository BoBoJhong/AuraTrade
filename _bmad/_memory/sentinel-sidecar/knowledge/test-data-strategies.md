# Test Data Strategies - 智慧測試資料生成策略

## 概述

超越基礎的 Schema 推斷，實現業務邏輯感知的測試資料生成，並支援從歷史資料學習。

---

## 測試資料生成層次

### Level 1: Schema-Based (基礎)
```yaml
來源: 資料庫 Schema / API 定義
方法: 型別推斷 + 隨機生成
限制: 不考慮業務邏輯約束
範例:
  - User.age → random.randint(1, 120)
  - User.email → f"user{random.randint(1,1000)}@example.com"
```

### Level 2: Constraint-Aware (進階)
```yaml
來源: Schema + 業務規則
方法: 約束驗證 + 邊界條件
優勢: 符合業務邏輯
範例:
  - User.age → random.randint(18, 65)  # 成人用戶
  - User.email → "{first_name}.{last_name}@company.com"  # 真實格式
  - Order.total → sum(item.price * item.quantity)  # 計算邏輯
```

### Level 3: Pattern-Learning (智慧)
```yaml
來源: 歷史測試資料 / 生產環境資料樣本
方法: 統計分析 + 模式識別
優勢: 高度擬真
範例:
  - User.age → 正態分佈 N(35, 10)  # 從歷史學習
  - Stock.price → 根據歷史波動範圍生成
  - Transaction.time → 符合交易高峰時段
```

---

## 測試資料生成器架構

### 檔案結構

```
_bmad/_memory/sentinel-sidecar/
  test-data-generators/
    base_generator.py           # 基礎生成器
    constraint_generator.py     # 約束感知生成器
    pattern_learner.py          # 模式學習生成器
    business_rules.yaml         # 業務規則定義
    historical_patterns.json    # 學習的模式
    strategies/
      user_strategy.py          # 用戶資料策略
      financial_strategy.py     # 財務資料策略
      stock_strategy.py         # 股票資料策略
```

---

## 實作：基礎生成器

### BaseGenerator

**檔案:** `base_generator.py`

```python
#!/usr/bin/env python3
"""
測試資料生成器基礎類
"""

import random
import string
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Type
from faker import Faker
from pydantic import BaseModel

fake = Faker(['zh_TW', 'en_US'])  # 支援中英文

class BaseGenerator:
    """基礎測試資料生成器"""
    
    @staticmethod
    def generate_string(min_length: int = 5, max_length: int = 20) -> str:
        """生成隨機字串"""
        length = random.randint(min_length, max_length)
        return ''.join(random.choices(string.ascii_letters, k=length))
    
    @staticmethod
    def generate_email() -> str:
        """生成真實格式的 Email"""
        return fake.email()
    
    @staticmethod
    def generate_phone() -> str:
        """生成台灣手機號碼"""
        return f"09{random.randint(10000000, 99999999)}"
    
    @staticmethod
    def generate_date(start_year: int = 2020, end_year: int = 2026) -> str:
        """生成日期"""
        start_date = datetime(start_year, 1, 1)
        end_date = datetime(end_year, 12, 31)
        delta = end_date - start_date
        random_days = random.randint(0, delta.days)
        return (start_date + timedelta(days=random_days)).strftime("%Y-%m-%d")
    
    @staticmethod
    def generate_from_pydantic(model: Type[BaseModel]) -> Dict[str, Any]:
        """從 Pydantic Model 自動生成資料"""
        data = {}
        for field_name, field in model.__fields__.items():
            field_type = field.annotation
            
            if field_type == str:
                data[field_name] = BaseGenerator.generate_string()
            elif field_type == int:
                data[field_name] = random.randint(1, 1000)
            elif field_type == float:
                data[field_name] = round(random.uniform(0, 1000), 2)
            elif field_type == bool:
                data[field_name] = random.choice([True, False])
            elif field_type == datetime:
                data[field_name] = fake.date_time_this_year()
            else:
                data[field_name] = None
        
        return data
```

---

## 實作：約束感知生成器

### ConstraintGenerator

**檔案:** `constraint_generator.py`

```python
#!/usr/bin/env python3
"""
約束感知測試資料生成器
"""

from typing import Any, Dict, Optional
from faker import Faker
import random

fake = Faker(['zh_TW'])

class ConstraintGenerator:
    """約束感知生成器 - 理解業務規則"""
    
    def __init__(self, rules_file: str = "business_rules.yaml"):
        self.rules = self._load_rules(rules_file)
    
    def _load_rules(self, file: str) -> Dict:
        """載入業務規則"""
        # 簡化版，實際應從 YAML 載入
        return {
            "User": {
                "age": {"min": 18, "max": 65, "distribution": "normal", "mean": 35, "std": 10},
                "email": {"pattern": "{first_name}.{last_name}@{domain}"},
                "username": {"min_length": 5, "max_length": 20, "pattern": "[a-z0-9_]+"},
                "password": {"min_length": 8, "require_uppercase": True, "require_digit": True}
            },
            "Stock": {
                "code": {"pattern": "[0-9]{4}", "range": [1000, 9999]},
                "price": {"min": 1.0, "max": 1000.0, "precision": 2},
                "volume": {"min": 1000, "max": 100000000}
            },
            "Order": {
                "quantity": {"min": 1, "max": 1000},
                "total": {"depends_on": ["price", "quantity"], "formula": "price * quantity"}
            }
        }
    
    def generate_user(self) -> Dict[str, Any]:
        """生成符合業務規則的用戶資料"""
        rules = self.rules["User"]
        
        # 年齡 - 正態分佈
        age = int(random.gauss(
            rules["age"]["mean"], 
            rules["age"]["std"]
        ))
        age = max(rules["age"]["min"], min(rules["age"]["max"], age))
        
        # Email - 真實格式
        first_name = fake.first_name().lower()
        last_name = fake.last_name().lower()
        domain = random.choice(["gmail.com", "yahoo.com", "company.com"])
        email = f"{first_name}.{last_name}@{domain}"
        
        # 密碼 - 符合強度要求
        password = self._generate_strong_password(
            rules["password"]["min_length"]
        )
        
        # 用戶名 - 符合格式
        username = f"{first_name}_{random.randint(100, 999)}"
        
        return {
            "username": username,
            "email": email,
            "password": password,
            "age": age,
            "full_name": f"{fake.last_name()} {fake.first_name()}",
            "phone": f"09{random.randint(10000000, 99999999)}",
            "is_active": True
        }
    
    def generate_stock(self) -> Dict[str, Any]:
        """生成股票資料"""
        rules = self.rules["Stock"]
        
        code = str(random.randint(
            rules["code"]["range"][0],
            rules["code"]["range"][1]
        ))
        
        price = round(random.uniform(
            rules["price"]["min"],
            rules["price"]["max"]
        ), rules["price"]["precision"])
        
        volume = random.randint(
            rules["volume"]["min"],
            rules["volume"]["max"]
        )
        
        return {
            "code": code,
            "name": f"{fake.company()} 股份有限公司",
            "price": price,
            "volume": volume,
            "change": round(random.uniform(-10, 10), 2)
        }
    
    def generate_order(self, price: float, quantity: int) -> Dict[str, Any]:
        """生成訂單 - 包含計算邏輯"""
        rules = self.rules["Order"]
        
        # 計算總額
        total = price * quantity
        fee = round(total * 0.001425, 2)  # 手續費 0.1425%
        tax = round(total * 0.003, 2)     # 證交稅 0.3%
        
        return {
            "order_id": f"ORD{random.randint(100000, 999999)}",
            "quantity": quantity,
            "price": price,
            "subtotal": total,
            "fee": fee,
            "tax": tax,
            "total": round(total + fee + tax, 2),
            "status": random.choice(["pending", "completed", "cancelled"])
        }
    
    def _generate_strong_password(self, length: int) -> str:
        """生成強密碼"""
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        password = [
            random.choice(string.ascii_uppercase),
            random.choice(string.ascii_lowercase),
            random.choice(string.digits),
            random.choice("!@#$%^&*")
        ]
        password += random.choices(chars, k=length - 4)
        random.shuffle(password)
        return ''.join(password)
```

---

## 實作：模式學習生成器

### PatternLearner

**檔案:** `pattern_learner.py`

```python
#!/usr/bin/env python3
"""
模式學習生成器 - 從歷史資料學習
"""

import json
import numpy as np
from typing import Dict, List, Any
from collections import Counter
from datetime import datetime

class PatternLearner:
    """從歷史資料學習生成模式"""
    
    def __init__(self, patterns_file: str = "historical_patterns.json"):
        self.patterns = self._load_patterns(patterns_file)
    
    def _load_patterns(self, file: str) -> Dict:
        """載入學習的模式"""
        try:
            with open(file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return self._initialize_patterns()
    
    def _initialize_patterns(self) -> Dict:
        """初始化模式"""
        return {
            "User": {
                "age_distribution": {"mean": 35, "std": 10, "min": 18, "max": 65},
                "email_domains": {"gmail.com": 0.4, "yahoo.com": 0.3, "hotmail.com": 0.2, "others": 0.1},
                "signup_hour": {hour: 0.04 for hour in range(24)}  # 均勻分佈
            },
            "Stock": {
                "price_ranges": {
                    "low": {"min": 1, "max": 50, "probability": 0.3},
                    "mid": {"min": 50, "max": 200, "probability": 0.5},
                    "high": {"min": 200, "max": 1000, "probability": 0.2}
                },
                "volume_distribution": {"mean": 10000000, "std": 5000000}
            },
            "Transaction": {
                "peak_hours": [9, 10, 11, 13, 14],  # 交易高峰時段
                "common_amounts": [1000, 5000, 10000, 50000, 100000]
            }
        }
    
    def learn_from_data(self, entity: str, historical_data: List[Dict]):
        """從歷史資料學習模式"""
        if entity == "User":
            self._learn_user_patterns(historical_data)
        elif entity == "Stock":
            self._learn_stock_patterns(historical_data)
        
        # 保存學習結果
        self._save_patterns()
    
    def _learn_user_patterns(self, data: List[Dict]):
        """學習用戶資料模式"""
        ages = [u["age"] for u in data if "age" in u]
        emails = [u["email"] for u in data if "email" in u]
        
        # 年齡分佈
        self.patterns["User"]["age_distribution"] = {
            "mean": np.mean(ages),
            "std": np.std(ages),
            "min": min(ages),
            "max": max(ages)
        }
        
        # Email 域名分佈
        domains = [email.split('@')[1] for email in emails]
        domain_counts = Counter(domains)
        total = len(domains)
        self.patterns["User"]["email_domains"] = {
            domain: count / total 
            for domain, count in domain_counts.most_common(10)
        }
    
    def _learn_stock_patterns(self, data: List[Dict]):
        """學習股票資料模式"""
        prices = [s["price"] for s in data if "price" in s]
        volumes = [s["volume"] for s in data if "volume" in s]
        
        # 價格範圍分佈
        low_count = sum(1 for p in prices if p < 50)
        mid_count = sum(1 for p in prices if 50 <= p < 200)
        high_count = sum(1 for p in prices if p >= 200)
        total = len(prices)
        
        self.patterns["Stock"]["price_ranges"] = {
            "low": {"min": 1, "max": 50, "probability": low_count / total},
            "mid": {"min": 50, "max": 200, "probability": mid_count / total},
            "high": {"min": 200, "max": 1000, "probability": high_count / total}
        }
        
        # 成交量分佈
        self.patterns["Stock"]["volume_distribution"] = {
            "mean": np.mean(volumes),
            "std": np.std(volumes)
        }
    
    def generate_user(self) -> Dict[str, Any]:
        """基於學習模式生成用戶"""
        patterns = self.patterns["User"]
        
        # 年齡 - 從學習的分佈生成
        age = int(np.random.normal(
            patterns["age_distribution"]["mean"],
            patterns["age_distribution"]["std"]
        ))
        age = max(patterns["age_distribution"]["min"], 
                 min(patterns["age_distribution"]["max"], age))
        
        # Email 域名 - 根據學習的機率選擇
        domains = list(patterns["email_domains"].keys())
        probabilities = list(patterns["email_domains"].values())
        domain = np.random.choice(domains, p=probabilities)
        
        fake_name = fake.name()
        email = f"{fake_name.lower().replace(' ', '.')}@{domain}"
        
        # 註冊時間 - 根據學習的高峰時段
        signup_hours = patterns["signup_hour"]
        hour = np.random.choice(
            list(signup_hours.keys()),
            p=list(signup_hours.values())
        )
        
        return {
            "email": email,
            "age": age,
            "signup_hour": hour,
            "full_name": fake_name
        }
    
    def generate_stock(self) -> Dict[str, Any]:
        """基於學習模式生成股票"""
        patterns = self.patterns["Stock"]
        
        # 根據機率選擇價格範圍
        ranges = patterns["price_ranges"]
        range_name = np.random.choice(
            list(ranges.keys()),
            p=[r["probability"] for r in ranges.values()]
        )
        
        price_range = ranges[range_name]
        price = round(np.random.uniform(
            price_range["min"],
            price_range["max"]
        ), 2)
        
        # 成交量 - 從學習的分佈生成
        volume_mean = patterns["volume_distribution"]["mean"]
        volume_std = patterns["volume_distribution"]["std"]
        volume = int(max(1000, np.random.normal(volume_mean, volume_std)))
        
        return {
            "code": str(np.random.randint(1000, 9999)),
            "price": price,
            "volume": volume,
            "range_category": range_name
        }
    
    def _save_patterns(self):
        """保存學習的模式"""
        with open("historical_patterns.json", 'w', encoding='utf-8') as f:
            json.dump(self.patterns, f, indent=2, ensure_ascii=False)
```

---

## 業務規則定義

### business_rules.yaml

```yaml
# 業務規則定義檔案

User:
  age:
    min: 18
    max: 65
    distribution: normal
    mean: 35
    std: 10
    note: "用戶年齡需為成年人，且符合主要客群"
  
  email:
    pattern: "{first_name}.{last_name}@{domain}"
    domains:
      - gmail.com
      - yahoo.com
      - company.com
    validation: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
  
  password:
    min_length: 8
    max_length: 32
    require_uppercase: true
    require_lowercase: true
    require_digit: true
    require_special: true
    note: "密碼需符合強度要求"
  
  phone:
    pattern: "09[0-9]{8}"
    validation: "^09\\d{8}$"
    note: "台灣手機號碼格式"

Stock:
  code:
    pattern: "[0-9]{4}"
    range: [1000, 9999]
    note: "台股代號為 4 位數字"
  
  price:
    min: 1.0
    max: 1000.0
    precision: 2
    note: "股價保留兩位小數"
  
  volume:
    min: 1000
    max: 100000000
    note: "成交量合理範圍"

Order:
  quantity:
    min: 1
    max: 10000
    note: "單筆訂單數量限制"
  
  calculations:
    subtotal: "price * quantity"
    fee: "subtotal * 0.001425"
    tax: "subtotal * 0.003"
    total: "subtotal + fee + tax"

Transaction:
  amount:
    min: 1000
    max: 10000000
    common_values: [1000, 5000, 10000, 50000, 100000]
    note: "常見交易金額"
  
  timestamp:
    peak_hours: [9, 10, 11, 13, 14]
    off_peak_hours: [0, 1, 2, 3, 4, 5, 6, 7, 8, 12, 15, 16, 17, 18, 19, 20, 21, 22, 23]
    note: "交易時間分佈"
```

---

## 使用範例

### 1. 基礎生成

```python
from base_generator import BaseGenerator

# 自動從 Pydantic Model 生成
from pydantic import BaseModel

class User(BaseModel):
    username: str
    email: str
    age: int

test_user = BaseGenerator.generate_from_pydantic(User)
print(test_user)
# {'username': 'jkxlMnop', 'email': 'john@example.com', 'age': 342}
```

### 2. 約束感知生成

```python
from constraint_generator import ConstraintGenerator

gen = ConstraintGenerator()

# 生成符合業務規則的用戶
user = gen.generate_user()
print(user)
# {
#   'username': 'john_456',
#   'email': 'john.doe@gmail.com',
#   'age': 38,
#   'password': 'SecureP@ss123',
#   'phone': '0912345678'
# }

# 生成股票資料
stock = gen.generate_stock()
print(stock)
# {
#   'code': '2330',
#   'name': '台積電股份有限公司',
#   'price': 582.50,
#   'volume': 35000000
# }
```

### 3. 模式學習生成

```python
from pattern_learner import PatternLearner

learner = PatternLearner()

# 從歷史資料學習
historical_users = [
    {"age": 25, "email": "user1@gmail.com"},
    {"age": 30, "email": "user2@yahoo.com"},
    # ... 更多資料
]
learner.learn_from_data("User", historical_users)

# 生成基於學習模式的資料
user = learner.generate_user()
print(user)
# 生成的資料符合歷史資料的分佈模式
```

---

## 整合到 Sentinel

### 自動選擇生成策略

```python
def select_generator(entity: str, has_historical_data: bool) -> Any:
    """智慧選擇生成器"""
    
    if has_historical_data:
        # Level 3: 模式學習生成器
        return PatternLearner()
    elif entity in BUSINESS_RULES:
        # Level 2: 約束感知生成器
        return ConstraintGenerator()
    else:
        # Level 1: 基礎生成器
        return BaseGenerator()

# Sentinel 自動執行
generator = select_generator("User", has_historical_data=True)
test_data = generator.generate_user()
```

---

## 配置文件

### `.sentinel-testdata.yaml`

```yaml
# 測試資料生成配置

strategy: "auto"  # auto / constraint / pattern

generators:
  User:
    strategy: "pattern"  # 使用模式學習
    historical_file: "tests/fixtures/historical_users.json"
    sample_size: 100
  
  Stock:
    strategy: "constraint"  # 使用約束生成
    rules_file: "business_rules.yaml"
  
  Order:
    strategy: "constraint"
    depends_on: ["User", "Stock"]

learning:
  enabled: true
  sample_size: 1000
  update_interval: "weekly"

output:
  format: "json"
  directory: "tests/fixtures/"
  naming: "{entity}_{timestamp}.json"
```

---

## 總結

✅ **三層策略** - Schema → Constraint → Pattern Learning  
✅ **業務感知** - 理解業務邏輯約束  
✅ **自動學習** - 從歷史資料學習模式  
✅ **高度擬真** - 生成符合實際場景的資料  
✅ **靈活配置** - 可自訂規則與策略

**Sentinel 現在能生成高品質、符合業務邏輯的測試資料！** 🎯📊
