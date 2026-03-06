# Code Analysis Tools - 自動化代碼分析工具整合

## 概述

本模組提供內建的代碼分析能力，消除對外部工具的硬性依賴，並自動安裝必要的分析工具。

---

## 支援的分析工具

### 1. Python 代碼分析

#### Radon (複雜度分析)
```yaml
功能: Cyclomatic Complexity、Maintainability Index
安裝: pip install radon
用途:
  - 函數複雜度計算
  - 模組維護性評分
  - 風險識別基礎
```

**使用範例:**
```bash
# 計算複雜度
radon cc apps/services/ -a -s

# 計算維護性指數
radon mi apps/services/ -s
```

#### Lizard (多語言支援)
```yaml
功能: 支援 Python/JavaScript/TypeScript/Java 等
安裝: pip install lizard
用途:
  - 跨語言複雜度分析
  - NLOC (淨代碼行數) 統計
  - 參數數量分析
```

#### Bandit (安全性掃描)
```yaml
功能: 安全漏洞檢測
安裝: pip install bandit
用途:
  - SQL Injection 檢測
  - 硬編碼密碼檢測
  - 不安全函數使用檢測
```

#### Pylint (代碼品質)
```yaml
功能: 代碼風格與品質檢查
安裝: pip install pylint
用途:
  - PEP 8 合規性
  - 未使用變數檢測
  - 代碼異味識別
```

---

### 2. JavaScript/TypeScript 代碼分析

#### ESLint (靜態檢查)
```yaml
功能: 代碼風格與錯誤檢測
安裝: npm install -D eslint
用途:
  - 語法錯誤檢測
  - 最佳實踐驗證
  - 可自訂規則
```

#### TypeScript Compiler (型別檢查)
```yaml
功能: 型別系統驗證
安裝: npm install -D typescript
用途:
  - 型別錯誤檢測
  - 介面合約驗證
  - 編譯時錯誤發現
```

#### SonarJS (複雜度與品質)
```yaml
功能: 代碼複雜度與異味檢測
安裝: npm install -D eslint-plugin-sonarjs
用途:
  - 認知複雜度計算
  - 重複代碼檢測
  - 代碼異味識別
```

---

## 自動安裝機制

### Python 專案自動安裝腳本

**檔案:** `_bmad/_memory/sentinel-sidecar/scripts/install-python-analyzers.py`

```python
#!/usr/bin/env python3
"""自動安裝 Python 代碼分析工具"""

import subprocess
import sys
from typing import List, Tuple

REQUIRED_TOOLS = [
    ("radon", "radon"),
    ("lizard", "lizard"),
    ("bandit", "bandit"),
    ("pylint", "pylint"),
    ("flake8", "flake8"),
]

def check_tool_installed(package: str) -> bool:
    """檢查工具是否已安裝"""
    try:
        __import__(package)
        return True
    except ImportError:
        return False

def install_tools() -> Tuple[List[str], List[str]]:
    """安裝缺少的工具"""
    installed = []
    failed = []
    
    for package, tool_name in REQUIRED_TOOLS:
        if check_tool_installed(package):
            print(f"✅ {tool_name} 已安裝")
            continue
        
        print(f"📦 安裝 {tool_name}...")
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", package],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            installed.append(tool_name)
            print(f"✅ {tool_name} 安裝成功")
        except subprocess.CalledProcessError:
            failed.append(tool_name)
            print(f"❌ {tool_name} 安裝失敗")
    
    return installed, failed

if __name__ == "__main__":
    print("🛡️ Sentinel - 代碼分析工具自動安裝")
    print("=" * 50)
    installed, failed = install_tools()
    print("=" * 50)
    print(f"✅ 成功安裝: {len(installed)} 個工具")
    if failed:
        print(f"❌ 失敗: {failed}")
        sys.exit(1)
```

---

### JavaScript/TypeScript 專案自動安裝腳本

**檔案:** `_bmad/_memory/sentinel-sidecar/scripts/install-js-analyzers.sh`

```bash
#!/bin/bash
# 自動安裝 JavaScript/TypeScript 代碼分析工具

echo "🛡️ Sentinel - JavaScript 代碼分析工具自動安裝"
echo "=================================================="

TOOLS=(
    "eslint"
    "typescript"
    "eslint-plugin-sonarjs"
    "@typescript-eslint/parser"
    "@typescript-eslint/eslint-plugin"
)

for tool in "${TOOLS[@]}"; do
    if npm list "$tool" &> /dev/null; then
        echo "✅ $tool 已安裝"
    else
        echo "📦 安裝 $tool..."
        npm install -D "$tool" &> /dev/null
        if [ $? -eq 0 ]; then
            echo "✅ $tool 安裝成功"
        else
            echo "❌ $tool 安裝失敗"
        fi
    fi
done

echo "=================================================="
echo "✅ 工具安裝完成"
```

---

## 內建代碼分析引擎

### 簡化版 Cyclomatic Complexity 計算器

**檔案:** `_bmad/_memory/sentinel-sidecar/scripts/simple-complexity.py`

```python
#!/usr/bin/env python3
"""
簡化版 Cyclomatic Complexity 計算器
當 Radon 不可用時的備用方案
"""

import ast
import os
from typing import Dict, List, Tuple
from pathlib import Path

class ComplexityVisitor(ast.NodeVisitor):
    """AST Visitor 計算複雜度"""
    
    def __init__(self):
        self.complexity = 1
        self.functions = []
    
    def visit_FunctionDef(self, node):
        """訪問函數定義"""
        func_complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                func_complexity += 1
            elif isinstance(child, ast.BoolOp):
                func_complexity += len(child.values) - 1
        
        self.functions.append({
            "name": node.name,
            "lineno": node.lineno,
            "complexity": func_complexity
        })
        self.generic_visit(node)
    
    visit_AsyncFunctionDef = visit_FunctionDef

def analyze_file(filepath: str) -> Dict:
    """分析單個檔案"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=filepath)
        
        visitor = ComplexityVisitor()
        visitor.visit(tree)
        
        return {
            "file": filepath,
            "functions": visitor.functions,
            "max_complexity": max((f["complexity"] for f in visitor.functions), default=0)
        }
    except Exception as e:
        return {"file": filepath, "error": str(e)}

def analyze_directory(directory: str) -> List[Dict]:
    """分析目錄中所有 Python 檔案"""
    results = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                results.append(analyze_file(filepath))
    return results

def generate_report(results: List[Dict]) -> str:
    """生成報告"""
    report = ["# Cyclomatic Complexity Report", ""]
    
    high_complexity = []
    for result in results:
        if "error" in result:
            continue
        for func in result.get("functions", []):
            if func["complexity"] > 10:
                high_complexity.append({
                    "file": result["file"],
                    "function": func["name"],
                    "line": func["lineno"],
                    "complexity": func["complexity"]
                })
    
    if high_complexity:
        report.append("## 🔴 高複雜度函數 (Complexity > 10)")
        report.append("")
        for item in sorted(high_complexity, key=lambda x: x["complexity"], reverse=True):
            report.append(f"- **{item['file']}:{item['line']}** - `{item['function']}()` - Complexity: {item['complexity']}")
    else:
        report.append("## ✅ 無高複雜度函數")
    
    return "\n".join(report)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("用法: python simple-complexity.py <directory>")
        sys.exit(1)
    
    directory = sys.argv[1]
    results = analyze_directory(directory)
    print(generate_report(results))
```

---

## 整合到 Sentinel 工作流

### 自動檢測與安裝流程

```yaml
階段 1: 檢測專案類型
  - 檢查 requirements.txt / package.json
  - 識別使用語言 (Python / JavaScript / TypeScript)

階段 2: 檢查工具可用性
  - 嘗試 import radon / 執行 eslint --version
  - 記錄缺少的工具清單

階段 3: 提示使用者
  如果工具缺失:
    詢問: "檢測到缺少代碼分析工具，是否自動安裝？ [Y/n]"
    
    [Y] → 執行自動安裝腳本
    [n] → 使用內建簡化版分析器（功能有限）

階段 4: 執行分析
  優先使用: 外部工具 (Radon/Lizard)
  備用方案: 內建簡化版分析器
  
階段 5: 生成報告
  - 複雜度矩陣
  - 風險熱圖
  - 改進建議
```

---

## 使用範例

### Python 專案分析

```python
# Sentinel 自動執行
from sentinel.analyzers import PythonAnalyzer

analyzer = PythonAnalyzer(project_root=".")
report = analyzer.analyze()

print(report.summary())
# 輸出:
# ✅ 已安裝工具: radon, lizard, bandit
# 📊 分析檔案: 45 個
# 🔴 高複雜度函數: 3 個
# ⚠️ 安全問題: 1 個
# 📈 平均複雜度: 4.2
```

### JavaScript 專案分析

```bash
# Sentinel 自動執行
$ sentinel scan-project

🛡️ Sentinel - 專案代碼分析
===========================
✅ 檢測專案類型: React + TypeScript
✅ 檢查分析工具: eslint ✅, typescript ✅
📊 開始分析...

結果:
- 分析檔案: 120 個
- 型別錯誤: 0 個
- ESLint 警告: 5 個
- 高複雜度函數: 2 個

詳細報告: tests/reports/code-analysis-20260206-001.md
```

---

## 配置檔案

### `.sentinel-analyzers.yaml`

```yaml
# 代碼分析工具配置
python:
  enabled: true
  tools:
    radon:
      enabled: true
      auto_install: true
      complexity_threshold: 10
    
    lizard:
      enabled: true
      auto_install: true
    
    bandit:
      enabled: true
      auto_install: true
      severity: ["HIGH", "MEDIUM"]
    
  fallback:
    use_builtin: true  # 工具不可用時使用內建分析器

javascript:
  enabled: true
  tools:
    eslint:
      enabled: true
      auto_install: true
      config: ".eslintrc.json"
    
    typescript:
      enabled: true
      strict_mode: true

output:
  format: "markdown"
  include_metrics: true
  generate_charts: true
```

---

## 效能優化

```yaml
快取機制:
  - 只分析變更的檔案
  - 快取分析結果至 .sentinel-cache/
  - 檔案 checksum 驗證

並行處理:
  - 多執行緒分析多個檔案
  - Python: concurrent.futures
  - JavaScript: Worker threads

增量分析:
  - git diff 檢測變更範圍
  - 只重新分析影響的函數
```

---

## 總結

✅ **消除外部依賴** - 內建簡化版分析器作為備用  
✅ **自動安裝** - 一鍵安裝所有必要工具  
✅ **多語言支援** - Python/JavaScript/TypeScript  
✅ **智慧備用** - 工具不可用時自動切換內建分析器  
✅ **配置靈活** - 可自訂閾值與分析策略

**Sentinel 現在可以獨立運作，不再強制依賴外部工具！** 🛡️
