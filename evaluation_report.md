# 飞书 OpenAPI MCP 工具搜索方案评测报告

> 生成时间: 2026-03-15 15:11:20

> 评测用例数: 35

## 一、候选集质量（搜索机制评估）

> help/schema 返回完整产品线目录，目录大小不是噪声，是设计意图。

| 方案 | 候选召回率 | 候选集大小 | 噪声率/目录大小 | 初始Token | 平均Token/次 | 总Token | 平均搜索轮次 |
|------|----------|----------|--------------|----------|-------------|---------|------------|
| Code Mode | 54.8% | 5.0 | 85.1% | 337 | 508 | 17,790 | 1.0 |
| help/schema | 91.4% | 39.2 | 目录 39 个 | 226 | 2,080 | 72,801 | 6.1 |
| Embedding 语义检索 | 73.8% | 4.5 | 76.2% | 191 | 288 | 10,067 | 1.0 |
| 树形导航 | 51.4% | 3.7 | 67.6% | 328 | 1,414 | 49,481 | 6.1 |

## 二、最终选择质量（模拟 LLM 从候选集选择）

> 假设 LLM 能从候选集中正确挑选期望工具，但会受噪声影响产生误选。

| 方案 | 选择准确率 | 选择召回率 | 选择F1 |
|------|----------|----------|--------|
| Code Mode | 51.1% | 54.8% | 52.5% |
| help/schema | 87.1% | 91.4% | 89.2% |
| Embedding 语义检索 | 72.7% | 73.8% | 72.4% |
| 树形导航 | 51.0% | 51.4% | 50.6% |

## 三、按意图类型细分

### 精确意图

| 方案 | 用例数 | 候选召回率 | 噪声率 | 选择准确率 | 选择F1 | 平均Token |
|------|-------|----------|--------|----------|--------|----------|
| Code Mode | 10 | 70.0% | 84.0% | 60.7% | 65.0% | 504 |
| help/schema | 10 | 90.0% | 95.8% | 85.7% | 87.8% | 1,902 |
| Embedding 语义检索 | 10 | 85.0% | 81.5% | 76.6% | 80.1% | 303 |
| 树形导航 | 10 | 85.0% | 45.8% | 83.6% | 83.3% | 659 |
### 模糊意图

| 方案 | 用例数 | 候选召回率 | 噪声率 | 选择准确率 | 选择F1 | 平均Token |
|------|-------|----------|--------|----------|--------|----------|
| Code Mode | 10 | 40.0% | 90.0% | 34.8% | 37.2% | 507 |
| help/schema | 10 | 80.0% | 75.8% | 76.2% | 78.0% | 1,655 |
| Embedding 语义检索 | 10 | 76.7% | 70.7% | 77.0% | 75.9% | 266 |
| 树形导航 | 10 | 30.0% | 72.0% | 26.2% | 28.0% | 2,451 |
### 跨域意图

| 方案 | 用例数 | 候选召回率 | 噪声率 | 选择准确率 | 选择F1 | 平均Token |
|------|-------|----------|--------|----------|--------|----------|
| Code Mode | 5 | 43.3% | 80.0% | 62.4% | 51.1% | 528 |
| help/schema | 5 | 100.0% | 95.8% | 95.2% | 97.6% | 3,390 |
| Embedding 语义检索 | 5 | 33.3% | 84.0% | 47.3% | 39.0% | 303 |
| 树形导航 | 5 | 60.0% | 56.0% | 70.0% | 63.6% | 1,606 |
### 中文口语意图

| 方案 | 用例数 | 候选召回率 | 噪声率 | 选择准确率 | 选择F1 | 平均Token |
|------|-------|----------|--------|----------|--------|----------|
| Code Mode | 10 | 60.0% | 84.0% | 52.3% | 55.9% | 504 |
| help/schema | 10 | 100.0% | 95.0% | 95.2% | 97.6% | 2,028 |
| Embedding 语义检索 | 10 | 80.0% | 72.7% | 77.1% | 77.7% | 286 |
| 树形导航 | 10 | 35.0% | 90.7% | 33.6% | 33.9% | 1,035 |

## 四、按难度细分

### 简单

| 方案 | 用例数 | 候选召回率 | 噪声率 | 选择准确率 | 选择F1 |
|------|-------|----------|--------|----------|--------|
| Code Mode | 7 | 85.7% | 82.9% | 73.9% | 79.4% |
| help/schema | 7 | 100.0% | 96.7% | 95.2% | 97.6% |
| Embedding 语义检索 | 7 | 85.7% | 82.9% | 73.9% | 79.4% |
| 树形导航 | 7 | 100.0% | 41.7% | 92.6% | 96.1% |
### 中等

| 方案 | 用例数 | 候选召回率 | 噪声率 | 选择准确率 | 选择F1 |
|------|-------|----------|--------|----------|--------|
| Code Mode | 12 | 55.6% | 81.7% | 56.1% | 55.1% |
| help/schema | 12 | 91.7% | 93.5% | 87.3% | 89.4% |
| Embedding 语义检索 | 12 | 65.3% | 78.5% | 69.3% | 66.2% |
| 树形导航 | 12 | 58.3% | 65.6% | 60.3% | 58.1% |
### 困难

| 方案 | 用例数 | 候选召回率 | 噪声率 | 选择准确率 | 选择F1 |
|------|-------|----------|--------|----------|--------|
| Code Mode | 16 | 40.6% | 88.8% | 37.4% | 38.7% |
| help/schema | 16 | 87.5% | 84.2% | 83.3% | 85.4% |
| Embedding 语义检索 | 16 | 75.0% | 71.7% | 74.7% | 73.9% |
| 树形导航 | 16 | 25.0% | 80.4% | 25.8% | 25.0% |

## 五、Token 消耗对比

| 方案 | 初始注入 | 搜索结果(平均) | 总计(平均) | 评价 |
|------|---------|---------------|----------|------|
| Code Mode | ~337 | ~171 | ~508 | 低 |
| help/schema | ~226 | ~1,854 | ~2,080 | 中 |
| Embedding 语义检索 | ~191 | ~97 | ~288 | 低 |
| 树形导航 | ~328 | ~1,086 | ~1,414 | 中 |

## 六、失败模式分析

### help/schema

| 失败模式 | 次数 | 占比 |
|---------|------|------|
| 产品线不在目录中 | 2 | 5.7% |
### 树形导航

| 失败模式 | 次数 | 占比 |
|---------|------|------|
| 导航路径不匹配 | 2 | 5.7% |

## 七、召回可靠性 · 失败模式对比

| 方案 | 失败表现 | LLM可感知性 | 失败次数 |
|------|---------|------------|---------|
| Code Mode | 返回空数组 | 静默，LLM无感知 | 0/35 |
| help/schema | 返回候选列表或明确提示 | 显式，LLM知道没找到 | 2/35 |
| Embedding 语义检索 | 返回相关性低的工具 | 半静默，有结果但可能是错的 | 0/35 |
| 树形导航 | 走错分支后找不到 | 半静默 | 2/35 |

## 八、典型用例详细结果

### Code Mode

**命中案例:**

- `创建一个多维表格记录` -> bitable.v1.appTableRecord.create
- `发送一条消息到群聊` -> im.v1.message.create
- `创建一个审批实例` -> approval.v4.instance.create

**未命中案例:**

- `获取日程列表` (期望: calendar.v4.calendarEvent.list, 返回: calendar.v4.calendar.get, calendar.v4.calendarEvent.get, calendar.v4.calendar.create, 漏掉: calendar.v4.calendarEvent.list)
- `删除知识库节点` (期望: wiki.v2.spaceNode.move, 返回: wiki.v2.spaceMember.delete, wiki.v2.space.create, wiki.v2.space.get, 漏掉: wiki.v2.spaceNode.move)
- `查询员工的请假记录` (期望: corehr.v1.leave.leaveRequestHistory, 返回: attendance.v1.userApproval.query, bitable.v1.appTableRecord.search, attendance.v1.group.search, 漏掉: corehr.v1.leave.leaveRequestHistory)

### help/schema

**命中案例:**

- `创建一个多维表格记录` -> bitable.v1.appTableRecord.create
- `发送一条消息到群聊` -> im.v1.message.create
- `获取日程列表` -> calendar.v4.calendarEvent.list

**未命中案例:**

- `查询员工的请假记录` (期望: corehr.v1.leave.leaveRequestHistory, 返回: bitable.v1.app.create, bitable.v1.app.get, bitable.v1.app.update, 漏掉: corehr.v1.leave.leaveRequestHistory)
- `谁还没看我发的那条信息` (期望: im.v1.message.readUsers, 返回: 无, 漏掉: im.v1.message.readUsers)
- `找一个词的解释` (期望: baike.v1.entity.search, baike.v1.entity.match, 返回: 无, 漏掉: baike.v1.entity.search, baike.v1.entity.match)

### Embedding 语义检索

**命中案例:**

- `发送一条消息到群聊` -> im.v1.message.create
- `获取日程列表` -> calendar.v4.calendarEvent.list
- `创建一个审批实例` -> approval.v4.instance.create

**未命中案例:**

- `创建一个多维表格记录` (期望: bitable.v1.appTableRecord.create, 返回: bitable.v1.app.create, bitable.v1.appTableRecord.get, bitable.v1.app.get, 漏掉: bitable.v1.appTableRecord.create)
- `公司组织架构是怎样的` (期望: contact.v3.department.list, contact.v3.department.children, 返回: corehr.v1.company.list, 漏掉: contact.v3.department.children, contact.v3.department.list)
- `在多维表格里新建一条记录，然后发消息通知群里的人` (期望: bitable.v1.appTableRecord.create, im.v1.message.create, 返回: im.v1.chatMembers.isInChat, bitable.v1.app.create, bitable.v1.appTableRecord.update, 漏掉: bitable.v1.appTableRecord.create, im.v1.message.create)

### 树形导航

**命中案例:**

- `创建一个多维表格记录` -> bitable.v1.appTableRecord.create
- `发送一条消息到群聊` -> im.v1.message.create
- `获取日程列表` -> calendar.v4.calendarEvent.list

**未命中案例:**

- `查询员工的请假记录` (期望: corehr.v1.leave.leaveRequestHistory, 返回: bitable.v1.appTableRecord.get, bitable.v1.appTableRecord.search, corehr.v2.employee.search, 漏掉: corehr.v1.leave.leaveRequestHistory)
- `我想把一些数据写进表格里` (期望: bitable.v1.appTableRecord.create, bitable.v1.appTableRecord.batchCreate, sheets.v3.spreadsheetSheet.write, 返回: bitable.v1.app.create, bitable.v1.app.get, bitable.v1.app.update, 漏掉: bitable.v1.appTableRecord.create, sheets.v3.spreadsheetSheet.write, bitable.v1.appTableRecord.batchCreate)
- `帮我约个会` (期望: calendar.v4.calendarEvent.create, 返回: calendar.v4.calendar.create, calendar.v4.calendar.delete, calendar.v4.calendar.get, 漏掉: calendar.v4.calendarEvent.create)


## 九、评测结论

### 核心发现

1. **候选召回率最优**: help/schema (Candidate Recall=91.4%)
2. **噪声率最低**: 树形导航 (Noise Ratio=67.6%)
3. **选择 F1 最优**: help/schema (Selection F1=89.2%)
4. **选择准确率最优**: help/schema (Selection Precision=87.1%)
5. **Token 最省**: Embedding 语义检索 (平均 288 token/次)
6. **中文意图最优**: help/schema (中文候选召回率=100.0%)
7. **模糊意图最优**: help/schema (模糊候选召回率=80.0%)

### 关键结论

- **候选召回率是搜索层的核心指标**：候选集没覆盖到，LLM 再强也选不出来。
- **噪声率影响 LLM 最终选择质量**：候选集越干净，LLM 选错的概率越低、token 浪费越少。
- **没有一个方案在所有维度上都最优**。通用性和可靠性之间存在根本性张力。
- **越通用（零维护）的方案**，把「理解 API」的工作越多地甩给了 LLM。
- **越可靠的方案**，越需要人工提前沉淀领域知识。
- **Token 消耗**：4 种按需加载方案相比全量下发（500+工具，20万+ token）均有显著节省。

## 十、选型建议

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
    |
01 主路径：help/schema
   利用飞书领域知识沉淀，保证核心场景召回可靠性
    | 未命中
02 兜底：Embedding 语义检索
   处理目录未覆盖的模糊意图和中文口语表达
    | 仍未命中
03 探索：Code Mode
   覆盖目录还没建全的边缘场景，灵活探索
    | 记录未命中 case
04 反馈闭环
   异步补充到 help 目录，持续提升覆盖率
```