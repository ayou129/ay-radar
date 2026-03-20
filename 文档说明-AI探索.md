# AI 探索：Playwright 自动巡检与内容采集

> 使用纯 Claude CLI + Playwright MCP 执行，非硬编码脚本
> 数据落 DB，通过 HTML 展示（复用竞品分析的 server + 新增菜单）

## 核心方向与目的

**AI（人工智能）**——这是唯一的探索方向，不涉及其他任何领域。
所有搜索、浏览、关注、采集行为都围绕 AI 展开，包括但不限于：
AI 工具、AI 模型、AI 产品、AI 论文、AI 工作流、AI 创作、AI 编程、AI Agent 等。

将分散在各平台的 AI 动态聚合为结构化摘要，服务两个目的：
1. **自媒体选题**：作为灵感来源和信息差优势
2. **产品复刻**：发现热门工具/产品时，评估是否适合快速复刻上线到 [onemake.dev](https://onemake.dev)（一人开发者产品集合，当前产品：KeyHint — macOS 快捷键提示工具）

## ⚡ 执行流程

### 单轮巡检（广度）

> **这是每轮巡检的完整执行步骤，收到启动命令后严格按此流程执行。**

#### Step 1：准备

1. 读取本文档 + `文档说明-Playwright.md`（反检测、延迟等操作规范）
2. 查 `ai_follow_log` 当日已关注数（阈值 30）
3. 查 `ai_discovery` 已有记录的 `url` 和 `title`，用于双重去重：
   - **URL 去重**：同一链接不重复插入
   - **标题/主题去重**：浏览时对比已有 title，同一事件/话题的不同来源不重复采集（如多人转发同一公告，只保留信息量最大的一条）
4. 注入反检测脚本（`addInitScript`）

#### Step 2：浏览采集

像一个真正的 AI 从业者一样自由浏览——刷时间线、搜索感兴趣的话题、点进博主主页深挖、滚动加载更多。自主决定浏览路径。

**数据提取必须用 `browser_run_code` 执行 JS 脚本**，返回结构化 JSON（作者、内容、URL、互动量）。
**禁止用 `browser_snapshot` 提取内容数据**——snapshot 仅在需要获取元素 `ref` 进行点击/关注时使用。

> 原因：X.com 时间线的 snapshot 动辄 16k+ tokens，而 JS 提取同样信息只需 ~500 tokens。

滚动与加载：
- X.com 等平台使用无限滚动，**必须模拟滚动才能触发旧内容请求**
- 每次滚动后等待 1-3 秒（随机）让新内容渲染完毕，再读取或继续滚动

ProductHunt 采集注意：
- PH 页面动态渲染，提取前**必须先等待元素就绪**：`await page.waitForSelector('[data-test^="post-name"]', {timeout: 10000})`
- 然后通过 `[data-test^="post-item"]` 遍历产品卡片，提取名称、tagline、分类、投票数

#### Step 3：入库 + 派发分析

**入库：**
- 对照 Step 1 查到的 title 列表，跳过主题重复的内容
- `INSERT OR IGNORE` 写入 `ai_discovery`，以 `url` 去重
- 已存在的 URL 如有变化（互动数据增长等），`UPDATE summary + updated_at`
- URL 必须从页面元素 href 中提取，**禁止拼接或猜测**（⚠️ 历史教训：曾因拼接错误导致数据污染）
- **`raw_data` 必须包含评论**：采集推文时同步提取前 5-8 条评论，JSON 存入 `raw_data` 字段，供分析 Agent 使用

**派发分析 Agent（后台）：**
- 每条内容入库后，立即启动一个后台 Agent（`run_in_background: true`）
- 将 `id`、`url`、`title`、`summary`、`raw_data`、`category`、`importance` 传给 Agent
- Agent 独立完成 md 分析并自己写入 DB，主会话继续探索下一条，不等待

```
主会话：INSERT 基础数据 → 拿到 id → 启动后台 Agent(id + 数据) → 继续探索
Agent：读数据 → 撰写 md → UPDATE ai_discovery SET md='...' WHERE id=X → 结束
```

#### Step 4：深度分析（由后台 Agent 执行）

> **这是核心输出价值，不可跳过。** 每条入库记录都必须完成 md 字段写入。
> **此步骤由 Step 3 派发的后台 Agent 独立执行，不使用 Playwright，不阻塞主会话探索。**

Agent 基于收到的 summary + raw_data（含评论）撰写中文深度分析（Markdown）：

- **不是翻译/搬运**：用自己的话解读，补充背景知识、关联分析、价值判断
- **自媒体创作者视角**（核心）：
  - **选题建议**：1-2 个具体的视频/文章选题方向，含建议标题（要有吸引力）
  - **目标受众**：开发者 / AI 爱好者 / 泛科技 / 大众 / 创业者
  - **内容形式建议**：实操教程 / 深度科普 / 热点评论 / 对比横评 / 故事复盘
  - **差异化角度**：怎么做才能和别人不一样？有没有反直觉的切入点？
- **商业/创业机会**：
  - 有没有可落地的产品、工具、服务方向？反映什么底层趋势？
  - **一人公司视角**：这个方向一个人能不能做？需要什么工具组合？变现路径是什么？
- **工具复刻评估**（当内容涉及具体工具/产品时）：
  - 核心功能是什么？解决什么痛点？
  - 技术上怎么实现？需要什么技术栈？
  - 变现模式？竞品密度如何？
  - 是否适合一人开发者做？和 onemake.dev 现有产品线是否互补？
- **如果内容价值不高，直接说明**，不要硬凑选题
- **自主判断长度**：短推文 3-5 句点评即可；有深度的内容展开分析

Agent 完成后直接执行 `sqlite3 data.db "UPDATE ai_discovery SET md='...' WHERE id=X"`。

> **为什么 Agent 不用 Playwright？** 同一 Claude Code 会话内的 sub-agent 共享同一个 MCP Playwright 实例（只有一个 page 引用），与主会话的浏览器操作会互踩。分析所需的信息（summary + 评论）已在入库时存入 raw_data，无需再打开页面。

#### Step 5：社交动作

发现内容质量高、方向匹配的博主时关注：

- **关注标准**：内容强相关 + 发帖频率合理（非僵尸号）+ 粉丝/互动量级合理 + **必须是原创内容源**
- **不关注**：信息搬运型账号——以转述/翻译/搬运为主，无原创观点、无实测、无独立判断。典型特征：推文高度模板化、评论区无真实讨论、只比别人早搬运几分钟但不提供增量信息
- **优先关注**：一手信息源（官方账号、产品/论文作者）、有深度实践的独立开发者/研究者、能提供信息差的原创博主
- **执行约束**：单日 ≤ 30 个，先查 `ai_follow_log` 当日数量
- **记录**：关注前写入 `ai_follow_log`（平台、用户名、理由、时间、状态）
- **去重**：`username` 为 UNIQUE，已关注的不重复操作

#### Step 6：结束

本轮采集完成，等待下一轮 cron 触发。

### 深度调研（深度）

> **以 `ai_discovery` 中某条记录为起点，用 MCP 浏览器做定向调研，输出与自有产品相关的可落地建议。**

#### Step 1：读取上下文

1. 从 `ai_discovery` 读取目标记录的 `title`、`summary`、`md`、`raw_data`
2. 读取 `CLAUDE.md` 中「自有产品」信息，明确当前产品线和关注方向
3. 读取 `文档说明-Playwright.md`（反检测、延迟等操作规范）

#### Step 2：确定调研方向

基于记录内容与自有产品的关联，列出 3-5 个调研问题，例如：
- 这个产品/工具的竞品有哪些？各自定价和差异点？
- 用户怎么评价？核心痛点和期望是什么？
- 技术上怎么实现的？有开源方案吗？
- 和自有产品有什么交叉机会？能借鉴什么？
- 这个方向的市场规模和趋势如何？

列出问题后**先展示给用户确认**，再开始浏览器调研。

#### Step 3：MCP 浏览器调研

根据 Step 2 的问题，在以下平台搜索：
- **X.com**：产品名 + 用户反馈、竞品对比讨论
- **GitHub**：同类开源项目、技术实现方案
- **ProductHunt**：竞品页面、评论区、投票数据
- **Google**：定价模型、技术博客、市场分析

遵循 `文档说明-Playwright.md` 的反检测和频率规范。

#### Step 4：输出报告

将调研结果整理为结构化报告，**追加到该条记录的 `md` 字段末尾**（以 `---\n## 深度调研` 分隔），包含：

1. **竞品图谱**：名称、定价、核心差异点、用户规模（如有）
2. **用户痛点**：从评论/讨论中提取的真实需求和不满
3. **与自有产品的交叉机会**：能借鉴的功能、设计、定位
4. **可落地建议**：按优先级排序的功能/方向建议
5. **信息来源**：所有引用的 URL 链接

---

## 浏览参考

### 平台

- x.com（主力，搜索 + 博主主页 + 时间线）
- github.com（trending + AI 开发者主页 + 项目动态，有 follow 机制）
- [先不考虑浏览]linkedin.com（AI 从业者/研究者动态，有 follow + 推荐机制）
- producthunt.com（AI 新产品发布）
- huggingface.co/papers（每日论文）
- www.reddit.com/r/artificial
- 各 AI 产品 changelog 页面

### 监控维度

- **AI 工具/产品迭代**：官方更新公告、changelog 变化；关键词 launch / release / update / new feature
- **AI 博主发现**：高影响力博主最新推文、大量转发的技术发现、新论文解读
- **热点趋势**：24h 内高互动的 AI 推文、新出现的高频关键词
- **热门工具/产品**：别人提到、推荐、讨论的工具和产品，尤其是功能明确、用户反馈好、适合独立开发者复刻的

## 数据存储

数据库：`data.db`（项目根目录）。

### 表结构

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增主键 |
| url | TEXT UNIQUE | 原始链接，作为去重主键 |
| platform | TEXT | 来源平台：x / github / linkedin / producthunt / huggingface / reddit / other |
| author | TEXT | 作者/账号名 |
| title | TEXT | 标题（如有），同时用于主题级去重 |
| summary | TEXT | Claude 总结的内容摘要 |
| category | TEXT | 分类：tool_update / blogger_insight / paper / trend |
| importance | TEXT | 重要度：high / medium / low（Claude 判断） |
| published_at | TEXT | 内容原始发布时间 |
| discovered_at | TEXT | 首次发现时间 |
| updated_at | TEXT | 最近更新时间 |
| round_id | TEXT | 巡检轮次标识（如 2026-03-19_22:00） |
| raw_data | TEXT | JSON 格式，**必须包含评论**（供分析 Agent 使用），如 `{"replies":["...",...],"likes":7660,"views":"76万"}` |
| md | TEXT | 深度分析文章（Markdown），写入规范见 Step 4 |

### URL 采集规范

采集 URL 时**必须从浏览器地址栏或页面元素的 href 属性中提取**，禁止拼接或猜测：

- **X.com 推文**：从推文的时间戳链接（`<a href="/{author}/status/{id}">`）中提取完整 URL
- **禁止**：用推文内容中提到的用户名 + 其他推文的 status ID 拼接 URL
- **验证**：URL 中的用户名必须与推文作者一致，status ID 必须是该推文自身的 ID
- **通用规则**：所有平台的 URL 都应从页面实际链接中获取，不要手动构造

### SQL 执行注意

- **禁止在 Bash 双引号中使用 `!=`**：zsh 会对 `!` 做历史展开，导致 `!=` 被转义为 `\!=`，SQLite 报错 `unrecognized token`
- 替代方案：用 `<>` 或 `length(field) > 0` 代替 `field != ''`
- 含 JSON 或特殊字符的字段（如 `raw_data`、`md`），**必须用 Python `sqlite3` 模块写入**，不要用 Bash 拼接 SQL

### 去重与更新规则

- 以 `url` 为唯一标识，INSERT OR IGNORE 避免重复
- 以 `title` 做主题级去重，同一事件的多条转发/报道只保留信息量最大的一条
- 同一 URL 再次出现时，如有变化（互动数据增长等），更新 `summary` + `updated_at`
- 同一作者短时间内的多条内容各自独立存储，通过 `author` 字段关联查看

### md 字段 API

- `GET /api/discoveries/{id}/article` — 读取 `md` 字段，渲染为 HTML 返回
- 前端：`md` 有值的记录显示绿色"阅读"按钮，点击弹出 Modal 展示

### 关注记录表 `ai_follow_log`

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增主键 |
| platform | TEXT | 平台 |
| username | TEXT UNIQUE | 用户名，去重 |
| reason | TEXT | 关注理由 |
| followed_at | TEXT | 关注时间 |
| status | TEXT | success / failed / skipped |

## 风控策略

### 轻度异常（验证码、弹窗、元素变化）
1. 截图保存到 `.screenshots/`
2. 尝试自动解决（最多 2 次）
3. 失败 → 跳过当前动作，记录日志，继续后续任务

### 严重异常（账号锁定、手机验证、IP 封禁提示）
1. 截图 + 记录
2. 整体暂停，不再继续任何操作
3. 等待用户确认后才恢复

### 频率保护
- 遵循 `文档说明-Playwright.md` 中的随机延迟规范
- 单平台单次会话不超过 **20 次**操作
- 连续巡检轮次间隔 ≥ 10 分钟

## 使用说明

### 启动前准备

1. 确保 AI Radar 服务已运行：`python server.py`（http://localhost:8002）
2. 确保 Chrome CDP 已就绪（MCP Playwright 会自动启动）

### 启动命令

```
/loop 20m 阅读 @文档说明-AI探索.md 和 @文档说明-Playwright.md 按「单轮执行流程」执行一轮 AI 内容巡检。
```

## 持续改进

执行巡检过程中，如果发现可优化的点（流程效率、执行方式、md 分析质量、去重策略、反检测等），**不要自行修改文档或流程**，而是：

1. 将优化建议追加到下方「待讨论优化项」列表
2. 在本轮巡检结束总结中提及新增的优化建议
3. 等待用户确认后再实施修改

### 待讨论优化项

<!-- 格式：- [日期] 建议内容（发现场景） -->
- [2026-03-20] X.com 搜索 `min_faves` 过滤效果有限，"model""agent""release" 等通用词噪音太大。建议维护一个高信号搜索词模板列表，按主题轮换使用（如 `from:账号列表`、`具体产品名 + launch`），而非泛关键词+互动量过滤。（本轮第一次搜索返回大量营销号和星座号）
