# AI Radar — 内容探索与监控

## 数据存储

- 数据库：`data.db`（项目根目录），包含 `ai_discovery` 和 `ai_follow_log` 两张表
- `ai_discovery` 通过 `category` 字段区分业务：`tool_update/blogger_insight/paper/trend`（AI 探索）、`hot_meme`（热梗）

## 服务

- 启动：`python server.py`（http://localhost:8002）
- 前端：`index.html`（单文件 React 应用）

## 启动命令

> 启动前确保：1) AI Radar 服务已运行 `python server.py`  2) Chrome CDP 已就绪（MCP Playwright 会自动启动）

### AI 巡检（广度）

```
/loop 30m 阅读 @产品说明-AI探索.md 按「单轮执行流程」执行一轮 AI 内容巡检。
```

### AI 深度调研

```
阅读 @产品说明-AI探索.md 按「深度调研流程」对 #<id> 进行深度调研。
```

也支持自由输入：`按深度调研流程，调研一下 macOS 快捷键工具的竞品格局`

### 热梗采集

```
阅读 @产品说明-热梗公众号.md 按「单轮采集流程」执行一轮热梗采集。
```

### 热梗发布到公众号

```
根据 #<id> 去微信公众号发布一下
```
