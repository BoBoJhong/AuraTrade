# CMMI Level 3 Standards Reference

## CMMI Overview（CMMI 概述）

### Maturity Levels（成熟度級別）
- **Level 1 - Initial**: 臨時的、混亂的流程
- **Level 2 - Managed**: 專案層級的流程管理
- **Level 3 - Defined**: 組織層級的流程標準化 ⭐ **我們的目標**
- **Level 4 - Quantitatively Managed**: 量化的流程管理
- **Level 5 - Optimizing**: 持續流程改進

## REQM - Requirements Management（需求管理）

### REQM SP 1.1 - Understand Requirements（理解需求）
**目標**: 與需求提供者建立對需求的共同理解

**實踐**:
- 建立需求理解的標準
- 定義需求屬性和元數據
- 確保需求的可理解性和可測試性

### REQM SP 1.2 - Obtain Commitment（獲得承諾）
**目標**: 從專案參與者獲得對需求的承諾

**實踐**:
- 評估需求的影響
- 協商並記錄承諾
- 管理需求變更的承諾

### REQM SP 1.3 - Manage Requirements Changes（管理需求變更）
**目標**: 在專案生命週期中管理需求變更

**實踐**:
- 建立變更控制流程
- 追蹤需求狀態
- 維護需求變更歷史

### REQM SP 1.4 - Maintain Bidirectional Traceability（維護雙向追溯性）
**目標**: 在需求和工作產品之間維護雙向追溯性

**實踐**:
- 建立追溯性矩陣
- 追蹤需求到設計、代碼、測試的映射
- 反向追溯測試到需求

### REQM SP 1.5 - Identify Inconsistencies（識別不一致性）
**目標**: 識別專案計劃和工作產品與需求之間的不一致性

**實踐**:
- 定期審查需求一致性
- 識別並記錄不一致性
- 採取糾正措施

## Requirements Attributes（需求屬性）

### Mandatory Attributes（強制屬性）
- **Unique ID**: 唯一識別碼（REQ-FUNC-XXX, REQ-NFR-XXX）
- **Description**: 清晰、明確的需求描述（使用 "shall"）
- **Priority**: 優先級（Must/Should/Could/Won't）
- **Status**: 狀態（Draft/Approved/Implemented/Verified）
- **Verification Method**: 驗證方法（Test/Inspection/Analysis/Demonstration）

### Optional Attributes（可選屬性）
- **Source**: 需求來源（User Story, Stakeholder, Regulation）
- **Rationale**: 需求理由
- **Risk**: 相關風險
- **Dependencies**: 依賴關係

## Verification Methods（驗證方法）

### Test（測試）
- 通過執行測試案例驗證
- 適用於功能需求
- 需要可測試的驗收標準

### Inspection（檢查）
- 通過視覺檢查或審查驗證
- 適用於文件、介面、設計
- 需要檢查清單

### Analysis（分析）
- 通過分析或計算驗證
- 適用於性能、容量需求
- 需要分析模型或工具

### Demonstration（演示）
- 通過操作演示驗證
- 適用於使用者介面、工作流程
- 需要演示腳本

## Requirement Quality Criteria（需求品質標準）

### Atomic（原子性）
- 每個需求只描述一個功能
- 不使用 "and" 或 "or" 連接多個需求
- 可獨立測試和驗證

### Unambiguous（明確性）
- 避免模糊術語（快速、簡單、使用者友善）
- 使用具體、可測量的指標
- 只有一種解釋方式

### Testable（可測試性）
- 可以設計測試案例驗證
- 有明確的驗收標準
- 可以判斷是否滿足

### Traceable（可追溯性）
- 有唯一識別碼
- 可追溯到業務目標
- 可追溯到測試案例

### Consistent（一致性）
- 與其他需求不衝突
- 使用一致的術語
- 遵循組織標準

## Common Violations（常見違規）

### ❌ Compound Requirements（複合需求）
```
錯誤: "系統應當驗證使用者並記錄登入時間"
正確: 
- REQ-FUNC-001: 系統應當驗證使用者憑證
- REQ-FUNC-002: 系統應當記錄使用者登入時間
```

### ❌ Ambiguous Terms（模糊術語）
```
錯誤: "系統應當快速響應"
正確: "系統應當在 200ms 內響應使用者請求（95th percentile）"
```

### ❌ Missing Verification Method（缺少驗證方法）
```
錯誤: REQ-FUNC-001: 系統應當支援 1000 個並發使用者
正確: 
REQ-FUNC-001: 系統應當支援 1000 個並發使用者
驗證方法: Test - 負載測試，測量並發使用者數
```

### ❌ No Traceability（無追溯性）
```
錯誤: 需求沒有 ID，無法追溯
正確: 
[REQ-FUNC-001] 使用者認證
追溯到: US-001（使用者登入）
追溯到: TC-001, TC-002（測試案例）
```

## CMMI + Agile Integration（CMMI + 敏捷整合）

### User Stories in CMMI Context（CMMI 上下文中的 User Stories）
- User Stories 作為需求的高層表達
- 從 User Stories 衍生正式的功能需求
- 維護 User Stories ↔ 功能需求的雙向追溯

### INVEST Principles（INVEST 原則）
- **I**ndependent: 獨立的
- **N**egotiable: 可協商的
- **V**aluable: 有價值的
- **E**stimable: 可估算的
- **S**mall: 小的
- **T**estable: 可測試的

### Hybrid Workflow（混合工作流程）
1. 從業務目標創建 User Stories
2. 驗證 User Stories 符合 INVEST 原則
3. 從 User Stories 衍生 CMMI 功能需求
4. 為功能需求定義驗證方法
5. 維護完整的追溯矩陣（RTM）

---

**Reference**: CMMI for Development, Version 1.3
**Last Updated**: 2026-01-07
**Version**: 1.0.0
