# 飞书 OpenAPI MCP 工具搜索方案评测

基于飞书 OpenAPI 的 MCP 工具搜索方案评测框架，对比 4 种工具检索策略的召回率、准确率和 Token 消耗。

## 四种方案

1. **全量下发 (Full Tool Injection)** - 将所有工具定义一次性传入 LLM
2. **向量检索 (Vector/Semantic Search)** - 基于语义嵌入的工具检索
3. **关键词匹配 (Keyword Matching)** - 基于关键词的工具检索
4. **分类路由 (Category Routing)** - 先分类再检索的两阶段方案

## 评测指标

- **召回率 (Recall)**: 期望工具被检索到的比例
- **准确率 (Precision)**: 检索到的工具中期望工具的比例
- **F1 Score**: 召回率和准确率的调和平均
- **Token 消耗**: 工具定义占用的 token 数量

## 使用方式

```bash
pip install -r requirements.txt
python run_evaluation.py
```

## 项目结构

```
├── data/
│   ├── tools_registry.py      # 飞书 OpenAPI 工具注册表
│   └── eval_dataset.py        # 评测数据集
├── strategies/
│   ├── base.py                # 策略基类
│   ├── full_injection.py      # 全量下发
│   ├── vector_search.py       # 向量检索
│   ├── keyword_match.py       # 关键词匹配
│   └── category_routing.py    # 分类路由
├── evaluation/
│   ├── metrics.py             # 评测指标计算
│   └── reporter.py            # 评测报告生成
├── utils/
│   └── token_counter.py       # Token 计数工具
├── run_evaluation.py          # 评测入口
└── requirements.txt
```
