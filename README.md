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

## 使用方式

1. **Fork** 本仓库
2. 编辑 `docs/AI探索规则.md` — 填入你的产品信息、调整探索优先级
3. 运行 `/setup-playwright` 配置浏览器自动化环境
4. 启动服务后，按 CLAUDE.md 中的启动命令开始巡检

## 功能

- 多平台 AI 内容采集（X、GitHub、Product Hunt、HuggingFace、Reddit）
- 按重要性 / 分类 / 平台筛选与排序
- 深度调研 Markdown 存储与渲染

## 技术栈

- 后端：Python + FastAPI + SQLite
- 前端：React + Ant Design（单文件 SPA）

## 文档结构

| 文件 | 职责 |
|------|------|
| [README.md](README.md) | 项目介绍、快速开始 |
| [CLAUDE.md](CLAUDE.md) | 数据库操作手册、启动命令 |
| [docs/AI探索规则.md](docs/AI探索规则.md) | 巡检执行规则（Fork 后自定义） |

## License

MIT
