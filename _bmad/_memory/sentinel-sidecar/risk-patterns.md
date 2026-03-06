# Sentinel Risk Patterns Knowledge Base

## 風險識別知識庫

本檔案儲存 Sentinel 用於識別代碼風險的模式與知識。

---

## 高風險代碼模式

### 1. 金額與貨幣計算

```javascript
// 🔴 高風險模式
function calculateTotal(items) {
  return items.reduce((sum, item) => sum + item.price, 0); // 浮點數精度問題
}

// ✅ 必須測試的邊界條件
- 空陣列
- 極小金額 (0.01)
- 極大金額 (999999999.99)
- 負數金額
- NaN / undefined price
```

**為什麼高風險：** 金錢計算錯誤直接影響業務，浮點數精度問題容易被忽略。

---

### 2. 認證與授權邏輯

```javascript
// 🔴 高風險模式
function canAccess(user, resource) {
  return user.role === 'admin' || user.id === resource.ownerId;
}

// ✅ 必須測試的邊界條件
- user 為 null / undefined
- role 為空字串
- resource 不存在
- 權限邊界（admin vs owner vs guest）
```

**為什麼高風險：** 權限漏洞可能導致安全問題，必須 100% 覆蓋。

---

### 3. 非同步操作與 Race Condition

```javascript
// 🔴 高風險模式
async function fetchData() {
  const data = await api.get('/data');
  return data; // 沒有錯誤處理
}

// ✅ 必須測試的邊界條件
- API 超時
- 網路錯誤 (500, 404, 403)
- 回傳 null / undefined
- Race condition（多次快速調用）
```

**為什麼高風險：** 非同步錯誤難以重現，容易在生產環境爆發。

---

### 4. 陣列與集合操作

```javascript
// 🔴 高風險模式
function getFirstActive(users) {
  return users.filter(u => u.active)[0]; // 可能 undefined
}

// ✅ 必須測試的邊界條件
- 空陣列
- 全部 inactive
- users 為 null / undefined
- 陣列中有 null 元素
```

**為什麼高風險：** 陣列操作容易產生 `undefined` 導致後續錯誤。

---

### 5. 日期與時間處理

```javascript
// 🔴 高風險模式
function isExpired(expiryDate) {
  return new Date(expiryDate) < new Date();
}

// ✅ 必須測試的邊界條件
- Invalid date string
- null / undefined
- 時區問題
- 閏年 / 夏令時
```

**為什麼高風險：** 日期處理容易受時區與格式影響，跨平台問題多。

---

## Cyclomatic Complexity 高風險函數

### 識別標準

```
Complexity > 15：🔴 Critical - 必須立即測試
Complexity 10-15：🟡 High - 強烈建議測試
Complexity 5-10：🟢 Medium - 建議測試
Complexity < 5：⚪ Low - 可選測試
```

### 高複雜度的常見原因

1. **多層嵌套 if-else**
2. **大量 switch-case**
3. **複雜的條件組合 (&&, ||)**
4. **遞迴函數**
5. **狀態機邏輯**

---

## 常見測試盲點

### 開發者容易忽略的情況

1. **樂觀路徑偏見**
   - 只測試「正常流程」
   - 忽略錯誤處理與邊界條件

2. **非同步盲點**
   - 忘記 await
   - 未處理 Promise rejection
   - Race condition

3. **型別轉換陷阱**
   - `"0"` vs `0` vs `false`
   - `null` vs `undefined`
   - 隱式型別轉換

4. **狀態管理盲點**
   - 初始狀態未測試
   - 狀態轉換邊界未覆蓋
   - 狀態競爭條件

---

## OWASP Top 10 測試檢查清單

### Web 應用常見安全風險

1. **Injection（注入攻擊）**
   - SQL Injection
   - XSS (Cross-Site Scripting)
   - Command Injection

2. **Broken Authentication（認證破解）**
   - 弱密碼策略
   - Session 管理漏洞
   - 暴力破解

3. **Sensitive Data Exposure（敏感資料洩漏）**
   - 未加密傳輸
   - 日誌中包含密碼
   - API 回傳過多資訊

4. **XML External Entities (XXE)**
5. **Broken Access Control（存取控制破解）**
6. **Security Misconfiguration（安全性配置錯誤）**
7. **Cross-Site Scripting (XSS)**
8. **Insecure Deserialization（不安全的反序列化）**
9. **Using Components with Known Vulnerabilities**
10. **Insufficient Logging & Monitoring**

---

## 測試優先級決策樹

```
是否涉及金錢/支付？
├── YES → Priority: Critical 🔴
└── NO ↓

是否涉及認證/授權？
├── YES → Priority: Critical 🔴
└── NO ↓

Cyclomatic Complexity > 15？
├── YES → Priority: High 🟡
└── NO ↓

Coverage < 50%？
├── YES → Priority: Medium 🟢
└── NO → Priority: Low ⚪
```

---

## 持續更新機制

Sentinel 會從每次互動中學習新的風險模式：

```yaml
learning:
  - date: "2026-02-06"
    pattern: "新的風險模式描述"
    source: "從專案 X 的測試失敗中學習"
    severity: "Critical / High / Medium / Low"
```

---

**Version:** 1.0.0  
**Last Updated:** 2026-02-06  
**Next Update:** 隨著與開發者互動持續更新
