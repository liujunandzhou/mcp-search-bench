"""
方案四：树形导航
层级目录，LLM 逐层下钻选择。
两个元工具：get_tools_in_category() 和 execute_tool()

设计原则：每层不超过 7 个选项
"""

import json
from data.tools_registry import (
    get_all_tools, get_tools_by_category, get_tool_by_id,
    ToolDefinition, CATEGORY_META, ALL_TOOL_GROUPS
)
from strategies.base import SearchStrategy, SearchResult
from utils.token_counter import count_tokens, estimate_meta_tool_tokens


# 树形导航暴露的两个元工具
TREE_NAV_META_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_tools_in_category",
            "description": "浏览工具分类目录。传入空字符串获取顶层分类，传入分类路径获取子分类或工具列表。",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "分类路径，如 '' (顶层)、'bitable' (多维表格)、'bitable.record' (记录操作)"
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "execute_tool",
            "description": "执行指定工具",
            "parameters": {
                "type": "object",
                "properties": {
                    "tool_path": {
                        "type": "string",
                        "description": "工具路径，如 'bitable.record.create'"
                    },
                    "arguments": {
                        "type": "object",
                        "description": "工具参数"
                    }
                },
                "required": ["tool_path"]
            }
        }
    }
]


class TreeNode:
    """树形目录节点"""
    def __init__(self, key: str, name: str, description: str = ""):
        self.key = key
        self.name = name
        self.description = description
        self.children: dict[str, 'TreeNode'] = {}
        self.tools: list[ToolDefinition] = []


class TreeNavigationStrategy(SearchStrategy):
    """树形导航：逐层下钻选择"""

    def __init__(self):
        self._all_tools = get_all_tools()
        self._build_tree()

    def _build_tree(self):
        """构建层级树"""
        self._root = TreeNode("", "飞书 OpenAPI", "飞书开放平台所有 API 工具")

        for cat_key, meta in CATEGORY_META.items():
            tools = ALL_TOOL_GROUPS.get(cat_key, [])
            if not tools:
                continue

            # 一级节点：产品线
            cat_node = TreeNode(cat_key, meta["name"], meta["description"])
            self._root.children[cat_key] = cat_node

            # 二级节点：按 sub_category 分组
            sub_groups: dict[str, list[ToolDefinition]] = {}
            for tool in tools:
                sub_key = tool.sub_category or "other"
                if sub_key not in sub_groups:
                    sub_groups[sub_key] = []
                sub_groups[sub_key].append(tool)

            for sub_key, sub_tools in sub_groups.items():
                sub_name = sub_key
                # 为子分类生成友好名称
                sub_desc_map = {
                    "chat": "群聊管理", "message": "消息操作", "chatMembers": "群成员",
                    "messageReaction": "消息表情", "chatAnnouncement": "群公告",
                    "pin": "消息置顶", "chatTab": "群标签页",
                    "app": "应用/表格", "appTable": "数据表", "appTableField": "字段",
                    "appTableRecord": "记录", "appTableView": "视图",
                    "appTableForm": "表单", "appTableFormField": "表单字段",
                    "appDashboard": "仪表盘", "appRole": "角色",
                    "appRoleMember": "角色成员", "appWorkflow": "自动化",
                    "document": "文档操作", "documentBlock": "文档块",
                    "space": "空间管理", "spaceNode": "节点管理",
                    "spaceMember": "空间成员", "spaceSetting": "空间设置",
                    "calendar": "日历管理", "calendarEvent": "日程",
                    "calendarEventAttendee": "参与人", "calendarAcl": "权限",
                    "freebusy": "忙闲查询", "timeoffEvent": "请假日程",
                    "user": "用户", "department": "部门", "group": "用户组",
                    "groupMember": "用户组成员", "scope": "授权范围",
                    "approval": "审批定义", "instance": "审批实例",
                    "task": "任务操作", "instanceComment": "审批评论",
                    "file": "文件操作", "permission": "权限管理",
                    "spreadsheet": "表格操作", "spreadsheetSheet": "工作表",
                    "employee": "员工", "employment": "雇佣",
                    "person": "个人信息", "jobChange": "异动",
                    "offboarding": "离职", "preHire": "待入职",
                    "leave": "假期", "job": "职务", "jobLevel": "职级",
                    "jobFamily": "序列", "company": "公司", "location": "地点",
                    "costCenter": "成本中心",
                }
                friendly_name = sub_desc_map.get(sub_key, sub_key)

                sub_node = TreeNode(
                    f"{cat_key}.{sub_key}",
                    friendly_name,
                    f"{meta['name']} - {friendly_name}"
                )
                sub_node.tools = sub_tools
                cat_node.children[sub_key] = sub_node

        # 构建关键词到分类的映射
        self._keyword_to_category = {}
        for cat_key, meta in CATEGORY_META.items():
            for kw in meta["keywords"]:
                self._keyword_to_category[kw.lower()] = cat_key

    def _navigate(self, path: str) -> dict:
        """导航到指定路径"""
        if not path:
            return {
                "categories": {
                    k: {"name": v.name, "description": v.description}
                    for k, v in self._root.children.items()
                }
            }

        parts = path.split(".")
        node = self._root

        for part in parts:
            if part in node.children:
                node = node.children[part]
            else:
                return {"error": f"路径 '{path}' 不存在"}

        result = {}
        if node.children:
            result["categories"] = {
                k: {"name": v.name, "description": v.description, "tool_count": len(v.tools)}
                for k, v in node.children.items()
            }
        if node.tools:
            result["tools"] = {
                t.operation or t.tool_id.split(".")[-1]: {
                    "id": t.tool_id,
                    "name": t.description,
                }
                for t in node.tools
            }
        return result

    def _infer_path(self, query: str) -> list[str]:
        """从查询中推断导航路径"""
        paths = []

        # 匹配产品线
        matched_cats = []
        for kw, cat in self._keyword_to_category.items():
            if kw in query.lower():
                if cat not in matched_cats:
                    matched_cats.append(cat)

        if not matched_cats:
            return [""]  # 回到顶层

        # 匹配操作意图 → 推断子分类
        operation_hints = {
            "消息": "message", "聊天": "chat", "群": "chat",
            "记录": "appTableRecord", "字段": "appTableField",
            "表": "appTable", "视图": "appTableView",
            "日程": "calendarEvent", "参与人": "calendarEventAttendee",
            "用户": "user", "部门": "department",
            "审批实例": "instance", "审批任务": "task",
            "文件": "file", "权限": "permission",
            "员工": "employee", "假期": "leave",
        }
        sub_cats = []
        for hint, sub in operation_hints.items():
            if hint in query:
                sub_cats.append(sub)

        for cat in matched_cats:
            paths.append(cat)
            for sub in sub_cats:
                full_path = f"{cat}.{sub}"
                # 验证路径有效
                nav = self._navigate(full_path)
                if "error" not in nav:
                    paths.append(full_path)

        return paths if paths else [""]

    @property
    def name(self) -> str:
        return "tree_navigation"

    @property
    def name_cn(self) -> str:
        return "树形导航"

    @property
    def description(self) -> str:
        return "层级目录，LLM 逐层下钻选择。结构清晰，适合多 server 聚合场景。"

    def search(self, query: str, top_k: int = 10) -> SearchResult:
        total_tokens = 0
        search_rounds = 0
        all_tools = []

        # 推断导航路径
        paths = self._infer_path(query)

        for path in paths:
            nav_result = self._navigate(path)
            search_rounds += 1
            nav_text = json.dumps(nav_result, ensure_ascii=False)
            total_tokens += count_tokens(nav_text)

            # 从导航结果中收集工具
            if "tools" in nav_result:
                for tool_info in nav_result["tools"].values():
                    tool = get_tool_by_id(tool_info["id"])
                    if tool and tool not in all_tools:
                        all_tools.append(tool)

            # 如果只有子分类，继续下钻
            if "categories" in nav_result and "tools" not in nav_result:
                for sub_key in nav_result["categories"]:
                    sub_path = f"{path}.{sub_key}" if path else sub_key
                    sub_nav = self._navigate(sub_path)
                    search_rounds += 1
                    sub_text = json.dumps(sub_nav, ensure_ascii=False)
                    total_tokens += count_tokens(sub_text)

                    if "tools" in sub_nav:
                        for tool_info in sub_nav["tools"].values():
                            tool = get_tool_by_id(tool_info["id"])
                            if tool and tool not in all_tools:
                                all_tools.append(tool)

        # 按操作意图进一步过滤
        op_keywords = {
            "创建": ["create"], "新建": ["create"], "发送": ["create"],
            "删除": ["delete"], "获取": ["get", "list"],
            "查询": ["get", "list", "search", "query"],
            "搜索": ["search"], "更新": ["update", "patch"],
            "修改": ["update", "patch"], "批量": ["batch"],
        }
        active_ops = []
        for cn, en_ops in op_keywords.items():
            if cn in query:
                active_ops.extend(en_ops)

        if active_ops and all_tools:
            filtered = [
                t for t in all_tools
                if any(op in t.operation.lower() or op in t.tool_id.lower()
                       for op in active_ops)
            ]
            if filtered:
                all_tools = filtered

        result_tools = all_tools[:top_k]
        tool_ids = [t.tool_id for t in result_tools]

        meta_tokens = estimate_meta_tool_tokens(TREE_NAV_META_TOOLS)
        failure_mode = ""
        if not result_tools:
            failure_mode = "navigation_path_mismatch"

        return SearchResult(
            tool_ids=tool_ids,
            tool_definitions=result_tools,
            token_cost=meta_tokens + total_tokens,
            search_rounds=search_rounds,
            meta_tool_tokens=meta_tokens,
            result_tokens=total_tokens,
            failure_mode=failure_mode,
            details={
                "paths_explored": paths,
                "total_navigation_rounds": search_rounds,
            }
        )

    def get_initial_token_cost(self) -> int:
        return estimate_meta_tool_tokens(TREE_NAV_META_TOOLS)
