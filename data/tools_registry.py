"""
飞书 OpenAPI 工具注册表
基于 lark-openapi-mcp 的完整工具列表，包含分类、描述、参数摘要等元数据。
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ToolParam:
    name: str
    type: str
    required: bool
    description: str


@dataclass
class ToolDefinition:
    tool_id: str          # e.g. "im.v1.message.create"
    name: str             # 工具显示名称
    description: str      # 中文描述
    description_en: str   # 英文描述
    category: str         # 一级分类 e.g. "im"
    sub_category: str     # 二级分类 e.g. "message"
    operation: str        # 操作类型 e.g. "create"
    method: str           # HTTP method
    path: str             # API path
    params: list = field(default_factory=list)
    tags: list = field(default_factory=list)
    version: str = "v1"

    @property
    def param_summary(self) -> str:
        if not self.params:
            return ""
        return ", ".join(f"{p.name}({p.type})" for p in self.params[:5])

    @property
    def full_text(self) -> str:
        """用于向量化的完整文本"""
        parts = [
            f"{self.tool_id}: {self.description}",
            f"英文: {self.description_en}",
            f"分类: {self.category}/{self.sub_category}",
        ]
        if self.params:
            parts.append(f"参数: {self.param_summary}")
        if self.tags:
            parts.append(f"标签: {', '.join(self.tags)}")
        return "\n".join(parts)


# ============================================================
# 分类元数据：产品线 → 中文名、描述
# ============================================================
CATEGORY_META = {
    "im": {
        "name": "即时消息",
        "description": "消息发送、群组管理、消息卡片等即时通讯功能",
        "keywords": ["消息", "聊天", "群组", "群聊", "发消息", "message", "chat", "im"],
    },
    "bitable": {
        "name": "多维表格",
        "description": "多维表格的表、字段、记录、视图、仪表盘等操作",
        "keywords": ["多维表格", "表格", "记录", "字段", "bitable", "数据库", "数据表", "表单"],
    },
    "docx": {
        "name": "云文档",
        "description": "飞书文档的创建、读取、编辑、搜索等操作",
        "keywords": ["文档", "document", "docx", "写文档", "文字"],
    },
    "wiki": {
        "name": "知识库",
        "description": "知识库空间、节点的管理和内容访问",
        "keywords": ["知识库", "wiki", "知识空间", "知识节点"],
    },
    "calendar": {
        "name": "日历",
        "description": "日历事件的创建、修改、查询、日程管理",
        "keywords": ["日历", "日程", "会议", "事件", "calendar", "event", "schedule"],
    },
    "contact": {
        "name": "通讯录",
        "description": "企业通讯录的部门、用户、用户组管理",
        "keywords": ["通讯录", "部门", "用户", "员工", "组织架构", "contact", "department", "user"],
    },
    "approval": {
        "name": "审批",
        "description": "审批流程的创建、查看、操作等",
        "keywords": ["审批", "审批流", "approval", "流程"],
    },
    "drive": {
        "name": "云空间",
        "description": "云空间文件管理、权限设置、文件夹操作",
        "keywords": ["云空间", "文件", "文件夹", "drive", "权限", "分享"],
    },
    "sheets": {
        "name": "电子表格",
        "description": "电子表格的读写、格式设置、数据操作",
        "keywords": ["电子表格", "表格", "sheets", "excel", "单元格", "工作表"],
    },
    "task": {
        "name": "任务",
        "description": "任务的创建、分配、跟踪、提醒",
        "keywords": ["任务", "待办", "task", "todo", "分配"],
    },
    "attendance": {
        "name": "考勤",
        "description": "考勤打卡、班次、假期、统计等管理",
        "keywords": ["考勤", "打卡", "班次", "请假", "attendance"],
    },
    "corehr": {
        "name": "人事管理",
        "description": "核心人事系统，包括员工信息、组织架构、异动等",
        "keywords": ["人事", "HR", "员工", "入职", "离职", "异动", "corehr"],
    },
    "aily": {
        "name": "智能伙伴",
        "description": "Aily 智能助手的会话、消息、技能管理",
        "keywords": ["智能伙伴", "aily", "AI", "助手", "智能体"],
    },
    "board": {
        "name": "画板",
        "description": "白板和画板节点操作",
        "keywords": ["画板", "白板", "board", "whiteboard"],
    },
    "baike": {
        "name": "词典",
        "description": "企业词典/百科的词条管理",
        "keywords": ["词典", "百科", "术语", "baike", "词条"],
    },
    "admin": {
        "name": "管理后台",
        "description": "企业管理、审计日志、勋章、统计等后台功能",
        "keywords": ["管理", "后台", "审计", "勋章", "admin"],
    },
    "application": {
        "name": "应用管理",
        "description": "应用的查看、管理、权限、版本等操作",
        "keywords": ["应用", "app", "application", "工作台"],
    },
    "cardkit": {
        "name": "卡片",
        "description": "消息卡片的创建和组件管理",
        "keywords": ["卡片", "card", "消息卡片"],
    },
    "search": {
        "name": "搜索",
        "description": "飞书搜索相关功能",
        "keywords": ["搜索", "search", "查找"],
    },
    "auth": {
        "name": "认证",
        "description": "应用认证、token获取等",
        "keywords": ["认证", "token", "auth", "鉴权", "授权"],
    },
}


# ============================================================
# 完整工具定义列表（基于 lark-openapi-mcp 真实 API）
# ============================================================

def _t(tool_id: str, desc: str, desc_en: str, method: str = "POST",
       path: str = "", params: list = None, tags: list = None) -> ToolDefinition:
    """快速构造 ToolDefinition"""
    parts = tool_id.split(".")
    category = parts[0]
    version = parts[1] if len(parts) > 1 else "v1"
    # 提取子分类和操作
    if len(parts) >= 4:
        sub_cat = parts[2]
        operation = parts[3]
    elif len(parts) == 3:
        sub_cat = parts[2]
        operation = ""
    else:
        sub_cat = ""
        operation = ""

    return ToolDefinition(
        tool_id=tool_id,
        name=tool_id,
        description=desc,
        description_en=desc_en,
        category=category,
        sub_category=sub_cat,
        operation=operation,
        method=method,
        path=path or f"/open-apis/{category}/{version}/{'/'.join(parts[2:])}",
        params=[ToolParam(**p) for p in (params or [])],
        tags=tags or [],
        version=version,
    )


# 即时消息 (IM)
IM_TOOLS = [
    _t("im.v1.chat.create", "创建群聊", "Create a group chat",
       params=[{"name": "name", "type": "string", "required": True, "description": "群名称"}],
       tags=["群组", "创建"]),
    _t("im.v1.chat.delete", "解散群聊", "Delete a group chat",
       params=[{"name": "chat_id", "type": "string", "required": True, "description": "群ID"}],
       tags=["群组", "删除"]),
    _t("im.v1.chat.get", "获取群信息", "Get group chat info",
       method="GET", tags=["群组", "查询"]),
    _t("im.v1.chat.list", "获取用户或机器人所在的群列表", "List group chats",
       method="GET", tags=["群组", "列表"]),
    _t("im.v1.chat.search", "搜索对用户或机器人可见的群列表", "Search group chats",
       method="GET", tags=["群组", "搜索"]),
    _t("im.v1.chat.update", "更新群信息", "Update group chat",
       tags=["群组", "更新"]),
    _t("im.v1.chatMembers.create", "将用户或机器人拉入群聊", "Add members to chat",
       tags=["群成员", "添加"]),
    _t("im.v1.chatMembers.delete", "将用户或机器人移出群聊", "Remove members from chat",
       tags=["群成员", "移除"]),
    _t("im.v1.chatMembers.get", "获取群成员列表", "Get chat members",
       method="GET", tags=["群成员", "查询"]),
    _t("im.v1.chatMembers.isInChat", "判断用户或机器人是否在群里", "Check if user is in chat",
       method="GET", tags=["群成员", "检查"]),
    _t("im.v1.message.create", "发送消息", "Send a message",
       params=[
           {"name": "receive_id", "type": "string", "required": True, "description": "接收者ID"},
           {"name": "msg_type", "type": "string", "required": True, "description": "消息类型"},
           {"name": "content", "type": "string", "required": True, "description": "消息内容"},
       ],
       tags=["消息", "发送"]),
    _t("im.v1.message.delete", "撤回消息", "Recall a message",
       tags=["消息", "撤回"]),
    _t("im.v1.message.get", "获取指定消息的内容", "Get message content",
       method="GET", tags=["消息", "查询"]),
    _t("im.v1.message.list", "获取会话历史消息", "List messages in a chat",
       method="GET", tags=["消息", "历史"]),
    _t("im.v1.message.patch", "编辑已发送的消息", "Edit a sent message",
       method="PATCH", tags=["消息", "编辑"]),
    _t("im.v1.message.reply", "回复消息", "Reply to a message",
       tags=["消息", "回复"]),
    _t("im.v1.message.forward", "转发消息", "Forward a message",
       tags=["消息", "转发"]),
    _t("im.v1.message.readUsers", "查询消息已读信息", "Get message read status",
       method="GET", tags=["消息", "已读"]),
    _t("im.v1.message.urgentApp", "发送应用内加急", "Send urgent message via app",
       tags=["消息", "加急"]),
    _t("im.v1.messageReaction.create", "添加消息表情回复", "Add message reaction",
       tags=["消息", "表情"]),
    _t("im.v1.messageReaction.delete", "删除消息表情回复", "Delete message reaction",
       tags=["消息", "表情"]),
    _t("im.v1.messageReaction.list", "获取消息表情回复", "List message reactions",
       method="GET", tags=["消息", "表情"]),
    _t("im.v1.chatAnnouncement.get", "获取群公告信息", "Get chat announcement",
       method="GET", tags=["群组", "公告"]),
    _t("im.v1.chatAnnouncement.patch", "更新群公告信息", "Update chat announcement",
       method="PATCH", tags=["群组", "公告"]),
    _t("im.v1.pin.create", "Pin消息", "Pin a message",
       tags=["消息", "置顶"]),
    _t("im.v1.pin.delete", "Un-Pin消息", "Unpin a message",
       tags=["消息", "置顶"]),
    _t("im.v1.pin.list", "获取群内Pin消息列表", "List pinned messages",
       method="GET", tags=["消息", "置顶"]),
    _t("im.v1.chatTab.create", "添加群标签页", "Add chat tab",
       tags=["群组", "标签页"]),
    _t("im.v1.chatTab.delete", "删除群标签页", "Delete chat tab",
       tags=["群组", "标签页"]),
    _t("im.v1.chatTab.list", "获取群标签页", "List chat tabs",
       method="GET", tags=["群组", "标签页"]),
]

# 多维表格 (Bitable)
BITABLE_TOOLS = [
    _t("bitable.v1.app.create", "创建多维表格", "Create a bitable app",
       tags=["多维表格", "创建"]),
    _t("bitable.v1.app.get", "获取多维表格元数据", "Get bitable app metadata",
       method="GET", tags=["多维表格", "查询"]),
    _t("bitable.v1.app.update", "更新多维表格元数据", "Update bitable app metadata",
       tags=["多维表格", "更新"]),
    _t("bitable.v1.app.copy", "复制多维表格", "Copy a bitable app",
       tags=["多维表格", "复制"]),
    _t("bitable.v1.appTable.create", "新增数据表", "Create a table",
       params=[{"name": "app_token", "type": "string", "required": True, "description": "多维表格token"}],
       tags=["数据表", "创建"]),
    _t("bitable.v1.appTable.delete", "删除数据表", "Delete a table",
       tags=["数据表", "删除"]),
    _t("bitable.v1.appTable.get", "获取数据表信息", "Get table info",
       method="GET", tags=["数据表", "查询"]),
    _t("bitable.v1.appTable.list", "列出数据表", "List tables",
       method="GET", tags=["数据表", "列表"]),
    _t("bitable.v1.appTable.patch", "更新数据表", "Update a table",
       method="PATCH", tags=["数据表", "更新"]),
    _t("bitable.v1.appTable.batchCreate", "批量新增数据表", "Batch create tables",
       tags=["数据表", "批量创建"]),
    _t("bitable.v1.appTable.batchDelete", "批量删除数据表", "Batch delete tables",
       tags=["数据表", "批量删除"]),
    _t("bitable.v1.appTableField.create", "新增字段", "Create a field",
       tags=["字段", "创建"]),
    _t("bitable.v1.appTableField.delete", "删除字段", "Delete a field",
       tags=["字段", "删除"]),
    _t("bitable.v1.appTableField.get", "获取字段信息", "Get field info",
       method="GET", tags=["字段", "查询"]),
    _t("bitable.v1.appTableField.list", "列出字段", "List fields",
       method="GET", tags=["字段", "列表"]),
    _t("bitable.v1.appTableField.update", "更新字段", "Update a field",
       tags=["字段", "更新"]),
    _t("bitable.v1.appTableRecord.create", "新增记录", "Create a record",
       params=[
           {"name": "app_token", "type": "string", "required": True, "description": "多维表格token"},
           {"name": "table_id", "type": "string", "required": True, "description": "数据表ID"},
           {"name": "fields", "type": "object", "required": True, "description": "记录字段值"},
       ],
       tags=["记录", "创建", "写入"]),
    _t("bitable.v1.appTableRecord.delete", "删除记录", "Delete a record",
       tags=["记录", "删除"]),
    _t("bitable.v1.appTableRecord.get", "获取记录", "Get a record",
       method="GET", tags=["记录", "查询"]),
    _t("bitable.v1.appTableRecord.list", "列出记录", "List records",
       method="GET", tags=["记录", "列表"]),
    _t("bitable.v1.appTableRecord.update", "更新记录", "Update a record",
       tags=["记录", "更新"]),
    _t("bitable.v1.appTableRecord.search", "查询记录", "Search records",
       params=[
           {"name": "app_token", "type": "string", "required": True, "description": "多维表格token"},
           {"name": "table_id", "type": "string", "required": True, "description": "数据表ID"},
       ],
       tags=["记录", "搜索", "查询"]),
    _t("bitable.v1.appTableRecord.batchCreate", "批量新增记录", "Batch create records",
       tags=["记录", "批量创建"]),
    _t("bitable.v1.appTableRecord.batchDelete", "批量删除记录", "Batch delete records",
       tags=["记录", "批量删除"]),
    _t("bitable.v1.appTableRecord.batchUpdate", "批量更新记录", "Batch update records",
       tags=["记录", "批量更新"]),
    _t("bitable.v1.appTableView.create", "新增视图", "Create a view",
       tags=["视图", "创建"]),
    _t("bitable.v1.appTableView.delete", "删除视图", "Delete a view",
       tags=["视图", "删除"]),
    _t("bitable.v1.appTableView.get", "获取视图信息", "Get view info",
       method="GET", tags=["视图", "查询"]),
    _t("bitable.v1.appTableView.list", "列出视图", "List views",
       method="GET", tags=["视图", "列表"]),
    _t("bitable.v1.appTableView.patch", "更新视图", "Update a view",
       method="PATCH", tags=["视图", "更新"]),
    _t("bitable.v1.appTableForm.get", "获取表单元数据", "Get form metadata",
       method="GET", tags=["表单", "查询"]),
    _t("bitable.v1.appTableForm.patch", "更新表单元数据", "Update form metadata",
       method="PATCH", tags=["表单", "更新"]),
    _t("bitable.v1.appTableFormField.list", "获取表单问题列表", "List form fields",
       method="GET", tags=["表单", "字段"]),
    _t("bitable.v1.appTableFormField.patch", "更新表单问题", "Update form field",
       method="PATCH", tags=["表单", "字段"]),
    _t("bitable.v1.appDashboard.list", "列出仪表盘", "List dashboards",
       method="GET", tags=["仪表盘", "列表"]),
    _t("bitable.v1.appDashboard.copy", "复制仪表盘", "Copy a dashboard",
       tags=["仪表盘", "复制"]),
    _t("bitable.v1.appRole.create", "新增自定义角色", "Create a custom role",
       tags=["角色", "创建"]),
    _t("bitable.v1.appRole.delete", "删除自定义角色", "Delete a custom role",
       tags=["角色", "删除"]),
    _t("bitable.v1.appRole.list", "列出自定义角色", "List custom roles",
       method="GET", tags=["角色", "列表"]),
    _t("bitable.v1.appRole.update", "更新自定义角色", "Update a custom role",
       tags=["角色", "更新"]),
    _t("bitable.v1.appRoleMember.create", "新增协作者", "Add role member",
       tags=["角色", "成员"]),
    _t("bitable.v1.appRoleMember.delete", "删除协作者", "Remove role member",
       tags=["角色", "成员"]),
    _t("bitable.v1.appRoleMember.list", "列出协作者", "List role members",
       method="GET", tags=["角色", "成员"]),
    _t("bitable.v1.appRoleMember.batchCreate", "批量新增协作者", "Batch add role members",
       tags=["角色", "成员", "批量"]),
    _t("bitable.v1.appWorkflow.list", "列出自动化流程", "List workflows",
       method="GET", tags=["自动化", "列表"]),
    _t("bitable.v1.appWorkflow.update", "更新自动化流程", "Update a workflow",
       tags=["自动化", "更新"]),
]

# 云文档 (Docx)
DOCX_TOOLS = [
    _t("docx.v1.document.create", "创建文档", "Create a document",
       tags=["文档", "创建"]),
    _t("docx.v1.document.get", "获取文档基本信息", "Get document info",
       method="GET", tags=["文档", "查询"]),
    _t("docx.v1.document.rawContent", "获取文档纯文本内容", "Get document raw content",
       method="GET", tags=["文档", "内容"]),
    _t("docx.v1.documentBlock.list", "获取文档所有块", "List document blocks",
       method="GET", tags=["文档", "块"]),
    _t("docx.v1.documentBlock.get", "获取文档块内容", "Get document block",
       method="GET", tags=["文档", "块"]),
    _t("docx.v1.documentBlock.create", "创建文档块", "Create document block",
       tags=["文档", "块", "创建"]),
    _t("docx.v1.documentBlock.patch", "更新文档块", "Update document block",
       method="PATCH", tags=["文档", "块", "更新"]),
    _t("docx.v1.documentBlock.delete", "删除文档块", "Delete document block",
       tags=["文档", "块", "删除"]),
    _t("docx.v1.documentBlock.batchUpdate", "批量更新文档块", "Batch update blocks",
       tags=["文档", "块", "批量"]),
    _t("docx.builtin.import", "导入文档", "Import document",
       tags=["文档", "导入"]),
    _t("docx.builtin.search", "搜索文档", "Search documents",
       tags=["文档", "搜索"]),
]

# 知识库 (Wiki)
WIKI_TOOLS = [
    _t("wiki.v2.space.create", "创建知识空间", "Create a wiki space",
       tags=["知识库", "空间", "创建"]),
    _t("wiki.v2.space.get", "获取知识空间信息", "Get wiki space info",
       method="GET", tags=["知识库", "空间", "查询"]),
    _t("wiki.v2.space.list", "获取知识空间列表", "List wiki spaces",
       method="GET", tags=["知识库", "空间", "列表"]),
    _t("wiki.v2.space.getNode", "获取知识空间节点信息", "Get wiki node info",
       method="GET", tags=["知识库", "节点", "查询"]),
    _t("wiki.v2.spaceNode.create", "创建知识空间节点", "Create a wiki node",
       tags=["知识库", "节点", "创建"]),
    _t("wiki.v2.spaceNode.list", "获取知识空间子节点列表", "List wiki child nodes",
       method="GET", tags=["知识库", "节点", "列表"]),
    _t("wiki.v2.spaceNode.move", "移动知识空间节点", "Move a wiki node",
       tags=["知识库", "节点", "移动"]),
    _t("wiki.v2.spaceMember.create", "添加知识空间成员", "Add wiki space member",
       tags=["知识库", "成员", "添加"]),
    _t("wiki.v2.spaceMember.delete", "删除知识空间成员", "Remove wiki space member",
       tags=["知识库", "成员", "删除"]),
    _t("wiki.v2.spaceSetting.update", "更新知识空间设置", "Update wiki space settings",
       tags=["知识库", "设置"]),
]

# 日历 (Calendar)
CALENDAR_TOOLS = [
    _t("calendar.v4.calendar.create", "创建日历", "Create a calendar",
       tags=["日历", "创建"]),
    _t("calendar.v4.calendar.delete", "删除日历", "Delete a calendar",
       tags=["日历", "删除"]),
    _t("calendar.v4.calendar.get", "获取日历信息", "Get calendar info",
       method="GET", tags=["日历", "查询"]),
    _t("calendar.v4.calendar.list", "获取日历列表", "List calendars",
       method="GET", tags=["日历", "列表"]),
    _t("calendar.v4.calendar.patch", "更新日历信息", "Update calendar info",
       method="PATCH", tags=["日历", "更新"]),
    _t("calendar.v4.calendar.search", "搜索日历", "Search calendars",
       tags=["日历", "搜索"]),
    _t("calendar.v4.calendar.subscribe", "订阅日历", "Subscribe to a calendar",
       tags=["日历", "订阅"]),
    _t("calendar.v4.calendar.unsubscribe", "取消订阅日历", "Unsubscribe from calendar",
       tags=["日历", "取消订阅"]),
    _t("calendar.v4.calendarEvent.create", "创建日程", "Create a calendar event",
       params=[
           {"name": "calendar_id", "type": "string", "required": True, "description": "日历ID"},
           {"name": "summary", "type": "string", "required": True, "description": "日程标题"},
           {"name": "start_time", "type": "object", "required": True, "description": "开始时间"},
           {"name": "end_time", "type": "object", "required": True, "description": "结束时间"},
       ],
       tags=["日程", "创建"]),
    _t("calendar.v4.calendarEvent.delete", "删除日程", "Delete a calendar event",
       tags=["日程", "删除"]),
    _t("calendar.v4.calendarEvent.get", "获取日程信息", "Get calendar event info",
       method="GET", tags=["日程", "查询"]),
    _t("calendar.v4.calendarEvent.list", "获取日程列表", "List calendar events",
       method="GET", tags=["日程", "列表"]),
    _t("calendar.v4.calendarEvent.patch", "更新日程", "Update a calendar event",
       method="PATCH", tags=["日程", "更新"]),
    _t("calendar.v4.calendarEvent.search", "搜索日程", "Search calendar events",
       tags=["日程", "搜索"]),
    _t("calendar.v4.calendarEvent.reply", "回复日程", "Reply to calendar event",
       tags=["日程", "回复"]),
    _t("calendar.v4.calendarEventAttendee.create", "添加日程参与人", "Add event attendee",
       tags=["日程", "参与人", "添加"]),
    _t("calendar.v4.calendarEventAttendee.delete", "删除日程参与人", "Remove event attendee",
       tags=["日程", "参与人", "删除"]),
    _t("calendar.v4.calendarEventAttendee.list", "获取日程参与人列表", "List event attendees",
       method="GET", tags=["日程", "参与人", "列表"]),
    _t("calendar.v4.freebusy.list", "查询主日历忙闲信息", "Query free/busy status",
       method="GET", tags=["日历", "忙闲"]),
    _t("calendar.v4.calendarAcl.create", "创建日历访问控制", "Create calendar ACL",
       tags=["日历", "权限"]),
    _t("calendar.v4.calendarAcl.delete", "删除日历访问控制", "Delete calendar ACL",
       tags=["日历", "权限"]),
    _t("calendar.v4.calendarAcl.list", "获取日历访问控制列表", "List calendar ACLs",
       method="GET", tags=["日历", "权限"]),
    _t("calendar.v4.timeoffEvent.create", "创建请假日程", "Create time-off event",
       tags=["日程", "请假"]),
    _t("calendar.v4.timeoffEvent.delete", "删除请假日程", "Delete time-off event",
       tags=["日程", "请假"]),
]

# 通讯录 (Contact)
CONTACT_TOOLS = [
    _t("contact.v3.user.create", "创建用户", "Create a user",
       tags=["用户", "创建"]),
    _t("contact.v3.user.delete", "删除用户", "Delete a user",
       tags=["用户", "删除"]),
    _t("contact.v3.user.get", "获取单个用户信息", "Get user info",
       method="GET", tags=["用户", "查询"]),
    _t("contact.v3.user.list", "获取用户列表", "List users",
       method="GET", tags=["用户", "列表"]),
    _t("contact.v3.user.patch", "修改用户信息", "Update user info",
       method="PATCH", tags=["用户", "更新"]),
    _t("contact.v3.user.batchGetId", "通过手机号或邮箱获取用户ID", "Get user ID by phone/email",
       tags=["用户", "查询", "ID"]),
    _t("contact.v3.user.findByDepartment", "获取部门直属用户列表", "List users in department",
       method="GET", tags=["用户", "部门"]),
    _t("contact.v3.department.create", "创建部门", "Create a department",
       tags=["部门", "创建"]),
    _t("contact.v3.department.delete", "删除部门", "Delete a department",
       tags=["部门", "删除"]),
    _t("contact.v3.department.get", "获取单个部门信息", "Get department info",
       method="GET", tags=["部门", "查询"]),
    _t("contact.v3.department.list", "获取部门列表", "List departments",
       method="GET", tags=["部门", "列表"]),
    _t("contact.v3.department.patch", "更新部门信息", "Update department info",
       method="PATCH", tags=["部门", "更新"]),
    _t("contact.v3.department.search", "搜索部门", "Search departments",
       tags=["部门", "搜索"]),
    _t("contact.v3.department.children", "获取子部门列表", "Get child departments",
       method="GET", tags=["部门", "子部门"]),
    _t("contact.v3.department.parent", "获取父部门信息", "Get parent department",
       method="GET", tags=["部门", "父部门"]),
    _t("contact.v3.group.create", "创建用户组", "Create a user group",
       tags=["用户组", "创建"]),
    _t("contact.v3.group.delete", "删除用户组", "Delete a user group",
       tags=["用户组", "删除"]),
    _t("contact.v3.group.get", "获取用户组信息", "Get user group info",
       method="GET", tags=["用户组", "查询"]),
    _t("contact.v3.group.list", "获取用户组列表", "List user groups",
       method="GET", tags=["用户组", "列表"]),
    _t("contact.v3.group.patch", "更新用户组信息", "Update user group info",
       method="PATCH", tags=["用户组", "更新"]),
    _t("contact.v3.groupMember.add", "添加用户组成员", "Add user group member",
       tags=["用户组", "成员", "添加"]),
    _t("contact.v3.groupMember.remove", "移除用户组成员", "Remove user group member",
       tags=["用户组", "成员", "移除"]),
    _t("contact.v3.groupMember.list", "获取用户组成员列表", "List user group members",
       method="GET", tags=["用户组", "成员", "列表"]),
    _t("contact.v3.scope.list", "获取通讯录授权范围", "List contact scope",
       method="GET", tags=["通讯录", "授权"]),
    _t("contact.v3.jobLevel.list", "获取职级列表", "List job levels",
       method="GET", tags=["职级", "列表"]),
    _t("contact.v3.jobFamily.list", "获取序列列表", "List job families",
       method="GET", tags=["序列", "列表"]),
    _t("contact.v3.employeeTypeEnum.list", "获取人员类型列表", "List employee types",
       method="GET", tags=["人员类型", "列表"]),
]

# 审批 (Approval)
APPROVAL_TOOLS = [
    _t("approval.v4.approval.create", "创建审批定义", "Create approval definition",
       tags=["审批", "定义", "创建"]),
    _t("approval.v4.approval.get", "获取审批定义", "Get approval definition",
       method="GET", tags=["审批", "定义", "查询"]),
    _t("approval.v4.instance.create", "创建审批实例", "Create an approval instance",
       tags=["审批", "实例", "创建", "发起"]),
    _t("approval.v4.instance.get", "获取审批实例详情", "Get approval instance detail",
       method="GET", tags=["审批", "实例", "查询"]),
    _t("approval.v4.instance.list", "获取审批实例列表", "List approval instances",
       method="GET", tags=["审批", "实例", "列表"]),
    _t("approval.v4.instance.cancel", "撤回审批实例", "Cancel an approval instance",
       tags=["审批", "实例", "撤回"]),
    _t("approval.v4.instance.cc", "抄送审批实例", "CC an approval instance",
       tags=["审批", "实例", "抄送"]),
    _t("approval.v4.instance.addSign", "加签审批实例", "Add signer to approval",
       tags=["审批", "实例", "加签"]),
    _t("approval.v4.task.approve", "同意审批任务", "Approve a task",
       tags=["审批", "任务", "同意"]),
    _t("approval.v4.task.reject", "拒绝审批任务", "Reject a task",
       tags=["审批", "任务", "拒绝"]),
    _t("approval.v4.task.transfer", "转交审批任务", "Transfer a task",
       tags=["审批", "任务", "转交"]),
    _t("approval.v4.task.list", "获取审批任务列表", "List approval tasks",
       method="GET", tags=["审批", "任务", "列表"]),
    _t("approval.v4.instanceComment.create", "创建审批评论", "Create approval comment",
       tags=["审批", "评论", "创建"]),
    _t("approval.v4.instanceComment.list", "获取审批评论列表", "List approval comments",
       method="GET", tags=["审批", "评论", "列表"]),
    _t("approval.v4.instanceComment.delete", "删除审批评论", "Delete approval comment",
       tags=["审批", "评论", "删除"]),
]

# 云空间 (Drive)
DRIVE_TOOLS = [
    _t("drive.v1.file.list", "获取文件夹下的文件清单", "List files in folder",
       method="GET", tags=["文件", "列表"]),
    _t("drive.v1.file.createFolder", "新建文件夹", "Create a folder",
       tags=["文件夹", "创建"]),
    _t("drive.v1.file.move", "移动文件", "Move a file",
       tags=["文件", "移动"]),
    _t("drive.v1.file.copy", "复制文件", "Copy a file",
       tags=["文件", "复制"]),
    _t("drive.v1.file.delete", "删除文件", "Delete a file",
       tags=["文件", "删除"]),
    _t("drive.v1.file.createShortcut", "创建快捷方式", "Create a shortcut",
       tags=["文件", "快捷方式"]),
    _t("drive.v1.permission.create", "创建文件权限", "Create file permission",
       tags=["文件", "权限", "创建"]),
    _t("drive.v1.permission.delete", "删除文件权限", "Delete file permission",
       tags=["文件", "权限", "删除"]),
    _t("drive.v1.permission.list", "获取文件权限列表", "List file permissions",
       method="GET", tags=["文件", "权限", "列表"]),
    _t("drive.v1.permission.update", "更新文件权限", "Update file permission",
       tags=["文件", "权限", "更新"]),
    _t("drive.v1.permission.publicGet", "获取文件公共设置", "Get public permission",
       method="GET", tags=["文件", "权限", "公共"]),
    _t("drive.v1.permission.publicUpdate", "更新文件公共设置", "Update public permission",
       tags=["文件", "权限", "公共"]),
]

# 电子表格 (Sheets)
SHEETS_TOOLS = [
    _t("sheets.v3.spreadsheet.create", "创建电子表格", "Create a spreadsheet",
       tags=["电子表格", "创建"]),
    _t("sheets.v3.spreadsheet.get", "获取电子表格信息", "Get spreadsheet info",
       method="GET", tags=["电子表格", "查询"]),
    _t("sheets.v3.spreadsheet.patch", "更新电子表格属性", "Update spreadsheet properties",
       method="PATCH", tags=["电子表格", "更新"]),
    _t("sheets.v3.spreadsheetSheet.get", "获取工作表信息", "Get sheet info",
       method="GET", tags=["工作表", "查询"]),
    _t("sheets.v3.spreadsheetSheet.list", "获取工作表列表", "List sheets",
       method="GET", tags=["工作表", "列表"]),
    _t("sheets.v3.spreadsheetSheet.query", "查询工作表数据", "Query sheet data",
       method="GET", tags=["工作表", "数据", "查询"]),
    _t("sheets.v3.spreadsheetSheet.moveDimension", "移动行列", "Move rows/columns",
       tags=["工作表", "行列"]),
    _t("sheets.v3.spreadsheetSheet.write", "写入数据", "Write data to sheet",
       tags=["工作表", "数据", "写入"]),
    _t("sheets.v3.spreadsheetSheet.batchWrite", "批量写入数据", "Batch write data",
       tags=["工作表", "数据", "批量写入"]),
    _t("sheets.v3.spreadsheetSheet.read", "读取数据", "Read data from sheet",
       method="GET", tags=["工作表", "数据", "读取"]),
    _t("sheets.v3.spreadsheetSheet.setStyle", "设置单元格样式", "Set cell style",
       tags=["工作表", "样式"]),
    _t("sheets.v3.spreadsheetSheet.merge", "合并单元格", "Merge cells",
       tags=["工作表", "合并"]),
    _t("sheets.v3.spreadsheetSheet.unmerge", "取消合并单元格", "Unmerge cells",
       tags=["工作表", "取消合并"]),
    _t("sheets.v3.spreadsheetSheet.filter", "设置筛选", "Set filter",
       tags=["工作表", "筛选"]),
]

# 任务 (Task)
TASK_TOOLS = [
    _t("task.v2.task.create", "创建任务", "Create a task",
       params=[
           {"name": "summary", "type": "string", "required": True, "description": "任务标题"},
       ],
       tags=["任务", "创建"]),
    _t("task.v2.task.get", "获取任务详情", "Get task details",
       method="GET", tags=["任务", "查询"]),
    _t("task.v2.task.list", "获取任务列表", "List tasks",
       method="GET", tags=["任务", "列表"]),
    _t("task.v2.task.patch", "更新任务", "Update a task",
       method="PATCH", tags=["任务", "更新"]),
    _t("task.v2.task.delete", "删除任务", "Delete a task",
       tags=["任务", "删除"]),
    _t("task.v2.task.complete", "完成任务", "Complete a task",
       tags=["任务", "完成"]),
    _t("task.v2.task.uncomplete", "取消完成任务", "Uncomplete a task",
       tags=["任务", "取消完成"]),
    _t("task.v2.task.addMembers", "添加任务成员", "Add task members",
       tags=["任务", "成员"]),
    _t("task.v2.task.removeMembers", "移除任务成员", "Remove task members",
       tags=["任务", "成员"]),
    _t("task.v2.task.addReminders", "添加任务提醒", "Add task reminders",
       tags=["任务", "提醒"]),
    _t("task.v2.taskList.create", "创建任务清单", "Create a task list",
       tags=["任务清单", "创建"]),
    _t("task.v2.taskList.get", "获取任务清单", "Get task list",
       method="GET", tags=["任务清单", "查询"]),
    _t("task.v2.taskList.list", "获取任务清单列表", "List task lists",
       method="GET", tags=["任务清单", "列表"]),
    _t("task.v2.taskList.patch", "更新任务清单", "Update task list",
       method="PATCH", tags=["任务清单", "更新"]),
    _t("task.v2.taskList.delete", "删除任务清单", "Delete task list",
       tags=["任务清单", "删除"]),
]

# 考勤 (Attendance)
ATTENDANCE_TOOLS = [
    _t("attendance.v1.group.create", "创建考勤组", "Create attendance group",
       tags=["考勤组", "创建"]),
    _t("attendance.v1.group.get", "获取考勤组详情", "Get attendance group",
       method="GET", tags=["考勤组", "查询"]),
    _t("attendance.v1.group.list", "获取考勤组列表", "List attendance groups",
       method="GET", tags=["考勤组", "列表"]),
    _t("attendance.v1.group.search", "搜索考勤组", "Search attendance groups",
       tags=["考勤组", "搜索"]),
    _t("attendance.v1.shift.create", "创建班次", "Create a shift",
       tags=["班次", "创建"]),
    _t("attendance.v1.shift.get", "获取班次详情", "Get shift details",
       method="GET", tags=["班次", "查询"]),
    _t("attendance.v1.shift.list", "获取班次列表", "List shifts",
       method="GET", tags=["班次", "列表"]),
    _t("attendance.v1.userFlow.batchCreate", "批量导入打卡流水", "Batch import punch records",
       tags=["打卡", "导入"]),
    _t("attendance.v1.userFlow.get", "获取打卡流水", "Get punch record",
       method="GET", tags=["打卡", "查询"]),
    _t("attendance.v1.userFlow.query", "查询打卡流水", "Query punch records",
       tags=["打卡", "查询"]),
    _t("attendance.v1.userTask.query", "查询打卡结果", "Query punch results",
       tags=["打卡", "结果"]),
    _t("attendance.v1.userStatsData.query", "查询统计数据", "Query attendance statistics",
       tags=["考勤", "统计"]),
    _t("attendance.v1.leaveAccrualRecord.patch", "修改发放记录", "Update leave grant record",
       method="PATCH", tags=["请假", "记录"]),
    _t("attendance.v1.userApproval.query", "获取审批通过数据", "Query approved data",
       tags=["考勤", "审批"]),
]

# 人事管理 (CoreHR) - 精选核心接口
COREHR_TOOLS = [
    _t("corehr.v2.employee.search", "搜索员工信息", "Search employees",
       tags=["员工", "搜索"]),
    _t("corehr.v2.employee.batchGet", "批量获取员工信息", "Batch get employees",
       tags=["员工", "批量查询"]),
    _t("corehr.v1.employment.create", "创建雇佣信息", "Create employment",
       tags=["雇佣", "创建"]),
    _t("corehr.v1.person.create", "创建个人信息", "Create person record",
       tags=["个人信息", "创建"]),
    _t("corehr.v1.person.patch", "更新个人信息", "Update person record",
       method="PATCH", tags=["个人信息", "更新"]),
    _t("corehr.v2.department.search", "搜索部门", "Search departments",
       tags=["部门", "搜索"]),
    _t("corehr.v2.department.batchGet", "批量获取部门信息", "Batch get departments",
       tags=["部门", "批量查询"]),
    _t("corehr.v1.department.create", "创建部门", "Create department",
       tags=["部门", "创建"]),
    _t("corehr.v1.department.patch", "更新部门", "Update department",
       method="PATCH", tags=["部门", "更新"]),
    _t("corehr.v1.jobChange.search", "搜索异动记录", "Search job changes",
       tags=["异动", "搜索"]),
    _t("corehr.v1.offboarding.search", "搜索离职记录", "Search offboarding records",
       tags=["离职", "搜索"]),
    _t("corehr.v2.preHire.search", "搜索待入职人员", "Search pre-hire",
       tags=["待入职", "搜索"]),
    _t("corehr.v1.leave.leaveBalances", "获取假期余额", "Get leave balances",
       method="GET", tags=["假期", "余额"]),
    _t("corehr.v1.leave.leaveRequestHistory", "获取请假记录", "Get leave request history",
       method="GET", tags=["请假", "记录"]),
    _t("corehr.v2.job.list", "获取职务列表", "List jobs",
       method="GET", tags=["职务", "列表"]),
    _t("corehr.v2.jobLevel.list", "获取职级列表", "List job levels",
       method="GET", tags=["职级", "列表"]),
    _t("corehr.v2.jobFamily.list", "获取序列列表", "List job families",
       method="GET", tags=["序列", "列表"]),
    _t("corehr.v1.company.list", "获取公司列表", "List companies",
       method="GET", tags=["公司", "列表"]),
    _t("corehr.v1.location.list", "获取地点列表", "List locations",
       method="GET", tags=["地点", "列表"]),
    _t("corehr.v2.costCenter.search", "搜索成本中心", "Search cost centers",
       tags=["成本中心", "搜索"]),
]

# 智能伙伴 (Aily)
AILY_TOOLS = [
    _t("aily.v1.ailySession.create", "创建智能伙伴会话", "Create Aily session",
       tags=["智能伙伴", "会话", "创建"]),
    _t("aily.v1.ailySession.get", "获取会话信息", "Get Aily session info",
       method="GET", tags=["智能伙伴", "会话", "查询"]),
    _t("aily.v1.ailySession.update", "更新会话", "Update Aily session",
       tags=["智能伙伴", "会话", "更新"]),
    _t("aily.v1.ailySession.delete", "删除会话", "Delete Aily session",
       tags=["智能伙伴", "会话", "删除"]),
    _t("aily.v1.ailySessionAilyMessage.create", "发送消息给智能伙伴", "Send message to Aily",
       tags=["智能伙伴", "消息", "发送"]),
    _t("aily.v1.ailySessionAilyMessage.get", "获取智能伙伴消息", "Get Aily message",
       method="GET", tags=["智能伙伴", "消息", "查询"]),
    _t("aily.v1.ailySessionAilyMessage.list", "获取智能伙伴消息列表", "List Aily messages",
       method="GET", tags=["智能伙伴", "消息", "列表"]),
    _t("aily.v1.ailySessionRun.create", "创建运行", "Create Aily run",
       tags=["智能伙伴", "运行", "创建"]),
    _t("aily.v1.ailySessionRun.get", "获取运行状态", "Get Aily run status",
       method="GET", tags=["智能伙伴", "运行", "查询"]),
    _t("aily.v1.appSkill.list", "获取技能列表", "List Aily skills",
       method="GET", tags=["智能伙伴", "技能", "列表"]),
    _t("aily.v1.appSkill.start", "调用技能", "Invoke Aily skill",
       tags=["智能伙伴", "技能", "调用"]),
]

# 词典 (Baike)
BAIKE_TOOLS = [
    _t("baike.v1.entity.create", "创建词条", "Create a glossary entry",
       tags=["词典", "词条", "创建"]),
    _t("baike.v1.entity.get", "获取词条详情", "Get glossary entry",
       method="GET", tags=["词典", "词条", "查询"]),
    _t("baike.v1.entity.list", "获取词条列表", "List glossary entries",
       method="GET", tags=["词典", "词条", "列表"]),
    _t("baike.v1.entity.update", "更新词条", "Update glossary entry",
       tags=["词典", "词条", "更新"]),
    _t("baike.v1.entity.delete", "删除词条", "Delete glossary entry",
       tags=["词典", "词条", "删除"]),
    _t("baike.v1.entity.search", "搜索词条", "Search glossary entries",
       tags=["词典", "词条", "搜索"]),
    _t("baike.v1.entity.highlight", "词条高亮", "Highlight glossary entry",
       tags=["词典", "词条", "高亮"]),
    _t("baike.v1.entity.match", "精准搜索词条", "Match glossary entry",
       tags=["词典", "词条", "匹配"]),
    _t("baike.v1.classification.list", "获取词典分类", "List glossary classifications",
       method="GET", tags=["词典", "分类"]),
]

# 管理后台 (Admin)
ADMIN_TOOLS = [
    _t("admin.v1.auditInfo.list", "获取审计日志", "List audit logs",
       method="GET", tags=["审计", "日志"]),
    _t("admin.v1.adminUserStat.list", "获取用户活跃统计", "List user activity stats",
       method="GET", tags=["统计", "用户"]),
    _t("admin.v1.adminDeptStat.list", "获取部门活跃统计", "List department activity stats",
       method="GET", tags=["统计", "部门"]),
    _t("admin.v1.badge.create", "创建勋章", "Create a badge",
       tags=["勋章", "创建"]),
    _t("admin.v1.badge.get", "获取勋章信息", "Get badge info",
       method="GET", tags=["勋章", "查询"]),
    _t("admin.v1.badge.list", "获取勋章列表", "List badges",
       method="GET", tags=["勋章", "列表"]),
    _t("admin.v1.badge.update", "更新勋章", "Update a badge",
       tags=["勋章", "更新"]),
    _t("admin.v1.badgeGrant.create", "颁发勋章", "Grant a badge",
       tags=["勋章", "颁发"]),
    _t("admin.v1.badgeGrant.delete", "撤销勋章", "Revoke a badge",
       tags=["勋章", "撤销"]),
    _t("admin.v1.badgeGrant.list", "获取勋章颁发记录", "List badge grants",
       method="GET", tags=["勋章", "记录"]),
    _t("admin.v1.password.reset", "重置企业邮箱密码", "Reset enterprise email password",
       tags=["密码", "重置"]),
]

# 应用管理 (Application)
APPLICATION_TOOLS = [
    _t("application.v6.application.get", "获取应用信息", "Get application info",
       method="GET", tags=["应用", "查询"]),
    _t("application.v6.application.list", "获取应用列表", "List applications",
       method="GET", tags=["应用", "列表"]),
    _t("application.v6.application.patch", "更新应用信息", "Update application info",
       method="PATCH", tags=["应用", "更新"]),
    _t("application.v6.applicationAppVersion.get", "获取应用版本信息", "Get app version",
       method="GET", tags=["应用", "版本"]),
    _t("application.v6.applicationAppVersion.list", "获取应用版本列表", "List app versions",
       method="GET", tags=["应用", "版本", "列表"]),
    _t("application.v6.applicationVisibility.checkWhiteBlackList", "查看应用白名单", "Check app whitelist",
       method="GET", tags=["应用", "可见性"]),
    _t("application.v6.applicationManagement.update", "启用/停用应用", "Enable/disable app",
       tags=["应用", "管理"]),
    _t("application.v6.applicationOwner.update", "转移应用所有者", "Transfer app ownership",
       tags=["应用", "所有者"]),
]

# 卡片 (CardKit)
CARDKIT_TOOLS = [
    _t("cardkit.v1.card.create", "创建卡片", "Create a card",
       tags=["卡片", "创建"]),
    _t("cardkit.v1.card.get", "获取卡片信息", "Get card info",
       method="GET", tags=["卡片", "查询"]),
    _t("cardkit.v1.card.update", "更新卡片", "Update a card",
       tags=["卡片", "更新"]),
    _t("cardkit.v1.card.settings", "更新卡片设置", "Update card settings",
       tags=["卡片", "设置"]),
    _t("cardkit.v1.cardElement.create", "添加卡片组件", "Add card element",
       tags=["卡片", "组件", "创建"]),
    _t("cardkit.v1.cardElement.update", "更新卡片组件", "Update card element",
       tags=["卡片", "组件", "更新"]),
    _t("cardkit.v1.cardElement.delete", "删除卡片组件", "Delete card element",
       tags=["卡片", "组件", "删除"]),
]

# 画板 (Board)
BOARD_TOOLS = [
    _t("board.v1.whiteboardNode.list", "获取画板所有节点", "List whiteboard nodes",
       method="GET", tags=["画板", "节点"]),
]

# 认证 (Auth)
AUTH_TOOLS = [
    _t("auth.v3.auth.appAccessTokenInternal", "获取自建应用token", "Get internal app access token",
       tags=["认证", "token"]),
    _t("auth.v3.auth.appAccessToken", "获取商店应用token", "Get store app access token",
       tags=["认证", "token"]),
    _t("auth.v3.auth.tenantAccessTokenInternal", "获取自建应用租户token", "Get internal tenant token",
       tags=["认证", "token"]),
    _t("auth.v3.auth.tenantAccessToken", "获取商店应用租户token", "Get store tenant token",
       tags=["认证", "token"]),
    _t("authen.v1.userInfo.get", "获取登录用户信息", "Get logged-in user info",
       method="GET", tags=["用户", "登录"]),
]

# 搜索 (Search)
SEARCH_TOOLS = [
    _t("search.v2.message.create", "搜索消息", "Search messages",
       tags=["搜索", "消息"]),
    _t("search.v2.app.create", "搜索应用", "Search apps",
       tags=["搜索", "应用"]),
]


# ============================================================
# 汇总所有工具
# ============================================================
ALL_TOOL_GROUPS = {
    "im": IM_TOOLS,
    "bitable": BITABLE_TOOLS,
    "docx": DOCX_TOOLS,
    "wiki": WIKI_TOOLS,
    "calendar": CALENDAR_TOOLS,
    "contact": CONTACT_TOOLS,
    "approval": APPROVAL_TOOLS,
    "drive": DRIVE_TOOLS,
    "sheets": SHEETS_TOOLS,
    "task": TASK_TOOLS,
    "attendance": ATTENDANCE_TOOLS,
    "corehr": COREHR_TOOLS,
    "aily": AILY_TOOLS,
    "baike": BAIKE_TOOLS,
    "admin": ADMIN_TOOLS,
    "application": APPLICATION_TOOLS,
    "cardkit": CARDKIT_TOOLS,
    "board": BOARD_TOOLS,
    "auth": AUTH_TOOLS,
    "search": SEARCH_TOOLS,
}


def get_all_tools() -> list[ToolDefinition]:
    """返回所有工具定义"""
    tools = []
    for group in ALL_TOOL_GROUPS.values():
        tools.extend(group)
    return tools


def get_tools_by_category(category: str) -> list[ToolDefinition]:
    """按分类获取工具"""
    return ALL_TOOL_GROUPS.get(category, [])


def get_tool_by_id(tool_id: str) -> ToolDefinition | None:
    """按 ID 获取工具"""
    for tool in get_all_tools():
        if tool.tool_id == tool_id:
            return tool
    return None


def get_category_list() -> list[dict]:
    """获取所有分类列表"""
    result = []
    for key, meta in CATEGORY_META.items():
        tools = ALL_TOOL_GROUPS.get(key, [])
        result.append({
            "key": key,
            "name": meta["name"],
            "description": meta["description"],
            "tool_count": len(tools),
        })
    return result


# 统计
if __name__ == "__main__":
    all_tools = get_all_tools()
    print(f"总工具数: {len(all_tools)}")
    for cat, tools in ALL_TOOL_GROUPS.items():
        meta = CATEGORY_META.get(cat, {})
        print(f"  {cat} ({meta.get('name', '?')}): {len(tools)} 个工具")
