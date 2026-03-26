# AI Radar — AI 内容探索与监控

## 项目结构

```
├── server.py              # FastAPI 后端（启动时自动建表）
├── index.html             # React 单页前端（Ant Design）
├── docs/
│   └── AI探索规则.md       # 巡检执行规则（Fork 后自定义）
└── data.db                # SQLite 数据库（自动生成，不入库）
```

## 环境准备

详见 [README.md](README.md#快速开始)。

## 数据库操作

### 安装 SQLite

| 平台 | 方式 |
|------|------|
| macOS | 系统自带，终端直接使用 `sqlite3` |
| Ubuntu / Debian | `sudo apt install sqlite3` |
| Windows 10+ | 从 [sqlite.org/download](https://sqlite.org/download.html) 下载 **sqlite-tools**，解压后将目录加入系统 PATH |

### 连接

```bash
sqlite3 data.db
```

Windows 下如果 sqlite3 已加入 PATH，在 cmd 或 PowerShell 中同样执行上述命令。

进入交互式控制台后，常用 dot 命令：

```
.tables              -- 查看所有表
.schema ai_discovery -- 查看建表语句
.headers on          -- 显示列名
.mode column         -- 列对齐显示（macOS/Linux）
.mode table          -- 表格显示（SQLite 3.37+，推荐 Windows）
.quit                -- 退出
```

### 表结构

**ai_discovery** — 内容发现记录

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增主键 |
| url | TEXT UNIQUE | 来源链接（去重键） |
| platform | TEXT | 平台：x / github / producthunt / huggingface / reddit |
| author | TEXT | 作者 |
| title | TEXT | 标题 |
| summary | TEXT | 摘要 |
| category | TEXT | 分类：tool_update / blogger_insight / paper / trend |
| importance | TEXT | 重要性：high / medium / low |
| published_at | TEXT | 原始发布时间 |
| discovered_at | TEXT | 发现时间 |
| updated_at | TEXT | 更新时间 |
| round_id | TEXT | 巡检轮次标识 |
| raw_data | TEXT(JSON) | 原始抓取数据 |
| md | TEXT | 深度分析 Markdown |
| user_note | TEXT | 用户备注 |

**ai_follow_log** — 关注记录

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增主键 |
| platform | TEXT | 平台 |
| username | TEXT UNIQUE | 用户名 |
| reason | TEXT | 关注原因 |
| followed_at | TEXT | 关注时间 |
| status | TEXT | 状态：success / failed |

### 查询

```sql
-- 最近 10 条
SELECT id, title, category, importance, discovered_at
FROM ai_discovery ORDER BY discovered_at DESC LIMIT 10;

-- 按分类统计
SELECT category, COUNT(*) as cnt FROM ai_discovery GROUP BY category;

-- 按重要性筛选
SELECT id, title, platform, author
FROM ai_discovery WHERE importance = 'high';

-- 按平台 + 时间范围
SELECT id, title, author FROM ai_discovery
WHERE platform = 'github'
  AND discovered_at >= datetime('now', '-7 days');

-- 模糊搜索标题
SELECT id, title FROM ai_discovery WHERE title LIKE '%claude%';

-- 有深度分析的记录
SELECT id, title FROM ai_discovery WHERE md IS NOT NULL AND md != '';
```

### 插入

```sql
INSERT INTO ai_discovery (url, platform, author, title, summary, category, importance)
VALUES ('https://example.com/post', 'x', 'author_name', '标题', '摘要内容', 'tool_update', 'high');

INSERT INTO ai_follow_log (platform, username, reason)
VALUES ('x', 'some_user', '关注原因');
```

### 更新

```sql
-- 更新笔记
UPDATE ai_discovery SET user_note = '这个值得深入调研', updated_at = datetime('now') WHERE id = 1;

-- 修改重要性
UPDATE ai_discovery SET importance = 'high', updated_at = datetime('now') WHERE id = 1;
```

### 删除

```sql
DELETE FROM ai_discovery WHERE id = 1;
```

### 导出

macOS / Linux：

```bash
sqlite3 -header -csv data.db "SELECT * FROM ai_discovery;" > export.csv
```

Windows（PowerShell）：

```powershell
sqlite3.exe -header -csv data.db "SELECT * FROM ai_discovery;" | Out-File -Encoding utf8 export.csv
```

交互模式通用：

```
.mode csv
.headers on
.output export.csv
SELECT * FROM ai_discovery;
.output stdout
```

### 备份与恢复

```bash
# macOS / Linux
cp data.db data.db.bak

# Windows
copy data.db data.db.bak
```

## 浏览器自动化（可选）

AI 巡检功能依赖 Playwright MCP + 共享 Chrome 实例来复用登录态。需要 Node.js（≥ 18）。

首次配置运行：

```
/setup-playwright
```

该 SKILL 会根据你的平台自动生成 `~/.claude/scripts/` 启动脚本和 `~/.claude/rules/` 操作规范。

## 启动命令

> 启动前确保：1) AI Radar 服务已运行 `python server.py`  2) Chrome CDP 已就绪（MCP Playwright 会自动启动）

### AI 巡检（广度）

```
/loop 30m 阅读 @docs/AI探索规则.md 按「单轮执行流程」执行一轮 AI 内容巡检。
```

### AI 深度调研

```
阅读 @docs/AI探索规则.md 按「深度调研流程」对 #<id> 进行深度调研。
```

也支持自由输入：`按深度调研流程，调研一下 macOS 快捷键工具的竞品格局`
