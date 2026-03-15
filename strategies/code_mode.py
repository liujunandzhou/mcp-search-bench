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

        # 先查语义索引
        for kw, cat in SEMANTIC_INDEX.items():
            if kw in query.lower():
                keywords.append(cat)

        # 英文关键词直接提取
        en_words = re.findall(r'[a-zA-Z]+', query)
        keywords.extend([w.lower() for w in en_words])

        # 从操作意图提取
        operation_map = {
            "创建": ["create"],
            "新建": ["create"],
            "新增": ["create"],
            "发送": ["create", "send"],
            "删除": ["delete", "remove"],
            "移除": ["delete", "remove"],
            "获取": ["get", "list", "query"],
            "查询": ["get", "list", "query", "search"],
            "查看": ["get", "list"],
            "搜索": ["search"],
            "更新": ["update", "patch"],
            "修改": ["update", "patch"],
            "编辑": ["update", "patch", "edit"],
            "列出": ["list"],
            "批量": ["batch"],
        }
        for cn, en_ops in operation_map.items():
            if cn in query:
                keywords.extend(en_ops)

        return list(set(keywords))

    def _simulate_code_search(self, query: str) -> tuple[list[ToolDefinition], str]:
        """
        模拟 LLM 生成的代码搜索行为。
        返回 (匹配工具列表, 失败模式描述)
        """
        keywords = self._extract_keywords(query)
        if not keywords:
            return [], "no_keywords_extracted"

        # 模拟代码过滤：基于 path 和 tool_id 关键词匹配
        matched = []
        for tool in self._all_tools:
            tool_text = f"{tool.tool_id} {tool.path} {tool.description_en}".lower()
            # 检查是否匹配任何关键词
            match_score = sum(1 for kw in keywords if kw in tool_text)
            if match_score > 0:
                matched.append((tool, match_score))

        # 按匹配度排序
        matched.sort(key=lambda x: x[1], reverse=True)

        if not matched:
            return [], "path_naming_mismatch"

        return [t for t, _ in matched], ""

    def search(self, query: str, top_k: int = 10) -> SearchResult:
        matched_tools, failure_mode = self._simulate_code_search(query)

        # 截取 top_k
        result_tools = matched_tools[:top_k]
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
