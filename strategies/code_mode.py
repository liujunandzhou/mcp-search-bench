"""
方案一：Code Mode
LLM 写 JS/Python 代码在 OpenAPI spec 上执行过滤。
服务端暴露 search() 和 execute() 两个元工具，沙箱中预注入 spec 对象。

在评测中，我们模拟 LLM 生成的搜索代码行为：
- 基于 path/tag 关键词过滤
- 模拟 LLM 猜测路径命名的不确定性
"""

import re
from data.tools_registry import get_all_tools, ToolDefinition, CATEGORY_META
from strategies.base import SearchStrategy, SearchResult
from utils.token_counter import count_tool_tokens, count_tokens, estimate_meta_tool_tokens


# Code Mode 暴露的两个元工具定义
CODE_MODE_META_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search",
            "description": "在 OpenAPI spec 上执行搜索代码，返回匹配的 API 端点列表。"
                           "沙箱中可用 spec（完整 OpenAPI spec, $refs 已内联）、"
                           "semanticIndex（意图→路径关键词映射）、specMeta（元数据）。",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "要执行的 JavaScript 过滤代码"
                    }
                },
                "required": ["code"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "execute",
            "description": "执行指定的 API 调用",
            "parameters": {
                "type": "object",
                "properties": {
                    "method": {"type": "string", "description": "HTTP method"},
                    "path": {"type": "string", "description": "API path"},
                    "body": {"type": "object", "description": "Request body"}
                },
                "required": ["method", "path"]
            }
        }
    }
]

# 语义索引：模拟沙箱中预注入的 semanticIndex
SEMANTIC_INDEX = {}
for cat_key, meta in CATEGORY_META.items():
    for kw in meta["keywords"]:
        SEMANTIC_INDEX[kw.lower()] = cat_key


class CodeModeStrategy(SearchStrategy):
    """Code Mode：LLM 写代码在 spec 上过滤"""

    def __init__(self):
        self._all_tools = get_all_tools()
        self._tool_index = {t.tool_id: t for t in self._all_tools}

    @property
    def name(self) -> str:
        return "code_mode"

    @property
    def name_cn(self) -> str:
        return "Code Mode"

    @property
    def description(self) -> str:
        return "LLM 写 JS 代码在 OpenAPI spec 上执行过滤，零维护但依赖 API 命名规范"

    def _extract_keywords(self, query: str) -> list[str]:
        """从查询中提取关键词（模拟 LLM 从意图中提取路径关键词）"""
        keywords = []

        # 先查语义索引（精确匹配）
        for kw, cat in SEMANTIC_INDEX.items():
            if kw in query.lower():
                keywords.append(cat)

        # 口语化表达 → 分类映射（Code Mode 的弱点，需要 LLM 理解）
        colloquial_map = {
            "约个会": "calendar", "开会": "calendar", "会议": "calendar",
            "安排": "calendar", "日程": "calendar", "挂个日程": "calendar",
            "拉个群": "im", "拉群": "im", "聊天": "im", "群": "im",
            "发消息": "im", "通知": "im", "信息": "im", "聊天记录": "im",
            "钉一下": "im", "置顶": "im", "加急": "im", "催": "im",
            "表情": "im", "回应": "im",
            "数据": "bitable", "写进表格": "bitable", "表格": "bitable",
            "请假": "approval", "审批": "approval", "流程": "approval",
            "组织架构": "contact", "联系方式": "contact", "同事": "contact",
            "通讯录": "contact", "新同事": "contact", "入职": "corehr",
            "打卡": "attendance", "考勤": "attendance",
            "知识库": "wiki", "资料": "wiki",
            "文档": "docx", "分享": "drive",
            "词典": "baike", "术语": "baike", "百科": "baike",
            "勋章": "admin",
            "任务": "task", "待办": "task",
            "卡片": "cardkit",
        }
        for pattern, cat in colloquial_map.items():
            if pattern in query:
                if cat not in keywords:
                    keywords.append(cat)

        # 英文关键词直接提取
        en_words = re.findall(r'[a-zA-Z]+', query)
        keywords.extend([w.lower() for w in en_words])

        # 从操作意图提取
        operation_map = {
            "创建": ["create"], "新建": ["create"], "新增": ["create"],
            "发送": ["create"], "发个": ["create"],
            "删除": ["delete"], "移除": ["delete"],
            "获取": ["get"], "查询": ["search", "query"],
            "查看": ["get"], "看看": ["list", "get"], "翻翻": ["list"],
            "搜索": ["search"], "找": ["search", "get"],
            "更新": ["update"], "修改": ["patch"],
            "编辑": ["patch"], "列出": ["list"],
            "批量": ["batch"],
            "添加": ["create"], "加": ["create"],
            "回复": ["reply"], "转发": ["forward"],
            "统计": ["query"], "开通": ["create"],
            "录入": ["create"],
        }
        for cn, en_ops in operation_map.items():
            if cn in query:
                keywords.extend(en_ops)

        return list(set(keywords))

    def _simulate_code_search(self, query: str, top_k: int = 5) -> tuple[list[ToolDefinition], str]:
        """
        模拟 LLM 生成的代码搜索行为。
        使用分层匹配：先匹配分类（product），再匹配操作（operation），
        要求两者都命中才视为有效匹配。
        """
        keywords = self._extract_keywords(query)
        if not keywords:
            return [], "no_keywords_extracted"

        # 区分分类关键词和操作关键词
        category_kws = [kw for kw in keywords if kw in SEMANTIC_INDEX.values() or kw in SEMANTIC_INDEX]
        operation_kws = [kw for kw in keywords if kw not in category_kws]

        matched = []
        for tool in self._all_tools:
            tool_text = f"{tool.tool_id} {tool.path} {tool.description_en}".lower()

            # 分类匹配得分
            cat_score = sum(1 for kw in category_kws if kw in tool_text)
            # 操作匹配得分
            op_score = sum(1 for kw in operation_kws if kw in tool_text)
            # 总分 = 分类权重 * 3 + 操作权重（分类匹配更重要）
            total_score = cat_score * 3 + op_score

            # 要求至少有一个分类关键词命中（如果有分类关键词的话）
            if category_kws and cat_score == 0:
                continue
            if total_score > 0:
                matched.append((tool, total_score))

        # 如果没有分类关键词，降级为全匹配但要求多个关键词命中
        if not matched and not category_kws:
            for tool in self._all_tools:
                tool_text = f"{tool.tool_id} {tool.path} {tool.description_en}".lower()
                score = sum(1 for kw in keywords if kw in tool_text)
                if score >= 2:  # 至少命中 2 个关键词
                    matched.append((tool, score))

        matched.sort(key=lambda x: x[1], reverse=True)

        if not matched:
            return [], "path_naming_mismatch"

        # 动态截断：只保留得分 >= 最高分 50% 的结果
        best_score = matched[0][1]
        threshold = best_score * 0.5
        filtered = [(t, s) for t, s in matched if s >= threshold]

        return [t for t, _ in filtered[:top_k]], ""

    def search(self, query: str, top_k: int = 5) -> SearchResult:
        matched_tools, failure_mode = self._simulate_code_search(query, top_k)

        result_tools = matched_tools
        tool_ids = [t.tool_id for t in result_tools]

        # Token 消耗计算
        meta_tokens = estimate_meta_tool_tokens(CODE_MODE_META_TOOLS)
        # 搜索代码本身的 token（模拟 LLM 生成的代码）
        code_tokens = count_tokens(f"search code for: {query}")
        # 搜索结果 token（返回的 API 摘要列表）
        result_text = "\n".join(
            f"{t.method} {t.path} - {t.description}" for t in result_tools
        )
        result_tokens = count_tokens(result_text)

        return SearchResult(
            tool_ids=tool_ids,
            tool_definitions=result_tools,
            token_cost=meta_tokens + code_tokens + result_tokens,
            search_rounds=1,
            meta_tool_tokens=meta_tokens,
            result_tokens=result_tokens,
            failure_mode=failure_mode,
            details={
                "keywords_extracted": self._extract_keywords(query),
                "total_matched": len(matched_tools),
            }
        )

    def get_initial_token_cost(self) -> int:
        return estimate_meta_tool_tokens(CODE_MODE_META_TOOLS)
