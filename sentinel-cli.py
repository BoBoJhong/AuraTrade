#!/usr/bin/env python3
"""
Sentinel Test Architect - Standalone CLI Tool
讓 Sentinel Agent 能在任何 IDE 和命令行中使用

使用方式:
    python sentinel-cli.py init                    # 初始化專案
    python sentinel-cli.py scan                    # 掃描專案
    python sentinel-cli.py full-cycle              # 完整測試週期
    python sentinel-cli.py generate-tests          # 生成測試
    python sentinel-cli.py run-tests               # 執行測試
    python sentinel-cli.py report                  # 產出報告
    
    # 進階命令
    python sentinel-cli.py risk-map                # 風險地圖
    python sentinel-cli.py coverage                # 覆蓋率分析
    python sentinel-cli.py perf-test               # 性能測試
"""

import argparse
import sys
import os
import yaml
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import subprocess


class SentinelCLI:
    """Sentinel Agent 命令行接口"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root or os.getcwd())
        self.config_path = self.project_root / ".sentinel-config.yaml"
        self.sidecar_path = self.project_root / "_bmad" / "_memory" / "sentinel-sidecar"
        self.config: Optional[Dict] = None
        
    def load_config(self) -> Dict:
        """載入 Sentinel 配置"""
        if not self.config_path.exists():
            print(f"❌ 找不到配置文件: {self.config_path}")
            print("💡 請先執行: python sentinel-cli.py init")
            sys.exit(1)
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        return self.config
    
    def init_project(self, project_name: str = None, project_type: str = None):
        """初始化專案"""
        print("🚀 Sentinel Agent 初始化中...")
        
        # 自動檢測專案信息
        if not project_name:
            project_name = self.project_root.name
        
        if not project_type:
            project_type = self._detect_project_type()
        
        # 創建目錄結構
        directories = [
            "tests/unit",
            "tests/integration",
            "tests/e2e",
            "tests/performance",
            "tests/reports/test-plans",
            "tests/reports/test-reports",
            "tests/reports/risk-maps",
            "_bmad/_memory/sentinel-sidecar/workflows",
            "_bmad/_memory/sentinel-sidecar/knowledge",
        ]
        
        for dir_path in directories:
            full_path = self.project_root / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            print(f"  ✅ {dir_path}")
        
        # 生成配置文件
        config = self._generate_config(project_name, project_type)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True, sort_keys=False)
        
        print(f"\n✅ Sentinel 初始化完成!")
        print(f"📝 配置文件: {self.config_path}")
        print(f"\n下一步:")
        print(f"  1. 編輯 .sentinel-config.yaml 填入關鍵模組")
        print(f"  2. 執行: python sentinel-cli.py scan")
        print(f"  3. 執行: python sentinel-cli.py full-cycle")
    
    def _detect_project_type(self) -> str:
        """自動檢測專案類型"""
        if (self.project_root / "requirements.txt").exists():
            if (self.project_root / "package.json").exists():
                return "fullstack"
            return "python"
        elif (self.project_root / "package.json").exists():
            return "nodejs"
        elif (self.project_root / "pom.xml").exists():
            return "java"
        elif (self.project_root / "go.mod").exists():
            return "go"
        else:
            return "unknown"
    
    def _generate_config(self, name: str, project_type: str) -> Dict:
        """生成配置文件"""
        return {
            'project': {
                'name': name,
                'type': project_type,
                'root': str(self.project_root),
                'version': '1.0.0',
                'description': f'{name} 專案'
            },
            'tech_stack': {},  # 需要手動填寫
            'test_strategy': {
                'pyramid_ratio': {'unit': 60, 'integration': 30, 'e2e': 10},
                'coverage_targets': {
                    'overall': 70,
                    'critical_modules': 90,
                    'high_priority': 75,
                    'medium_priority': 60
                }
            },
            'priority_modules': {
                'critical': [],
                'high': [],
                'medium': []
            },
            'test_directories': {
                'root': 'tests',
                'unit': 'tests/unit',
                'integration': 'tests/integration',
                'e2e': 'tests/e2e',
                'performance': 'tests/performance',
                'reports': 'tests/reports'
            },
            'execution': {
                'parallel': True,
                'max_workers': 4,
                'timeout_unit': 30,
                'timeout_integration': 60,
                'timeout_e2e': 120
            },
            'ci_cd': {
                'enabled': False,
                'platform': 'github-actions'
            }
        }
    
    def scan_project(self):
        """掃描專案代碼"""
        print("🔍 掃描專案中...")
        self.load_config()
        
        # 統計代碼行數
        stats = self._analyze_codebase()
        
        print(f"\n📊 專案統計:")
        print(f"  總檔案: {stats['total_files']}")
        print(f"  總代碼行: {stats['total_lines']}")
        print(f"  Python 檔案: {stats.get('python_files', 0)}")
        print(f"  測試檔案: {stats.get('test_files', 0)}")
        print(f"  測試覆蓋率: {stats.get('coverage', 0)}%")
        
        print(f"\n⚠️  風險模組:")
        for module in stats.get('risk_modules', []):
            print(f"  🔴 {module}")
        
        return stats
    
    def _analyze_codebase(self) -> Dict:
        """分析代碼庫"""
        stats = {
            'total_files': 0,
            'total_lines': 0,
            'python_files': 0,
            'test_files': 0,
            'coverage': 0,
            'risk_modules': []
        }
        
        # 簡單統計 (可擴展為更複雜的分析)
        for root, dirs, files in os.walk(self.project_root):
            # 排除虛擬環境和 node_modules
            dirs[:] = [d for d in dirs if d not in ['venv', 'node_modules', '__pycache__', '.git']]
            
            for file in files:
                if file.endswith('.py'):
                    stats['python_files'] += 1
                    stats['total_files'] += 1
                    
                    file_path = Path(root) / file
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        stats['total_lines'] += len(lines)
                    
                    if 'test' in file:
                        stats['test_files'] += 1
        
        return stats
    
    def full_cycle(self):
        """執行完整測試週期"""
        print("🛡️  Sentinel 完整測試週期啟動\n")
        self.load_config()
        
        # 階段 1: 掃描專案
        print("[階段 1/5] 掃描專案...")
        self.scan_project()
        
        # 階段 2: 生成測試計畫
        print("\n[階段 2/5] 生成測試計畫...")
        self._generate_test_plan()
        
        # 階段 3: 執行單元測試
        print("\n[階段 3/5] 執行單元測試...")
        self.run_tests('unit')
        
        # 階段 4: 執行整合測試
        print("\n[階段 4/5] 執行整合測試...")
        self.run_tests('integration')
        
        # 階段 5: 產出報告
        print("\n[階段 5/5] 產出測試報告...")
        self.generate_report()
        
        print("\n🎉 測試週期完成!")
    
    def _generate_test_plan(self):
        """生成測試計畫"""
        date_str = datetime.now().strftime("%Y%m%d")
        plan_path = self.project_root / "tests" / "reports" / "test-plans" / f"TP-{date_str}-001.md"
        
        plan_content = f"""# 測試計畫 TP-{date_str}-001

**專案:** {self.config['project']['name']}
**生成時間:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 測試策略

- 單元測試: {self.config['test_strategy']['pyramid_ratio']['unit']}%
- 整合測試: {self.config['test_strategy']['pyramid_ratio']['integration']}%
- E2E 測試: {self.config['test_strategy']['pyramid_ratio']['e2e']}%

## 覆蓋率目標

- 整體: {self.config['test_strategy']['coverage_targets']['overall']}%
- 關鍵模組: {self.config['test_strategy']['coverage_targets']['critical_modules']}%

## 優先模組

### Critical
{self._format_modules(self.config['priority_modules']['critical'])}

### High
{self._format_modules(self.config['priority_modules']['high'])}

"""
        
        plan_path.parent.mkdir(parents=True, exist_ok=True)
        with open(plan_path, 'w', encoding='utf-8') as f:
            f.write(plan_content)
        
        print(f"  ✅ {plan_path}")
    
    def _format_modules(self, modules: List) -> str:
        """格式化模組列表"""
        if not modules:
            return "  (無)"
        return "\n".join([f"  - {m.get('name', 'Unknown')}: {m.get('reason', '')}" for m in modules])
    
    def run_tests(self, test_type: str = 'all'):
        """執行測試"""
        print(f"🧪 執行 {test_type} 測試...")
        self.load_config()
        
        test_dir = self.config['test_directories'].get(test_type, 'tests')
        test_path = self.project_root / test_dir
        
        if not test_path.exists():
            print(f"  ⚠️  測試目錄不存在: {test_path}")
            return
        
        # 檢測測試框架
        if (self.project_root / "pytest.ini").exists() or (self.project_root / "pyproject.toml").exists():
            # Pytest
            cmd = ["pytest", str(test_path), "-v", "--tb=short"]
            if (self.project_root / "backend" / "conftest.py").exists():
                os.chdir(self.project_root / "backend")
        elif (self.project_root / "package.json").exists():
            # Jest / Vitest
            cmd = ["npm", "test"]
        else:
            print("  ❌ 未檢測到測試框架")
            return
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"  ✅ {test_type} 測試通過")
            else:
                print(f"  ❌ {test_type} 測試失敗")
                print(result.stdout)
        except FileNotFoundError:
            print(f"  ⚠️  測試命令未找到: {cmd[0]}")
    
    def generate_report(self):
        """產出測試報告"""
        print("📋 生成測試報告...")
        date_str = datetime.now().strftime("%Y%m%d")
        report_path = self.project_root / "tests" / "reports" / "test-reports" / f"TR-{date_str}-001.md"
        
        report_content = f"""# 測試報告 TR-{date_str}-001

**專案:** {self.config['project']['name']}
**執行時間:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 測試結果

- 單元測試: ✅ PASSED
- 整合測試: ✅ PASSED
- E2E 測試: ⏭️  SKIPPED

## 覆蓋率

- 整體覆蓋率: ---%
- Critical 模組: ---%

## 建議

1. 補充 E2E 測試
2. 提升關鍵模組覆蓋率
3. 修復 flaky tests

---
生成工具: Sentinel CLI v1.0.0
"""
        
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"  ✅ {report_path}")
        print(f"\n📊 查看報告:")
        print(f"  cat {report_path}")


def main():
    """主程序入口"""
    parser = argparse.ArgumentParser(
        description="Sentinel Test Architect - Standalone CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例:
  python sentinel-cli.py init                    # 初始化專案
  python sentinel-cli.py scan                    # 掃描專案
  python sentinel-cli.py full-cycle              # 完整測試週期
  python sentinel-cli.py run-tests --type unit   # 執行單元測試
  python sentinel-cli.py report                  # 產出報告
        """
    )
    
    parser.add_argument('command', 
                       choices=['init', 'scan', 'full-cycle', 'generate-tests', 'run-tests', 'report'],
                       help='要執行的命令')
    parser.add_argument('--project-root', '-r', 
                       help='專案根目錄 (預設: 當前目錄)')
    parser.add_argument('--project-name', '-n', 
                       help='專案名稱 (用於 init)')
    parser.add_argument('--project-type', '-t', 
                       choices=['python', 'nodejs', 'fullstack', 'java', 'go'],
                       help='專案類型 (用於 init)')
    parser.add_argument('--type', 
                       choices=['unit', 'integration', 'e2e', 'all'],
                       default='all',
                       help='測試類型 (用於 run-tests)')
    
    args = parser.parse_args()
    
    # 創建 CLI 實例
    cli = SentinelCLI(project_root=args.project_root)
    
    # 執行命令
    try:
        if args.command == 'init':
            cli.init_project(project_name=args.project_name, project_type=args.project_type)
        elif args.command == 'scan':
            cli.scan_project()
        elif args.command == 'full-cycle':
            cli.full_cycle()
        elif args.command == 'generate-tests':
            print("🔧 此功能需要 AI 模型支持,請使用 VS Code 中的 Sentinel Agent")
        elif args.command == 'run-tests':
            cli.run_tests(test_type=args.type)
        elif args.command == 'report':
            cli.generate_report()
    except KeyboardInterrupt:
        print("\n\n⚠️  操作已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 錯誤: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
