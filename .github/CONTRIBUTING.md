# 貢獻指南

## 🎯 歡迎貢獻

感謝你對 AuraTrade 專案的關注！

## 🔄 開發流程

### 1. Fork 與 Clone

```bash
git clone https://github.com/your-username/AuraTrade.git
cd AuraTrade
```

### 2. 建立分支

```bash
# 功能分支
git checkout -b feature/stock-alert

# 修復分支
git checkout -b fix/price-calculation
```

### 3. 開發與測試

- 遵循 [開發規範](../.antigravity/rules.md)
- 使用 TDD 開發
- 確保測試覆蓋率 ≥ 70%

### 4. 提交代碼

```bash
git add .
git commit -m "feat(stock): add price alert feature (US-10, FR-14)"
```

## 📋 Commit 訊息規範

格式: `<type>(<scope>): <subject> (<requirements>)`

**Type**:

- `feat`: 新功能
- `fix`: Bug 修復
- `docs`: 文檔變更
- `test`: 測試相關
- `refactor`: 重構

**範例**:

```
feat(api): add stock price alert endpoint (US-10, FR-14)
fix(ui): correct price color for negative values
docs(api): update authentication examples
```

## ✅ Pull Request 檢查清單

- [ ] 代碼符合 DDD 架構
- [ ] 測試全部通過
- [ ] 文檔已更新
- [ ] 無 Linter 錯誤

## 📚 相關文檔

- [開發規範](../.antigravity/rules.md)
- [Skills 使用指南](../.agent/skills/README.MD)
