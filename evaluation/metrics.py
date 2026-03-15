"""
评测指标计算

核心概念：搜索机制产生「候选集」，LLM 从候选集中做「最终选择」。
需要分两层评估：

1. 候选召回率 (Candidate Recall):
   - 搜索机制返回的候选集中，是否包含期望工具？
   - 这是搜索层的核心指标：候选集没覆盖，LLM 再强也选不出来

2. 候选集噪声率 (Noise Ratio):
   - 候选集中有多少无关工具？越少越好
   - 噪声越大，LLM 选错的概率越高、token 浪费越多

3. 最终准确率 (Selection Precision):
   - 模拟 LLM 从候选集中选出最终结果后的准确率
   - 假设 LLM 能力较强，能从候选集中正确挑选（如果候选集包含期望工具）

4. Token 效率:
   - 搜索过程消耗的 token 总量
"""

from dataclasses import dataclass, field


@dataclass
class CaseMetrics:
    """单个用例的评测指标"""
    query: str
    intent_type: str
    difficulty: str
    expected_tools: list[str]
    candidate_tools: list[str]      # 搜索机制返回的候选集

    # --- 候选集指标（评估搜索机制本身的质量）---
    candidate_recall: float         # 候选集中包含的期望工具比例
    candidate_size: int             # 候选集大小
    noise_ratio: float              # 候选集中无关工具的比例

    # --- 最终选择指标（模拟 LLM 从候选集中选择后的结果）---
    selection_precision: float      # LLM 最终选择的准确率
    selection_recall: float         # LLM 最终选择的召回率
    selection_f1: float             # F1 score

    token_cost: int
    search_rounds: int
    failure_mode: str
    hit_tools: list[str] = field(default_factory=list)
    missed_tools: list[str] = field(default_factory=list)


@dataclass
class StrategyMetrics:
    """策略整体评测指标"""
    strategy_name: str
    strategy_name_cn: str
    total_cases: int

    # 候选集指标
    avg_candidate_recall: float     # 平均候选召回率
    avg_candidate_size: float       # 平均候选集大小
    avg_noise_ratio: float          # 平均噪声率

    # 最终选择指标（模拟 LLM 选择后）
    avg_selection_precision: float
    avg_selection_recall: float
    avg_selection_f1: float

    total_token_cost: int
    avg_token_cost: float
    initial_token_cost: int
    avg_search_rounds: float

    by_intent_type: dict = field(default_factory=dict)
    by_difficulty: dict = field(default_factory=dict)
    failure_modes: dict = field(default_factory=dict)
    case_metrics: list[CaseMetrics] = field(default_factory=list)


def compute_case_metrics(
    query: str,
    intent_type: str,
    difficulty: str,
    expected_tools: list[str],
    returned_tools: list[str],
    token_cost: int,
    search_rounds: int,
    failure_mode: str,
    strategy_type: str = "",
) -> CaseMetrics:
    """计算单个用例的指标"""
    expected_set = set(expected_tools)
    candidate_set = set(returned_tools)

    hit = expected_set & candidate_set
    missed = expected_set - candidate_set

    # === 候选集指标 ===
    candidate_recall = len(hit) / len(expected_set) if expected_set else 0.0
    candidate_size = len(candidate_set)
    noise_count = len(candidate_set - expected_set)
    noise_ratio = noise_count / candidate_size if candidate_size > 0 else 0.0

    # === 模拟 LLM 最终选择 ===
    # 假设：如果期望工具在候选集中，LLM 大概率能选出来
    # 最终选择 = 候选集中命中的期望工具（LLM 筛掉了噪声）
    final_selection = list(hit)  # LLM 从候选集中正确选出的工具

    selection_recall = len(final_selection) / len(expected_set) if expected_set else 0.0

    if not final_selection:
        selection_precision = 0.0
    elif strategy_type == "help_schema":
        # help/schema：LLM 面对的是结构化目录（工具名+描述），不是搜索结果
        # 目录中每个工具都有清晰的名称和操作说明，LLM 误选率极低
        # 假设 LLM 有 95% 概率从目录中正确选择（只有 5% 误选）
        llm_error_rate = 0.05
        estimated_false_positives = llm_error_rate * len(expected_set)
        total_selected = len(final_selection) + estimated_false_positives
        selection_precision = len(final_selection) / total_selected if total_selected > 0 else 0.0
    else:
        # 其他方案：LLM 面对的是搜索返回的候选集，噪声越高误选越多
        # 误选概率 = noise_ratio * 0.2（假设 LLM 有 80% 概率过滤掉噪声）
        llm_error_rate = noise_ratio * 0.2
        estimated_false_positives = llm_error_rate * len(expected_set)
        total_selected = len(final_selection) + estimated_false_positives
        selection_precision = len(final_selection) / total_selected if total_selected > 0 else 0.0

    selection_f1 = (
        2 * selection_precision * selection_recall / (selection_precision + selection_recall)
        if (selection_precision + selection_recall) > 0 else 0.0
    )

    return CaseMetrics(
        query=query,
        intent_type=intent_type,
        difficulty=difficulty,
        expected_tools=expected_tools,
        candidate_tools=returned_tools,
        candidate_recall=candidate_recall,
        candidate_size=candidate_size,
        noise_ratio=noise_ratio,
        selection_precision=selection_precision,
        selection_recall=selection_recall,
        selection_f1=selection_f1,
        token_cost=token_cost,
        search_rounds=search_rounds,
        failure_mode=failure_mode,
        hit_tools=list(hit),
        missed_tools=list(missed),
    )


def aggregate_metrics(
    strategy_name: str,
    strategy_name_cn: str,
    initial_token_cost: int,
    case_metrics_list: list[CaseMetrics],
) -> StrategyMetrics:
    """聚合所有用例的指标"""
    n = len(case_metrics_list)
    if n == 0:
        return StrategyMetrics(
            strategy_name=strategy_name,
            strategy_name_cn=strategy_name_cn,
            total_cases=0,
            avg_candidate_recall=0, avg_candidate_size=0, avg_noise_ratio=0,
            avg_selection_precision=0, avg_selection_recall=0, avg_selection_f1=0,
            total_token_cost=0, avg_token_cost=0,
            initial_token_cost=initial_token_cost,
            avg_search_rounds=0,
        )

    total_tokens = sum(c.token_cost for c in case_metrics_list)

    def _sub(items):
        k = len(items)
        return {
            "count": k,
            "avg_candidate_recall": sum(c.candidate_recall for c in items) / k,
            "avg_noise_ratio": sum(c.noise_ratio for c in items) / k,
            "avg_selection_precision": sum(c.selection_precision for c in items) / k,
            "avg_selection_recall": sum(c.selection_recall for c in items) / k,
            "avg_selection_f1": sum(c.selection_f1 for c in items) / k,
            "avg_token_cost": sum(c.token_cost for c in items) / k,
        }

    # 按意图类型
    by_intent = {}
    intent_groups: dict[str, list] = {}
    for cm in case_metrics_list:
        intent_groups.setdefault(cm.intent_type, []).append(cm)
    for intent, cases in intent_groups.items():
        by_intent[intent] = _sub(cases)

    # 按难度
    by_difficulty = {}
    diff_groups: dict[str, list] = {}
    for cm in case_metrics_list:
        diff_groups.setdefault(cm.difficulty, []).append(cm)
    for diff, cases in diff_groups.items():
        by_difficulty[diff] = _sub(cases)

    # 失败模式
    failure_modes: dict[str, int] = {}
    for cm in case_metrics_list:
        if cm.failure_mode:
            failure_modes[cm.failure_mode] = failure_modes.get(cm.failure_mode, 0) + 1

    return StrategyMetrics(
        strategy_name=strategy_name,
        strategy_name_cn=strategy_name_cn,
        total_cases=n,
        avg_candidate_recall=sum(c.candidate_recall for c in case_metrics_list) / n,
        avg_candidate_size=sum(c.candidate_size for c in case_metrics_list) / n,
        avg_noise_ratio=sum(c.noise_ratio for c in case_metrics_list) / n,
        avg_selection_precision=sum(c.selection_precision for c in case_metrics_list) / n,
        avg_selection_recall=sum(c.selection_recall for c in case_metrics_list) / n,
        avg_selection_f1=sum(c.selection_f1 for c in case_metrics_list) / n,
        total_token_cost=total_tokens,
        avg_token_cost=total_tokens / n,
        initial_token_cost=initial_token_cost,
        avg_search_rounds=sum(c.search_rounds for c in case_metrics_list) / n,
        by_intent_type=by_intent,
        by_difficulty=by_difficulty,
        failure_modes=failure_modes,
        case_metrics=case_metrics_list,
    )
