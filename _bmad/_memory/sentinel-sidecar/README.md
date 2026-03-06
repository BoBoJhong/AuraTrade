# Sentinel Sidecar - Persistent Memory

本資料夾儲存 **Sentinel** Expert Agent 的持久化記憶與知識庫。

## Purpose

Sentinel 使用此 sidecar 來儲存:
- 專案測試策略偏好
- 學習到的常見錯誤模式
- 風險識別知識庫
- 完整測試工作流定義
- 測試框架參考資料
- 最佳實踐指南

## Files Structure

### 核心記憶檔案
- **memories.md** - 專案偏好與學習到的模式 (持久化記憶)
- **instructions.md** - 測試策略指導與品質標準
- **risk-patterns.md** - 風險識別知識庫與常見陷阱

### 工作流定義 (workflows/)
- **full-test-cycle.md** - 完整測試週期工作流 (計畫→單元→整合→E2E→報告)
- **test-plan-template.md** - 測試計畫模板與檢查清單
- **test-output-structure.md** - 測試輸出結構規範與追溯性編號系統 🆕
- **unit-test-flow.md** - 單元測試詳細工作流 *(預留)*
- **integration-test-flow.md** - 整合測試詳細工作流 *(預留)*
- **e2e-test-flow.md** - E2E 測試詳細工作流 *(預留)*

### 知識庫 (knowledge/)
- **testing-pyramid.md** - 測試金字塔理論詳解與實戰策略
- **framework-references.md** - Jest/Vitest/Pytest/Playwright 快速參考
- **best-practices.md** - 測試最佳實踐與常見反模式
- **common-pitfalls.md** - 常見陷阱深度解析 *(預留)*
- **test-data-strategies.md** - 測試數據管理策略 *(預留)*

## Access Pattern

Agent 透過以下路徑存取這些檔案:
```
{project-root}/_bmad/_memory/sentinel-sidecar/{filename}.md
{project-root}/_bmad/_memory/sentinel-sidecar/workflows/{filename}.md
{project-root}/_bmad/_memory/sentinel-sidecar/knowledge/{filename}.md
```

## Agent Activation

當 Sentinel 啟動時,會自動載入:
1. `memories.md` - 恢復專案情境與偏好
2. `instructions.md` - 載入測試策略指引
3. `risk-patterns.md` - 載入風險識別知識
4. `workflows/full-test-cycle.md` - 完整測試週期流程定義
5. `workflows/test-output-structure.md` - 輸出結構規範與追溯性編號系統 🆕
6. `knowledge/testing-pyramid.md` - 測試理論基礎
7. `knowledge/framework-references.md` - 框架語法速查
8. `knowledge/best-practices.md` - 最佳實踐指南

## Usage

### 完整測試週期
使用 `[FC]` 或 `*full-cycle` 命令執行完整流程:
```
開發者: *full-cycle
Sentinel: 
  🛡️ 開始完整測試週期...
  [1/5] 測試計畫生成中...
  [2/5] 單元測試執行中...
  [3/5] 整合測試執行中...
  [4/5] E2E 測試執行中...
  [5/5] 測試報告生成中...
  🎉 測試週期完成!
```

### 其他命令
- `[SC]` 掃描專案代碼
- `[GT]` 自動生成測試
- `[RM]` 產生風險地圖
- `[GM]` 生成 Mock 資料
- `[TS]` 建議測試策略
- `[FP]` 修復失敗測試
- `[TD]` TDD 模式
- `[QR]` 品質報告

---

**創建日期:** 2026-02-06  
**最後更新:** 2026-02-06  
**Agent:** Sentinel (Test Architect & Quality Guardian)  
**類型:** Expert Agent with Persistent Memory  
**版本:** 1.0.0
