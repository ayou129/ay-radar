# AI Radar

AI 内容探索与监控工具。自动巡检多平台 AI 动态，结构化存储，支持深度调研。

## 快速开始

```bash
# 安装依赖
pip install fastapi uvicorn markdown

# 启动服务
python server.py

# 打开 http://localhost:8002
```

首次启动自动创建 `data.db`，无需手动建表。

Windows 用户如 `pip` 不可用，使用 `python -m pip install`。

## 功能

- 多平台 AI 内容采集（X、GitHub、Product Hunt、HuggingFace、Reddit）
- 按重要性 / 分类 / 平台筛选与排序
- 深度调研 Markdown 存储与渲染

## 浏览器自动化（可选）

巡检功能依赖 Playwright MCP 操作浏览器。首次使用执行 `/setup-playwright` 完成配置。

详见 [CLAUDE.md](CLAUDE.md)。

## 技术栈

- 后端：Python + FastAPI + SQLite
- 前端：React + Ant Design（单文件 SPA）

## License

MIT
