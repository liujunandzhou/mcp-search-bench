"""
方案二：help/schema
两阶段确定性查询协议，类比 CLI 的 --help 机制：
  1. search(type="help", target="多维表格") → 返回命令目录
  2. search(type="schema", target="bitable.record.create") → 返回完整定义

核心优势：永远不静默失败，找不到时给候选列表。
"""

import re
from data.tools_registry import (
    get_all_tools, get_tools_by_category, get_tool_by_id,
    ToolDefinition, CATEGORY_META, ALL_TOOL_GROUPS
)
from strategies.base import SearchStrategy, SearchResult
from utils.token_counter import count_tool_tokens, count_tokens, estimate_meta_tool_tokens


# help/schema 暴露的两个元工具
HELP_SCHEMA_META_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search",
            "description": "飞书 API 工具发现。type=help 返回命令目录，type=schema 返回具体接口定义。",
            "parameters": {
                "type": "object",
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": ["help", "schema"],
                        "description": "查询类型：help 获取命令目录，schema 获取接口定义"
                    },
                    "target": {
                        "type": "string",
                        "description": "help 时为产品名/关键词，schema 时为 command id"
                    }
                },
                "required": ["type", "target"]
            }
        }
    }
]


class HelpCatalog:
    """语义目录：产品线 → 命令列表"""

    def __init__(self):
        self._build_catalog()

    def _build_catalog(self):
        """从工具注册表构建语义目录"""
        self.products = {}
        for cat_key, meta in CATEGORY_META.items():
            tools = ALL_TOOL_GROUPS.get(cat_key, [])
            if not tools:
                continue
            commands = []
            for tool in tools:
                commands.append({
                    "id": tool.tool_id,
                    "name": tool.description,
                    "operation": tool.operation,
                })
            self.products[cat_key] = {
                "key": cat_key,
                "name": meta["name"],
                "description": meta["description"],
                "keywords": meta["keywords"],
                "commands": commands,
            }

    def search_help(self, target: str) -> dict:
        """
        搜索产品线目录。
        找不到时返回所有产品线摘要（永不静默失败）。
        """
        target_lower = target.lower()

        # 1. 精确匹配 key
        if target_lower in self.products:
            return {"matched": True, "product": self.products[target_lower]}

        # 2. 关键词匹配
        matched_products = []
        for key, product in self.products.items():
            for kw in product["keywords"]:
                if kw.lower() in target_lower or target_lower in kw.lower():
                    matched_products.append(product)
                    break

        if matched_products:
            return {"matched": True, "products": matched_products}

        # 3. 没找到 → 返回所有产品线摘要
        return {
            "matched": False,
            "message": f'未找到 "{target}"，可用产品线：',
            "available": [
                {
                    "key": p["key"],
                    "name": p["name"],
                    "description": p["description"],
                    "count": len(p["commands"]),
                }
                for p in self.products.values()
            ]
        }


class SchemaIndex:
    """Schema 索引：command id → 工具定义"""

    def __init__(self):
        self._index = {}
        for tool in get_all_tools():
            self._index[tool.tool_id] = tool

    def get_schema(self, command_id: str) -> dict:
        """
        获取命令的完整 schema。
        找不到时返回模糊候选（永不静默失败）。
        """
        if command_id in self._index:
            return {"found": True, "tool": self._index[command_id]}

        # 模糊匹配
        last_part = command_id.split(".")[-1] if "." in command_id else command_id
        candidates = [
            tid for tid in self._index
            if last_part.lower() in tid.lower()
        ][:5]

        return {
            "found": False,
            "error": f'未找到 "{command_id}"',
            "suggestion": f'你是否要找：{", ".join(candidates)}' if candidates else "无候选"
        }


class HelpSchemaStrategy(SearchStrategy):
    """help/schema 两阶段确定性查询"""

    def __init__(self):
        self._catalog = HelpCatalog()
        self._schema_index = SchemaIndex()
        self._all_tools = get_all_tools()

    @property
    def name(self) -> str:
        return "help_schema"

    @property
    def name_cn(self) -> str:
        return "help/schema"

    @property
    def description(self) -> str:
        return "两阶段确定性查询：先语义目录，再精确查定义。永不静默失败。"

    def _extract_intent(self, query: str) -> tuple[str, list[str]]:
        """提取产品线意图和操作意图"""
        product_target = ""
        operations = []

        # 匹配产品线
        for cat_key, meta in CATEGORY_META.items():
            for kw in meta["keywords"]:
                if kw in query:
                    product_target = kw
                    break
            if product_target:
                break

        # 匹配操作
        op_map = {
            "创建": "create", "新建": "create", "新增": "create",
            "发送": "create", "删除": "delete", "获取": "get",
            "查询": "search", "查看": "get", "搜索": "search",
            "更新": "update", "修改": "update", "编辑": "patch",
            "列出": "list", "批量": "batch",
            "回复": "reply", "转发": "forward", "撤回": "delete",
        }
        for cn, en in op_map.items():
            if cn in query:
                operations.append(en)

        return product_target, operations

    def search(self, query: str, top_k: int = 10) -> SearchResult:
        total_tokens = 0
        search_rounds = 0

        # 阶段一：help 查询
        product_target, operations = self._extract_intent(query)
        if not product_target:
            product_target = query

        help_result = self._catalog.search_help(product_target)
        search_rounds += 1

        # 计算 help 结果的 token
        import json
        help_text = json.dumps(help_result, ensure_ascii=False, default=str)
        help_tokens = count_tokens(help_text)
        total_tokens += help_tokens

        # 收集候选命令
        candidate_commands = []
        if help_result.get("matched"):
            products = help_result.get("products", [])
            if not products and "product" in help_result:
                products = [help_result["product"]]
            for product in products:
                for cmd in product.get("commands", []):
                    candidate_commands.append(cmd)
        else:
            # 没匹配到产品线 → 返回所有产品线摘要
            # LLM 看到摘要后可以继续选择（但这里模拟单轮）
            pass

        # 按操作过滤
        if operations and candidate_commands:
            filtered = [
                cmd for cmd in candidate_commands
                if any(op in cmd.get("operation", "").lower() or op in cmd["id"].lower()
                       for op in operations)
            ]
            if filtered:
                candidate_commands = filtered

        # 阶段二：schema 查询
        result_tools = []
        for cmd in candidate_commands[:top_k]:
            schema_result = self._schema_index.get_schema(cmd["id"])
            search_rounds += 1
            schema_text = json.dumps(
                {"id": cmd["id"], "found": schema_result.get("found")},
                ensure_ascii=False
            )
            total_tokens += count_tokens(schema_text)

            if schema_result.get("found"):
                result_tools.append(schema_result["tool"])

        tool_ids = [t.tool_id for t in result_tools]
        meta_tokens = estimate_meta_tool_tokens(HELP_SCHEMA_META_TOOLS)

        # 失败模式
        failure_mode = ""
        if not help_result.get("matched"):
            failure_mode = "product_not_in_catalog"
        elif not result_tools:
            failure_mode = "no_matching_commands"

        return SearchResult(
            tool_ids=tool_ids,
            tool_definitions=result_tools,
            token_cost=meta_tokens + total_tokens,
            search_rounds=search_rounds,
            meta_tool_tokens=meta_tokens,
            result_tokens=total_tokens,
            failure_mode=failure_mode,
            details={
                "product_target": product_target,
                "operations": operations,
                "candidates_found": len(candidate_commands),
                "help_matched": help_result.get("matched", False),
            }
        )

    def get_initial_token_cost(self) -> int:
        return estimate_meta_tool_tokens(HELP_SCHEMA_META_TOOLS)
