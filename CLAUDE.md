# AI Radar — AI 内容探索与监控

## 执行硬约束

- commit message 必须使用中文
- 不添加 Co-Authored-By 行，直接使用 git 全局配置的作者信息提交
- 允许按改动范围分批提交（1-5 次），每批聚焦一个主题
- 没有用户允许不能 git 提交

## 全局必读文档

- `文档说明-AI探索.md`：AI 巡检流程、`ai_discovery` 表结构、采集规范、分析规范
- `文档说明-Playwright.md`（symlink → `~/.chrome-shared/playwright.md`）：所有浏览器操作规范

## 数据存储

- 数据库：`data.db`（项目根目录），包含 `ai_discovery` 和 `ai_follow_log` 两张表
- 查询示例：`sqlite3 data.db "PRAGMA table_info(ai_discovery);"`

## 服务

- 启动：`python server.py`（http://localhost:8002）
- 前端：`index.html`（单文件 React 应用）

## 浏览器共享

所有项目共用同一个 Chrome 实例（CDP 端口 9222），profile 位于 `~/.chrome-shared/.chrome-profile/`。
启动脚本通过 symlink 引用：`.claude/scripts/start-playwright-mcp.sh` → `~/.chrome-shared/start-playwright-mcp.sh`

## 启动命令

```
/loop 20m 阅读 @文档说明-AI探索.md 和 @文档说明-Playwright.md 按「单轮执行流程」执行一轮 AI 内容巡检。
```
