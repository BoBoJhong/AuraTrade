# AI-Driven Test Generation - AI 驅動的智慧測試生成

## 概述

整合 LLM (Large Language Model) 能力，實現代碼理解、意圖推斷、智慧測試案例生成。

---

## 核心能力

### 1. 代碼意圖理解
```yaml
輸入: 函數源代碼
處理: LLM 分析代碼邏輯與意圖
輸出: 
  - 函數用途描述
  - 關鍵邏輯識別
  - 潛在邊界條件
  - 異常處理路徑
```

### 2. 測試案例生成
```yaml
輸入: 代碼 + 上下文
處理: LLM 生成測試案例
輸出:
  - Happy Path 測試
  - 邊界條件測試
  - 錯誤處理測試
  - 完整測試代碼
```

### 3. 測試代碼審查
```yaml
輸入: 現有測試代碼
處理: LLM 審查測試品質
輸出:
  - 覆蓋缺口識別
  - 測試案例建議
  - 代碼改進建議
```

---

## 支援的 LLM 提供商

### 1. OpenAI (GPT-4)
```yaml
模型: gpt-4-turbo, gpt-4o
API: OpenAI REST API
優勢: 
  - 代碼理解能力強
  - 測試生成品質高
  - 支援多語言
費用: $10-30 / 1M tokens
```

### 2. Anthropic (Claude)
```yaml
模型: claude-3-opus, claude-3-sonnet
API: Anthropic REST API
優勢:
  - 上下文窗口大 (200K)
  - 安全性高
  - 代碼生成準確
費用: $15-75 / 1M tokens
```

### 3. Google (Gemini)
```yaml
模型: gemini-1.5-pro
API: Google AI Studio API
優勢:
  - 免費額度大
  - 多模態支援
  - 整合 Google Cloud
費用: $3.5-10.5 / 1M tokens
```

### 4. 本地部署 (Ollama)
```yaml
模型: codellama, deepseek-coder
API: Local HTTP API
優勢:
  - 完全免費
  - 資料隱私
  - 離線可用
費用: 免費 (需 GPU)
```

---

## 架構設計

### 模組結構

```
_bmad/_memory/sentinel-sidecar/ai-engine/
  llm_client.py               # LLM 客戶端基礎類
  providers/
    openai_provider.py        # OpenAI 整合
    anthropic_provider.py     # Anthropic 整合
    gemini_provider.py        # Gemini 整合
    ollama_provider.py        # Ollama 本地整合
  prompts/
    test_generation.txt       # 測試生成 Prompt 範本
    code_review.txt           # 代碼審查 Prompt 範本
    intent_analysis.txt       # 意圖分析 Prompt 範本
  test_generator.py           # AI 測試生成器
```

---

## 實作：LLM 客戶端基礎類

### LLMClient

**檔案:** `llm_client.py`

```python
#!/usr/bin/env python3
"""
LLM 客戶端基礎類
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class LLMConfig:
    """LLM 配置"""
    provider: str  # openai / anthropic / gemini / ollama
    model: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.2
    max_tokens: int = 4000

@dataclass
class LLMResponse:
    """LLM 回應"""
    content: str
    model: str
    usage: Dict[str, int]
    finish_reason: str

class LLMClient(ABC):
    """LLM 客戶端抽象基類"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
    
    @abstractmethod
    def generate(self, prompt: str, system: Optional[str] = None) -> LLMResponse:
        """生成回應"""
        pass
    
    @abstractmethod
    def generate_with_schema(self, prompt: str, schema: Dict) -> Dict:
        """生成結構化回應"""
        pass

class PromptTemplate:
    """Prompt 範本管理"""
    
    @staticmethod
    def load_template(name: str) -> str:
        """載入 Prompt 範本"""
        templates = {
            "test_generation": """
你是一個專業的測試架構師。請為以下函數生成完整的測試案例。

## 目標函數

```{language}
{code}
```

## 要求

1. 生成至少 3 種測試案例：
   - Happy Path (正常流程)
   - Edge Cases (邊界條件)
   - Error Handling (錯誤處理)

2. 測試必須：
   - 完整可執行
   - 包含 Mock 依賴
   - 有清晰的斷言
   - 包含註解說明

3. 測試框架：{framework}

請直接輸出測試代碼，不需要額外解釋。
""",
            
            "intent_analysis": """
你是一個代碼分析專家。請分析以下函數的意圖與邏輯。

## 函數代碼

```{language}
{code}
```

## 分析要求

請提供：
1. 函數用途（一句話描述）
2. 主要邏輯流程（步驟列表）
3. 輸入參數說明
4. 輸出結果說明
5. 潛在風險點
6. 建議測試重點

請以 JSON 格式輸出，格式如下：
```json
{
  "purpose": "函數用途",
  "logic_flow": ["步驟1", "步驟2"],
  "inputs": ["參數1說明", "參數2說明"],
  "outputs": "輸出說明",
  "risks": ["風險1", "風險2"],
  "test_focuses": ["測試重點1", "測試重點2"]
}
```
""",
            
            "code_review": """
你是一個測試代碼審查專家。請審查以下測試代碼的品質。

## 原始代碼

```{language}
{source_code}
```

## 測試代碼

```{language}
{test_code}
```

## 審查要求

請檢查：
1. 測試覆蓋率是否足夠？
2. 是否遺漏關鍵邊界條件？
3. 錯誤處理是否完整測試？
4. 測試代碼品質如何？
5. 改進建議

請以 Markdown 格式輸出報告。
"""
        }
        
        return templates.get(name, "")
    
    @classmethod
    def format_template(cls, template_name: str, **kwargs) -> str:
        """格式化 Prompt 範本"""
        template = cls.load_template(template_name)
        return template.format(**kwargs)
```

---

## 實作：OpenAI Provider

### OpenAIProvider

**檔案:** `providers/openai_provider.py`

```python
#!/usr/bin/env python3
"""
OpenAI Provider
"""

import openai
from typing import Dict, Optional
from ..llm_client import LLMClient, LLMConfig, LLMResponse

class OpenAIProvider(LLMClient):
    """OpenAI LLM Provider"""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        openai.api_key = config.api_key
        if config.base_url:
            openai.api_base = config.base_url
    
    def generate(self, prompt: str, system: Optional[str] = None) -> LLMResponse:
        """生成回應"""
        messages = []
        
        if system:
            messages.append({"role": "system", "content": system})
        
        messages.append({"role": "user", "content": prompt})
        
        response = openai.ChatCompletion.create(
            model=self.config.model,
            messages=messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens
        )
        
        return LLMResponse(
            content=response.choices[0].message.content,
            model=response.model,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            },
            finish_reason=response.choices[0].finish_reason
        )
    
    def generate_with_schema(self, prompt: str, schema: Dict) -> Dict:
        """生成結構化回應 (JSON mode)"""
        response = openai.ChatCompletion.create(
            model=self.config.model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=self.config.temperature
        )
        
        import json
        return json.loads(response.choices[0].message.content)
```

---

## 實作：Gemini Provider

### GeminiProvider

**檔案:** `providers/gemini_provider.py`

```python
#!/usr/bin/env python3
"""
Google Gemini Provider
"""

import google.generativeai as genai
from typing import Dict, Optional
from ..llm_client import LLMClient, LLMConfig, LLMResponse

class GeminiProvider(LLMClient):
    """Google Gemini LLM Provider"""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        genai.configure(api_key=config.api_key)
        self.model = genai.GenerativeModel(config.model)
    
    def generate(self, prompt: str, system: Optional[str] = None) -> LLMResponse:
        """生成回應"""
        full_prompt = prompt
        if system:
            full_prompt = f"{system}\n\n{prompt}"
        
        response = self.model.generate_content(
            full_prompt,
            generation_config={
                "temperature": self.config.temperature,
                "max_output_tokens": self.config.max_tokens
            }
        )
        
        return LLMResponse(
            content=response.text,
            model=self.config.model,
            usage={
                "prompt_tokens": response.usage_metadata.prompt_token_count,
                "completion_tokens": response.usage_metadata.candidates_token_count,
                "total_tokens": response.usage_metadata.total_token_count
            },
            finish_reason="stop"
        )
    
    def generate_with_schema(self, prompt: str, schema: Dict) -> Dict:
        """生成結構化回應"""
        response = self.generate(prompt)
        
        import json
        # 提取 JSON 內容
        content = response.content
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        
        return json.loads(content)
```

---

## 實作：AI 測試生成器

### AITestGenerator

**檔案:** `test_generator.py`

```python
#!/usr/bin/env python3
"""
AI 驅動的測試生成器
"""

import ast
from typing import Dict, List, Optional
from pathlib import Path
from .llm_client import LLMConfig, PromptTemplate
from .providers.openai_provider import OpenAIProvider
from .providers.gemini_provider import GeminiProvider

class AITestGenerator:
    """AI 測試生成器主類"""
    
    def __init__(self, provider: str = "gemini", api_key: Optional[str] = None):
        config = LLMConfig(
            provider=provider,
            model="gpt-4o" if provider == "openai" else "gemini-1.5-pro",
            api_key=api_key,
            temperature=0.2
        )
        
        if provider == "openai":
            self.client = OpenAIProvider(config)
        elif provider == "gemini":
            self.client = GeminiProvider(config)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def generate_tests_for_function(
        self,
        code: str,
        language: str = "python",
        framework: str = "pytest"
    ) -> str:
        """為單個函數生成測試"""
        
        # 構建 Prompt
        prompt = PromptTemplate.format_template(
            "test_generation",
            language=language,
            code=code,
            framework=framework
        )
        
        # 調用 LLM
        response = self.client.generate(
            prompt,
            system="你是一個專業的測試工程師，精通 TDD 與測試最佳實踐。"
        )
        
        # 提取代碼
        test_code = self._extract_code_blocks(response.content)
        
        return test_code
    
    def analyze_function_intent(self, code: str, language: str = "python") -> Dict:
        """分析函數意圖"""
        
        prompt = PromptTemplate.format_template(
            "intent_analysis",
            language=language,
            code=code
        )
        
        # 使用結構化輸出
        return self.client.generate_with_schema(prompt, schema={})
    
    def review_test_code(
        self,
        source_code: str,
        test_code: str,
        language: str = "python"
    ) -> str:
        """審查測試代碼"""
        
        prompt = PromptTemplate.format_template(
            "code_review",
            language=language,
            source_code=source_code,
            test_code=test_code
        )
        
        response = self.client.generate(prompt)
        return response.content
    
    def generate_tests_for_file(
        self,
        filepath: str,
        output_dir: str = "tests/unit"
    ) -> Dict[str, str]:
        """為整個檔案生成測試"""
        
        # 讀取檔案
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 解析 Python 代碼
        tree = ast.parse(content)
        
        generated_tests = {}
        
        # 提取所有函數
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_code = ast.get_source_segment(content, node)
                
                # 生成測試
                test_code = self.generate_tests_for_function(func_code)
                generated_tests[node.name] = test_code
        
        # 組合成完整測試檔案
        full_test = self._combine_tests(generated_tests, filepath)
        
        # 保存
        output_path = Path(output_dir) / f"test_{Path(filepath).name}"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(full_test, encoding='utf-8')
        
        return {
            "output_path": str(output_path),
            "tests_generated": len(generated_tests),
            "functions": list(generated_tests.keys())
        }
    
    def _extract_code_blocks(self, content: str) -> str:
        """提取 Markdown 代碼塊"""
        if "```python" in content:
            blocks = content.split("```python")
            code = blocks[1].split("```")[0].strip()
            return code
        elif "```" in content:
            blocks = content.split("```")
            return blocks[1].strip()
        else:
            return content.strip()
    
    def _combine_tests(self, tests: Dict[str, str], source_file: str) -> str:
        """組合測試代碼"""
        header = f'''"""
測試檔案: {source_file}
自動生成: AI Test Generator
"""

import pytest
from unittest.mock import Mock, patch
from {Path(source_file).stem} import *

'''
        
        test_code = header + "\n\n".join(tests.values())
        return test_code
```

---

## 使用範例

### 1. 基本使用

```python
from ai_test_generator import AITestGenerator

# 初始化生成器
generator = AITestGenerator(
    provider="gemini",
    api_key="YOUR_API_KEY"
)

# 生成單個函數測試
code = """
def calculate_total(price: float, quantity: int, discount: float = 0) -> float:
    \"\"\"計算訂單總額\"\"\"
    if price <= 0 or quantity <= 0:
        raise ValueError("價格與數量必須大於 0")
    
    subtotal = price * quantity
    discount_amount = subtotal * discount
    return subtotal - discount_amount
"""

test_code = generator.generate_tests_for_function(code)
print(test_code)

# 輸出完整的測試代碼，包含：
# - test_calculate_total_valid_input()
# - test_calculate_total_with_discount()
# - test_calculate_total_invalid_price()
# - test_calculate_total_invalid_quantity()
```

### 2. 分析函數意圖

```python
# 分析函數意圖
analysis = generator.analyze_function_intent(code)

print(f"用途: {analysis['purpose']}")
print(f"邏輯流程: {analysis['logic_flow']}")
print(f"測試重點: {analysis['test_focuses']}")

# 輸出:
# 用途: 計算訂單總額，支援折扣
# 邏輯流程: ['輸入驗證', '計算小計', '計算折扣', '返回總額']
# 測試重點: ['零值/負值驗證', '折扣計算正確性', '邊界條件']
```

### 3. 批次生成測試

```python
# 為整個檔案生成測試
result = generator.generate_tests_for_file(
    filepath="apps/services/payment_service.py",
    output_dir="tests/unit/services"
)

print(f"✅ 生成測試檔案: {result['output_path']}")
print(f"✅ 生成測試函數: {result['tests_generated']} 個")
print(f"✅ 覆蓋函數: {', '.join(result['functions'])}")
```

### 4. 測試代碼審查

```python
# 審查現有測試
review = generator.review_test_code(
    source_code=original_code,
    test_code=existing_test
)

print(review)

# 輸出審查報告:
# ## 覆蓋率評估
# - ✅ Happy Path: 已覆蓋
# - ⚠️ 邊界條件: 缺少零值測試
# - ❌ 錯誤處理: 未測試異常情況
#
# ## 改進建議
# 1. 補充 ValueError 測試
# 2. 增加極端值測試 (MAX_INT)
# 3. 測試並發場景
```

---

## 整合到 Sentinel

### 自動觸發 AI 生成

```yaml
Sentinel 工作流整合:

1. 掃描專案階段:
   - 檢測未測試函數
   - 分析複雜度與風險
   - 詢問: "檢測到 15 個未測試函數，是否使用 AI 自動生成測試？[Y/n]"

2. AI 生成階段:
   - 並行生成多個函數測試
   - 自動插入 Mock 依賴
   - 驗證語法正確性

3. 審查階段:
   - 顯示生成的測試代碼
   - 詢問: "查看生成的測試代碼？[Y/n]"
   - 允許手動調整

4. 執行驗證:
   - 執行生成的測試
   - 檢查通過率
   - 報告結果
```

### Sentinel 命令

```bash
# 啟用 AI 測試生成
$ sentinel generate-tests --ai

🛡️ Sentinel - AI 測試生成
=========================
🤖 使用 AI: Gemini 1.5 Pro
📊 掃描檔案: 23 個
🎯 未測試函數: 15 個

生成中...
  ✅ calculate_total() - 4 個測試
  ✅ process_payment() - 5 個測試
  ✅ validate_order() - 3 個測試
  ...

✅ 生成完成！
📁 測試檔案: tests/unit/test_payment_service.py
🧪 總測試案例: 45 個
⏱️ 耗時: 28 秒

執行測試...
  ✅ 42/45 通過 (93.3%)
  ⚠️ 3 個需要調整

報告: tests/reports/ai-generation-20260206-001.md
```

---

## 成本控制

### Token 使用優化

```python
class CostOptimizer:
    """成本優化器"""
    
    @staticmethod
    def estimate_tokens(code: str) -> int:
        """估算 Token 數量"""
        # 約 4 個字元 = 1 token
        return len(code) // 4
    
    @staticmethod
    def should_use_ai(complexity: int, cost_threshold: float) -> bool:
        """判斷是否使用 AI"""
        # 只對高複雜度函數使用 AI
        if complexity < 5:
            return False  # 簡單函數用範本
        
        estimated_cost = complexity * 0.01  # 每個複雜度單位 $0.01
        return estimated_cost < cost_threshold
```

### 免費 Provider 優先

```yaml
Provider 優先級:
  1. Gemini (免費額度大)
  2. Ollama (完全免費，本地)
  3. OpenAI (付費，品質最高)

策略:
  - 簡單函數: 使用範本生成
  - 中等複雜度: 使用 Gemini
  - 高複雜度: 使用 OpenAI GPT-4
```

---

## 配置文件

### `.sentinel-ai.yaml`

```yaml
# AI 測試生成配置

enabled: true

provider: "gemini"  # openai / gemini / anthropic / ollama
api_key: "${GEMINI_API_KEY}"

models:
  openai: "gpt-4o"
  gemini: "gemini-1.5-pro"
  anthropic: "claude-3-sonnet"
  ollama: "codellama:13b"

generation:
  temperature: 0.2
  max_tokens: 4000
  language: "python"
  framework: "pytest"

optimization:
  use_cache: true
  cost_threshold: 1.0  # 每個函數最多 $1
  min_complexity_for_ai: 5
  batch_size: 5

fallback:
  use_template: true  # AI 失敗時使用範本

output:
  auto_save: true
  require_review: true
  format: "pytest"
```

---

## 隱私與安全

### 資料脫敏

```python
class DataSanitizer:
    """資料脫敏器"""
    
    @staticmethod
    def sanitize_code(code: str) -> str:
        """脫敏代碼"""
        # 移除敏感資訊
        code = re.sub(r'API_KEY\s*=\s*["\'][^"\']+["\']', 'API_KEY = "***"', code)
        code = re.sub(r'PASSWORD\s*=\s*["\'][^"\']+["\']', 'PASSWORD = "***"', code)
        code = re.sub(r'SECRET\s*=\s*["\'][^"\']+["\']', 'SECRET = "***"', code)
        return code
```

### 本地部署選項

```bash
# 使用 Ollama 本地部署
$ ollama pull codellama:13b

# Sentinel 配置使用本地模型
provider: "ollama"
base_url: "http://localhost:11434"
```

---

## 總結

✅ **多 Provider 支援** - OpenAI / Gemini / Anthropic / Ollama  
✅ **智慧生成** - 理解代碼意圖，生成高品質測試  
✅ **自動審查** - AI 審查測試覆蓋缺口  
✅ **成本優化** - 免費 Provider 優先，智慧選擇  
✅ **隱私保護** - 資料脫敏，支援本地部署  
✅ **無縫整合** - 融入 Sentinel 工作流

**Sentinel 現在擁有 AI 超能力，測試生成更智慧！** 🤖🚀
