# 測試框架快速參考 (Testing Framework Quick Reference)

**目標：** 為 Sentinel 提供各框架的慣用語法與最佳實踐速查

---

## 目錄
- [Jest / Vitest](#jest--vitest)
- [Pytest (Python)](#pytest-python)
- [React Testing Library](#react-testing-library)
- [Playwright (E2E)](#playwright-e2e)
- [Supertest (API Testing)](#supertest-api-testing)

---

## Jest / Vitest

### 基本結構
```typescript
describe('GroupName', () => {
  beforeEach(() => {
    // 每個測試前執行
  });

  afterEach(() => {
    // 每個測試後執行
  });

  it('should do something', () => {
    // 測試邏輯
    expect(result).toBe(expected);
  });

  it.skip('temporarily disabled', () => {
    // 暫時跳過
  });

  it.only('run only this test', () => {
    // 只執行這個測試（除錯用）
  });
});
```

### 常用 Matchers
```typescript
// 相等性
expect(value).toBe(42);                    // 嚴格相等 (===)
expect(obj).toEqual({ a: 1, b: 2 });      // 深度相等

// Truthiness
expect(value).toBeTruthy();               // 真值
expect(value).toBeFalsy();                // 假值
expect(value).toBeNull();                 // null
expect(value).toBeUndefined();            // undefined
expect(value).toBeDefined();              // 非 undefined

// 數字比較
expect(value).toBeGreaterThan(10);
expect(value).toBeGreaterThanOrEqual(10);
expect(value).toBeLessThan(10);
expect(value).toBeCloseTo(0.3, 2);        // 浮點數比較（精度 2 位）

// 字串
expect(str).toMatch(/pattern/);
expect(str).toContain('substring');

// 陣列/可迭代物件
expect(arr).toContain(item);
expect(arr).toHaveLength(3);
expect(arr).toEqual(expect.arrayContaining([1, 2]));

// 例外
expect(() => fn()).toThrow();
expect(() => fn()).toThrow('Error message');
expect(() => fn()).toThrow(TypeError);

// 物件結構
expect(obj).toHaveProperty('key', value);
expect(obj).toMatchObject({ a: 1 });      // 部分匹配

// Promise
await expect(promise).resolves.toBe(value);
await expect(promise).rejects.toThrow();
```

### Mock 函數
```typescript
// 建立 Mock
const mockFn = jest.fn();
const mockFn = jest.fn(() => 42);         // 帶回傳值
const mockFn = jest.fn().mockReturnValue(42);

// Mock 實作
mockFn.mockImplementation((x) => x * 2);
mockFn.mockResolvedValue('async result'); // Promise
mockFn.mockRejectedValue(new Error());    // Promise rejection

// 驗證呼叫
expect(mockFn).toHaveBeenCalled();
expect(mockFn).toHaveBeenCalledTimes(2);
expect(mockFn).toHaveBeenCalledWith(arg1, arg2);
expect(mockFn).toHaveBeenLastCalledWith(arg);

// Mock 模組
jest.mock('./module', () => ({
  default: jest.fn(),
  namedExport: jest.fn()
}));

// 部分 Mock
jest.mock('./module', () => ({
  ...jest.requireActual('./module'),
  specificFn: jest.fn()
}));

// Spy on existing methods
const spy = jest.spyOn(obj, 'method');
spy.mockReturnValue(42);
spy.mockRestore(); // 恢復原始實作
```

### 非同步測試
```typescript
// Async/Await
it('should fetch data', async () => {
  const data = await fetchData();
  expect(data).toEqual({ id: 1 });
});

// Promise
it('should return promise', () => {
  return fetchData().then(data => {
    expect(data).toBeDefined();
  });
});

// 等待所有非同步完成
await waitFor(() => {
  expect(element).toBeInTheDocument();
});
```

### Snapshot 測試
```typescript
it('should match snapshot', () => {
  const tree = renderer.create(<Component />).toJSON();
  expect(tree).toMatchSnapshot();
});

// Inline snapshot
expect(value).toMatchInlineSnapshot(`"expected value"`);

// Property matchers
expect(obj).toMatchSnapshot({
  createdAt: expect.any(Date),
  id: expect.any(Number)
});
```

---

## Pytest (Python)

### 基本結構
```python
import pytest

def test_simple():
    assert 1 + 1 == 2

def test_with_message():
    assert value == expected, "Custom error message"

@pytest.mark.skip(reason="Not implemented yet")
def test_skipped():
    pass

@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 4),
    (3, 6)
])
def test_multiple_cases(input, expected):
    assert input * 2 == expected
```

### Fixtures
```python
import pytest

@pytest.fixture
def sample_data():
    """Setup test data"""
    data = {"id": 1, "name": "Test"}
    yield data  # 測試執行
    # Teardown (optional)
    print("Cleanup")

def test_using_fixture(sample_data):
    assert sample_data["id"] == 1

@pytest.fixture(scope="module")
def db_connection():
    """整個模組共用"""
    conn = create_connection()
    yield conn
    conn.close()

@pytest.fixture(autouse=True)
def reset_database():
    """每個測試自動執行"""
    db.reset()
```

### 斷言
```python
# 相等性
assert value == expected
assert value != other

# 身份
assert obj is same_obj
assert obj is not other_obj

# 成員
assert item in collection
assert item not in collection

# 型別
assert isinstance(obj, MyClass)

# 例外
with pytest.raises(ValueError):
    raise_error()

with pytest.raises(ValueError, match="invalid"):
    raise_error()

# 警告
with pytest.warns(UserWarning):
    trigger_warning()

# 近似值
assert value == pytest.approx(0.3, abs=0.01)
```

### Mock (pytest-mock)
```python
def test_with_mock(mocker):
    # Mock 函數
    mock_fn = mocker.Mock(return_value=42)
    assert mock_fn() == 42
    
    # Mock 方法
    mocker.patch('module.function', return_value='mocked')
    
    # Spy on existing method
    spy = mocker.spy(obj, 'method')
    obj.method()
    spy.assert_called_once()
    
    # Mock 物件屬性
    mocker.patch.object(obj, 'attribute', 'new_value')
    
    # Mock 多個回傳值
    mock_fn = mocker.Mock(side_effect=[1, 2, 3])
    assert mock_fn() == 1
    assert mock_fn() == 2
```

### 非同步測試 (pytest-asyncio)
```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    result = await async_fetch_data()
    assert result is not None

@pytest.fixture
async def async_client():
    client = AsyncClient()
    yield client
    await client.close()
```

---

## React Testing Library

### 基本查詢
```typescript
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

it('should render and interact', async () => {
  render(<MyComponent />);
  
  // 查詢元素（優先級由高到低）
  const button = screen.getByRole('button', { name: /submit/i });
  const label = screen.getByLabelText('Username');
  const placeholder = screen.getByPlaceholderText('Enter name');
  const text = screen.getByText(/hello/i);
  const testId = screen.getByTestId('custom-element');
  
  // 查詢變體
  screen.queryByRole('button');    // 不存在時返回 null（不拋錯）
  await screen.findByRole('button'); // 非同步等待出現
  
  // 批次查詢
  const buttons = screen.getAllByRole('button');
  expect(buttons).toHaveLength(3);
});
```

### 使用者互動
```typescript
import userEvent from '@testing-library/user-event';

it('should handle user interactions', async () => {
  const user = userEvent.setup();
  render(<LoginForm />);
  
  // 點擊
  await user.click(screen.getByRole('button'));
  
  // 輸入文字
  await user.type(screen.getByLabelText('Email'), 'test@example.com');
  
  // 清除輸入
  await user.clear(screen.getByRole('textbox'));
  
  // 選擇下拉選單
  await user.selectOptions(screen.getByRole('combobox'), 'option1');
  
  // 上傳檔案
  const file = new File(['content'], 'test.png', { type: 'image/png' });
  await user.upload(screen.getByLabelText('Upload'), file);
  
  // 鍵盤操作
  await user.keyboard('{Enter}');
  await user.keyboard('{Shift>}A{/Shift}'); // Shift+A
});
```

### 斷言
```typescript
import '@testing-library/jest-dom'; // 擴展 matchers

it('should verify element state', () => {
  render(<Component />);
  
  const element = screen.getByRole('button');
  
  // 可見性
  expect(element).toBeInTheDocument();
  expect(element).toBeVisible();
  expect(element).not.toBeInTheDocument();
  
  // 內容
  expect(element).toHaveTextContent('Click me');
  expect(element).toHaveAttribute('href', '/home');
  expect(element).toHaveClass('btn-primary');
  
  // 狀態
  expect(element).toBeDisabled();
  expect(element).toBeEnabled();
  expect(element).toBeChecked();
  expect(element).toHaveFocus();
  
  // 表單
  expect(input).toHaveValue('test');
  expect(select).toHaveDisplayValue('Option 1');
});
```

### 非同步等待
```typescript
import { waitFor, waitForElementToBeRemoved } from '@testing-library/react';

it('should handle async updates', async () => {
  render(<AsyncComponent />);
  
  // 等待元素出現
  const element = await screen.findByText('Loaded');
  
  // 等待條件
  await waitFor(() => {
    expect(screen.getByRole('status')).toHaveTextContent('Success');
  });
  
  // 等待元素消失
  await waitForElementToBeRemoved(() => screen.queryByText('Loading...'));
  
  // 自訂 timeout
  await waitFor(() => {
    expect(element).toBeInTheDocument();
  }, { timeout: 5000 });
});
```

---

## Playwright (E2E)

### 基本操作
```typescript
import { test, expect } from '@playwright/test';

test('basic interactions', async ({ page }) => {
  // 導航
  await page.goto('https://example.com');
  await page.goto('/relative-path'); // 需配置 baseURL
  
  // 等待載入
  await page.waitForLoadState('networkidle');
  await page.waitForURL('/dashboard');
  
  // 元素定位（由穩定到脆弱）
  await page.locator('[data-testid="submit"]').click();     // ✅ 最穩定
  await page.getByRole('button', { name: 'Submit' }).click(); // ✅ 語意化
  await page.getByLabel('Username').fill('admin');           // ✅ 無障礙
  await page.getByText('Welcome').isVisible();               // 🟡 易變動
  await page.locator('#submit-btn').click();                 // ❌ 脆弱
  
  // 點擊
  await page.click('button');
  await page.dblclick('button');
  await page.hover('.menu-item');
  
  // 輸入
  await page.fill('input[name="email"]', 'test@example.com');
  await page.type('input', 'slow typing', { delay: 100 });
  await page.press('input', 'Enter');
  
  // 選擇
  await page.selectOption('select', 'option1');
  await page.check('input[type="checkbox"]');
  await page.uncheck('input[type="checkbox"]');
});
```

### 斷言
```typescript
test('assertions', async ({ page }) => {
  await page.goto('/');
  
  // URL
  await expect(page).toHaveURL('/dashboard');
  await expect(page).toHaveURL(/dashboard/);
  
  // 標題
  await expect(page).toHaveTitle('My App');
  
  // 元素狀態
  const button = page.locator('button');
  await expect(button).toBeVisible();
  await expect(button).toBeHidden();
  await expect(button).toBeEnabled();
  await expect(button).toBeDisabled();
  await expect(button).toBeChecked();
  await expect(button).toBeFocused();
  
  // 內容
  await expect(button).toHaveText('Submit');
  await expect(button).toContainText('Sub');
  await expect(button).toHaveAttribute('href', '/home');
  await expect(button).toHaveClass(/btn-primary/);
  
  // 數量
  await expect(page.locator('.item')).toHaveCount(5);
  
  // 截圖比對
  await expect(page).toHaveScreenshot('homepage.png');
});
```

### 高級功能
```typescript
// 等待策略
await page.waitForSelector('.content');
await page.waitForTimeout(1000); // ❌ 避免使用
await page.waitForResponse(resp => resp.url().includes('/api/data'));
await page.waitForFunction(() => document.querySelector('.loaded'));

// 多個元素
const items = page.locator('.item');
const count = await items.count();
const first = items.first();
const last = items.last();
const nth = items.nth(2);

// 網路攔截
await page.route('**/api/users', route => {
  route.fulfill({
    status: 200,
    body: JSON.stringify([{ id: 1, name: 'Mock User' }])
  });
});

// 檔案上傳
await page.setInputFiles('input[type="file"]', 'path/to/file.pdf');

// 截圖與錄影
await page.screenshot({ path: 'screenshot.png' });
await page.screenshot({ path: 'screenshot.png', fullPage: true });

// 執行 JavaScript
const result = await page.evaluate(() => {
  return window.innerWidth;
});

// 多頁籤處理
const [newPage] = await Promise.all([
  context.waitForEvent('page'),
  page.click('a[target="_blank"]')
]);
await newPage.waitForLoadState();
```

---

## Supertest (API Testing)

### 基本請求
```typescript
import request from 'supertest';
import { app } from '../src/app';

describe('API Tests', () => {
  it('GET /api/users', async () => {
    const response = await request(app)
      .get('/api/users')
      .expect(200)
      .expect('Content-Type', /json/);
    
    expect(response.body).toEqual([
      { id: 1, name: 'User 1' },
      { id: 2, name: 'User 2' }
    ]);
  });
  
  it('POST /api/users', async () => {
    await request(app)
      .post('/api/users')
      .send({ name: 'New User', email: 'new@example.com' })
      .set('Accept', 'application/json')
      .expect(201)
      .expect(res => {
        expect(res.body).toHaveProperty('id');
        expect(res.body.name).toBe('New User');
      });
  });
  
  it('PUT /api/users/:id', async () => {
    await request(app)
      .put('/api/users/1')
      .send({ name: 'Updated' })
      .expect(200);
  });
  
  it('DELETE /api/users/:id', async () => {
    await request(app)
      .delete('/api/users/1')
      .expect(204);
  });
});
```

### 認證與 Headers
```typescript
it('should require authentication', async () => {
  await request(app)
    .get('/api/protected')
    .expect(401);
  
  const token = 'Bearer jwt-token';
  await request(app)
    .get('/api/protected')
    .set('Authorization', token)
    .expect(200);
});

it('should handle custom headers', async () => {
  await request(app)
    .get('/api/data')
    .set('X-Custom-Header', 'value')
    .set('Accept-Language', 'zh-TW')
    .expect(200);
});
```

### 錯誤處理
```typescript
it('should return 400 for invalid data', async () => {
  await request(app)
    .post('/api/users')
    .send({ name: '' }) // 缺少 email
    .expect(400)
    .expect(res => {
      expect(res.body.error).toContain('email is required');
    });
});

it('should return 404 for non-existent resource', async () => {
  await request(app)
    .get('/api/users/999999')
    .expect(404);
});
```

---

## 框架選擇決策樹

```yaml
需求: 測試前端元件
  → 框架: React Testing Library
  → 適用: React/Vue/Svelte 元件

需求: 測試後端 API
  → 語言: Node.js → Supertest
  → 語言: Python → httpx + pytest
  → 語言: Go → net/http/httptest

需求: E2E 測試
  → 跨瀏覽器: Playwright ✅
  → 只需 Chrome: Playwright 或 Puppeteer
  → 需錄製功能: Playwright ✅

需求: 單元測試
  → JavaScript/TypeScript: Jest or Vitest
  → Python: Pytest
  → Go: testing package
```

---

**版本:** 1.0.0  
**維護者:** Sentinel Agent  
**更新頻率:** 隨框架版本更新
