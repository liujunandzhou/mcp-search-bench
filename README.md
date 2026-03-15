# 飞书 OpenAPI MCP 工具搜索方案评测

基于飞书 OpenAPI 的 MCP 工具搜索方案评测框架，对比 4 种工具发现策略的召回率、准确率和 Token 消耗。

## 四种方案

| 方案 | 核心思路 | 匹配方式 |
|------|---------|---------|
| **Code Mode** | LLM 写 JS 代码在 OpenAPI spec 上过滤 | LLM 生成的代码逻辑 |
| **help/schema** | 两阶段：先语义目录，再精确查定义 | 确定性 id 查找 |
| **Embedding** | 工具描述向量化，相似度召回 | 向量余弦相似度 |
| **树形导航** | 层级目录，LLM 逐层下钻选择 | LLM 逐层决策 |

## 评测指标

- **召回率 (Recall)**: 期望工具被检索到的比例
- **准确率 (Precision)**: 检索到的工具中期望工具的比例
- **F1 Score**: 召回率和准确率的调和平均
- **Token 消耗**: 搜索过程占用的 token 数量

## 使用方式

```bash
pip install -r requirements.txt
python run_evaluation.py
```

运行后会输出控制台摘要，并生成 `evaluation_report.md` 详细报告。

## 项目结构

```
├── data/
│   ├── tools_registry.py      # 飞书 OpenAPI 工具注册表 (292 个工具，20 个分类)
│   └── eval_dataset.py        # 评测数据集 (35 个用例，4 种意图类型)
├── strategies/
│   ├── base.py                # 策略基类
│   ├── code_mode.py           # Code Mode: LLM 写代码过滤 spec
│   ├── help_schema.py         # help/schema: 两阶段确定性查询
│   ├── embedding_search.py    # Embedding: 向量语义检索
│   └── tree_navigation.py     # 树形导航: 层级目录下钻
├── evaluation/
│   ├── metrics.py             # 评测指标计算 (Recall/Precision/F1)
│   └── reporter.py            # Markdown 评测报告生成器
├── utils/
│   └── token_counter.py       # Token 计数工具
├── run_evaluation.py          # 评测入口
├── evaluation_report.md       # 生成的评测报告
└── requirements.txt
```

## 评测数据集

35 个评测用例，覆盖 4 种意图类型 × 3 种难度：

| 意图类型 | 用例数 | 说明 |
|---------|--------|------|
| 精确意图 | 10 | 明确指定操作和对象 |
| 模糊意图 | 10 | 自然语言描述，无技术术语 |
| 跨域意图 | 5 | 涉及多个产品线 |
| 中文口语 | 10 | 中文惯用表达 |

## 评测结论速览

详见 `evaluation_report.md`，核心发现：

- **没有一个方案在所有维度上都最优**
- **Embedding** 在召回率和中文模糊意图上表现最好
- **help/schema** 在准确率和可靠性上领先（唯一不会静默失败的方案）
- **Code Mode** Token 消耗低且零维护，但依赖 API 命名规范
- **树形导航** 结构清晰，适合多 server 聚合，但导航轮次多
