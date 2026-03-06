# AuraTrade 前端測試環境設置腳本 (PowerShell)
# 用途: 自動安裝 Vitest 和相關測試工具

Write-Host ""
Write-Host "🚀 AuraTrade 前端測試環境設置" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""

# 切換到前端目錄
Set-Location frontend

# 1. 安裝 Vitest 核心
Write-Host "📦 安裝 Vitest..." -ForegroundColor Cyan
npm install -D vitest @vitest/ui

# 2. 安裝 React 測試工具
Write-Host "📦 安裝 React Testing Library..." -ForegroundColor Cyan
npm install -D @testing-library/react @testing-library/jest-dom @testing-library/user-event

# 3. 安裝 TypeScript 支持
Write-Host "📦 安裝 TypeScript 類型定義..." -ForegroundColor Cyan
npm install -D @types/node

# 4. 安裝 Happy DOM (輕量級瀏覽器環境)
Write-Host "📦 安裝 Happy DOM..." -ForegroundColor Cyan
npm install -D happy-dom

# 5. 創建 Vitest 配置檔
Write-Host "⚙️  創建 vitest.config.ts..." -ForegroundColor Cyan
$vitestConfig = @'
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'happy-dom',
    setupFiles: ['./tests/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'tests/',
        '**/*.d.ts',
        '**/*.config.*',
        '**/mockData',
        'dist/'
      ]
    }
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  }
})
'@
$vitestConfig | Out-File -FilePath "vitest.config.ts" -Encoding UTF8

# 6. 創建測試目錄和設置檔
Write-Host "⚙️  創建測試目錄..." -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path "tests" | Out-Null

Write-Host "⚙️  創建 tests/setup.ts..." -ForegroundColor Cyan
$setupContent = @'
import { expect, afterEach } from 'vitest'
import { cleanup } from '@testing-library/react'
import '@testing-library/jest-dom'

// 每個測試後清理
afterEach(() => {
  cleanup()
})
'@
$setupContent | Out-File -FilePath "tests\setup.ts" -Encoding UTF8

# 7. 更新 package.json 腳本
Write-Host "⚙️  更新 package.json 測試腳本..." -ForegroundColor Cyan
npm pkg set scripts.test="vitest"
npm pkg set scripts.test:ui="vitest --ui"
npm pkg set scripts.test:coverage="vitest --coverage"
npm pkg set scripts.test:watch="vitest --watch"

Write-Host ""
Write-Host "✅ 前端測試環境設置完成！" -ForegroundColor Green
Write-Host ""
Write-Host "📋 可用命令：" -ForegroundColor Yellow
Write-Host "  npm run test              # 執行測試" -ForegroundColor White
Write-Host "  npm run test:ui           # 測試 UI 介面" -ForegroundColor White
Write-Host "  npm run test:coverage     # 覆蓋率報告" -ForegroundColor White
Write-Host "  npm run test:watch        # 監聽模式" -ForegroundColor White
Write-Host ""
Write-Host "🎯 下一步：" -ForegroundColor Yellow
Write-Host "  1. 執行 Sentinel 初始化: *init" -ForegroundColor White
Write-Host "  2. 掃描專案: *scan-project" -ForegroundColor White
Write-Host "  3. 生成測試: *generate-tests" -ForegroundColor White
Write-Host ""

# 返回專案根目錄
Set-Location ..
