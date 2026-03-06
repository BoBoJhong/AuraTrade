# 測試最佳實踐 (Testing Best Practices)

**目標：** 提供可執行的測試編寫指南，避免常見陷阱

---

## 核心原則

### 1. FIRST 原則

```yaml
F - Fast (快速):
  - 單元測試應在毫秒級完成
  - 避免真實網路請求/資料庫連線
  - 使用 in-memory 替代品

I - Independent (獨立):
  - 測試之間不應相互依賴
  - 測試順序不影響結果
  - 避免共享可變狀態

R - Repeatable (可重複):
  - 每次執行結果一致
  - 避免依賴外部環境（時間、網路、隨機數）
  - 使用 Mock 控制外部依賴

S - Self-Validating (自我驗證):
  - 測試自動判斷通過/失敗
  - 不需人工檢查 log 或輸出
  - 清晰的斷言

T - Timely (及時):
  - TDD: 測試先於實作
  - 最晚在功能完成當下寫測試
  - 不要「之後再補」
```

---

## 測試命名

### ✅ Good: 描述性命名
```typescript
// 模式: should_ExpectedBehavior_When_StateUnderTest
test('should return discount price when discount rate is valid', () => {
  expect(calculatePrice(1000, 0.2)).toBe(800);
});

test('should throw error when discount rate exceeds 1', () => {
  expect(() => calculatePrice(1000, 1.5)).toThrow();
});

// 或使用 BDD 風格
describe('calculatePrice', () => {
  describe('when discount rate is valid', () => {
    it('returns discount price', () => {
      expect(calculatePrice(1000, 0.2)).toBe(800);
    });
  });
  
  describe('when discount rate is invalid', () => {
    it('throws error', () => {
      expect(() => calculatePrice(1000, 1.5)).toThrow();
    });
  });
});
```

### ❌ Bad: 模糊命名
```typescript
test('test1', () => { /* ... */ });           // ❌ 無意義
test('price', () => { /* ... */ });           // ❌ 不夠描述
test('calculatePrice works', () => { /* ... */ }); // ❌ 太籠統
```

---

## AAA 模式 (Arrange-Act-Assert)

### ✅ Good: 結構清晰
```typescript
test('should create order with correct total amount', () => {
  // Arrange (準備)
  const user = { id: 1, balance: 1000 };
  const product = { id: 100, price: 500 };
  const quantity = 2;
  
  // Act (執行)
  const order = createOrder(user, product, quantity);
  
  // Assert (驗證)
  expect(order).toMatchObject({
    userId: 1,
    productId: 100,
    quantity: 2,
    totalAmount: 1000
  });
});
```

### ❌ Bad: 混亂的結構
```typescript
test('order test', () => {
  const user = { id: 1, balance: 1000 };
  expect(user.balance).toBe(1000); // ❌ 過早驗證
  const product = { id: 100, price: 500 };
  const order = createOrder(user, product, 2);
  const quantity = 2; // ❌ 順序錯亂
  expect(order.totalAmount).toBe(1000);
  expect(order.quantity).toBe(2); // ❌ 可合併
});
```

---

## 邊界條件測試

### 完整檢查清單
```yaml
數值輸入:
  - 零 (0)
  - 負數 (-1)
  - 極大值 (Number.MAX_SAFE_INTEGER)
  - 極小值 (Number.MIN_SAFE_INTEGER)
  - 浮點數精度 (0.1 + 0.2)
  
字串輸入:
  - 空字串 ("")
  - 只有空白 ("   ")
  - 特殊字元 ("<script>alert('XSS')</script>")
  - 超長字串 ("a".repeat(10000))
  - Unicode 字元 ("表情符號 😀")
  
陣列/集合:
  - 空陣列 ([])
  - 單一元素 ([item])
  - 大量元素 (Array(10000).fill(item))
  - null/undefined 元素
  
物件:
  - null
  - undefined
  - 空物件 ({})
  - 缺少必要欄位
  
日期時間:
  - 無效日期 (new Date('invalid'))
  - 時區差異
  - 閏年/閏秒
  - DST (日光節約時間) 轉換
```

### 範例實作
```typescript
describe('validateAge', () => {
  const validCases = [
    [18, true],
    [65, true],
    [100, true]
  ];
  
  const invalidCases = [
    [0, false],     // 邊界
    [-1, false],    // 負數
    [17, false],    // 未成年
    [150, false],   // 不合理
    [null, false],  // null
    [undefined, false],
    ['18', false],  // 型別錯誤
    [NaN, false]
  ];
  
  test.each(validCases)('should accept age %i', (age, expected) => {
    expect(validateAge(age)).toBe(expected);
  });
  
  test.each(invalidCases)('should reject age %p', (age, expected) => {
    expect(validateAge(age)).toBe(expected);
  });
});
```

---

## Mock 最佳實踐

### ✅ Good: 只 Mock 外部依賴
```typescript
// ✅ Mock 外部 API
test('should fetch user data', async () => {
  const mockFetch = jest.fn().mockResolvedValue({
    json: async () => ({ id: 1, name: 'User' })
  });
  global.fetch = mockFetch;
  
  const user = await fetchUser(1);
  
  expect(user).toEqual({ id: 1, name: 'User' });
  expect(mockFetch).toHaveBeenCalledWith('https://api.example.com/users/1');
});

// ✅ Mock 資料庫
test('should save order', async () => {
  const mockDb = {
    orders: {
      create: jest.fn().mockResolvedValue({ id: 1, status: 'pending' })
    }
  };
  
  const order = await saveOrder(mockDb, orderData);
  
  expect(order.id).toBeDefined();
  expect(mockDb.orders.create).toHaveBeenCalledWith(orderData);
});
```

### ❌ Bad: 過度 Mock
```typescript
// ❌ Mock 內部邏輯（應該真實測試）
test('should calculate total', () => {
  const mockCalculate = jest.fn().mockReturnValue(1000);
  const result = mockCalculate(500, 2);
  expect(result).toBe(1000); // ❌ 測試的是 Mock，不是真實邏輯
});
```

### Mock 重置
```typescript
describe('API Tests', () => {
  const mockFetch = jest.fn();
  
  beforeEach(() => {
    mockFetch.mockClear(); // 清除呼叫記錄
    global.fetch = mockFetch;
  });
  
  afterEach(() => {
    jest.restoreAllMocks(); // 恢復原始實作
  });
  
  test('test 1', async () => {
    mockFetch.mockResolvedValueOnce({ data: 'test1' });
    // ...
  });
  
  test('test 2', async () => {
    mockFetch.mockResolvedValueOnce({ data: 'test2' });
    // 不會受 test1 影響
  });
});
```

---

## 非同步測試

### ✅ Good: 正確等待
```typescript
// ✅ Async/Await
test('should fetch data', async () => {
  const data = await fetchData();
  expect(data).toBeDefined();
});

// ✅ waitFor (React Testing Library)
test('should show success message', async () => {
  render(<AsyncComponent />);
  
  await waitFor(() => {
    expect(screen.getByText('Success')).toBeInTheDocument();
  });
});

// ✅ findBy (自動等待)
test('should render loaded content', async () => {
  render(<AsyncComponent />);
  
  const content = await screen.findByText('Loaded');
  expect(content).toBeVisible();
});
```

### ❌ Bad: 常見錯誤
```typescript
// ❌ 忘記 await
test('should fetch data', () => {
  fetchData(); // ❌ Promise 未等待
  expect(data).toBeDefined(); // ❌ data 是 undefined
});

// ❌ 使用 setTimeout (反模式)
test('should update after delay', (done) => {
  triggerUpdate();
  setTimeout(() => {
    expect(element).toHaveText('Updated'); // ❌ 不穩定
    done();
  }, 1000);
});

// ✅ 正確做法: 等待條件
test('should update after delay', async () => {
  triggerUpdate();
  await waitFor(() => {
    expect(element).toHaveText('Updated');
  }, { timeout: 3000 });
});
```

---

## 測試數據管理

### Factory Pattern
```typescript
// tests/factories/userFactory.ts
export const createUser = (overrides = {}) => ({
  id: 1,
  email: 'test@example.com',
  name: 'Test User',
  role: 'user',
  createdAt: new Date('2024-01-01'),
  ...overrides
});

// 使用
test('admin should have access', () => {
  const admin = createUser({ role: 'admin' });
  expect(hasAccess(admin, '/admin')).toBe(true);
});

test('regular user should not have access', () => {
  const user = createUser(); // 使用預設值
  expect(hasAccess(user, '/admin')).toBe(false);
});
```

### Fixture Files
```typescript
// tests/fixtures/users.json
[
  { "id": 1, "name": "User 1", "email": "user1@example.com" },
  { "id": 2, "name": "User 2", "email": "user2@example.com" }
]

// 測試中使用
import users from './fixtures/users.json';

test('should load users', () => {
  const result = processUsers(users);
  expect(result).toHaveLength(2);
});
```

### Builder Pattern
```typescript
class UserBuilder {
  private user = {
    id: 1,
    email: 'default@example.com',
    name: 'Default User',
    role: 'user'
  };
  
  withId(id: number) {
    this.user.id = id;
    return this;
  }
  
  withEmail(email: string) {
    this.user.email = email;
    return this;
  }
  
  asAdmin() {
    this.user.role = 'admin';
    return this;
  }
  
  build() {
    return { ...this.user };
  }
}

// 使用
test('admin user', () => {
  const admin = new UserBuilder()
    .withId(999)
    .withEmail('admin@example.com')
    .asAdmin()
    .build();
  
  expect(admin.role).toBe('admin');
});
```

---

## 測試覆蓋率策略

### 有意義的覆蓋率
```yaml
優先測試:
  1. 業務邏輯 → 95%+ 覆蓋率
  2. 安全相關 → 100% 覆蓋率
  3. 金額計算 → 100% 覆蓋率
  4. 資料驗證 → 90%+ 覆蓋率

可以跳過:
  - 純型別定義 (TypeScript interfaces)
  - 簡單的 getter/setter
  - 框架產生的代碼
  - 配置檔案
```

### Coverage 配置範例
```javascript
// jest.config.js
module.exports = {
  collectCoverageFrom: [
    'src/**/*.{js,ts,tsx}',
    '!src/**/*.d.ts',           // 排除型別定義
    '!src/**/*.stories.tsx',     // 排除 Storybook
    '!src/index.tsx',            // 排除入口檔案
    '!src/config/**'             // 排除配置
  ],
  coverageThresholds: {
    global: {
      branches: 80,
      functions: 85,
      lines: 85,
      statements: 85
    },
    './src/services/payment.ts': { // 關鍵檔案更高標準
      branches: 100,
      functions: 100,
      lines: 100,
      statements: 100
    }
  }
};
```

---

## 常見反模式 (Anti-Patterns)

### ❌ 測試實作細節
```typescript
// ❌ Bad: 測試內部狀態
test('should set loading state', () => {
  const component = render(<MyComponent />);
  expect(component.state.loading).toBe(true); // ❌ 測試內部實作
});

// ✅ Good: 測試使用者可見行為
test('should show loading indicator', () => {
  render(<MyComponent />);
  expect(screen.getByText('Loading...')).toBeVisible(); // ✅ 測試外部行為
});
```

### ❌ 脆弱的選擇器
```typescript
// ❌ Bad: 依賴 CSS 類別
await page.click('.btn.btn-primary.submit-btn');

// ✅ Good: 使用語意化選擇器
await page.click('[data-testid="submit-button"]');
await page.getByRole('button', { name: 'Submit' });
```

### ❌ 測試過多東西
```typescript
// ❌ Bad: 一個測試驗證太多
test('complete user flow', async () => {
  // 100 行測試，包含註冊、登入、編輯、刪除...
  // 失敗時難以定位問題
});

// ✅ Good: 拆分成多個測試
describe('User Management', () => {
  test('should register new user', () => { /* ... */ });
  test('should login with valid credentials', () => { /* ... */ });
  test('should update user profile', () => { /* ... */ });
  test('should delete user account', () => { /* ... */ });
});
```

### ❌ 依賴測試順序
```typescript
// ❌ Bad: 測試間有依賴
let userId;

test('1. should create user', () => {
  userId = createUser(); // ❌ 共享狀態
  expect(userId).toBeDefined();
});

test('2. should fetch user', () => {
  const user = getUser(userId); // ❌ 依賴前一個測試
  expect(user).toBeDefined();
});

// ✅ Good: 獨立測試
test('should create user', () => {
  const userId = createUser();
  expect(userId).toBeDefined();
});

test('should fetch user', () => {
  const userId = createUser(); // ✅ 獨立準備
  const user = getUser(userId);
  expect(user).toBeDefined();
});
```

---

## 效能優化

### 平行執行
```javascript
// jest.config.js
module.exports = {
  maxWorkers: '50%', // 使用 50% CPU 核心
  // 或固定數量
  maxWorkers: 4
};
```

### 選擇性執行
```bash
# 只跑變更相關測試
npm test -- --onlyChanged

# 只跑特定檔案
npm test -- user.test.ts

# 只跑符合名稱的測試
npm test -- --testNamePattern="should login"

# 跳過慢測試
npm test -- --testPathIgnorePatterns=e2e
```

### 測試分層
```yaml
CI Pipeline:
  - PR commit: 只跑單元測試 (2 min)
  - PR merge: 跑單元 + 整合測試 (5 min)
  - Nightly build: 跑完整測試含 E2E (15 min)
```

---

## 測試文件化

### 自我解釋的測試
```typescript
// ✅ Good: 測試即文件
describe('Payment Processing', () => {
  describe('when payment succeeds', () => {
    it('deducts amount from user balance', () => { /* ... */ });
    it('creates transaction record', () => { /* ... */ });
    it('sends confirmation email', () => { /* ... */ });
  });
  
  describe('when payment fails', () => {
    it('does not deduct balance', () => { /* ... */ });
    it('logs error details', () => { /* ... */ });
    it('notifies user of failure', () => { /* ... */ });
  });
  
  describe('when balance is insufficient', () => {
    it('rejects payment with clear error message', () => { /* ... */ });
  });
});
```

執行後產生可讀報告:
```
Payment Processing
  when payment succeeds
    ✓ deducts amount from user balance
    ✓ creates transaction record
    ✓ sends confirmation email
  when payment fails
    ✓ does not deduct balance
    ✓ logs error details
    ✓ notifies user of failure
  when balance is insufficient
    ✓ rejects payment with clear error message
```

---

## 檢查清單

### 新功能開發前
- [ ] 了解需求與預期行為
- [ ] 識別邊界條件
- [ ] 規劃測試案例（至少涵蓋正常/異常/邊界）

### 測試撰寫時
- [ ] 使用描述性命名
- [ ] 遵循 AAA 模式
- [ ] 一個測試只驗證一個行為
- [ ] Mock 外部依賴
- [ ] 處理非同步正確

### Code Review 時
- [ ] 測試覆蓋所有分支
- [ ] 無測試實作細節
- [ ] 無依賴測試順序
- [ ] 無硬編碼魔術數字
- [ ] 失敗時提供清晰錯誤訊息

---

**版本:** 1.0.0  
**維護者:** Sentinel Agent  
**參考資料:**
- [Google Testing Blog](https://testing.googleblog.com/)
- [Kent C. Dodds - Common Testing Mistakes](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)
