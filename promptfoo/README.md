# 基于 promptfoo 的端到端评测

使用 [promptfoo](https://www.promptfoo.dev/) 接入真实 LLM，端到端评测 4 种工具搜索方案。

## 安装

```bash
npm install -g promptfoo
# 或
npx promptfoo@latest
```

## 运行评测

```bash
cd promptfoo
promptfoo eval
promptfoo view  # 打开可视化面板
```

## 评测原理

每个方案对应一个 prompt 模板，模拟 LLM 在该方案下的工具选择行为：
- **Code Mode**: LLM 收到 search/execute 两个元工具 + OpenAPI spec 结构
- **help/schema**: LLM 收到 help/schema 元工具 + 语义目录
- **Embedding**: LLM 收到语义检索元工具返回的候选列表
- **树形导航**: LLM 收到目录导航元工具 + 层级结构

使用 `tool-call-f1` 和自定义 assertion 评估工具选择准确性。
