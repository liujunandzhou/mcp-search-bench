#!/usr/bin/env python3
"""
飞书 OpenAPI MCP 工具搜索方案评测入口

对比 4 种方案：
1. Code Mode - LLM 写代码在 spec 上过滤
2. help/schema - 两阶段确定性查询
3. Embedding - 向量语义检索
4. 树形导航 - 层级目录逐层下钻

评测指标：召回率、准确率、F1、Token 消耗
"""

import sys
import os

# 确保项目根目录在 path 中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data.tools_registry import get_all_tools
from data.eval_dataset import get_eval_dataset
from strategies.code_mode import CodeModeStrategy
from strategies.help_schema import HelpSchemaStrategy
from strategies.embedding_search import EmbeddingSearchStrategy
from strategies.tree_navigation import TreeNavigationStrategy
from evaluation.metrics import compute_case_metrics, aggregate_metrics
from evaluation.reporter import generate_report, print_summary


def run_strategy_evaluation(strategy, dataset, top_k=10):
    """对单个策略运行所有评测用例"""
    case_metrics_list = []

    for case in dataset:
        result = strategy.search(case.query, top_k=top_k)

        cm = compute_case_metrics(
            query=case.query,
            intent_type=case.intent_type,
            difficulty=case.difficulty,
            expected_tools=case.expected_tools,
            returned_tools=result.tool_ids,
            token_cost=result.token_cost,
            search_rounds=result.search_rounds,
            failure_mode=result.failure_mode,
        )
        case_metrics_list.append(cm)

    return aggregate_metrics(
        strategy_name=strategy.name,
        strategy_name_cn=strategy.name_cn,
        initial_token_cost=strategy.get_initial_token_cost(),
        case_metrics_list=case_metrics_list,
    )


def main():
    print("=" * 60)
    print("飞书 OpenAPI MCP 工具搜索方案评测")
    print("=" * 60)

    # 加载数据
    all_tools = get_all_tools()
    dataset = get_eval_dataset()
    print(f"\n工具注册表: {len(all_tools)} 个工具")
    print(f"评测数据集: {len(dataset)} 个用例")

    # 初始化 4 种策略
    print("\n初始化搜索策略...")
    strategies = [
        CodeModeStrategy(),
        HelpSchemaStrategy(),
        EmbeddingSearchStrategy(),
        TreeNavigationStrategy(),
    ]

    for s in strategies:
        print(f"  ✓ {s.name_cn} ({s.name}) - 初始 token: ~{s.get_initial_token_cost()}")

    # 运行评测
    print("\n开始评测...")
    all_metrics = []

    for strategy in strategies:
        print(f"\n  评测 {strategy.name_cn}...")
        metrics = run_strategy_evaluation(strategy, dataset)
        all_metrics.append(metrics)
        print(f"    召回率: {metrics.avg_recall:.1%}, "
              f"准确率: {metrics.avg_precision:.1%}, "
              f"F1: {metrics.avg_f1:.1%}, "
              f"平均Token: {metrics.avg_token_cost:,.0f}")

    # 打印控制台摘要
    print_summary(all_metrics)

    # 生成详细报告
    report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "evaluation_report.md")
    report = generate_report(all_metrics, report_path)
    print(f"\n详细评测报告已生成: {report_path}")
    print(f"报告长度: {len(report)} 字符")

    return all_metrics


if __name__ == "__main__":
    main()
