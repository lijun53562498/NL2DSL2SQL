# NL2DSL2SQL 智能引擎程序设计文档

## 1. 项目概述

### 1.1 项目背景
随着企业数字化转型加速，数据驱动决策已成为核心竞争力。传统SQL查询要求用户具备专业的数据库知识，这大幅提高了数据访问门槛。同时，直接将自然语言转换为SQL（NL2SQL）面临诸多挑战：语义理解歧义、字段映射错误、多表关联复杂、数据库方言差异等。

为解决上述问题，本项目设计开发一个NL2DSL2SQL智能引擎，采用"自然语言→DSL中间表示→SQL"的两阶段转换架构：
- 第一阶段：利用大语言模型(LLM)的语义理解能力，将自然语言转换为结构化的DSL中间表示
- 第二阶段：将DSL映射为目标数据库的SQL语句，支持多方言适配

该架构通过引入DSL层实现语义标准化，降低LLM直接生成SQL的不确定性，提升转换准确率和稳定性。

### 1.2 项目目标
- 实现自然语言到SQL的高效转换
- 构建可扩展的DSL中间表示层
- 支持多种数据库方言
- 提供可解释的查询转换过程
- 保证转换结果的准确性和安全性

### 1.3 技术选型
- **编程语言**: Python 3.10+
- **LLM框架**: LangChain (ChatOpenAI)
- **LLM模型**: 阿里云通义千问 (qwen3-max)
- **配置管理**: Pydantic + YAML
- **日志管理**: Python logging
- **数据库**: SQLite (测试)、PostgreSQL (生产)
- **测试框架**: pytest

## 2. 系统架构

### 2.1 整体架构
系统采用流水线架构，包含以下层次：

```
┌─────────────────────────────────────────────────────────────────┐ 
│                        用户输入层                                 │ 
│                    自然语言查询 (NL)                              │ 
└────────────────────────┬────────────────────────────────────────┘ 
                          │ 
                          ▼ 
┌─────────────────────────────────────────────────────────────────┐ 
│                      预处理模块                                   │ 
│  • 查询规范化  • 实体识别  • 意图分类  • 上下文理解                   │ 
└────────────────────────┬────────────────────────────────────────┘ 
                          │ 
                          ▼ 
┌─────────────────────────────────────────────────────────────────┐ 
│                   大模型语义理解层                                │ 
│  • 语义解析  • 意图识别  • 实体抽取  • 关系推理                      │ 
│  • Schema过滤  • 表关联合并推理                                    │ 
└────────────────────────┬────────────────────────────────────────┘ 
                          │ 
                          ▼ 
┌─────────────────────────────────────────────────────────────────┐ 
│                      DSL生成模块                                 │ 
│  • 中间表示生成  • 语义验证  • DSL规范化  • 可解释性标注               │ 
└────────────────────────┬────────────────────────────────────────┘ 
                          │ 
                          ▼ 
┌─────────────────────────────────────────────────────────────────┐ 
│                      DSL优化模块                                 │ 
│  • 语义等价检查  • 性能优化  • 安全验证  • DSL标准化                  │ 
└────────────────────────┬────────────────────────────────────────┘ 
                          │ 
                          ▼ 
┌─────────────────────────────────────────────────────────────────┐ 
│                      SQL生成模块                                 │ 
│  • LLM生成SQL  • 语法验证  • 性能优化  • 安全检查                    │ 
│  • 字段映射元数据  • 数据库方言适配                                  │ 
└────────────────────────┬────────────────────────────────────────┘ 
                          │ 
                          ▼ 
┌─────────────────────────────────────────────────────────────────┐ 
│                      后处理模块                                   │ 
│  • 结果验证  • 格式化输出  • 错误处理  • 日志记录                     │ 
└────────────────────────┬────────────────────────────────────────┘ 
                          │ 
                          ▼ 
┌─────────────────────────────────────────────────────────────────┐ 
│                      输出层                                      │ 
│  • SQL语句  • DSL表示  • 解释信息  • 执行结果                       │ 
└─────────────────────────────────────────────────────────────────┘ 
```

### 2.2 模块设计

#### 2.2.1 预处理模块 (Preprocessor)
**功能职责**:
- 查询规范化：统一文本格式，处理特殊字符
- 实体识别：识别表名、字段名、关键词
- 意图分类：判断查询类型（SELECT/INSERT/UPDATE/DELETE）
- 上下文理解：处理多轮对话上下文

**核心类**:
- `QueryNormalizer`: 规范化输入查询
- `EntityRecognizer`: 识别数据库实体
- `IntentClassifier`: 分类查询意图
- `ContextManager`: 管理对话上下文

#### 2.2.2 大模型语义理解层 (LLMUnderstanding)
**功能职责**:
- 语义解析：理解查询深层含义
- 意图识别：精确识别用户查询意图
- 实体抽取：抽取数据库相关实体
- 关系推理：推理表间关系

**核心类**:
- `LLMParser`: 调用大模型进行语义解析
- `IntentExtractor`: 提取查询意图
- `EntityExtractor`: 提取数据库实体
- `RelationReasoner`: 推理实体关系

#### 2.2.3 DSL生成模块 (DSLGenerator)
**功能职责**:
- 中间表示生成：将语义解析结果转为DSL
- 语义验证：验证DSL语义正确性
- DSL规范化：标准化DSL格式
- 可解释性标注：为DSL添加解释信息

**核心类**:
- `DSLBuilder`: 构建DSL中间表示
- `DSLSemanticValidator`: 验证DSL语义
- `DSLC_normalizer`: 规范化DSL
- `DSLAnnotator`: 添加解释标注

#### 2.2.4 DSL优化模块 (DSLOptimizer)
**功能职责**:
- 语义等价检查：检查优化前后语义等价性
- 性能优化：优化DSL结构提升性能
- 安全验证：验证DSL安全性
- DSL标准化：输出标准化DSL

**核心类**:
- `SemanticEquivalenceChecker`: 检查语义等价
- `PerformanceOptimizer`: 优化DSL性能
- `SecurityValidator`: 验证DSL安全
- `DSLStandardizer`: 标准化DSL输出

#### 2.2.5 SQL生成模块 (SQLGenerator)
**功能职责**:
- LLM生成SQL：调用大模型根据DSL生成SQL语句
- 字段映射支持：根据schema中的field_mappings进行字段别名转换
- 数据库方言适配：支持PostgreSQL、MySQL、SQLite等数据库语法
- 语法验证：验证SQL语法正确性
- 性能优化：优化SQL性能
- 安全检查：防止SQL注入、限制只允许SELECT查询

**核心类**:
- `SQLGenerator`: 主生成器，协调LLM生成和规则映射
- `DSLTOSQLMapper`: DSL到SQL规则映射器（备用方案）
- `SQLSyntaxValidator`: SQL语法验证器
- `SQLPerformanceOptimizer`: SQL性能优化器
- `SQLSecurityChecker`: SQL安全检查器

#### 2.2.6 后处理模块 (Postprocessor)
**功能职责**:
- 结果验证：验证最终结果正确性
- 格式化输出：格式化SQL输出
- 错误处理：处理转换过程中的错误
- 日志记录：记录转换过程日志

**核心类**:
- `ResultValidator`: 验证结果正确性
- `OutputFormatter`: 格式化输出
- `ErrorHandler`: 处理错误
- `LogRecorder`: 记录日志

## 3. 数据流设计

### 3.1 主数据流
```
输入 (NL) 
    → 预处理 → LLM语义理解 → DSL生成 → DSL优化 → SQL生成 → 后处理 
    → 输出 (SQL + DSL + 解释)
```

### 3.2 DSL中间表示设计
DSL采用JSON结构定义，支持以下核心元素：

```json
{
    "operation": "SELECT",
    "tables": ["users"],
    "fields": ["id", "name", "email"],
    "conditions": [
        {"field": "age", "operator": ">", "value": 18}
    ],
    "joins": [],
    "group_by": [],
    "order_by": [],
    "limit": null,
    "annotations": {}
}
```

**扩展DSL结构（含完整字段）**:

```json
{
    "operation": "SELECT",
    "tables": ["orders", "users"],
    "fields": ["orders.id", "orders.order_no", "users.username", "users.email"],
    "conditions": [
        {"field": "orders.user_id", "operator": "=", "value": "users.id"},
        {"field": "orders.order_status", "operator": "=", "value": "completed"}
    ],
    "joins": [
        {
            "type": "INNER",
            "from_table": "orders",
            "from_field": "user_id",
            "to_table": "users",
            "to_field": "id"
        }
    ],
    "group_by": ["users.id"],
    "order_by": [{"field": "orders.created_at", "direction": "DESC"}],
    "limit": 300,
    "annotations": {
        "reasoning": "通过orders.user_id与users.id进行关联查询...",
        "join_info": "orders INNER JOIN users ON orders.user_id = users.id"
    }
}
```

## 4. 接口设计

### 4.1 核心接口
```python
class NL2SQLEngine:
    def __init__(self, config: EngineConfig): ...
    
    def process(self, natural_language_query: str, schema: DatabaseSchema) -> QueryResult:
        """主处理接口"""
        pass
    
    def get_intermediate_dsl(self) -> Optional[DSL]:
        """获取中间DSL表示"""
        pass
```

### 4.2 模块接口
各模块遵循统一的接口规范：
- `process(input_data) -> output_data`: 处理数据
- `validate(input_data) -> bool`: 验证输入
- `explain() -> str`: 提供解释信息

### 4.3 DatabaseSchema 数据结构
```python
@dataclass
class DatabaseSchema:
    tables: Dict[str, Dict[str, Any]]  # 表定义
    relations: List[Dict[str, str]]     # 表关系
    field_mappings: Dict[str, Dict[str, str]]  # 字段别名映射
```

**表定义结构**:
```python
{
    'table_name': {
        'description': '表描述',
        'columns': ['id', 'name', ...],
        'column_descriptions': {'id': 'ID', 'name': '名称', ...},
        'column_types': {'id': 'INTEGER', 'name': 'VARCHAR', ...}
    }
}
```

**字段映射示例**:
```python
{
    'orders': {'amount': 'pay_amount', 'total_amount': 'pay_amount'},
    'stock_logs': {'stock': 'change_quantity', 'warehouse': 'warehouse_id'}
}
```

## 5. 配置设计

### 5.1 配置文件结构
```yaml
llm:
  provider: "openai"  # 兼容模式
  model: "qwen3-max"  # 阿里云通义千问
  api_key: "${API_KEY}"
  base_url: "https://dashscope.aliyuncs.com/compatible-mode/v1"

database:
  default_dialect: "sqlite"  # 测试环境默认SQLite
  supported_dialects:
    - "postgresql"
    - "mysql"
    - "sqlite"

security:
  enable_sql_injection_check: true
  max_query_depth: 10
  allowed_operations: ["SELECT"]  # 只允许查询操作

logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

### 5.2 字段映射配置
字段映射可独立配置在schema中或通过YAML加载：

```yaml
field_mappings:
  orders:
    amount: pay_amount
    total_amount: pay_amount
    order_amount: pay_amount
  stock_logs:
    stock: change_quantity
    quantity: change_quantity
    warehouse: warehouse_id
  products:
    cost_price: cost
    profit: "(price - cost)"
```

## 6. 错误处理设计

### 6.1 错误类型
- `PreprocessError`: 预处理阶段错误
- `LLMError`: LLM调用错误
- `DSLError`: DSL生成/验证错误
- `SQLError`: SQL生成/验证错误
- `SecurityError`: 安全检查错误

### 6.2 错误处理策略
- 降级处理：当某模块失败时，尝试降级到简单模式
- 重试机制：对临时性错误进行重试
- 错误传播：将错误信息传递给用户

## 7. 扩展性设计

### 7.1 LLM Provider扩展
通过抽象接口支持多种LLM Provider：
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude)
- 本地模型 (Llama, ChatGLM)

### 7.2 数据库方言扩展
通过方言适配器支持多种数据库：
- PostgreSQL
- MySQL
- SQLite
- SQL Server

### 7.3 自定义DSL扩展
支持用户自定义DSL扩展，实现业务特定查询逻辑

## 8. 测试策略

### 8.1 单元测试
- 各模块独立测试
- Mock外部依赖（LLM API）

### 8.2 集成测试
- 端到端流程测试
- 多种查询场景测试

### 8.3 性能测试
- 并发查询测试
- 大规模数据测试

## 9. 项目目录结构

```
src/
├── nl2sql/
│   ├── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── config.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── engine.py
│   │   └── schema.py
│   ├── modules/
│   │   ├── __init__.py
│   │   ├── preprocessor/
│   │   │   ├── __init__.py
│   │   │   ├── normalizer.py
│   │   │   ├── entity_recognizer.py
│   │   │   ├── intent_classifier.py
│   │   │   └── context_manager.py
│   │   ├── llm_understanding/
│   │   │   ├── __init__.py
│   │   │   ├── parser.py
│   │   │   ├── intent_extractor.py
│   │   │   ├── entity_extractor.py
│   │   │   └── relation_reasoner.py
│   │   ├── dsl_generator/
│   │   │   ├── __init__.py
│   │   │   ├── builder.py
│   │   │   ├── semantic_validator.py
│   │   │   └── annotator.py
│   │   ├── dsl_optimizer/
│   │   │   ├── __init__.py
│   │   │   ├── equivalence_checker.py
│   │   │   ├── performance_optimizer.py
│   │   │   └── security_validator.py
│   │   ├── sql_generator/
│   │   │   ├── __init__.py
│   │   │   ├── mapper.py
│   │   │   ├── syntax_validator.py
│   │   │   └── security_checker.py
│   │   └── postprocessor/
│   │       ├── __init__.py
│   │       ├── result_validator.py
│   │       ├── formatter.py
│   │       └── error_handler.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── dsl.py
│   │   └── query_result.py
│   └── utils/
│       ├── __init__.py
│       ├── logger.py
│       └── exceptions.py
├── tests/
│   ├── __init__.py
│   ├── test_preprocessor.py
│   ├── test_llm_understanding.py
│   ├── test_dsl_generator.py
│   ├── test_dsl_optimizer.py
│   ├── test_sql_generator.py
│   └── test_integration.py
├── config/
│   └── default.yaml
├── requirements.txt
├── init_database.py          # 数据库初始化脚本
├── test_engine.py            # 集成测试脚本
├── nl2sql_test.db           # SQLite测试数据库
└── 程序设计文档.md
```

## 10. 实施计划

### 10.1 阶段一：基础框架搭建 ✅ 已完成
- 项目结构初始化
- 配置管理模块
- 核心引擎框架
- 基础日志和异常处理

### 10.2 阶段二：核心模块实现 ✅ 已完成
- 预处理模块
- LLM语义理解层（含Schema过滤优化）
- DSL生成模块

### 10.3 阶段三：优化和转换模块 ✅ 已完成
- DSL优化模块
- SQL生成模块（LLM生成+字段映射支持）
- 后处理模块
- 数据库集成（SQLite/PostgreSQL）

### 10.4 阶段四：测试和优化 ✅ 已完成
- 单元测试编写
- 集成测试（43个测试用例，100%通过）
- 性能优化（Schema过滤，响应时间降低42%）
- 文档完善
