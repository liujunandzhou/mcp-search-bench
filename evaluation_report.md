# 飞书 OpenAPI MCP 工具搜索方案评测报告

> 生成时间: 2026-03-15 14:18:44

> 评测用例数: 35

## 一、总体评测结果

| 方案 | 平均召回率 | 平均准确率 | 平均F1 | 初始Token | 平均Token/次 | 总Token | 平均搜索轮次 |
|------|-----------|-----------|--------|----------|-------------|---------|------------|
| Code Mode | 54.8% | 14.9% | 22.8% | 337 | 508 | 17,790 | 1.0 |
| help/schema | 49.0% | 23.8% | 29.9% | 226 | 1,590 | 55,636 | 4.5 |
| Embedding 语义检索 | 73.8% | 23.8% | 33.4% | 191 | 288 | 10,067 | 1.0 |
| 树形导航 | 51.4% | 26.7% | 32.0% | 328 | 1,414 | 49,481 | 6.1 |

## 二、按意图类型细分

### 精确意图

| 方案 | 用例数 | 召回率 | 准确率 | F1 | 平均Token |
|------|-------|--------|--------|-----|----------|
| Code Mode | 10 | 70.0% | 16.0% | 25.7% | 504 |
| help/schema | 10 | 60.0% | 26.3% | 34.0% | 1,595 |
| Embedding 语义检索 | 10 | 85.0% | 18.5% | 30.2% | 303 |
| 树形导航 | 10 | 85.0% | 54.2% | 60.7% | 659 |
### 模糊意图

| 方案 | 用例数 | 召回率 | 准确率 | F1 | 平均Token |
|------|-------|--------|--------|-----|----------|
| Code Mode | 10 | 40.0% | 10.0% | 15.7% | 507 |
| help/schema | 10 | 40.0% | 13.5% | 19.7% | 1,541 |
| Embedding 语义检索 | 10 | 76.7% | 29.3% | 38.5% | 266 |
| 树形导航 | 10 | 30.0% | 8.0% | 12.4% | 2,451 |
### 跨域意图

| 方案 | 用例数 | 召回率 | 准确率 | F1 | 平均Token |
|------|-------|--------|--------|-----|----------|
| Code Mode | 5 | 43.3% | 20.0% | 27.1% | 528 |
| help/schema | 5 | 43.3% | 22.7% | 29.4% | 1,794 |
| Embedding 语义检索 | 5 | 33.3% | 16.0% | 21.4% | 303 |
| 树形导航 | 5 | 60.0% | 44.0% | 49.0% | 1,606 |
### 中文口语意图

| 方案 | 用例数 | 召回率 | 准确率 | F1 | 平均Token |
|------|-------|--------|--------|-----|----------|
| Code Mode | 10 | 60.0% | 16.0% | 24.8% | 504 |
| help/schema | 10 | 50.0% | 32.0% | 36.3% | 1,531 |
| Embedding 语义检索 | 10 | 80.0% | 27.3% | 37.4% | 286 |
| 树形导航 | 10 | 35.0% | 9.3% | 14.5% | 1,035 |

## 三、按难度细分

### 简单

| 方案 | 用例数 | 召回率 | 准确率 | F1 |
|------|-------|--------|--------|-----|
| Code Mode | 7 | 85.7% | 17.1% | 28.6% |
| help/schema | 7 | 71.4% | 31.9% | 40.5% |
| Embedding 语义检索 | 7 | 85.7% | 17.1% | 28.6% |
| 树形导航 | 7 | 100.0% | 58.3% | 70.0% |
### 中等

| 方案 | 用例数 | 召回率 | 准确率 | F1 |
|------|-------|--------|--------|-----|
| Code Mode | 12 | 55.6% | 18.3% | 26.8% |
| help/schema | 12 | 55.6% | 25.4% | 32.9% |
| Embedding 语义检索 | 12 | 65.3% | 21.5% | 30.9% |
| 树形导航 | 12 | 58.3% | 34.4% | 38.1% |
### 困难

| 方案 | 用例数 | 召回率 | 准确率 | F1 |
|------|-------|--------|--------|-----|
| Code Mode | 16 | 40.6% | 11.2% | 17.3% |
| help/schema | 16 | 34.4% | 19.0% | 23.1% |
| Embedding 语义检索 | 16 | 75.0% | 28.3% | 37.4% |
| 树形导航 | 16 | 25.0% | 7.1% | 10.9% |

## 四、Token 消耗对比

| 方案 | 初始注入 | 搜索结果(平均) | 总计(平均) | 评价 |
|------|---------|---------------|----------|------|
| Code Mode | ~337 | ~171 | ~508 | ✅ 低 |
| help/schema | ~226 | ~1,364 | ~1,590 | ⚠️ 中 |
| Embedding 语义检索 | ~191 | ~97 | ~288 | ✅ 低 |
| 树形导航 | ~328 | ~1,086 | ~1,414 | ⚠️ 中 |

## 五、失败模式分析

### help/schema

| 失败模式 | 次数 | 占比 |
|---------|------|------|
| 产品线不在目录中 | 2 | 5.7% |
### 树形导航

| 失败模式 | 次数 | 占比 |
|---------|------|------|
| 导航路径不匹配 | 2 | 5.7% |

## 六、召回可靠性 · 失败模式对比

| 方案 | 失败表现 | LLM可感知性 | 失败次数 |
|------|---------|------------|---------|
| Code Mode | 返回空数组 | ❌ 静默，LLM无感知 | 0/35 |
| help/schema | 返回候选列表或明确提示 | ✅ 显式，LLM知道没找到 | 2/35 |
| Embedding 语义检索 | 返回相关性低的工具 | ⚠️ 半静默，有结果但可能是错的 | 0/35 |
| 树形导航 | 走错分支后找不到 | ⚠️ 半静默 | 2/35 |

## 七、典型用例详细结果

### Code Mode

**命中案例:**

- ✅ `创建一个多维表格记录` → bitable.v1.appTableRecord.create
- ✅ `发送一条消息到群聊` → im.v1.message.create
- ✅ `创建一个审批实例` → approval.v4.instance.create

**未命中案例:**

- ❌ `获取日程列表` (期望: calendar.v4.calendarEvent.list, 返回: calendar.v4.calendar.get, calendar.v4.calendarEvent.get, calendar.v4.calendar.create, 漏掉: calendar.v4.calendarEvent.list)
- ❌ `删除知识库节点` (期望: wiki.v2.spaceNode.move, 返回: wiki.v2.spaceMember.delete, wiki.v2.space.create, wiki.v2.space.get, 漏掉: wiki.v2.spaceNode.move)
- ❌ `查询员工的请假记录` (期望: corehr.v1.leave.leaveRequestHistory, 返回: attendance.v1.userApproval.query, bitable.v1.appTableRecord.search, attendance.v1.group.search, 漏掉: corehr.v1.leave.leaveRequestHistory)

### help/schema

**命中案例:**

- ✅ `创建一个多维表格记录` → bitable.v1.appTableRecord.create
- ✅ `发送一条消息到群聊` → im.v1.message.create
- ✅ `创建一个审批实例` → approval.v4.instance.create

**未命中案例:**

- ❌ `获取日程列表` (期望: calendar.v4.calendarEvent.list, 返回: calendar.v4.calendarEvent.get, 漏掉: calendar.v4.calendarEvent.list)
- ❌ `删除知识库节点` (期望: wiki.v2.spaceNode.move, 返回: wiki.v2.spaceMember.delete, 漏掉: wiki.v2.spaceNode.move)
- ❌ `批量更新多维表格记录` (期望: bitable.v1.appTableRecord.batchUpdate, 返回: bitable.v1.app.update, bitable.v1.appTable.batchCreate, bitable.v1.appTable.batchDelete, 漏掉: bitable.v1.appTableRecord.batchUpdate)

### Embedding 语义检索

**命中案例:**

- ✅ `发送一条消息到群聊` → im.v1.message.create
- ✅ `获取日程列表` → calendar.v4.calendarEvent.list
- ✅ `创建一个审批实例` → approval.v4.instance.create

**未命中案例:**

- ❌ `创建一个多维表格记录` (期望: bitable.v1.appTableRecord.create, 返回: bitable.v1.app.create, bitable.v1.appTableRecord.get, bitable.v1.app.get, 漏掉: bitable.v1.appTableRecord.create)
- ❌ `公司组织架构是怎样的` (期望: contact.v3.department.list, contact.v3.department.children, 返回: corehr.v1.company.list, 漏掉: contact.v3.department.list, contact.v3.department.children)
- ❌ `在多维表格里新建一条记录，然后发消息通知群里的人` (期望: bitable.v1.appTableRecord.create, im.v1.message.create, 返回: im.v1.chatMembers.isInChat, bitable.v1.app.create, bitable.v1.appTableRecord.update, 漏掉: im.v1.message.create, bitable.v1.appTableRecord.create)

### 树形导航

**命中案例:**

- ✅ `创建一个多维表格记录` → bitable.v1.appTableRecord.create
- ✅ `发送一条消息到群聊` → im.v1.message.create
- ✅ `获取日程列表` → calendar.v4.calendarEvent.list

**未命中案例:**

- ❌ `查询员工的请假记录` (期望: corehr.v1.leave.leaveRequestHistory, 返回: bitable.v1.appTableRecord.get, bitable.v1.appTableRecord.search, corehr.v2.employee.search, 漏掉: corehr.v1.leave.leaveRequestHistory)
- ❌ `我想把一些数据写进表格里` (期望: bitable.v1.appTableRecord.create, bitable.v1.appTableRecord.batchCreate, sheets.v3.spreadsheetSheet.write, 返回: bitable.v1.app.create, bitable.v1.app.get, bitable.v1.app.update, 漏掉: bitable.v1.appTableRecord.batchCreate, sheets.v3.spreadsheetSheet.write, bitable.v1.appTableRecord.create)
- ❌ `帮我约个会` (期望: calendar.v4.calendarEvent.create, 返回: calendar.v4.calendar.create, calendar.v4.calendar.delete, calendar.v4.calendar.get, 漏掉: calendar.v4.calendarEvent.create)


## 八、评测结论

### 核心发现

1. **综合 F1 最优**: Embedding 语义检索 (F1=33.4%)
2. **召回率最优**: Embedding 语义检索 (Recall=73.8%)
3. **准确率最优**: 树形导航 (Precision=26.7%)
4. **Token 最省**: Embedding 语义检索 (平均 288 token/次)
5. **中文意图最优**: Embedding 语义检索 (中文召回率=80.0%)
6. **模糊意图最优**: Embedding 语义检索 (模糊召回率=76.7%)

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