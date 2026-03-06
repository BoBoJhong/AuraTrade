# Visualization Engine - 測試報告視覺化引擎

## 概述

將測試報告中的文字描述轉換為專業的圖表圖片，提升報告可讀性與專業度。

---

## 支援的圖表類型

### 1. 測試結果圖表

#### 圓餅圖 (Test Results Pie Chart)
```yaml
用途: 測試通過/失敗/跳過比例
工具: Matplotlib / Chart.js
資料: {passed: 120, failed: 3, skipped: 2}
輸出: test-results-pie.png
```

#### 長條圖 (Module Coverage Bar Chart)
```yaml
用途: 各模組覆蓋率比較
工具: Matplotlib
資料: {AuthService: 85%, PaymentService: 92%, ...}
輸出: module-coverage-bar.png
```

---

### 2. 趨勢圖表

#### 折線圖 (Coverage Trend)
```yaml
用途: 覆蓋率歷史趨勢
工具: Matplotlib
資料: [(2026-02-01, 65%), (2026-02-02, 68%), ...]
輸出: coverage-trend-line.png
```

#### 堆疊面積圖 (Test Type Distribution)
```yaml
用途: 單元/整合/E2E 測試數量趨勢
工具: Matplotlib
輸出: test-type-area.png
```

---

### 3. 風險地圖

#### 熱圖 (Complexity vs Coverage Heatmap)
```yaml
用途: 複雜度與覆蓋率矩陣
工具: Seaborn / Matplotlib
軸: X=覆蓋率, Y=複雜度
顏色: 紅(高風險) → 綠(低風險)
輸出: risk-heatmap.png
```

#### 散點圖 (Risk Distribution)
```yaml
用途: 檔案風險分佈
工具: Matplotlib
資料: [(filename, complexity, coverage), ...]
輸出: risk-scatter.png
```

---

### 4. 品質儀表板

#### 儀表盤 (Quality Dashboard)
```yaml
用途: 一頁總覽所有指標
包含: 
  - 品質評分卡 (0-100分)
  - 測試通過率圓餅圖
  - 覆蓋率趨勢折線圖
  - 風險分佈熱圖
輸出: quality-dashboard.png
```

---

## Python 實作 (Matplotlib)

### 圖表生成器基礎類

**檔案:** `_bmad/_memory/sentinel-sidecar/scripts/visualization_engine.py`

```python
#!/usr/bin/env python3
"""
Sentinel Visualization Engine
測試報告圖表生成引擎
"""

import matplotlib
matplotlib.use('Agg')  # 無 GUI 後端
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime

# 設定中文字體
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'Arial Unicode MS', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False  # 解決負號顯示問題

@dataclass
class ChartConfig:
    """圖表配置"""
    title: str
    filename: str
    figsize: Tuple[int, int] = (10, 6)
    dpi: int = 300
    style: str = "seaborn-v0_8-darkgrid"

class VisualizationEngine:
    """視覺化引擎主類"""
    
    def __init__(self, output_dir: str = "tests/reports/charts"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_test_results_pie(
        self, 
        passed: int, 
        failed: int, 
        skipped: int,
        config: Optional[ChartConfig] = None
    ) -> str:
        """生成測試結果圓餅圖"""
        if config is None:
            config = ChartConfig(
                title="測試結果分布",
                filename="test-results-pie.png",
                figsize=(8, 8)
            )
        
        plt.style.use(config.style)
        fig, ax = plt.subplots(figsize=config.figsize)
        
        sizes = [passed, failed, skipped]
        labels = [f'通過\n{passed}', f'失敗\n{failed}', f'跳過\n{skipped}']
        colors = ['#2ecc71', '#e74c3c', '#f39c12']
        explode = (0.1, 0, 0)  # 突出通過部分
        
        ax.pie(
            sizes, 
            explode=explode, 
            labels=labels, 
            colors=colors,
            autopct='%1.1f%%',
            shadow=True, 
            startangle=90,
            textprops={'fontsize': 14, 'weight': 'bold'}
        )
        ax.axis('equal')
        
        plt.title(config.title, fontsize=18, weight='bold', pad=20)
        
        output_path = self.output_dir / config.filename
        plt.savefig(output_path, dpi=config.dpi, bbox_inches='tight')
        plt.close()
        
        return str(output_path)
    
    def generate_coverage_bar(
        self,
        modules: Dict[str, float],
        config: Optional[ChartConfig] = None
    ) -> str:
        """生成模組覆蓋率長條圖"""
        if config is None:
            config = ChartConfig(
                title="模組測試覆蓋率",
                filename="module-coverage-bar.png",
                figsize=(12, 8)
            )
        
        plt.style.use(config.style)
        fig, ax = plt.subplots(figsize=config.figsize)
        
        modules_sorted = dict(sorted(modules.items(), key=lambda x: x[1], reverse=True))
        names = list(modules_sorted.keys())
        values = list(modules_sorted.values())
        
        # 顏色編碼: 綠(>80%) 黃(60-80%) 紅(<60%)
        colors = ['#2ecc71' if v >= 80 else '#f39c12' if v >= 60 else '#e74c3c' for v in values]
        
        bars = ax.barh(names, values, color=colors, edgecolor='black', linewidth=1.2)
        
        # 添加數值標籤
        for i, (bar, value) in enumerate(zip(bars, values)):
            ax.text(value + 1, i, f'{value:.1f}%', 
                   va='center', fontsize=11, weight='bold')
        
        ax.set_xlabel('覆蓋率 (%)', fontsize=14, weight='bold')
        ax.set_title(config.title, fontsize=18, weight='bold', pad=20)
        ax.set_xlim(0, 110)
        
        # 添加目標線
        ax.axvline(x=80, color='green', linestyle='--', linewidth=2, alpha=0.5, label='目標: 80%')
        ax.legend(fontsize=12)
        
        plt.tight_layout()
        output_path = self.output_dir / config.filename
        plt.savefig(output_path, dpi=config.dpi, bbox_inches='tight')
        plt.close()
        
        return str(output_path)
    
    def generate_coverage_trend(
        self,
        dates: List[str],
        coverage_values: List[float],
        config: Optional[ChartConfig] = None
    ) -> str:
        """生成覆蓋率趨勢折線圖"""
        if config is None:
            config = ChartConfig(
                title="測試覆蓋率趨勢",
                filename="coverage-trend-line.png"
            )
        
        plt.style.use(config.style)
        fig, ax = plt.subplots(figsize=config.figsize)
        
        ax.plot(dates, coverage_values, 
                marker='o', markersize=8, linewidth=2.5,
                color='#3498db', label='覆蓋率')
        
        # 填充區域
        ax.fill_between(dates, coverage_values, alpha=0.3, color='#3498db')
        
        # 添加數值標籤
        for i, (date, value) in enumerate(zip(dates, coverage_values)):
            ax.text(date, value + 2, f'{value:.1f}%', 
                   ha='center', fontsize=10, weight='bold')
        
        ax.set_xlabel('日期', fontsize=14, weight='bold')
        ax.set_ylabel('覆蓋率 (%)', fontsize=14, weight='bold')
        ax.set_title(config.title, fontsize=18, weight='bold', pad=20)
        ax.legend(fontsize=12)
        ax.grid(True, alpha=0.3)
        
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        output_path = self.output_dir / config.filename
        plt.savefig(output_path, dpi=config.dpi, bbox_inches='tight')
        plt.close()
        
        return str(output_path)
    
    def generate_risk_heatmap(
        self,
        modules: List[str],
        complexity: List[int],
        coverage: List[float],
        config: Optional[ChartConfig] = None
    ) -> str:
        """生成風險熱圖"""
        if config is None:
            config = ChartConfig(
                title="程式碼風險熱圖",
                filename="risk-heatmap.png",
                figsize=(12, 10)
            )
        
        # 構建矩陣資料
        # 將複雜度和覆蓋率離散化
        complexity_bins = [0, 5, 10, 15, np.inf]
        coverage_bins = [0, 50, 70, 85, 100]
        
        matrix = np.zeros((len(complexity_bins)-1, len(coverage_bins)-1))
        
        for comp, cov in zip(complexity, coverage):
            comp_idx = np.digitize([comp], complexity_bins)[0] - 1
            cov_idx = np.digitize([cov], coverage_bins)[0] - 1
            if 0 <= comp_idx < matrix.shape[0] and 0 <= cov_idx < matrix.shape[1]:
                matrix[comp_idx, cov_idx] += 1
        
        plt.style.use(config.style)
        fig, ax = plt.subplots(figsize=config.figsize)
        
        sns.heatmap(
            matrix, 
            annot=True, 
            fmt='.0f',
            cmap='RdYlGn_r',  # 紅(高風險) → 綠(低風險)
            cbar_kws={'label': '模組數量'},
            xticklabels=['< 50%', '50-70%', '70-85%', '> 85%'],
            yticklabels=['< 5', '5-10', '10-15', '> 15'],
            linewidths=1,
            linecolor='black',
            ax=ax
        )
        
        ax.set_xlabel('測試覆蓋率', fontsize=14, weight='bold')
        ax.set_ylabel('圈複雜度', fontsize=14, weight='bold')
        ax.set_title(config.title, fontsize=18, weight='bold', pad=20)
        
        plt.tight_layout()
        output_path = self.output_dir / config.filename
        plt.savefig(output_path, dpi=config.dpi, bbox_inches='tight')
        plt.close()
        
        return str(output_path)
    
    def generate_quality_dashboard(
        self,
        quality_score: float,
        test_data: Dict[str, int],
        coverage_data: Dict[str, float],
        risk_data: Dict[str, Tuple[int, float]],
        config: Optional[ChartConfig] = None
    ) -> str:
        """生成品質儀表板（多圖組合）"""
        if config is None:
            config = ChartConfig(
                title="品質儀表板",
                filename="quality-dashboard.png",
                figsize=(16, 12)
            )
        
        plt.style.use(config.style)
        fig = plt.figure(figsize=config.figsize)
        
        # 創建 2x2 網格
        gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
        
        # 1. 品質評分卡 (左上)
        ax1 = fig.add_subplot(gs[0, 0])
        self._draw_quality_scorecard(ax1, quality_score)
        
        # 2. 測試結果圓餅圖 (右上)
        ax2 = fig.add_subplot(gs[0, 1])
        self._draw_test_pie(ax2, test_data)
        
        # 3. 覆蓋率長條圖 (左下)
        ax3 = fig.add_subplot(gs[1, 0])
        self._draw_coverage_bars(ax3, coverage_data)
        
        # 4. 風險散點圖 (右下)
        ax4 = fig.add_subplot(gs[1, 1])
        self._draw_risk_scatter(ax4, risk_data)
        
        fig.suptitle(config.title, fontsize=22, weight='bold', y=0.98)
        
        output_path = self.output_dir / config.filename
        plt.savefig(output_path, dpi=config.dpi, bbox_inches='tight')
        plt.close()
        
        return str(output_path)
    
    def _draw_quality_scorecard(self, ax, score: float):
        """繪製品質評分卡"""
        # 繪製儀表盤
        theta = np.linspace(0, np.pi, 100)
        r = np.ones(100)
        
        # 顏色分段
        colors_map = plt.cm.RdYlGn(np.linspace(0, 1, 100))
        
        for i in range(99):
            ax.fill_between(
                theta[i:i+2], 0, r[i:i+2],
                color=colors_map[i], alpha=0.8
            )
        
        # 指針
        angle = np.pi * (1 - score / 100)
        ax.arrow(0, 0, 0.8 * np.cos(angle), 0.8 * np.sin(angle),
                head_width=0.1, head_length=0.1, fc='black', ec='black', lw=3)
        
        # 分數標籤
        ax.text(0, -0.3, f'{score:.0f}', 
               ha='center', va='center', fontsize=48, weight='bold')
        ax.text(0, -0.5, '品質評分', 
               ha='center', va='center', fontsize=16)
        
        ax.set_xlim(-1.2, 1.2)
        ax.set_ylim(-0.7, 1.2)
        ax.axis('off')
        ax.set_title('品質評分', fontsize=14, weight='bold', pad=10)
    
    def _draw_test_pie(self, ax, data: Dict[str, int]):
        """繪製測試結果圓餅圖"""
        sizes = [data.get('passed', 0), data.get('failed', 0), data.get('skipped', 0)]
        labels = ['通過', '失敗', '跳過']
        colors = ['#2ecc71', '#e74c3c', '#f39c12']
        
        ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
              startangle=90, textprops={'fontsize': 11, 'weight': 'bold'})
        ax.set_title('測試結果', fontsize=14, weight='bold', pad=10)
    
    def _draw_coverage_bars(self, ax, data: Dict[str, float]):
        """繪製覆蓋率長條圖"""
        names = list(data.keys())[:5]  # 只顯示前 5 個
        values = [data[name] for name in names]
        colors = ['#2ecc71' if v >= 80 else '#f39c12' if v >= 60 else '#e74c3c' for v in values]
        
        ax.barh(names, values, color=colors, edgecolor='black')
        ax.set_xlabel('覆蓋率 (%)', fontsize=12)
        ax.set_title('模組覆蓋率', fontsize=14, weight='bold', pad=10)
        ax.set_xlim(0, 100)
    
    def _draw_risk_scatter(self, ax, data: Dict[str, Tuple[int, float]]):
        """繪製風險散點圖"""
        complexity = [v[0] for v in data.values()]
        coverage = [v[1] for v in data.values()]
        
        # 顏色編碼: 高複雜度低覆蓋=紅, 低複雜度高覆蓋=綠
        colors = ['#e74c3c' if c > 10 and cov < 70 else '#2ecc71' 
                 for c, cov in zip(complexity, coverage)]
        
        ax.scatter(coverage, complexity, s=100, c=colors, alpha=0.6, edgecolors='black')
        ax.set_xlabel('覆蓋率 (%)', fontsize=12)
        ax.set_ylabel('複雜度', fontsize=12)
        ax.set_title('風險分佈', fontsize=14, weight='bold', pad=10)
        ax.grid(True, alpha=0.3)

# === 使用範例 ===
if __name__ == "__main__":
    engine = VisualizationEngine()
    
    # 1. 測試結果圓餅圖
    engine.generate_test_results_pie(passed=120, failed=3, skipped=2)
    
    # 2. 模組覆蓋率長條圖
    modules = {
        "AuthService": 85.5,
        "PaymentService": 92.3,
        "TradingService": 78.2,
        "NotificationService": 65.1
    }
    engine.generate_coverage_bar(modules)
    
    # 3. 覆蓋率趨勢
    dates = ["2026-02-01", "2026-02-02", "2026-02-03", "2026-02-04", "2026-02-05"]
    values = [65.2, 68.5, 72.1, 75.8, 79.3]
    engine.generate_coverage_trend(dates, values)
    
    print("✅ 所有圖表已生成至 tests/reports/charts/")
```

---

## 整合到測試報告

### 自動生成圖表並嵌入 Markdown

```python
def generate_test_report_with_charts(test_data: Dict) -> str:
    """生成帶圖表的測試報告"""
    engine = VisualizationEngine()
    
    # 生成圖表
    pie_chart = engine.generate_test_results_pie(
        passed=test_data["passed"],
        failed=test_data["failed"],
        skipped=test_data["skipped"]
    )
    
    bar_chart = engine.generate_coverage_bar(test_data["module_coverage"])
    
    # Markdown 報告
    report = f"""
# 測試報告

## 1. 測試結果概覽

![測試結果分布]({pie_chart})

總測試案例: {test_data['total']}  
通過率: {test_data['passed'] / test_data['total'] * 100:.1f}%

## 2. 模組覆蓋率

![模組覆蓋率]({bar_chart})
    """
    
    return report
```

---

## JavaScript 實作 (Chart.js)

### 前端報告視覺化

**檔案:** `_bmad/_memory/sentinel-sidecar/scripts/chart-generator.js`

```javascript
// 使用 Chart.js 生成互動式圖表
const Chart = require('chart.js/auto');
const { createCanvas } = require('canvas');
const fs = require('fs');

class ChartGenerator {
  generateTestResultsPie(data, outputPath) {
    const canvas = createCanvas(800, 600);
    const ctx = canvas.getContext('2d');
    
    new Chart(ctx, {
      type: 'pie',
      data: {
        labels: ['通過', '失敗', '跳過'],
        datasets: [{
          data: [data.passed, data.failed, data.skipped],
          backgroundColor: ['#2ecc71', '#e74c3c', '#f39c12']
        }]
      },
      options: {
        plugins: {
          title: {
            display: true,
            text: '測試結果分布',
            font: { size: 18 }
          }
        }
      }
    });
    
    const buffer = canvas.toBuffer('image/png');
    fs.writeFileSync(outputPath, buffer);
  }
}

module.exports = ChartGenerator;
```

---

## 配置文件

### `.sentinel-visualization.yaml`

```yaml
# 視覺化引擎配置
enabled: true

charts:
  test_results_pie:
    enabled: true
    format: "png"
    dpi: 300
  
  module_coverage_bar:
    enabled: true
    show_target_line: true
    target: 80
  
  coverage_trend:
    enabled: true
    show_forecast: true
  
  risk_heatmap:
    enabled: true
    colormap: "RdYlGn_r"
  
  quality_dashboard:
    enabled: true
    components:
      - scorecard
      - test_pie
      - coverage_bar
      - risk_scatter

output:
  directory: "tests/reports/charts"
  embed_in_markdown: true
  generate_html: true

dependencies:
  auto_install: true
  python:
    - matplotlib>=3.7.0
    - seaborn>=0.12.0
    - numpy>=1.24.0
  javascript:
    - chart.js>=4.0.0
    - canvas>=2.11.0
```

---

## 自動安裝依賴

### Python 依賴安裝腳本

```python
#!/usr/bin/env python3
"""安裝視覺化依賴"""
import subprocess
import sys

PACKAGES = ["matplotlib", "seaborn", "numpy"]

for pkg in PACKAGES:
    print(f"📦 安裝 {pkg}...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

print("✅ 視覺化依賴安裝完成")
```

---

## 使用範例

### Sentinel 自動生成圖表

```bash
# 執行完整測試週期
$ sentinel full-cycle

🛡️ [1/8] 測試計畫生成中...
...
🛡️ [8/8] 測試報告產出中...

📊 生成圖表...
  ✅ test-results-pie.png
  ✅ module-coverage-bar.png
  ✅ coverage-trend-line.png
  ✅ risk-heatmap.png
  ✅ quality-dashboard.png

✅ 報告已產出: tests/reports/test-reports/TR-20260206-003.md
📊 圖表目錄: tests/reports/charts/
```

### 報告中嵌入圖表

```markdown
# 測試報告

## 1. 執行摘要

![品質儀表板](../charts/quality-dashboard.png)

## 2. 測試結果

![測試結果分布](../charts/test-results-pie.png)

整體通過率: 97.5%

## 3. 模組覆蓋率

![模組覆蓋率](../charts/module-coverage-bar.png)

## 4. 風險分析

![風險熱圖](../charts/risk-heatmap.png)
```

---

## 總結

✅ **專業圖表** - Matplotlib 高品質 PNG 圖片  
✅ **自動嵌入** - 圖表自動插入 Markdown 報告  
✅ **多種類型** - 圓餅圖、長條圖、折線圖、熱圖、儀表板  
✅ **自動安裝** - 依賴自動安裝，零配置使用  
✅ **高解析度** - DPI 300，適合印刷與簡報

**Sentinel 報告現在擁有專業級視覺化！** 📊🎨
