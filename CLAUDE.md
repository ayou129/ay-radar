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

## 自有产品

- **KeyHint**（[keyhint.onemake.dev](https://keyhint.onemake.dev/)）：长按 ⌘ Command 键，即刻显示当前 macOS 应用的所有快捷键，松开即消失
  - 技术栈：Swift / macOS 原生（≥ 13.0 Ventura）
  - 安装：DMG 直装 或 `brew tap ayou129/keyhint && brew install keyhint`
  - 定位：一人开发者免费产品，隶属 [onemake.dev](https://onemake.dev)（Small, focused tools for Mac users）
  - 特性：自动读取当前 App 菜单栏快捷键、含系统级快捷键、中英双语、Menu Bar 常驻零占用
  - 关注方向：功能拓展、变现路径、同类或相邻产品动态

## 巡检结束必做

每轮巡检完成后（Step 6），在结束总结中必须包含：

1. **Idea 发现**：本轮浏览中有没有发现适合复刻、适合做自媒体选题、或有商业潜力的 idea？逐条列出，标注来源和可行性判断
2. **优化建议**：流程/效率/质量方面的可优化点，追加到 `文档说明-AI探索.md` 的「待讨论优化项」列表

## 启动命令

### 巡检（广度）

```
/loop 20m 阅读 @文档说明-AI探索.md 和 @文档说明-Playwright.md 按「单轮执行流程」执行一轮 AI 内容巡检。
```

### 深度调研（深度）

```
阅读 @文档说明-AI探索.md 和 @文档说明-Playwright.md 按「深度调研流程」对 #<id> 进行深度调研。
```
