"""
方案二：help/schema
两阶段确定性查询协议，类比 CLI 的 --help 机制：
  1. search(type="help", target="多维表格") → 返回完整产品线命令目录
  2. search(type="schema", target="bitable.record.create") → 返回完整定义

核心设计：
- help 返回完整目录，不做精排（精排是 LLM 的事）
- 候选集 = 产品线全部工具 → 召回率取决于产品线识别准确性
- 永不静默失败：找不到时给候选列表
"""

import re
import json
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
        返回完整的产品线命令目录（不做过滤）。
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
    """
    help/schema 两阶段确定性查询。

    评测逻辑：
    - 候选集 = help 返回的完整产品线目录（所有工具 ID）
    - 这体现了 help/schema 的核心优势：只要产品线对了，候选集就是完整的
    - LLM 从完整目录中选择 1-3 个工具（模拟选择阶段）
    """

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

    def _identify_product_lines(self, query: str) -> list[str]:
        """
        识别查询对应的产品线。
        这是 help/schema 唯一需要做的"搜索"——找到正确的产品线。
        返回产品线关键词列表。
        """
        targets = []

        # 口语化 → 产品线映射
        colloquial_product_map = {
            "约个会": "日历", "开会": "日历", "会议": "日历",
            "安排": "日历", "挂个日程": "日历", "日程": "日历",
            "拉个群": "消息", "拉群": "消息", "聊天记录": "消息",
            "钉一下": "消息", "加急": "消息", "催": "消息",
            "表情": "消息", "回应": "消息", "消息": "消息",
            "群聊": "消息", "群": "消息",
            "卡片": "消息",
            "数据": "多维表格", "写进表格": "多维表格",
            "多维表格": "多维表格", "记录": "多维表格",
            "请假": "审批", "流程": "审批", "审批": "审批",
            "组织架构": "通讯录", "联系方式": "通讯录",
            "同事": "通讯录", "新同事": "通讯录", "部门": "通讯录",
            "入职": "人事", "录入HR": "人事",
            "打卡": "考勤", "没打卡": "考勤", "考勤": "考勤",
            "文档": "云文档", "分享": "云空间", "权限": "云空间",
            "术语": "词典", "百科": "词典",
            "勋章": "管理后台",
            "任务": "任务",
            "知识库": "知识库",
        }

        matched_names = set()
        for pattern, product_name in colloquial_product_map.items():
            if pattern in query:
                matched_names.add(product_name)

        # 标准关键词匹配
        if not matched_names:
            for cat_key, meta in CATEGORY_META.items():
                for kw in meta["keywords"]:
                    if kw in query:
                        matched_names.add(kw)
                        break

        # 转换为产品线关键词
        for name in matched_names:
            targets.append(name)

        return targets if targets else [query]

    def search(self, query: str, top_k: int = 5) -> SearchResult:
        total_tokens = 0
        search_rounds = 0

        # 阶段一：识别产品线并获取完整目录
        product_targets = self._identify_product_lines(query)

        all_candidate_ids = []
        help_matched = False

        for target in product_targets:
            help_result = self._catalog.search_help(target)
            search_rounds += 1

            help_text = json.dumps(help_result, ensure_ascii=False, default=str)
            help_tokens = count_tokens(help_text)
            total_tokens += help_tokens

            if help_result.get("matched"):
                help_matched = True
                products = help_result.get("products", [])
                if not products and "product" in help_result:
                    products = [help_result["product"]]
                for product in products:
                    for cmd in product.get("commands", []):
                        if cmd["id"] not in all_candidate_ids:
                            all_candidate_ids.append(cmd["id"])

        # 候选集 = help 返回的完整产品线目录（所有工具）
        # 这是 help/schema 的核心：完整目录作为候选集
        # LLM 会从中选择，我们不做内部过滤

        # 阶段二：模拟 LLM 查看目录后调用 schema（取前几个作为最终结果）
        # 但候选集仍然是完整目录
        result_tools = []
        schema_checked = 0
        for tool_id in all_candidate_ids[:top_k]:
            schema_result = self._schema_index.get_schema(tool_id)
            search_rounds += 1
            schema_checked += 1
            schema_text = json.dumps(
                {"id": tool_id, "found": schema_result.get("found")},
                ensure_ascii=False
            )
            total_tokens += count_tokens(schema_text)
            if schema_result.get("found"):
                result_tools.append(schema_result["tool"])

        meta_tokens = estimate_meta_tool_tokens(HELP_SCHEMA_META_TOOLS)

        # 失败模式
        failure_mode = ""
        if not help_matched:
            failure_mode = "product_not_in_catalog"
        elif not all_candidate_ids:
            failure_mode = "no_matching_commands"

        # 关键：返回的 tool_ids 是完整的产品线目录
        # 这代表 help/schema 的候选集是完整目录
        return SearchResult(
            tool_ids=all_candidate_ids,
            tool_definitions=result_tools,
            token_cost=meta_tokens + total_tokens,
            search_rounds=search_rounds,
            meta_tool_tokens=meta_tokens,
            result_tokens=total_tokens,
            failure_mode=failure_mode,
            details={
                "product_targets": product_targets,
                "help_matched": help_matched,
                "candidate_count": len(all_candidate_ids),
                "schema_checked": schema_checked,
            }
        )

    def get_initial_token_cost(self) -> int:
        return estimate_meta_tool_tokens(HELP_SCHEMA_META_TOOLS)
