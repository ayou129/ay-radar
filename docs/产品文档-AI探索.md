# AI 探索：Playwright 自动巡检与内容采集

> 使用纯 Claude CLI + Playwright MCP 执行，非硬编码脚本
> 数据落 DB，通过 HTML 展示（复用竞品分析的 server + 新增菜单）

## 探索方向和目的

**AI（人工智能）** 是核心探索方向。所有搜索、浏览、关注、采集行为围绕 AI 展开。

将分散在各平台的 AI 动态聚合为结构化摘要，服务两个目的：
1. **自媒体选题**：作为灵感来源和信息差优势
2. **产品机会**：发现热门工具/产品时，评估是否适合复刻或借鉴优化到自有产品线

### 自有产品

- **KeyHint**（[onemake.dev/keyhint](https://onemake.dev/keyhint)）：长按 ⌘ Command 键，即刻显示当前 macOS 应用的所有快捷键，松开即消失
  - 技术栈：Swift / macOS 原生（≥ 13.0 Ventura）
  - 定位：一人开发者免费产品，隶属 [onemake.dev](https://onemake.dev)（Small, focused tools for Mac & iOS users）
  - 关注方向：功能拓展、变现路径、同类或相邻产品动态、**iOS 端产品机会**

### 探索优先级

- **L1 核心**：AI 全领域广度探索（工具、模型、产品、趋势、实践），每轮必须覆盖
- **L2 微调**：`user_note` 中的正面/负面反馈，在同等质量下倾斜方向，不缩小探索范围
- **L2 PC 独立游戏**：一人可做的 PC 端游方向（AI 辅助游戏 UI/美术生产、独立游戏开发工具链、小体量游戏的成功案例），同等质量下关注
- **L3 开放**：非 AI 但有价值的内容（indie dev 实战、macOS/iOS 工具生态、创业方法论等），允许少量采集

## 探索流程

### 单轮巡检（广度）

> **这是每轮巡检的完整执行步骤，收到启动命令后严格按此流程执行。**

#### Step 1：准备

1. 读取本文档 + Playwright 操作规范（反检测、延迟等，自动加载自用户级 rules）
2. 查 `ai_follow_log` 当日已关注数（阈值 30）
3. 查 `ai_discovery` 已有记录的 `url` 和 `title`，用于双重去重：
   - **URL 去重**：同一链接不重复插入
   - **标题/主题去重**：浏览时对比已有 title，同一事件/话题的不同来源不重复采集（如多人转发同一公告，只保留信息量最大的一条）
4. 查 `ai_discovery` 中有 `user_note` 的记录，了解用户偏好反馈（参考上方「探索优先级」L2 定义）
5. 注入反检测脚本（`addInitScript`）

#### Step 2：浏览采集

像一个真正的 AI 从业者一样自由浏览——刷时间线、搜索感兴趣的话题、点进博主主页深挖、滚动加载更多。自主决定浏览路径和关键词选择。

搜索关键词：
- **控制在 2-3 个词**，长组合词在多数平台返回空结果
- 关键词在哪个平台搜由内容特性决定，不强制跨平台

时间范围：
- **只采集近一个月内的内容**（X.com 搜索加 `since:YYYY-MM-DD`），避免采集过时信息

数据提取方式：
- **用 `browser_run_code` 执行 JS 脚本**提取结构化 JSON（作者、内容、URL、互动量）
- **禁止用 `browser_snapshot` 提取内容数据**——snapshot 仅在需要获取元素 `ref` 进行点击/关注时使用
- 原因：X.com 时间线的 snapshot 动辄 16k+ tokens，而 JS 提取同样信息只需 ~500 tokens

滚动与数据完整性：
- 无限滚动平台（X.com、Reddit）使用虚拟列表，旧 DOM 节点会被回收
- 必须采用**滚动-提取-累积**模式，而非滚动结束后一次性提取：
  1. 每滚动 3-5 次，立即用 JS 提取当前可见内容，追加到累积数组（用 URL 去重）
  2. 重复直到内容开始明显重复或超出时间范围
  3. **禁止**只提取首屏数据就离开——首屏通常只有 5-10 条，远不够覆盖
- 一页可展示全部内容的平台（GitHub Trending、ProductHunt leaderboard）无需此模式
- 每次滚动后等待 1-3 秒（随机）让新内容渲染完毕

平台注意事项：
- **ProductHunt**：页面动态渲染，提取前必须先等待产品列表元素就绪再提取
- **X.com**：首页时间线信噪比通常高于搜索，建议优先刷时间线（"为你推荐"+"正在关注"），搜索作为补充

博主发现路径（X.com）：
- **搜索结果右侧**"推荐关注"——搜索 AI 关键词时自动出现
- **博主主页侧边栏**"你可能会喜欢"——浏览高质量博主时查看
- **关注后弹出**"已推荐"列表——关注某人后 X 推荐同领域账号
- 发现感兴趣的推荐账号时，快速浏览其最近几条推文判断是否符合关注标准

监控维度（浏览时关注什么）：
- **AI 工具/产品迭代**：官方更新公告、changelog 变化
- **AI 博主发现**：高影响力博主最新推文、大量转发的技术发现、新论文解读
- **热点趋势**：高互动的 AI 推文、新出现的高频关键词
- **热门工具/产品**：别人提到、推荐、讨论的工具和产品，尤其适合独立开发者复刻的
- **Prompt / Skill / Spec 实践**：高质量的 prompt 工程实践、SKILL.md 模板、Spec 驱动开发、Agent 工作流等实战内容

#### Step 3：入库 + 派发分析

**入库：**
- 对照 Step 1 查到的 title 列表，跳过主题重复的内容
- `INSERT OR IGNORE` 写入 `ai_discovery`，以 `url` 去重
- 已存在的 URL 如有变化（互动数据增长等），`UPDATE summary + updated_at`
- URL 必须从页面元素 href 中提取，**禁止拼接或猜测**（⚠️ 历史教训：曾因拼接错误导致数据污染）
- `raw_data` 是分析 Agent 的**主要信息来源**，必须尽量丰富：
  - X.com：完整推文文本 + 互动数据 + 有价值的评论
  - ProductHunt：进入产品详情页提取完整描述 + maker 评论 + 前几条社区评论
  - GitHub：README 摘要 + 核心特性 + star/fork 数据
  - HuggingFace：论文摘要 + 方法概述
  - **原则**：raw_data 信息量不足时，分析 Agent 写出的 md 质量会明显下降，采集阶段多花 30 秒远好过分析阶段凭空编造

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

Agent 基于收到的 summary + raw_data 撰写中文深度分析（Markdown）：

- **信息补充机制**：优先使用 raw_data 中的信息；如果 raw_data 信息量不足以支撑有深度的分析（如只有一句 tagline），Agent 应先用 `WebSearch` / `WebFetch` 搜索补充背景信息（产品官网、相关评测、技术文档），再撰写分析
- **不是翻译/搬运**：用自己的话解读，补充背景知识、关联分析、价值判断
- **自主判断深度和长度**：内容价值不高就 3-5 句点评，不要硬凑；有深度的内容展开分析
- 以下维度**按需展开**，不是每条都要覆盖全部：
  - **自媒体创作者视角**：选题方向、目标受众、差异化角度
  - **商业/创业机会**：可落地的产品/服务方向，一人公司视角
  - **工具复刻评估**（当内容涉及具体工具/产品时）：核心功能、技术栈、变现模式、竞品密度、是否适合一人开发者、与 onemake.dev 是否互补

Agent 完成后用 Python `sqlite3` 模块写入 DB。

> **为什么 Agent 不用 Playwright？** 同一 Claude Code 会话内的 sub-agent 共享同一个 MCP Playwright 实例（只有一个 page 引用），与主会话的浏览器操作会互踩。Agent 需要补充信息时使用 `WebSearch` / `WebFetch`（HTTP 请求，不依赖浏览器实例）。

#### Step 5：社交动作

发现内容质量高、方向匹配的博主时关注：

- **关注标准**：内容强相关 + 发帖频率合理（非僵尸号）+ 粉丝/互动量级合理 + **必须是原创内容源**
- **不关注**：信息搬运型账号——以转述/翻译/搬运为主，无原创观点、无实测、无独立判断
- **优先关注**：一手信息源（官方账号、产品/论文作者）、有深度实践的独立开发者/研究者、能提供信息差的原创博主
- **执行约束**：单日 ≤ 50 个，先查 `ai_follow_log` 当日数量
- **记录**：关注前写入 `ai_follow_log`（平台、用户名、理由、时间、状态）
- **去重**：`username` 为 UNIQUE，已关注的不重复操作

#### Step 6：结束

1. 输出本轮总结（采集概览 + 高价值发现），必须包含：
   - **Idea 发现**：适合复刻、做选题、或有商业潜力的 idea，逐条追加到本文档「Idea 发现」列表
   - **优化建议**：流程/效率/质量方面的可优化点，追加到本文档「待讨论优化项」列表

### 深度调研（深度）

> **用 MCP 浏览器做定向深度调研，支持三种输入方式：**
> - `#<id>`：以 `ai_discovery` 中某条记录为起点展开
> - 自由文字：围绕用户描述的想法、话题、趋势进行探索
> - 自有产品：针对本文档「自有产品」做竞品/拓展方向调研

#### Step 1：读取上下文

1. **若输入为 `#<id>`**：从 `ai_discovery` 读取该记录的 `title`、`summary`、`md`、`raw_data`
2. **若输入为自由文字或产品调研**：以用户描述作为调研起点
3. 读取本文档「自有产品」信息，明确当前产品线和关注方向
4. 读取 Playwright 操作规范（反检测、延迟等，自动加载自用户级 rules）

#### Step 2：确定调研方向

基于输入内容，列出 3-5 个调研问题，例如：
- 这个产品/工具/方向的竞品有哪些？各自定价和差异点？
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

遵循 Playwright 操作规范的反检测和频率规范（自动加载自用户级 rules）。

#### Step 4：输出报告

将调研结果整理为结构化报告。**若输入为 `#<id>`**，追加到该条记录的 `md` 字段末尾（以 `---\n## 深度调研` 分隔）；**若为自由输入**，直接在对话中输出。报告包含：

1. **竞品图谱**：名称、定价、核心差异点、用户规模（如有）
2. **用户痛点**：从评论/讨论中提取的真实需求和不满
3. **与自有产品的交叉机会**：能借鉴的功能、设计、定位
4. **可落地建议**：按优先级排序的功能/方向建议
5. **信息来源**：所有引用的 URL 链接

---

## 浏览平台

- x.com（搜索 + 博主主页 + 时间线，适度浏览，不必每轮都以 X 为主）
- github.com（trending + AI 开发者主页 + 项目动态，有 follow 机制）
- producthunt.com（AI 新产品发布）
- huggingface.co/papers（每日论文）
- www.reddit.com/r/artificial
- 各 AI 产品 changelog 页面
- [先不考虑] linkedin.com
- [不再采集] zhihu.com（信息密度低，缺乏一手工具发现）

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
| raw_data | TEXT | JSON 格式，含互动数据和评论（如有），供分析 Agent 使用 |
| md | TEXT | 深度分析文章（Markdown），写入规范见 Step 4 |
| user_note | TEXT | 用户备注——主观评价、关联 idea、方向偏好等，巡检时作为 L2 探索参考 |

### 采集规则

**URL 规范：**
- URL 必须从页面元素 href 中提取，**禁止拼接或猜测**
- X.com 推文：从时间戳链接提取，URL 中的用户名必须与推文作者一致

**去重与更新：**
- 以 `url` 为唯一标识，INSERT OR IGNORE 避免重复
- 以 `title` 做主题级去重，同一事件只保留信息量最大的一条
- 同一 URL 再次出现且有变化时，更新 `summary` + `updated_at`

**SQL 注意：**
- 含特殊字符的字段（`raw_data`、`md`），**必须用 Python `sqlite3` 模块写入**

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
3. 失败 → 跳过当前动作，继续后续任务

### 严重异常（账号锁定、手机验证、IP 封禁提示）
1. 截图 + 记录
2. 整体暂停，不再继续任何操作
3. 等待用户确认后才恢复

## 持续改进

执行巡检过程中发现可优化的点，**不要自行修改文档或流程**，而是：

1. 将优化建议追加到「待讨论优化项」
2. 将发现的 Idea 追加到「Idea 发现」
3. 在本轮结束总结中提及
4. 等待用户确认后再实施修改

### 待讨论优化项

<!-- 格式：- [日期] 建议内容（发现场景） -->
- [2026-03-20] X.com 搜索 `min_faves` 过滤效果有限，通用词噪音太大。建议维护高信号搜索词模板列表，按主题轮换使用
- [2026-03-20] X.com 首页时间线信噪比高于搜索结果，建议优先刷时间线，搜索作为补充
- [2026-03-20] GitHub Trending 和 ProductHunt 跨轮重复率高，建议建立近期已采集项目快速检查列表
- [2026-03-21] 本文档本质上就是一个 Claude Code SKILL，后期改造为标准 SKILL.md 格式放入 `~/.claude/skills/`，实现 `/ai-explore` 一键调用。参考 [gstack](https://github.com/garrytan/gstack) 的结构
- [2026-03-21] GitHub Trending 和 ProductHunt 本轮几乎全部重复，建议将这两个平台降为隔轮检查，或只在有新日期数据时访问（节省操作配额）
- [2026-03-21] HuggingFace Daily Papers 当日更新时间较晚（UTC），早间巡检容易与前一天重复，建议下午/晚间巡检时再访问
- [2026-03-21] X.com 时间线信噪比确认高于搜索结果——本轮时间线发现了 Cursor/VESPER/Schoger 等高价值内容，搜索结果多为低互动转载
- [2026-03-21] GitHub Trending 连续两轮几乎全部重复，建议降频为隔轮检查或仅在新日期数据时访问
- [2026-03-21] ProductHunt 今日新品质量尚可（Novi Notes、Caplo、Design Agent），但投票数普遍较低（<20），建议关注 Featured 而非 All 以提高信噪比
- [2026-03-23] MCP 配置文件应放项目根目录 `.mcp.json` 而非 `.claude/.mcp.json`——后者不会被 Claude Code 识别。已踩坑修复
- [2026-03-23] X.com "正在关注"标签 AI 信噪比极高（本轮 12 条中 10 条直接 AI 相关），"为你推荐"标签 Elon Musk 内容占比过高但偶有高价值 AI 推荐（如 DeerFlow 2.0、Claude Code 配置指南 9K likes）
- [2026-03-24] ProductHunt Cloudflare 验证需手动点击复选框才能通过，且首次通过后 URL 会跳转到错误日期（3/1），需二次导航。考虑优先用 WebSearch 抓取 PH 数据代替浏览器访问
- [2026-03-24] GitHub Trending 连续三轮高重复率（本轮 15 项中约 10 项已在 DB），确认降频为隔轮检查的必要性
- [2026-03-24] Claude Computer Use 发布当天，X.com 时间线被相关内容刷屏——重大产品发布日应聚焦该主题深挖，而非平铺浏览多平台
- [2026-03-25] 本轮跳过了 GitHub Trending 和 ProductHunt（连续高重复率），专注 X.com 时间线 + HuggingFace + Reddit，效率明显提升。建议正式将 GH Trending 和 PH 降为隔轮检查
- [2026-03-25] X.com 搜索补充（如 "litellm attack"）对获取事件全貌非常有效——发现了 Karpathy 原推（15K likes vs Elon 转发 3.7K）和关键技术细节（受影响版本、攻击路径）。建议重大事件时主动用搜索补充时间线
- [2026-03-26] HuggingFace Daily Papers 今日仅 2 篇且价值一般，确认下午/晚间巡检效果更好（UTC 更新时间差）。早间巡检可跳过 HF
- [2026-03-26] Claude 官方账号 @claudeai 一天内发布 Auto Mode + 移动端 MCP 两个重磅更新，"为你推荐"标签在大版本发布日信噪比显著提升——建议关注 Anthropic 发布节奏，发布日优先刷"为你推荐"

### Idea 发现

<!-- 格式：- [日期] #来源ID Idea描述（可行性判断） -->
- [2026-03-21] #181 Looq 类 macOS Quick Look 增强工具：与 KeyHint 同技术栈/用户画像，可作为 onemake.dev 第二款产品（可行性：高）
- [2026-03-21] #174 DuckDB + Claude Code 数据分析教程选题：零代码本地数据分析（自媒体价值：高）
- [2026-03-21] #175 Claude Code 云端定时任务可能替代本地 /loop 巡检模式（需评估功能边界）
- [2026-03-21] #185 Mistral Vibe 开源 CLI Agent 的架构值得研究：LLM 提供商抽象层设计，可借鉴做多模型切换的工具框架（技术参考）
- [2026-03-21] #186 OpenAI vs Anthropic 的 Skill 生态对比选题：frontend-skill vs frontend-design，谁的开发者体验更好（自媒体价值：高）
- [2026-03-21] #196 Claude Channels 变现模式：$497 安装费 + MRR 月度订阅，一人即可执行的 AI 助手安装服务（商业可行性：高）
- [2026-03-21] #194 Steve Schoger「Claude Code 作为设计工具」教程拆解选题：Refactoring UI 作者的实战方法论（自媒体价值：高）
- [2026-03-21] #202 异构多 Agent 架构选题：强模型规划 + 多弱模型并行执行，成本降10倍效率不减（自媒体+技术参考）
- [2026-03-21] #204 Novi Notes（MCP 原生 Mac 笔记）模式值得研究：MCP 作为 App 差异化卖点，无需 API Key 即可接入 Claude，买断制。与 KeyHint 同为 macOS 工具 + 独立开发者，可借鉴 MCP 集成思路（产品参考：高）
- [2026-03-21] #203 Everything Claude Code 的 91K Stars 验证了「Claude Code 配置即产品」的方向——28 个 Agent + 116 条规则的标准化配置库可以作为自媒体选题：拆解其架构设计（自媒体价值：高）
- [2026-03-21] #205 Caplo（iOS 实时 AI 字幕翻译）：iOS 端 AI 工具方向，利用系统级能力（屏幕覆盖 + 语音识别）做差异化，可评估 onemake.dev iOS 产品线（产品参考：中）
- [2026-03-21] #210 Bezi AI（Unity 专用 AI 助手）：解决游戏开发中「引擎内 AI 编码」痛点，直接在 Unity 编辑器中 vibe coding（游戏开发：高）
- [2026-03-21] #211 Tripo AI Smart Mesh：2秒生成 <5K 面 AAA 级 3D 网格直接导入引擎——独立游戏开发者 3D 资产瓶颈的潜在解法（游戏开发：高）
- [2026-03-21] #214 全 AI 游戏开发栈（Claude + World Labs + MeshyAI + Three.js）验证了一人全栈做游戏的可行路径（游戏开发：高）
- [2026-03-21] #218 Sprite Sheet Creator：AI 文本→2D 游戏角色精灵图+行走动画。1768 likes 验证强需求，直接解决 2D 游戏美术瓶颈（游戏开发：高，你的 UI 卡点的直接解法之一）
- [2026-03-21] #220 Cascadeur：本地 AI 3D 动画，无限生成无需云端。解决角色动画瓶颈（游戏开发：高）
- [2026-03-23] #238 AlphaClaw Apex（macOS 原生 OpenClaw Fleet Manager）：与 KeyHint 同为 macOS 原生工具，验证了 macOS AI Agent 管理工具的市场需求（产品参考：中）
- [2026-03-23] #243 Obsidian Skills（Kepano 官方发布）：笔记工具 + Agent Skills 的结合模式，KeyHint 也可探索「教 AI 使用快捷键」的 Skill 化方向（产品参考：高）
- [2026-03-23] #244 n8n-MCP 验证了「MCP 连接一切」的趋势——用 MCP 让 Claude Code 自动构建自动化工作流，15.8K Stars（技术参考）
- [2026-03-23] #223 Claude Code 项目配置指南 9K+ likes：说明开发者配置痛点真实存在，可做中文版深度教程（自媒体价值：高）
- [2026-03-23] #247 Hyperagents（Jeff Clune）：Agent 自主构建和改进其他 Agent，Meta-Evolution 方向的学术验证——可做「AI 自进化」系列选题（自媒体价值：高）
- [2026-03-24] #248 Claude Computer Use + Dispatch 深度选题：AI 从文本交互到物理设备操控的里程碑，可拆解为「Claude 帮你操作电脑」实测教程（自媒体价值：极高，36K likes）
- [2026-03-24] #249 Anthropic Phone Use（Orbit）：Claude 即将能操控手机，对 iOS App 开发者意味着什么？KeyHint 可考虑「AI 操控时的快捷键辅助」场景（产品参考：高）
- [2026-03-24] #252 Sahil Lavingia 的 9 个 OPC Agent Skills 可直接用于 onemake.dev 的产品决策流程——Find Community、Build MVP、Launch 等 Skill 直接可用（工具参考：高）
- [2026-03-24] #254 redline「用竞品审查竞品」的模式值得借鉴：Claude Code 写代码 → OpenAI Codex 审查 → 双重质量保障，Hook 机制的创新应用（技术参考：中）
- [2026-03-24] #263 MoneyPrinterV2 今日爆发+2880 Stars，验证了「AI 自动化内容变现」的强烈需求，可做自媒体拆解选题（自媒体价值：高）
- [2026-03-25] #264 litellm 供应链攻击（Karpathy 15K likes，598万 views）：pip install 即窃取全部凭证。可做安全警示选题，公众号+抖音双平台（自媒体价值：极高）
- [2026-03-25] #265 Sora 关停 + Disney 合作终止：大厂明星产品半年即死，开源视频生成的窗口期。可做「Sora 死了，然后呢」系列选题（自媒体价值：极高）
- [2026-03-25] #266 Writing Style Skill 自进化方法：AI 写初稿→人改→diff→规则回写→越写越像你。可做「训练 AI 写出你的风格」教程（自媒体价值：高）
- [2026-03-25] #269 Hesam 反直觉预测：5年后 SWE 需求激增但无人供给——适合抖音争议话题视频（自媒体价值：高）
- [2026-03-25] #279 OpenResearcher（457 upvotes）：Gemini/Perplexity Deep Research 的开源替代，可评估集成到自有工作流（工具参考：高）
- [2026-03-25] #284 三家公司两周内同时发布桌面 AI Agent：Claude Computer Use + Operator + Mariner，桌面 Agent 范式转移对 macOS 工具开发者意味着什么（产品参考：高）
- [2026-03-26] #288 Claude Code Auto Mode（37K likes）：AI 自主权限决策选题——可做「Auto Mode 实测：效率提升多少？安全吗？」深度教程（自媒体价值：极高）
- [2026-03-26] #289 Claude 移动端 MCP 工具上线：MCP 从桌面扩展到手机，KeyHint 应考虑 MCP 集成——让 AI Agent 能查询当前应用快捷键（产品参考：高）
- [2026-03-26] #295 小互公众号排版 Skill 开源：与我们现有公众号工作流直接相关，评估是否集成或借鉴其 AI 分析内容结构自动排版的思路（工具参考：高）
- [2026-03-26] #290 Browser Use SOTA 97% + Karpathy Auto-Research：用 Claude Code in a loop 自动优化产品——可应用到我们自己的巡检流程优化（技术参考：高）
- [2026-03-26] #296 G0DM0D3 越狱 1024 likes：AI 安全攻防话题自带流量，可做「33种技术同时突破51个模型」的安全科普选题（自媒体价值：高）
