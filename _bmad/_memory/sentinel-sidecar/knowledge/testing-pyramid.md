# 測試金字塔理論 (Testing Pyramid)

**核心概念：** 用適當的測試層級，以最低成本達成最高品質

---

## 金字塔結構

```
           /\
          /  \        E2E Tests (10%)
         /    \       - 最慢
        /------\      - 最貴
       /        \     - 最脆弱
      /   整合測試 \    Integration Tests (30%)
     /------------\   - 中速
    /              \  - 中等成本
   /    單元測試     \ Unit Tests (60%)
  /------------------\ - 最快
 /                    \ - 最便宜
                       - 最穩定
```

### 層級特性對照

| 層級 | 比例 | 執行速度 | 維護成本 | 穩定性 | 除錯難度 | 信心指數 |
|------|------|---------|---------|--------|---------|---------|
| 單元測試 | 60% | ⚡️ 極快 (ms) | 💰 低 | ✅ 高 | 🟢 易 | 🟡 中 |
| 整合測試 | 30% | ⏱️ 中速 (s) | 💰💰 中 | 🟡 中 | 🟡 中 | 🟢 高 |
| E2E 測試 | 10% | 🐌 慢 (10s+) | 💰💰💰 高 | ❌ 低 | 🔴 難 | 🟢 極高 |

---

## 層級一: 單元測試 (Unit Tests)

### 定義
測試單一函數、模組、或元件的**邏輯正確性**，完全隔離外部依賴。

### 何時使用
```yaml
適合場景:
  - 純函數運算 (輸入 → 輸出)
  - 業務邏輯驗證
  - 邊界條件測試
  - 錯誤處理驗證

不適合場景:
  - 需要真實資料庫
  - 需要真實網路請求
  - 需要瀏覽器環境
```

### 最佳實踐

#### ✅ Good: 快速且聚焦
```typescript
// src/utils/priceCalculator.ts
export function calculateDiscount(price: number, discountRate: number): number {
  if (price < 0) throw new Error('Price cannot be negative');
  if (discountRate < 0 || discountRate > 1) throw new Error('Invalid discount rate');
  return price * (1 - discountRate);
}

// src/utils/__tests__/priceCalculator.test.ts
describe('calculateDiscount', () => {
  it('應計算正確折扣', () => {
    expect(calculateDiscount(1000, 0.2)).toBe(800);
  });

  it('應拒絕負數價格', () => {
    expect(() => calculateDiscount(-100, 0.2)).toThrow('Price cannot be negative');
  });

  it('應拒絕無效折扣率', () => {
    expect(() => calculateDiscount(1000, 1.5)).toThrow('Invalid discount rate');
  });

  it('應處理零折扣', () => {
    expect(calculateDiscount(1000, 0)).toBe(1000);
  });

  it('應處理全額折扣', () => {
    expect(calculateDiscount(1000, 1)).toBe(0);
  });
});
```
**特點：** 5 個測試，執行時間 < 10ms，無外部依賴

#### ❌ Bad: 偽裝成單元測試的整合測試
```typescript
// ❌ 這不是單元測試！
it('should save user to database', async () => {
  const user = await db.users.create({ name: 'Test' }); // 真實資料庫
  expect(user.id).toBeDefined();
});
```

---

## 層級二: 整合測試 (Integration Tests)

### 定義
測試多個模組協作或與外部系統（資料庫/API）的**互動正確性**。

### 何時使用
```yaml
適合場景:
  - API endpoint 測試
  - 資料庫 CRUD 操作
  - 服務間協作
  - 訊息佇列消費

不適合場景:
  - 複雜的 UI 互動
  - 跨多頁面流程
  - 瀏覽器相容性測試
```

### 最佳實踐

#### ✅ Good: 測試真實協作
```typescript
// tests/integration/api.test.ts
import request from 'supertest';
import { app } from '../src/app';
import { testDb } from './helpers/testDatabase';

describe('POST /api/orders', () => {
  beforeEach(async () => {
    await testDb.seed(); // 準備測試資料
  });

  afterEach(async () => {
    await testDb.cleanup();
  });

  it('應成功建立訂單', async () => {
    const response = await request(app)
      .post('/api/orders')
      .send({
        userId: 1,
        productId: 100,
        quantity: 2
      })
      .expect(201);

    expect(response.body).toMatchObject({
      orderId: expect.any(Number),
      status: 'pending',
      totalAmount: 2000
    });

    // 驗證資料庫變更
    const order = await testDb.orders.findById(response.body.orderId);
    expect(order.userId).toBe(1);
  });

  it('應拒絕庫存不足訂單', async () => {
    await request(app)
      .post('/api/orders')
      .send({
        userId: 1,
        productId: 999, // 無庫存商品
        quantity: 1
      })
      .expect(400)
      .expect({ error: 'Out of stock' });
  });
});
```
**特點：** 真實資料庫交易，執行時間 ~2-5s

---

## 層級三: E2E 測試 (End-to-End Tests)

### 定義
模擬真實使用者操作，測試完整業務流程的**端到端正確性**。

### 何時使用
```yaml
適合場景:
  - 關鍵業務流程 (登入、購物、支付)
  - 跨頁面互動
  - 真實瀏覽器行為
  - 跨平台驗證

不適合場景:
  - 邊界條件測試 (太慢)
  - 單一函數驗證 (大材小用)
  - 快速回歸測試 (等待時間長)
```

### 最佳實踐

#### ✅ Good: 關鍵流程測試
```typescript
// e2e/checkout.spec.ts
import { test, expect } from '@playwright/test';

test('使用者應能完成完整購物流程', async ({ page }) => {
  // 1. 登入
  await page.goto('https://example.com/login');
  await page.fill('[data-testid="email"]', 'test@example.com');
  await page.fill('[data-testid="password"]', 'password123');
  await page.click('[data-testid="login-button"]');
  await expect(page).toHaveURL(/dashboard/);

  // 2. 搜尋商品
  await page.fill('[data-testid="search-input"]', 'iPhone 15');
  await page.press('[data-testid="search-input"]', 'Enter');
  await page.waitForSelector('[data-testid="product-list"]');

  // 3. 加入購物車
  await page.click('[data-testid="product-item"]:first-child >> text=加入購物車');
  await expect(page.locator('[data-testid="cart-count"]')).toHaveText('1');

  // 4. 結帳
  await page.click('[data-testid="cart-icon"]');
  await page.click('[data-testid="checkout-button"]');
  
  // 5. 填寫配送資訊
  await page.fill('[data-testid="address"]', '台北市信義區信義路五段7號');
  await page.click('[data-testid="confirm-order"]');

  // 6. 驗證成功
  await expect(page.locator('[data-testid="order-success"]')).toBeVisible();
  await expect(page.locator('[data-testid="order-number"]')).toContainText(/ORD-\d+/);
});
```
**特點：** 完整流程，執行時間 ~15-30s，高信心度

#### ❌ Bad: 過度使用 E2E
```typescript
// ❌ 這應該是單元測試！
test('calculateDiscount should return correct value', async ({ page }) => {
  await page.goto('https://example.com/calculator');
  await page.fill('#price', '1000');
  await page.fill('#discount', '0.2');
  await page.click('#calculate');
  await expect(page.locator('#result')).toHaveText('800');
});
```

---

## 反模式：測試冰淇淋筒 (Test Ice Cream Cone)

### ❌ 錯誤的比例
```
            🍦
           /  \  E2E (60%)  ← 大部分測試在這裡
          /    \ 
         /------\
        / 整合測試 \ (30%)
       /----------\
      /   單元測試  \ (10%)  ← 太少了！
     /--------------\
```

### 問題
```yaml
症狀:
  - CI/CD 執行超過 30 分鐘
  - 測試經常因為網路/環境問題失敗
  - 失敗時難以定位問題
  - 維護成本高（UI 改動 → 大量測試失敗）

原因:
  - 過度信賴 E2E，忽略單元測試
  - 把邊界條件測試寫在 E2E 層
  - 沒有適當 Mock 外部依賴
```

---

## Sentinel 建議策略

### 動態調整比例

#### 新創產品 (快速迭代)
```yaml
比例: 70% 單元 / 20% 整合 / 10% E2E
原因:
  - 需求變動快 → 降低維護成本
  - 關鍵流程少 → E2E 聚焦核心
```

#### 金融系統 (高穩定性)
```yaml
比例: 50% 單元 / 35% 整合 / 15% E2E
原因:
  - 資料正確性重要 → 增加整合測試
  - 合規需求 → 更多端到端驗證
```

#### CLI 工具 (無 UI)
```yaml
比例: 80% 單元 / 20% 整合 / 0% E2E
原因:
  - 無瀏覽器需求 → 跳過 E2E
  - 邏輯密集 → 大量單元測試
```

---

## 實戰檢查清單

### 單元測試覆蓋率目標
- [ ] 業務邏輯函數: 95%+
- [ ] 工具函數: 90%+
- [ ] 邊界條件: 每個函數至少 3 個案例
- [ ] 錯誤處理: 100% 涵蓋 throw/catch

### 整合測試覆蓋率目標
- [ ] API endpoints: 100% 涵蓋
- [ ] 資料庫操作: 關鍵 CRUD 全測
- [ ] 外部服務: 至少 Mock 成功/失敗兩種情境

### E2E 測試覆蓋率目標
- [ ] 關鍵業務流程: 100%
- [ ] 跨平台驗證: 至少 2 個瀏覽器
- [ ] 效能基準: 記錄載入時間

---

## 常見問題 FAQ

### Q: 覆蓋率 100% 就等於高品質嗎？
**A:** 不一定。覆蓋率只代表「程式碼有被執行」，不代表「邏輯被驗證」。

```typescript
// ❌ 100% 覆蓋率但沒意義
function divide(a: number, b: number) {
  return a / b; // 沒處理除以零！
}

test('divide', () => {
  divide(10, 2); // ✅ 通過，但沒驗證結果
});
```

### Q: 整合測試可以取代單元測試嗎？
**A:** 不行。整合測試失敗時，你不知道是哪個模組出錯。

```yaml
範例:
  整合測試失敗: POST /api/orders → 500 Error
  
  可能原因:
    - 資料庫連線失敗？
    - 商品庫存檢查邏輯錯誤？
    - 折扣計算錯誤？
    - 訂單建立邏輯錯誤？
  
  解決方案:
    若有完整單元測試 → 快速定位到 calculateDiscount()
```

### Q: E2E 測試太慢，如何加速？
**A:** 平行執行 + 選擇性執行

```yaml
策略:
  1. 平行執行: Playwright 支援多 worker
     workers: 4 → 速度提升 3-4x
  
  2. 關鍵路徑優先:
     - 每次 commit: 只跑核心流程 (5 個場景)
     - 每日定時: 跑完整套件 (20 個場景)
  
  3. 善用快照:
     - 登入後儲存 cookie
     - 重複使用已建立的測試資料
```

---

**版本:** 1.0.0  
**維護者:** Sentinel Agent  
**參考資料:**
- [Martin Fowler - Testing Pyramid](https://martinfowler.com/bliki/TestPyramid.html)
- [Google Testing Blog](https://testing.googleblog.com/)
