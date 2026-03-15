"""
评测报告生成器
生成 Markdown 格式的详细评测报告

两层评估模型：
- 候选集质量（搜索机制本身）：candidate_recall, noise_ratio
- 最终选择质量（模拟 LLM 从候选集选择）：selection_precision, selection_recall, selection_f1
"""

import json
from datetime import datetime
from evaluation.metrics import StrategyMetrics, CaseMetrics


def generate_report(all_metrics: list[StrategyMetrics], output_path: str = "evaluation_report.md"):
    """生成完整的评测报告"""
    lines = []

    lines.append("# 飞书 OpenAPI MCP 工具搜索方案评测报告\n")
    lines.append(f"> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    lines.append(f"> 评测用例数: {all_metrics[0].total_cases if all_metrics else 0}\n")

    # 1. 总览表 - 候选集质量
    lines.append("## 一、候选集质量（搜索机制评估）\n")
    lines.append("> help/schema 返回完整产品线目录，目录大小不是噪声，是设计意图。\n")
    lines.append("| 方案 | 候选召回率 | 候选集大小 | 噪声率/目录大小 | 初始Token | 平均Token/次 | 总Token | 平均搜索轮次 |")
    lines.append("|------|----------|----------|--------------|----------|-------------|---------|------------|")
    for m in all_metrics:
        if m.strategy_name == "help_schema":
            noise_col = f"目录 {m.avg_candidate_size:.0f} 个"
        else:
            noise_col = f"{m.avg_noise_ratio:.1%}"
        lines.append(
            f"| {m.strategy_name_cn} "
            f"| {m.avg_candidate_recall:.1%} "
            f"| {m.avg_candidate_size:.1f} "
            f"| {noise_col} "
            f"| {m.initial_token_cost:,} "
            f"| {m.avg_token_cost:,.0f} "
            f"| {m.total_token_cost:,} "
            f"| {m.avg_search_rounds:.1f} |"
        )

    # 1.5 最终选择质量
    lines.append("\n## 二、最终选择质量（模拟 LLM 从候选集选择）\n")
    lines.append("> 假设 LLM 能从候选集中正确挑选期望工具，但会受噪声影响产生误选。\n")
    lines.append("| 方案 | 选择准确率 | 选择召回率 | 选择F1 |")
    lines.append("|------|----------|----------|--------|")
    for m in all_metrics:
        lines.append(
            f"| {m.strategy_name_cn} "
            f"| {m.avg_selection_precision:.1%} "
            f"| {m.avg_selection_recall:.1%} "
            f"| {m.avg_selection_f1:.1%} |"
        )

    # 2. 按意图类型的细分
    lines.append("\n## 三、按意图类型细分\n")

    intent_labels = {
        "precise": "精确意图",
        "fuzzy": "模糊意图",
        "cross_domain": "跨域意图",
        "chinese": "中文口语意图",
    }

    for intent_key, intent_name in intent_labels.items():
        lines.append(f"### {intent_name}\n")
        lines.append("| 方案 | 用例数 | 候选召回率 | 噪声率 | 选择准确率 | 选择F1 | 平均Token |")
        lines.append("|------|-------|----------|--------|----------|--------|----------|")
        for m in all_metrics:
            data = m.by_intent_type.get(intent_key, {})
            if data:
                lines.append(
                    f"| {m.strategy_name_cn} "
                    f"| {data['count']} "
                    f"| {data['avg_candidate_recall']:.1%} "
                    f"| {data['avg_noise_ratio']:.1%} "
                    f"| {data['avg_selection_precision']:.1%} "
                    f"| {data['avg_selection_f1']:.1%} "
                    f"| {data['avg_token_cost']:,.0f} |"
                )
            else:
                lines.append(f"| {m.strategy_name_cn} | 0 | - | - | - | - | - |")

    # 3. 按难度细分
    lines.append("\n## 四、按难度细分\n")
    diff_labels = {"easy": "简单", "normal": "中等", "hard": "困难"}

    for diff_key, diff_name in diff_labels.items():
        lines.append(f"### {diff_name}\n")
        lines.append("| 方案 | 用例数 | 候选召回率 | 噪声率 | 选择准确率 | 选择F1 |")
        lines.append("|------|-------|----------|--------|----------|--------|")
        for m in all_metrics:
            data = m.by_difficulty.get(diff_key, {})
            if data:
                lines.append(
                    f"| {m.strategy_name_cn} "
                    f"| {data['count']} "
                    f"| {data['avg_candidate_recall']:.1%} "
                    f"| {data['avg_noise_ratio']:.1%} "
                    f"| {data['avg_selection_precision']:.1%} "
                    f"| {data['avg_selection_f1']:.1%} |"
                )

    # 4. Token 消耗分析
    lines.append("\n## 五、Token 消耗对比\n")
    lines.append("| 方案 | 初始注入 | 搜索结果(平均) | 总计(平均) | 评价 |")
    lines.append("|------|---------|---------------|----------|------|")
    for m in all_metrics:
        avg_result_tokens = m.avg_token_cost - m.initial_token_cost
        if m.avg_token_cost < 1000:
            rating = "低"
        elif m.avg_token_cost < 3000:
            rating = "中"
        else:
            rating = "高"
        lines.append(
            f"| {m.strategy_name_cn} "
            f"| ~{m.initial_token_cost:,} "
            f"| ~{max(0, avg_result_tokens):,.0f} "
            f"| ~{m.avg_token_cost:,.0f} "
            f"| {rating} |"
        )

    # 5. 失败模式分析
    lines.append("\n## 六、失败模式分析\n")
    for m in all_metrics:
        if m.failure_modes:
            lines.append(f"### {m.strategy_name_cn}\n")
            lines.append("| 失败模式 | 次数 | 占比 |")
            lines.append("|---------|------|------|")
            for mode, count in sorted(m.failure_modes.items(), key=lambda x: x[1], reverse=True):
                pct = count / m.total_cases
                mode_desc = {
                    "no_keywords_extracted": "无法提取关键词",
                    "path_naming_mismatch": "路径命名不匹配（静默失败）",
                    "product_not_in_catalog": "产品线不在目录中",
                    "no_matching_commands": "无匹配命令",
                    "no_semantic_match": "无语义匹配",
                    "low_confidence_match": "低置信度匹配",
                    "navigation_path_mismatch": "导航路径不匹配",
                }.get(mode, mode)
                lines.append(f"| {mode_desc} | {count} | {pct:.1%} |")

    # 6. 召回可靠性对比（核心表格）
    lines.append("\n## 七、召回可靠性 · 失败模式对比\n")
    lines.append("| 方案 | 失败表现 | LLM可感知性 | 失败次数 |")
    lines.append("|------|---------|------------|---------|")

    failure_desc = {
        "code_mode": ("返回空数组", "静默，LLM无感知"),
        "help_schema": ("返回候选列表或明确提示", "显式，LLM知道没找到"),
        "embedding": ("返回相关性低的工具", "半静默，有结果但可能是错的"),
        "tree_navigation": ("走错分支后找不到", "半静默"),
    }
    for m in all_metrics:
        desc = failure_desc.get(m.strategy_name, ("未知", "未知"))
        fail_count = sum(m.failure_modes.values()) if m.failure_modes else 0
        lines.append(
            f"| {m.strategy_name_cn} "
            f"| {desc[0]} "
            f"| {desc[1]} "
            f"| {fail_count}/{m.total_cases} |"
        )

    # 7. 详细用例结果（选取典型 case）
    lines.append("\n## 八、典型用例详细结果\n")

    for m in all_metrics:
        lines.append(f"### {m.strategy_name_cn}\n")

        sorted_cases = sorted(m.case_metrics, key=lambda c: c.candidate_recall)
        worst_cases = [c for c in sorted_cases if c.candidate_recall < 1.0][:3]
        best_cases = [c for c in sorted_cases if c.candidate_recall == 1.0][:3]

        if best_cases:
            lines.append("**命中案例:**\n")
            for c in best_cases:
                lines.append(f"- `{c.query}` -> {', '.join(c.hit_tools)}")

        if worst_cases:
            lines.append("\n**未命中案例:**\n")
            for c in worst_cases:
                lines.append(
                    f"- `{c.query}` "
                    f"(期望: {', '.join(c.expected_tools)}, "
                    f"返回: {', '.join(c.candidate_tools[:3]) or '无'}, "
                    f"漏掉: {', '.join(c.missed_tools)})"
                )
        lines.append("")

    # 8. 结论
    lines.append("\n## 九、评测结论\n")
    lines.append(_generate_conclusion(all_metrics))

    # 9. 选型建议
    lines.append("\n## 十、选型建议\n")
    lines.append(_generate_recommendations(all_metrics))

    report = "\n".join(lines)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)

    return report


def _generate_conclusion(all_metrics: list[StrategyMetrics]) -> str:
    """生成评测结论"""
    best_recall = max(all_metrics, key=lambda m: m.avg_candidate_recall)
    best_precision = max(all_metrics, key=lambda m: m.avg_selection_precision)
    best_f1 = max(all_metrics, key=lambda m: m.avg_selection_f1)
    lowest_token = min(all_metrics, key=lambda m: m.avg_token_cost)
    lowest_noise = min(all_metrics, key=lambda m: m.avg_noise_ratio)

    # 找中文意图最优
    best_chinese = None
    best_chinese_recall = 0
    for m in all_metrics:
        cn_data = m.by_intent_type.get("chinese", {})
        if cn_data and cn_data.get("avg_candidate_recall", 0) > best_chinese_recall:
            best_chinese_recall = cn_data["avg_candidate_recall"]
            best_chinese = m

    # 找模糊意图最优
    best_fuzzy = None
    best_fuzzy_recall = 0
    for m in all_metrics:
        fz_data = m.by_intent_type.get("fuzzy", {})
        if fz_data and fz_data.get("avg_candidate_recall", 0) > best_fuzzy_recall:
            best_fuzzy_recall = fz_data["avg_candidate_recall"]
            best_fuzzy = m

    lines = []
    lines.append("### 核心发现\n")
    lines.append(f"1. **候选召回率最优**: {best_recall.strategy_name_cn} (Candidate Recall={best_recall.avg_candidate_recall:.1%})")
    lines.append(f"2. **噪声率最低**: {lowest_noise.strategy_name_cn} (Noise Ratio={lowest_noise.avg_noise_ratio:.1%})")
    lines.append(f"3. **选择 F1 最优**: {best_f1.strategy_name_cn} (Selection F1={best_f1.avg_selection_f1:.1%})")
    lines.append(f"4. **选择准确率最优**: {best_precision.strategy_name_cn} (Selection Precision={best_precision.avg_selection_precision:.1%})")
    lines.append(f"5. **Token 最省**: {lowest_token.strategy_name_cn} (平均 {lowest_token.avg_token_cost:,.0f} token/次)")
    if best_chinese:
        lines.append(f"6. **中文意图最优**: {best_chinese.strategy_name_cn} (中文候选召回率={best_chinese_recall:.1%})")
    if best_fuzzy:
        lines.append(f"7. **模糊意图最优**: {best_fuzzy.strategy_name_cn} (模糊候选召回率={best_fuzzy_recall:.1%})")

    lines.append("\n### 关键结论\n")
    lines.append("- **候选召回率是搜索层的核心指标**：候选集没覆盖到，LLM 再强也选不出来。")
    lines.append("- **噪声率影响 LLM 最终选择质量**：候选集越干净，LLM 选错的概率越低、token 浪费越少。")
    lines.append("- **没有一个方案在所有维度上都最优**。通用性和可靠性之间存在根本性张力。")
    lines.append("- **越通用（零维护）的方案**，把「理解 API」的工作越多地甩给了 LLM。")
    lines.append("- **越可靠的方案**，越需要人工提前沉淀领域知识。")
    lines.append("- **Token 消耗**：4 种按需加载方案相比全量下发（500+工具，20万+ token）均有显著节省。")

    return "\n".join(lines)


def _generate_recommendations(all_metrics: list[StrategyMetrics]) -> str:
    """生成选型建议"""
    lines = []
    lines.append("### 场景化推荐\n")
    lines.append("| 场景 | 主方案 | 辅助方案 | 原因 |")
    lines.append("|------|-------|---------|------|")
    lines.append("| 飞书 MCP 内部接口发现 | help/schema | Embedding 兜底 | 领域知识深，可靠性优先 |")
    lines.append("| 对外开放的通用 MCP | Code Mode | Embedding 补充 | 无法要求接入方维护目录 |")
    lines.append("| 多 server 聚合网关 | 树形导航 | Code Mode 兜底 | 跨 server 边界清晰 |")
    lines.append("| 中文模糊意图为主 | Embedding | help/schema 精确查 | 语义理解优先 |")
    lines.append("| API 命名极度混乱 | help/schema | 无 | 其他方案都依赖命名 |")

    lines.append("\n### 飞书 MCP 推荐的分层组合\n")
    lines.append("```")
    lines.append("用户意图")
    lines.append("    |")
    lines.append("01 主路径：help/schema")
    lines.append("   利用飞书领域知识沉淀，保证核心场景召回可靠性")
    lines.append("    | 未命中")
    lines.append("02 兜底：Embedding 语义检索")
    lines.append("   处理目录未覆盖的模糊意图和中文口语表达")
    lines.append("    | 仍未命中")
    lines.append("03 探索：Code Mode")
    lines.append("   覆盖目录还没建全的边缘场景，灵活探索")
    lines.append("    | 记录未命中 case")
    lines.append("04 反馈闭环")
    lines.append("   异步补充到 help 目录，持续提升覆盖率")
    lines.append("```")

    return "\n".join(lines)


def print_summary(all_metrics: list[StrategyMetrics]):
    """打印精简的控制台摘要"""
    print("\n" + "=" * 90)
    print("飞书 OpenAPI MCP 工具搜索方案评测摘要")
    print("=" * 90)

    # 候选集质量
    print(f"\n--- 候选集质量（搜索机制评估）---")
    print(f"  (help/schema 返回完整目录，无噪声率概念)")
    print(f"\n{'方案':<18} {'候选召回率':>10} {'候选集大小':>10} {'噪声率':>10} {'Token/次':>10} {'搜索轮次':>8}")
    print("-" * 82)
    for m in all_metrics:
        if m.strategy_name == "help_schema":
            noise_str = f"{'N/A (目录)':>10}"
        else:
            noise_str = f"{m.avg_noise_ratio:>10.1%}"
        print(
            f"{m.strategy_name_cn:<16} "
            f"{m.avg_candidate_recall:>10.1%} "
            f"{m.avg_candidate_size:>10.1f} "
            f"{noise_str} "
            f"{m.avg_token_cost:>10,.0f} "
            f"{m.avg_search_rounds:>8.1f}"
        )

    # 最终选择质量
    print(f"\n--- 最终选择质量（模拟 LLM 选择）---")
    print(f"\n{'方案':<18} {'选择准确率':>10} {'选择召回率':>10} {'选择F1':>8}")
    print("-" * 56)
    for m in all_metrics:
        print(
            f"{m.strategy_name_cn:<16} "
            f"{m.avg_selection_precision:>10.1%} "
            f"{m.avg_selection_recall:>10.1%} "
            f"{m.avg_selection_f1:>8.1%}"
        )
    print("-" * 56)

    # 按意图类型的候选召回率
    print(f"\n{'意图类型候选召回率':<18}", end="")
    for m in all_metrics:
        print(f" {m.strategy_name_cn:>14}", end="")
    print()
    print("-" * 74)

    intent_labels = {
        "precise": "精确意图",
        "fuzzy": "模糊意图",
        "cross_domain": "跨域意图",
        "chinese": "中文口语",
    }
    for intent_key, intent_name in intent_labels.items():
        print(f"  {intent_name:<16}", end="")
        for m in all_metrics:
            data = m.by_intent_type.get(intent_key, {})
            if data:
                print(f" {data['avg_candidate_recall']:>13.1%}", end="")
            else:
                print(f" {'N/A':>13}", end="")
        print()
    print()
