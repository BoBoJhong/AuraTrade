# AuraTrade UML 圖表目錄

本目錄存放所有系統設計相關的 UML 圖表，使用 **PlantUML** 格式。

## 📋 圖表清單

### 系統架構圖

- [x] `architecture.puml` - 系統整體架構圖

### 資料庫設計

- [x] `database-er.puml` - 資料庫 ER 圖

### 類別圖 (Class Diagrams)

- [ ] `backend-classes.puml` - 後端核心類別圖
- [ ] `frontend-components.puml` - 前端元件結構圖

### 序列圖 (Sequence Diagrams)

- [x] `stock-price-flow.puml` - 股價查詢流程
- [x] `ai-analysis-flow.puml` - AI 分析流程
- [x] `authentication-flow.puml` - 認證流程

### 狀態圖 (State Diagrams)

- [ ] `order-state.puml` - 訂單狀態轉換（未來功能）

## 🛠️ 如何使用 PlantUML

### 1. 安裝 PlantUML

#### VSCode 擴展（推薦）

```bash
# 安裝 PlantUML 擴展
code --install-extension jebbs.plantuml
```

#### 本地安裝

```bash
# macOS
brew install plantuml

# Ubuntu/Debian
sudo apt-get install plantuml

# Windows
# 下載 plantuml.jar 從 https://plantuml.com/download
```

### 2. 渲染 UML 圖

#### 使用 VSCode

1. 開啟 `.puml` 檔案
2. 按 `Alt+D` 預覽圖表
3. 右鍵 → Export Current Diagram

#### 使用命令列

```bash
# 生成 PNG
plantuml docs/diagrams/architecture.puml

# 生成 SVG（推薦，可縮放）
plantuml -tsvg docs/diagrams/*.puml

# 批量生成
plantuml docs/diagrams/*.puml
```

### 3. 在 Markdown 中引用

```markdown
## 系統架構

![系統架構圖](./diagrams/architecture.png)

## 資料庫設計

![ER 圖](./diagrams/database-er.svg)
```

## 📝 PlantUML 編寫規範

### 命名規範

- 檔案名稱：小寫，使用連字號 `-`
- 範例：`user-authentication-flow.puml`

### 檔案結構

```plantuml
@startuml
' 標題
title 系統名稱 - 圖表標題

' 作者與版本
' Author: Team Name
' Version: 1.0
' Last Updated: 2026-01-29

' 樣式設定（可選）
skinparam backgroundColor #FEFEFE
skinparam handwritten false

' 圖表內容
...

@enduml
```

### 顏色規範

```plantuml
' 使用一致的配色
!define PRIMARY_COLOR #4A90E2
!define SECONDARY_COLOR #50C878
!define WARNING_COLOR #FFA500
!define DANGER_COLOR #DC3545
```

## 🔗 相關文檔

- [PlantUML 官方文檔](https://plantuml.com/)
- [PlantUML 語法速查](https://plantuml.com/zh/)
- [SDD - 軟體設計文檔](../SDD.md)
- [ARCHITECTURE - 系統架構](../ARCHITECTURE.md)

## 📊 圖表維護規則

1. **新增圖表時**
   - ✅ 更新本 README.MD 的圖表清單
   - ✅ 在 SDD.md 中引用圖表
   - ✅ 提交圖表源文件 (.puml) 到 Git

2. **修改圖表時**
   - ✅ 更新版本號與修改日期
   - ✅ 重新生成圖片檔案
   - ✅ 同步更新相關文檔

3. **圖片格式選擇**
   - 優先使用 **SVG**（可縮放、檔案小）
   - 需要編輯時使用 **PNG**
   - 文檔中優先使用 SVG

---

**最後更新**: 2026-01-29  
**維護者**: AuraTrade Architecture Team
