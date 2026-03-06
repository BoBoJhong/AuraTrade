#!/bin/bash
#
# Sentinel Agent 快速安裝腳本
# 用於將 Sentinel 部署到任意專案
#
# 使用方式:
#   curl -sSL https://raw.githubusercontent.com/.../install-sentinel.sh | bash
#   或
#   wget -qO- https://raw.githubusercontent.com/.../install-sentinel.sh | bash

set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 日誌函數
log_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 檢查依賴
check_dependencies() {
    log_info "檢查依賴..."
    
    # 檢查 Python
    if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
        log_error "未找到 Python,請先安裝 Python 3.8+"
        exit 1
    fi
    
    # 檢查 pip
    if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
        log_error "未找到 pip,請先安裝 pip"
        exit 1
    fi
    
    log_success "依賴檢查通過"
}

# 安裝 Sentinel CLI
install_sentinel() {
    log_info "安裝 Sentinel CLI..."
    
    # 下載 sentinel-cli.py
    SENTINEL_URL="https://raw.githubusercontent.com/your-org/sentinel-agent/main/sentinel-cli.py"
    
    if command -v curl &> /dev/null; then
        curl -sSL "$SENTINEL_URL" -o sentinel-cli.py
    elif command -v wget &> /dev/null; then
        wget -q "$SENTINEL_URL" -O sentinel-cli.py
    else
        log_error "需要 curl 或 wget 下載文件"
        exit 1
    fi
    
    # 賦予執行權限
    chmod +x sentinel-cli.py
    
    log_success "Sentinel CLI 下載完成"
}

# 安裝 Python 依賴
install_python_deps() {
    log_info "安裝 Python 依賴..."
    
    if command -v pip3 &> /dev/null; then
        pip3 install pyyaml --quiet
    else
        pip install pyyaml --quiet
    fi
    
    log_success "依賴安裝完成"
}

# 初始化專案
init_project() {
    log_info "初始化 Sentinel..."
    
    # 獲取專案名稱
    PROJECT_NAME=$(basename "$(pwd)")
    
    # 檢測專案類型
    if [ -f "requirements.txt" ]; then
        PROJECT_TYPE="python"
    elif [ -f "package.json" ]; then
        PROJECT_TYPE="nodejs"
    elif [ -f "pom.xml" ]; then
        PROJECT_TYPE="java"
    elif [ -f "go.mod" ]; then
        PROJECT_TYPE="go"
    else
        PROJECT_TYPE="unknown"
    fi
    
    # 執行初始化
    if command -v python3 &> /dev/null; then
        python3 sentinel-cli.py init --project-name "$PROJECT_NAME" --project-type "$PROJECT_TYPE"
    else
        python sentinel-cli.py init --project-name "$PROJECT_NAME" --project-type "$PROJECT_TYPE"
    fi
    
    log_success "Sentinel 初始化完成"
}

# 主程序
main() {
    echo ""
    echo "🛡️  Sentinel Agent 安裝程序"
    echo "=============================="
    echo ""
    
    # 檢查是否在專案根目錄
    if [ ! -d ".git" ]; then
        log_warning "建議在 Git 專案根目錄執行此腳本"
        read -p "是否繼續? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    # 執行安裝步驟
    check_dependencies
    install_sentinel
    install_python_deps
    init_project
    
    echo ""
    echo "🎉 Sentinel Agent 安裝成功!"
    echo ""
    echo "下一步:"
    echo "  1. 編輯 .sentinel-config.yaml 填入關鍵模組"
    echo "  2. 執行: python sentinel-cli.py scan"
    echo "  3. 執行: python sentinel-cli.py full-cycle"
    echo ""
    echo "快捷命令 (可選):"
    echo "  echo 'alias sentinel=\"python sentinel-cli.py\"' >> ~/.bashrc"
    echo "  echo 'alias st-fc=\"python sentinel-cli.py full-cycle\"' >> ~/.bashrc"
    echo ""
}

# 執行主程序
main "$@"
