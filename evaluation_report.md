# 飞书 OpenAPI MCP 工具搜索方案评测报告

> 生成时间: 2026-03-15 14:02:32

> 评测用例数: 35

## 一、总体评测结果

| 方案 | 平均召回率 | 平均准确率 | 平均F1 | 初始Token | 平均Token/次 | 总Token | 平均搜索轮次 |
|------|-----------|-----------|--------|----------|-------------|---------|------------|
| Code Mode | 40.0% | 5.5% | 9.4% | 337 | 603 | 21,101 | 1.0 |
| help/schema | 37.1% | 9.9% | 14.1% | 226 | 1,618 | 56,624 | 7.5 |
| Embedding 语义检索 | 65.2% | 8.9% | 15.3% | 191 | 407 | 14,252 | 1.0 |
| 树形导航 | 41.0% | 8.3% | 13.2% | 328 | 2,851 | 99,792 | 13.7 |

## 二、按意图类型细分

### 精确意图

| 方案 | 用例数 | 召回率 | 准确率 | F1 | 平均Token |
|------|-------|--------|--------|-----|----------|
| Code Mode | 10 | 80.0% | 9.0% | 16.1% | 648 |
| help/schema | 10 | 70.0% | 23.1% | 30.6% | 1,735 |
| Embedding 语义检索 | 10 | 95.0% | 10.0% | 18.0% | 418 |
| 树形导航 | 10 | 80.0% | 16.9% | 26.7% | 2,376 |
### 模糊意图

| 方案 | 用例数 | 召回率 | 准确率 | F1 | 平均Token |
|------|-------|--------|--------|-----|----------|
| Code Mode | 10 | 13.3% | 2.0% | 3.4% | 537 |
| help/schema | 10 | 10.0% | 1.0% | 1.8% | 1,550 |
| Embedding 语义检索 | 10 | 58.3% | 8.0% | 13.8% | 380 |
| 树形导航 | 10 | 13.3% | 2.0% | 3.4% | 3,084 |
### 跨域意图

| 方案 | 用例数 | 召回率 | 准确率 | F1 | 平均Token |
|------|-------|--------|--------|-----|----------|
| Code Mode | 5 | 33.3% | 8.0% | 12.8% | 671 |
| help/schema | 5 | 40.0% | 12.9% | 19.4% | 2,107 |
| Embedding 语义检索 | 5 | 50.0% | 12.0% | 19.2% | 416 |
| 树形导航 | 5 | 40.0% | 12.0% | 18.2% | 3,986 |
### 中文口语意图

| 方案 | 用例数 | 召回率 | 准确率 | F1 | 平均Token |
|------|-------|--------|--------|-----|----------|
| Code Mode | 10 | 30.0% | 4.1% | 7.2% | 589 |
| help/schema | 10 | 30.0% | 4.1% | 7.2% | 1,324 |
| Embedding 语义检索 | 10 | 50.0% | 7.0% | 12.1% | 419 |
| 树形导航 | 10 | 30.0% | 4.1% | 7.2% | 2,527 |

## 三、按难度细分

### 简单

| 方案 | 用例数 | 召回率 | 准确率 | F1 |
|------|-------|--------|--------|-----|
| Code Mode | 7 | 100.0% | 10.0% | 18.2% |
| help/schema | 7 | 85.7% | 27.3% | 35.5% |
| Embedding 语义检索 | 7 | 100.0% | 10.0% | 18.2% |
| 树形导航 | 7 | 100.0% | 18.4% | 30.0% |
### 中等

| 方案 | 用例数 | 召回率 | 准确率 | F1 |
|------|-------|--------|--------|-----|
| Code Mode | 12 | 41.7% | 7.6% | 12.6% |
| help/schema | 12 | 41.7% | 10.4% | 16.0% |
| Embedding 语义检索 | 12 | 66.7% | 10.0% | 17.0% |
| 树形导航 | 12 | 44.4% | 10.9% | 16.8% |
### 困难

| 方案 | 用例数 | 召回率 | 准确率 | F1 |
|------|-------|--------|--------|-----|
| Code Mode | 16 | 12.5% | 1.9% | 3.2% |
| help/schema | 16 | 12.5% | 1.9% | 3.2% |
| Embedding 语义检索 | 16 | 49.0% | 7.5% | 12.8% |
| 树形导航 | 16 | 12.5% | 1.9% | 3.2% |

## 四、Token 消耗对比

| 方案 | 初始注入 | 搜索结果(平均) | 总计(平均) | 评价 |
|------|---------|---------------|----------|------|
| Code Mode | ~337 | ~266 | ~603 | ✅ 低 |
| help/schema | ~226 | ~1,392 | ~1,618 | ⚠️ 中 |
| Embedding 语义检索 | ~191 | ~216 | ~407 | ✅ 低 |
| 树形导航 | ~328 | ~2,523 | ~2,851 | ⚠️ 中 |

## 五、失败模式分析

### Code Mode

| 失败模式 | 次数 | 占比 |
|---------|------|------|
| 无法提取关键词 | 6 | 17.1% |
### help/schema

| 失败模式 | 次数 | 占比 |
|---------|------|------|
| 产品线不在目录中 | 6 | 17.1% |
### 树形导航

| 失败模式 | 次数 | 占比 |
|---------|------|------|
| 导航路径不匹配 | 6 | 17.1% |

## 六、召回可靠性 · 失败模式对比

| 方案 | 失败表现 | LLM可感知性 | 失败次数 |
|------|---------|------------|---------|
| Code Mode | 返回空数组 | ❌ 静默，LLM无感知 | 6/35 |
| help/schema | 返回候选列表或明确提示 | ✅ 显式，LLM知道没找到 | 6/35 |
| Embedding 语义检索 | 返回相关性低的工具 | ⚠️ 半静默，有结果但可能是错的 | 0/35 |
| 树形导航 | 走错分支后找不到 | ⚠️ 半静默 | 6/35 |

## 七、典型用例详细结果

### Code Mode

**命中案例:**

- ✅ `创建一个多维表格记录` → bitable.v1.appTableRecord.create
- ✅ `发送一条消息到群聊` → im.v1.message.create
- ✅ `获取日程列表` → calendar.v4.calendarEvent.list

**未命中案例:**

- ❌ `删除知识库节点` (期望: wiki.v2.spaceNode.move, 返回: wiki.v2.spaceMember.delete, im.v1.chatMembers.delete, bitable.v1.appRoleMember.delete, 漏掉: wiki.v2.spaceNode.move)
- ❌ `查询员工的请假记录` (期望: corehr.v1.leave.leaveRequestHistory, 返回: bitable.v1.app.get, bitable.v1.appTable.get, bitable.v1.appTable.list, 漏掉: corehr.v1.leave.leaveRequestHistory)
- ❌ `帮我约个会` (期望: calendar.v4.calendarEvent.create, 返回: 无, 漏掉: calendar.v4.calendarEvent.create)

### help/schema

**命中案例:**

- ✅ `创建一个多维表格记录` → bitable.v1.appTableRecord.create
- ✅ `发送一条消息到群聊` → im.v1.message.create
- ✅ `创建一个审批实例` → approval.v4.instance.create

**未命中案例:**

- ❌ `获取日程列表` (期望: calendar.v4.calendarEvent.list, 返回: calendar.v4.calendar.get, calendar.v4.calendarEvent.get, 漏掉: calendar.v4.calendarEvent.list)
- ❌ `删除知识库节点` (期望: wiki.v2.spaceNode.move, 返回: wiki.v2.spaceMember.delete, 漏掉: wiki.v2.spaceNode.move)
- ❌ `查询员工的请假记录` (期望: corehr.v1.leave.leaveRequestHistory, 返回: bitable.v1.appTableRecord.search, 漏掉: corehr.v1.leave.leaveRequestHistory)

### Embedding 语义检索

**命中案例:**

- ✅ `创建一个多维表格记录` → bitable.v1.appTableRecord.create
- ✅ `发送一条消息到群聊` → im.v1.message.create
- ✅ `获取日程列表` → calendar.v4.calendarEvent.list

**未命中案例:**

- ❌ `帮我约个会` (期望: calendar.v4.calendarEvent.create, 返回: corehr.v1.person.create, corehr.v1.person.patch, contact.v3.department.get, 漏掉: calendar.v4.calendarEvent.create)
- ❌ `这个文档分享给同事看看` (期望: drive.v1.permission.create, 返回: docx.v1.document.create, docx.v1.documentBlock.get, docx.v1.documentBlock.create, 漏掉: drive.v1.permission.create)
- ❌ `查一下小王的联系方式` (期望: contact.v3.user.get, contact.v3.user.list, 返回: drive.v1.file.createShortcut, sheets.v3.spreadsheetSheet.setStyle, drive.v1.file.list, 漏掉: contact.v3.user.get, contact.v3.user.list)

### 树形导航

**命中案例:**

- ✅ `创建一个多维表格记录` → bitable.v1.appTableRecord.create
- ✅ `发送一条消息到群聊` → im.v1.message.create
- ✅ `获取日程列表` → calendar.v4.calendarEvent.list

**未命中案例:**

- ❌ `删除知识库节点` (期望: wiki.v2.spaceNode.move, 返回: wiki.v2.spaceMember.delete, 漏掉: wiki.v2.spaceNode.move)
- ❌ `查询员工的请假记录` (期望: corehr.v1.leave.leaveRequestHistory, 返回: bitable.v1.app.get, bitable.v1.appTable.get, bitable.v1.appTable.list, 漏掉: corehr.v1.leave.leaveRequestHistory)
- ❌ `帮我约个会` (期望: calendar.v4.calendarEvent.create, 返回: 无, 漏掉: calendar.v4.calendarEvent.create)


## 八、评测结论

### 核心发现

1. **综合 F1 最优**: Embedding 语义检索 (F1=15.3%)
2. **召回率最优**: Embedding 语义检索 (Recall=65.2%)
3. **准确率最优**: help/schema (Precision=9.9%)
4. **Token 最省**: Embedding 语义检索 (平均 407 token/次)
5. **中文意图最优**: Embedding 语义检索 (中文召回率=50.0%)
6. **模糊意图最优**: Embedding 语义检索 (模糊召回率=58.3%)

### 关键结论

- **没有一个方案在所有维度上都最优**。通用性和可靠性之间存在根本性张力。
- **越通用（零维护）的方案**，把「理解 API」的工作越多地甩给了 LLM。
- **越可靠的方案**，越需要人工提前沉淀领域知识。
- **Token 消耗**：4 种按需加载方案相比全量下发（500+工具，20万+ token）均有显著节省。

## 九、选型建议

### 场景化推荐

| 场景 | 主方案 | 辅助方案 | 原因 |
|------|-------|---------|------|
| 飞书 MCP 内部接口发现 | help/schema | Embedding 兜底 | 领域知识深，可靠性优先 |
| 对外开放的通用 MCP | Code Mode | Embedding 补充 | 无法要求接入方维护目录 |
| 多 server 聚合网关 | 树形导航 | Code Mode 兜底 | 跨 server 边界清晰 |
| 中文模糊意图为主 | Embedding | help/schema 精确查 | 语义理解优先 |
| API 命名极度混乱 | help/schema | 无 | 其他方案都依赖命名 |

### 飞书 MCP 推荐的分层组合

```
用户意图
    ↓
01 主路径：help/schema
   利用飞书领域知识沉淀，保证核心场景召回可靠性
    ↓ 未命中
02 兜底：Embedding 语义检索
   处理目录未覆盖的模糊意图和中文口语表达
    ↓ 仍未命中
03 探索：Code Mode
   覆盖目录还没建全的边缘场景，灵活探索
    ↓ 记录未命中 case
04 反馈闭环
   异步补充到 help 目录，持续提升覆盖率
```