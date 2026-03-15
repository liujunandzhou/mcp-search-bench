"""
评测指标计算
"""

from dataclasses import dataclass, field


@dataclass
class CaseMetrics:
    """单个用例的评测指标"""
    query: str
    intent_type: str
    difficulty: str
    expected_tools: list[str]
    returned_tools: list[str]
    recall: float              # 召回率
    precision: float           # 准确率
    f1: float                  # F1 score
    token_cost: int            # token 消耗
    search_rounds: int         # 搜索轮次
    failure_mode: str          # 失败模式
    hit_tools: list[str] = field(default_factory=list)    # 命中的工具
    missed_tools: list[str] = field(default_factory=list)  # 漏掉的工具


@dataclass
class StrategyMetrics:
    """策略整体评测指标"""
    strategy_name: str
    strategy_name_cn: str
    total_cases: int
    avg_recall: float
    avg_precision: float
    avg_f1: float
    total_token_cost: int
    avg_token_cost: float
    initial_token_cost: int      # 元工具的初始 token 消耗
    avg_search_rounds: float
    # 按意图类型的细分指标
    by_intent_type: dict = field(default_factory=dict)
    # 按难度的细分指标
    by_difficulty: dict = field(default_factory=dict)
    # 失败模式统计
    failure_modes: dict = field(default_factory=dict)
    # 每个用例的详细指标
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
) -> CaseMetrics:
    """计算单个用例的指标"""
    expected_set = set(expected_tools)
    returned_set = set(returned_tools)

    hit = expected_set & returned_set
    missed = expected_set - returned_set

    recall = len(hit) / len(expected_set) if expected_set else 0.0
    precision = len(hit) / len(returned_set) if returned_set else 0.0
    f1 = (2 * recall * precision / (recall + precision)) if (recall + precision) > 0 else 0.0

    return CaseMetrics(
        query=query,
        intent_type=intent_type,
        difficulty=difficulty,
        expected_tools=expected_tools,
        returned_tools=returned_tools,
        recall=recall,
        precision=precision,
        f1=f1,
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
            avg_recall=0, avg_precision=0, avg_f1=0,
            total_token_cost=0, avg_token_cost=0,
            initial_token_cost=initial_token_cost,
            avg_search_rounds=0,
        )

    avg_recall = sum(c.recall for c in case_metrics_list) / n
    avg_precision = sum(c.precision for c in case_metrics_list) / n
    avg_f1 = sum(c.f1 for c in case_metrics_list) / n
    total_tokens = sum(c.token_cost for c in case_metrics_list)
    avg_tokens = total_tokens / n
    avg_rounds = sum(c.search_rounds for c in case_metrics_list) / n

    # 按意图类型聚合
    by_intent = {}
    intent_groups: dict[str, list[CaseMetrics]] = {}
    for cm in case_metrics_list:
        intent_groups.setdefault(cm.intent_type, []).append(cm)
    for intent, cases in intent_groups.items():
        k = len(cases)
        by_intent[intent] = {
            "count": k,
            "avg_recall": sum(c.recall for c in cases) / k,
            "avg_precision": sum(c.precision for c in cases) / k,
            "avg_f1": sum(c.f1 for c in cases) / k,
            "avg_token_cost": sum(c.token_cost for c in cases) / k,
        }

    # 按难度聚合
    by_difficulty = {}
    diff_groups: dict[str, list[CaseMetrics]] = {}
    for cm in case_metrics_list:
        diff_groups.setdefault(cm.difficulty, []).append(cm)
    for diff, cases in diff_groups.items():
        k = len(cases)
        by_difficulty[diff] = {
            "count": k,
            "avg_recall": sum(c.recall for c in cases) / k,
            "avg_precision": sum(c.precision for c in cases) / k,
            "avg_f1": sum(c.f1 for c in cases) / k,
        }

    # 失败模式统计
    failure_modes: dict[str, int] = {}
    for cm in case_metrics_list:
        if cm.failure_mode:
            failure_modes[cm.failure_mode] = failure_modes.get(cm.failure_mode, 0) + 1

    return StrategyMetrics(
        strategy_name=strategy_name,
        strategy_name_cn=strategy_name_cn,
        total_cases=n,
        avg_recall=avg_recall,
        avg_precision=avg_precision,
        avg_f1=avg_f1,
        total_token_cost=total_tokens,
        avg_token_cost=avg_tokens,
        initial_token_cost=initial_token_cost,
        avg_search_rounds=avg_rounds,
        by_intent_type=by_intent,
        by_difficulty=by_difficulty,
        failure_modes=failure_modes,
        case_metrics=case_metrics_list,
    )
