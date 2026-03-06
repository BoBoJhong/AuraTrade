# Sentinel Agent IDE 整合指南

**目標:** 讓 Sentinel Agent 能在任何 IDE 中使用

---

## 🎯 支持的使用方式

### 1. VS Code + GitHub Copilot (✅ 完整支持)

**安裝:**
```bash
# 已內建支持,無需額外安裝
```

**使用:**
```
在 Copilot Chat 中輸入:
  "啟動 Sentinel Agent"
  "FC"  # Full Cycle
  "*full-cycle"
  "幫我生成測試"
```

**優點:**
- ✅ 完整 AI 支持 (自動生成測試)
- ✅ 對話式交互
- ✅ 上下文感知
- ✅ 代碼自動生成

**限制:**
- ❌ 需要 GitHub Copilot 訂閱
- ❌ 僅限 VS Code

---

### 2. 命令行 CLI (✅ 新增支持)

**安裝:**
```bash
# 1. 確保在專案根目錄
cd /path/to/your/project

# 2. 複製 sentinel-cli.py 到專案
cp /path/to/AuraTrade/sentinel-cli.py ./

# 3. 安裝依賴
pip install pyyaml

# 4. 賦予執行權限 (Linux/Mac)
chmod +x sentinel-cli.py
```

**使用:**
```bash
# 初始化專案
python sentinel-cli.py init --project-name "MyProject" --project-type python

# 掃描專案
python sentinel-cli.py scan

# 完整測試週期
python sentinel-cli.py full-cycle

# 執行特定測試
python sentinel-cli.py run-tests --type unit

# 產出報告
python sentinel-cli.py report
```

**優點:**
- ✅ IDE 無關 (任何編輯器都能用)
- ✅ 可在 CI/CD 中使用
- ✅ 腳本化自動化
- ✅ 無需訂閱服務

**限制:**
- ❌ 無 AI 自動生成測試 (僅框架和報告)
- ❌ 需要手動執行命令

---

### 3. JetBrains IDEs (IntelliJ, PyCharm, WebStorm) (🟡 部分支持)

**方案 A: 使用 External Tools**

```xml
<!-- Settings → Tools → External Tools → 新增 -->
<tool name="Sentinel - Full Cycle">
  <program>python</program>
  <parameters>$ProjectFileDir$/sentinel-cli.py full-cycle</parameters>
  <workingDir>$ProjectFileDir$</workingDir>
</tool>

<tool name="Sentinel - Scan">
  <program>python</program>
  <parameters>$ProjectFileDir$/sentinel-cli.py scan</parameters>
  <workingDir>$ProjectFileDir$</workingDir>
</tool>
```

**使用:**
1. 右鍵專案 → External Tools → Sentinel - Full Cycle
2. 或設定快捷鍵: Settings → Keymap → External Tools

**方案 B: 使用 Run Configuration**

```kotlin
// .idea/runConfigurations/sentinel_full_cycle.xml
<component name="ProjectRunConfigurationManager">
  <configuration name="Sentinel - Full Cycle" type="PythonConfigurationType">
    <script>$PROJECT_DIR$/sentinel-cli.py</script>
    <parameters>full-cycle</parameters>
    <workingDirectory>$PROJECT_DIR$</workingDirectory>
  </configuration>
</component>
```

**優點:**
- ✅ 整合進 IDE 工具欄
- ✅ 可設定快捷鍵
- ✅ 輸出直接顯示在 IDE 中

**限制:**
- ❌ 需要手動配置
- ❌ 無 AI 生成功能

---

### 4. Vim / Neovim (🟡 部分支持)

**方案 A: 使用 Vim Command**

```vim
" 在 .vimrc 或 init.vim 中添加
command! SentinelInit :!python sentinel-cli.py init
command! SentinelScan :!python sentinel-cli.py scan
command! SentinelFullCycle :!python sentinel-cli.py full-cycle
command! SentinelTest :!python sentinel-cli.py run-tests

" 快捷鍵綁定
nnoremap <leader>si :SentinelInit<CR>
nnoremap <leader>ss :SentinelScan<CR>
nnoremap <leader>sf :SentinelFullCycle<CR>
nnoremap <leader>st :SentinelTest<CR>
```

**使用:**
```vim
:SentinelFullCycle
" 或
<leader>sf
```

**方案 B: 使用 Telescope (Neovim)**

```lua
-- 在 telescope 配置中添加
local pickers = require "telescope.pickers"
local finders = require "telescope.finders"

vim.keymap.set('n', '<leader>sm', function()
  pickers.new({}, {
    prompt_title = "Sentinel Commands",
    finder = finders.new_table {
      results = {
        "init", "scan", "full-cycle", "run-tests", "report"
      }
    },
  }):find()
end)
```

**優點:**
- ✅ 原生 Vim 體驗
- ✅ 快捷鍵支持
- ✅ 終端整合

**限制:**
- ❌ 僅基礎功能

---

### 5. Sublime Text / Atom (🟡 部分支持)

**Sublime Text: Build System**

```json
// Tools → Build System → New Build System
{
    "shell_cmd": "python sentinel-cli.py full-cycle",
    "working_dir": "$project_path",
    "variants": [
        {
            "name": "Scan",
            "shell_cmd": "python sentinel-cli.py scan"
        },
        {
            "name": "Run Tests",
            "shell_cmd": "python sentinel-cli.py run-tests"
        }
    ]
}
```

**使用:**
- Ctrl+B (執行預設命令)
- Ctrl+Shift+B (選擇變體)

---

### 6. CI/CD 整合 (✅ 完整支持)

**GitHub Actions:**

```yaml
name: Sentinel Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install Sentinel CLI
        run: |
          pip install pyyaml
          chmod +x sentinel-cli.py
      
      - name: Run Sentinel Full Cycle
        run: python sentinel-cli.py full-cycle
      
      - name: Upload Test Reports
        uses: actions/upload-artifact@v4
        with:
          name: test-reports
          path: tests/reports/
```

**GitLab CI:**

```yaml
sentinel-tests:
  stage: test
  script:
    - pip install pyyaml
    - python sentinel-cli.py full-cycle
  artifacts:
    paths:
      - tests/reports/
```

**Jenkins:**

```groovy
stage('Sentinel Tests') {
    steps {
        sh 'pip install pyyaml'
        sh 'python sentinel-cli.py full-cycle'
    }
}
```

---

## 🔧 自訂整合

### 創建專案別名 (推薦)

**Bash/Zsh:**
```bash
# 在 ~/.bashrc 或 ~/.zshrc 中添加
alias sentinel='python sentinel-cli.py'
alias st-init='python sentinel-cli.py init'
alias st-scan='python sentinel-cli.py scan'
alias st-fc='python sentinel-cli.py full-cycle'
alias st-test='python sentinel-cli.py run-tests'
```

**使用:**
```bash
st-fc  # 完整測試週期
st-scan  # 掃描專案
st-test --type unit  # 執行單元測試
```

**PowerShell:**
```powershell
# 在 $PROFILE 中添加
function Sentinel-Init { python sentinel-cli.py init $args }
function Sentinel-Scan { python sentinel-cli.py scan }
function Sentinel-FullCycle { python sentinel-cli.py full-cycle }
function Sentinel-Test { python sentinel-cli.py run-tests $args }

Set-Alias st-init Sentinel-Init
Set-Alias st-scan Sentinel-Scan
Set-Alias st-fc Sentinel-FullCycle
Set-Alias st-test Sentinel-Test
```

---

## 📊 功能對比表

| 功能 | VS Code + Copilot | CLI | JetBrains | Vim | CI/CD |
|------|-------------------|-----|-----------|-----|-------|
| 專案初始化 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 代碼掃描 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 執行測試 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 產出報告 | ✅ | ✅ | ✅ | ✅ | ✅ |
| **AI 生成測試** | ✅ | ❌ | ❌ | ❌ | ❌ |
| 對話式交互 | ✅ | ❌ | ❌ | ❌ | ❌ |
| 上下文感知 | ✅ | 🟡 | 🟡 | 🟡 | ❌ |
| 無需訂閱 | ❌ | ✅ | ✅ | ✅ | ✅ |
| 腳本化自動化 | 🟡 | ✅ | ✅ | ✅ | ✅ |

---

## 💡 最佳實踐

### 混合使用策略 (推薦)

```yaml
開發階段:
  - VS Code + Copilot: AI 生成測試、對話式調試
  - CLI: 快速執行測試、產出報告

團隊協作:
  - 統一使用 CLI 腳本
  - CI/CD 自動化執行
  - 報告集中管理

遠端開發:
  - SSH + CLI: 無 GUI 環境使用
  - Vim + Sentinel CLI: 終端專家
```

### 團隊標準化

```bash
# 1. 將 sentinel-cli.py 提交到版本控制
git add sentinel-cli.py
git commit -m "Add Sentinel CLI tool"

# 2. 在 README.md 中添加使用說明
echo "## Testing with Sentinel" >> README.md
echo "python sentinel-cli.py full-cycle" >> README.md

# 3. 在 Makefile 中統一命令
# Makefile
test:
	python sentinel-cli.py run-tests

full-test:
	python sentinel-cli.py full-cycle
```

---

## 🚀 未來擴展

### 計畫中的功能

- [ ] **Web Dashboard:** 瀏覽器訪問測試報告
- [ ] **語言服務器 (LSP):** 任何支持 LSP 的 IDE 都能用
- [ ] **REST API:** HTTP 接口調用
- [ ] **Plugin System:** 自訂工作流插件
- [ ] **AI SDK:** 離線 AI 測試生成

### 貢獻機會

歡迎提交 PR:
- JetBrains 官方插件
- Vim/Neovim 插件
- Emacs integration
- VS Code 擴展 (非 Copilot)

---

**結論:**

Sentinel Agent 現在支持:
- ✅ **VS Code (完整):** AI 生成 + 對話式
- ✅ **CLI (新增):** 任何 IDE + 自動化
- ✅ **JetBrains (配置):** 整合進工具欄
- ✅ **Vim/Neovim (配置):** 快捷鍵支持
- ✅ **CI/CD (完整):** 自動化測試

**快速開始:**
```bash
# 複製 CLI 工具
cp sentinel-cli.py your-project/

# 初始化
python sentinel-cli.py init

# 開始測試
python sentinel-cli.py full-cycle
```
