"""
评测数据集
包含不同类型的用户意图查询及其期望匹配的工具。

意图类型：
- precise: 精确意图（明确指定了操作和对象）
- fuzzy: 模糊意图（自然语言描述，没有技术术语）
- cross_domain: 跨域意图（涉及多个产品线）
- chinese: 中文特有意图（使用中文惯用表达）
"""

from dataclasses import dataclass, field


@dataclass
class EvalCase:
    query: str                     # 用户查询
    expected_tools: list[str]      # 期望匹配的工具 ID 列表
    intent_type: str               # 意图类型
    difficulty: str = "normal"     # 难度：easy, normal, hard
    description: str = ""          # 用例描述


EVAL_DATASET: list[EvalCase] = [
    # ===== 精确意图 (precise) =====
    EvalCase(
        query="创建一个多维表格记录",
        expected_tools=["bitable.v1.appTableRecord.create"],
        intent_type="precise",
        difficulty="easy",
        description="精确指定了操作(创建)和对象(多维表格记录)",
    ),
    EvalCase(
        query="发送一条消息到群聊",
        expected_tools=["im.v1.message.create"],
        intent_type="precise",
        difficulty="easy",
        description="精确的消息发送意图",
    ),
    EvalCase(
        query="获取日程列表",
        expected_tools=["calendar.v4.calendarEvent.list"],
        intent_type="precise",
        difficulty="easy",
        description="精确的日程查询意图",
    ),
    EvalCase(
        query="创建一个审批实例",
        expected_tools=["approval.v4.instance.create"],
        intent_type="precise",
        difficulty="easy",
        description="精确的审批发起意图",
    ),
    EvalCase(
        query="搜索部门信息",
        expected_tools=["contact.v3.department.search"],
        intent_type="precise",
        difficulty="easy",
        description="精确的部门搜索意图",
    ),
    EvalCase(
        query="删除知识库节点",
        expected_tools=["wiki.v2.spaceNode.move"],  # 无直接delete，move是最近的
        intent_type="precise",
        difficulty="normal",
        description="精确但目标工具不完全匹配",
    ),
    EvalCase(
        query="批量更新多维表格记录",
        expected_tools=["bitable.v1.appTableRecord.batchUpdate"],
        intent_type="precise",
        difficulty="easy",
        description="批量操作的精确意图",
    ),
    EvalCase(
        query="创建一个日历事件并添加参与人",
        expected_tools=[
            "calendar.v4.calendarEvent.create",
            "calendar.v4.calendarEventAttendee.create",
        ],
        intent_type="precise",
        difficulty="normal",
        description="多步骤精确意图",
    ),
    EvalCase(
        query="获取群聊成员列表",
        expected_tools=["im.v1.chatMembers.get"],
        intent_type="precise",
        difficulty="easy",
        description="精确的群成员查询",
    ),
    EvalCase(
        query="查询员工的请假记录",
        expected_tools=["corehr.v1.leave.leaveRequestHistory"],
        intent_type="precise",
        difficulty="normal",
        description="精确的 HR 查询意图",
    ),

    # ===== 模糊意图 (fuzzy) =====
    EvalCase(
        query="我想把一些数据写进表格里",
        expected_tools=[
            "bitable.v1.appTableRecord.create",
            "bitable.v1.appTableRecord.batchCreate",
            "sheets.v3.spreadsheetSheet.write",
        ],
        intent_type="fuzzy",
        difficulty="normal",
        description="模糊的数据写入意图，可能是多维表格或电子表格",
    ),
    EvalCase(
        query="帮我约个会",
        expected_tools=["calendar.v4.calendarEvent.create"],
        intent_type="fuzzy",
        difficulty="hard",
        description="非常口语化的日程创建意图",
    ),
    EvalCase(
        query="看看有没有什么新消息",
        expected_tools=["im.v1.message.list"],
        intent_type="fuzzy",
        difficulty="hard",
        description="口语化的消息查看意图",
    ),
    EvalCase(
        query="公司组织架构是怎样的",
        expected_tools=[
            "contact.v3.department.list",
            "contact.v3.department.children",
        ],
        intent_type="fuzzy",
        difficulty="normal",
        description="组织架构查询，映射到部门列表",
    ),
    EvalCase(
        query="谁还没看我发的那条信息",
        expected_tools=["im.v1.message.readUsers"],
        intent_type="fuzzy",
        difficulty="hard",
        description="口语化的已读状态查询",
    ),
    EvalCase(
        query="统计一下这个月的考勤情况",
        expected_tools=["attendance.v1.userStatsData.query"],
        intent_type="fuzzy",
        difficulty="normal",
        description="模糊的考勤统计意图",
    ),
    EvalCase(
        query="找一个词的解释",
        expected_tools=[
            "baike.v1.entity.search",
            "baike.v1.entity.match",
        ],
        intent_type="fuzzy",
        difficulty="hard",
        description="模糊的词典查询意图",
    ),
    EvalCase(
        query="这个文档分享给同事看看",
        expected_tools=[
            "drive.v1.permission.create",
        ],
        intent_type="fuzzy",
        difficulty="hard",
        description="文档分享意图，映射到权限设置",
    ),
    EvalCase(
        query="给团队定个任务",
        expected_tools=["task.v2.task.create"],
        intent_type="fuzzy",
        difficulty="normal",
        description="模糊的任务创建意图",
    ),
    EvalCase(
        query="查一下小王的联系方式",
        expected_tools=[
            "contact.v3.user.get",
            "contact.v3.user.list",
        ],
        intent_type="fuzzy",
        difficulty="normal",
        description="模糊的用户信息查询",
    ),

    # ===== 跨域意图 (cross_domain) =====
    EvalCase(
        query="在多维表格里新建一条记录，然后发消息通知群里的人",
        expected_tools=[
            "bitable.v1.appTableRecord.create",
            "im.v1.message.create",
        ],
        intent_type="cross_domain",
        difficulty="normal",
        description="多维表格 + 即时消息",
    ),
    EvalCase(
        query="查看审批状态，如果通过了就在日历上创建日程",
        expected_tools=[
            "approval.v4.instance.get",
            "calendar.v4.calendarEvent.create",
        ],
        intent_type="cross_domain",
        difficulty="normal",
        description="审批 + 日历",
    ),
    EvalCase(
        query="获取部门所有人员信息，然后批量导入考勤打卡记录",
        expected_tools=[
            "contact.v3.user.findByDepartment",
            "attendance.v1.userFlow.batchCreate",
        ],
        intent_type="cross_domain",
        difficulty="hard",
        description="通讯录 + 考勤",
    ),
    EvalCase(
        query="把知识库文档内容同步到多维表格",
        expected_tools=[
            "wiki.v2.space.getNode",
            "docx.v1.document.rawContent",
            "bitable.v1.appTableRecord.create",
        ],
        intent_type="cross_domain",
        difficulty="hard",
        description="知识库 + 文档 + 多维表格",
    ),
    EvalCase(
        query="创建群聊并发送卡片消息",
        expected_tools=[
            "im.v1.chat.create",
            "im.v1.message.create",
            "cardkit.v1.card.create",
        ],
        intent_type="cross_domain",
        difficulty="normal",
        description="群聊 + 消息 + 卡片",
    ),

    # ===== 中文特有意图 (chinese) =====
    EvalCase(
        query="拉个群把大家加进去",
        expected_tools=[
            "im.v1.chat.create",
            "im.v1.chatMembers.create",
        ],
        intent_type="chinese",
        difficulty="hard",
        description="中文口语：创建群+添加成员",
    ),
    EvalCase(
        query="催一下审批流程",
        expected_tools=["im.v1.message.urgentApp"],
        intent_type="chinese",
        difficulty="hard",
        description="中文口语：加急催办",
    ),
    EvalCase(
        query="挂个日程提醒开会",
        expected_tools=["calendar.v4.calendarEvent.create"],
        intent_type="chinese",
        difficulty="hard",
        description="中文口语：创建会议日程",
    ),
    EvalCase(
        query="把这条消息钉一下",
        expected_tools=["im.v1.pin.create"],
        intent_type="chinese",
        difficulty="hard",
        description="中文口语：置顶/Pin消息",
    ),
    EvalCase(
        query="给新来的同事开通系统权限",
        expected_tools=[
            "contact.v3.user.create",
        ],
        intent_type="chinese",
        difficulty="hard",
        description="中文口语：创建用户/开通权限",
    ),
    EvalCase(
        query="看看谁今天没打卡",
        expected_tools=[
            "attendance.v1.userTask.query",
            "attendance.v1.userStatsData.query",
        ],
        intent_type="chinese",
        difficulty="hard",
        description="中文口语：考勤异常查询",
    ),
    EvalCase(
        query="发个表情回应一下",
        expected_tools=["im.v1.messageReaction.create"],
        intent_type="chinese",
        difficulty="hard",
        description="中文口语：消息表情回复",
    ),
    EvalCase(
        query="翻翻群里之前的聊天记录",
        expected_tools=["im.v1.message.list"],
        intent_type="chinese",
        difficulty="hard",
        description="中文口语：查看历史消息",
    ),
    EvalCase(
        query="新同事入职需要录入HR系统",
        expected_tools=[
            "corehr.v1.person.create",
            "corehr.v1.employment.create",
        ],
        intent_type="chinese",
        difficulty="hard",
        description="中文口语：HR入职流程",
    ),
    EvalCase(
        query="在飞书百科里加个术语解释",
        expected_tools=["baike.v1.entity.create"],
        intent_type="chinese",
        difficulty="normal",
        description="中文特有：飞书百科/词典",
    ),
]


def get_eval_dataset() -> list[EvalCase]:
    """获取完整评测数据集"""
    return EVAL_DATASET


def get_eval_by_type(intent_type: str) -> list[EvalCase]:
    """按意图类型获取评测用例"""
    return [c for c in EVAL_DATASET if c.intent_type == intent_type]


def get_eval_by_difficulty(difficulty: str) -> list[EvalCase]:
    """按难度获取评测用例"""
    return [c for c in EVAL_DATASET if c.difficulty == difficulty]


# 统计
if __name__ == "__main__":
    dataset = get_eval_dataset()
    print(f"评测用例总数: {len(dataset)}")
    from collections import Counter
    type_counts = Counter(c.intent_type for c in dataset)
    diff_counts = Counter(c.difficulty for c in dataset)
    print(f"按类型: {dict(type_counts)}")
    print(f"按难度: {dict(diff_counts)}")
