---
name: setup-playwright
description: 配置 Playwright MCP 共享浏览器环境（启动脚本 + 操作规范），支持 macOS / Linux / Windows
user_invocable: true
---

# Setup Playwright — 共享浏览器环境初始化

## 目标

在用户机器上生成 Playwright MCP 所需的基础设施文件，使所有项目共享同一个 Chrome 实例和登录态。

## 前置依赖

- **Node.js**（≥ 18）：用于运行 `npx @playwright/mcp`
  - macOS：`brew install node` 或从 [nodejs.org](https://nodejs.org) 下载
  - Ubuntu / Debian：`sudo apt install nodejs npm`
  - Windows 10+：从 [nodejs.org](https://nodejs.org) 下载 LTS 版本，安装时勾选 **Add to PATH**

## 执行步骤

### 1. 检测平台

判断当前操作系统：macOS / Linux / Windows。

### 2. 检查现有配置

检查以下路径是否已存在文件：
- `~/.claude/scripts/start-playwright-mcp.sh`（macOS/Linux）或 `~/.claude/scripts/start-playwright-mcp.ps1`（Windows）
- `~/.claude/rules/playwright.md`

如果已存在，询问用户是否覆盖。

### 3. 创建共享 Chrome profile 目录

```bash
# macOS / Linux
mkdir -p ~/.chrome-shared/.chrome-profile

# Windows (PowerShell)
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.chrome-shared\.chrome-profile"
```

### 4. 生成启动脚本

创建 `~/.claude/scripts/` 目录（如不存在），然后根据平台生成启动脚本。

#### macOS — `~/.claude/scripts/start-playwright-mcp.sh`

```bash
#!/bin/bash
# Playwright MCP 共享浏览器启动脚本
# 先确保 Chrome CDP 就绪，再启动 MCP Playwright

CDP_URL="http://127.0.0.1:9222"
CHROME_PROFILE="$HOME/.chrome-shared/.chrome-profile"

cdp_ready() {
  curl -s --max-time 2 "$CDP_URL/json/version" >/dev/null 2>&1
}

if ! cdp_ready; then
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
    --remote-debugging-port=9222 \
    --remote-debugging-address=127.0.0.1 \
    --user-data-dir="$CHROME_PROFILE" \
    --disable-features=AutomationControlled \
    --no-first-run \
    --no-default-browser-check &

  for i in $(seq 1 15); do
    sleep 1
    if cdp_ready; then
      break
    fi
  done
fi

if ! cdp_ready; then
  echo "Chrome CDP 启动超时" >&2
  exit 1
fi

exec npx -y @playwright/mcp@latest --cdp-endpoint "$CDP_URL"
```

生成后执行 `chmod +x ~/.claude/scripts/start-playwright-mcp.sh`。

#### Linux — `~/.claude/scripts/start-playwright-mcp.sh`

与 macOS 相同，但 Chrome 路径改为：

```bash
CHROME_BIN=$(which google-chrome || which google-chrome-stable || which chromium-browser || which chromium)
if [ -z "$CHROME_BIN" ]; then
  echo "未找到 Chrome/Chromium，请先安装" >&2
  exit 1
fi
```

启动命令中将 `"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"` 替换为 `"$CHROME_BIN"`。

#### Windows — `~/.claude/scripts/start-playwright-mcp.ps1`

```powershell
# Playwright MCP 共享浏览器启动脚本 (Windows)
$CDP_URL = "http://127.0.0.1:9222"
$CHROME_PROFILE = "$env:USERPROFILE\.chrome-shared\.chrome-profile"

function Test-CDP {
    try {
        $null = Invoke-WebRequest -Uri "$CDP_URL/json/version" -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
        return $true
    } catch {
        return $false
    }
}

if (-not (Test-CDP)) {
    $chromePaths = @(
        "${env:ProgramFiles}\Google\Chrome\Application\chrome.exe",
        "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
        "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe"
    )
    $chromeBin = $chromePaths | Where-Object { Test-Path $_ } | Select-Object -First 1

    if (-not $chromeBin) {
        Write-Error "未找到 Chrome，请先安装 Google Chrome"
        exit 1
    }

    Start-Process -FilePath $chromeBin -ArgumentList @(
        "--remote-debugging-port=9222",
        "--remote-debugging-address=127.0.0.1",
        "--user-data-dir=$CHROME_PROFILE",
        "--disable-features=AutomationControlled",
        "--no-first-run",
        "--no-default-browser-check"
    )

    for ($i = 0; $i -lt 15; $i++) {
        Start-Sleep -Seconds 1
        if (Test-CDP) { break }
    }
}

if (-not (Test-CDP)) {
    Write-Error "Chrome CDP 启动超时"
    exit 1
}

npx -y @playwright/mcp@latest --cdp-endpoint $CDP_URL
```

### 5. 生成操作规范

创建 `~/.claude/rules/playwright.md`，内容为 Playwright 操作规范（反检测、行为模拟、异常处理等）。

规范文件模板如下，根据平台调整路径示例：

```markdown
---
globs: ["**/playwright*", "**/browser*", "**/publisher*", "**/crawler*", "**/scraper*", "**/collector*", "**/explorer*"]
---
# Playwright 操作规范

所有使用 Playwright（MCP 或代码）操作浏览器的行为，**必须遵循以下规则**。

## 1. 浏览器共享机制

MCP、各项目脚本、手动操作**共用同一个 Chrome 实例和登录态**。

### 核心架构

Chrome（带 CDP，端口 9222，profile = {{CHROME_PROFILE_PATH}}）
  ├── MCP Playwright ──── 通过 CDP 连接
  ├── 各项目脚本 ──────── 通过 CDP 连接
  └── 用户手动操作 ────── 直接使用

- **Chrome profile**：`{{CHROME_PROFILE_PATH}}`（全局共享），存储 Cookie、登录态
- **CDP 端口**：`127.0.0.1:9222`
- **登录态持久化**：存在 profile 目录中，关闭 Chrome 后仍保留

### 启动 Chrome

Claude Code 启动时，MCP Playwright 通过共享启动脚本自动完成：
1. 检测 CDP 是否就绪
2. 未就绪则启动 Chrome（带 CDP 9222 + 共享 profile）
3. 等待 CDP 就绪后启动 MCP Playwright 连接

## 2. 反检测

### 启动参数（第一层）

`--disable-features=AutomationControlled` — 禁用自动化标记（已在启动脚本中设置）

### JS 注入（第二层）

通过 `page.addInitScript()` 注册，每个 tab 只需调用一次：

await page.addInitScript(() => {
  Object.defineProperty(navigator, 'webdriver', { get: () => false });
  delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
  delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
  delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
});

## 3. 操作行为规范

### 随机延迟

| 操作类型 | 延迟范围 |
|---------|---------|
| 页面导航后 | 1-3 秒 |
| 点击按钮前 | 0.5-1.5 秒 |
| 输入文字 | 200-500 毫秒/单词 |
| 提交表单后 | 3-8 秒 |
| 等待内容加载 | 10-30 秒 |
| 连续任务间隔 | 15-45 秒 |

延迟使用随机值，不能是固定值。

### 导航模式

避免循环 `page.goto()` 逐个访问 URL 列表。优先通过页面内点击、搜索等自然路径导航。

### 操作频率

- 单次会话同一平台不超过 20 次操作
- 分多次会话执行，间隔至少 10 分钟

## 4. 异常处理

### 验证码

1. 截图查看类型，尝试自动解决
2. 失败则停止，截图保存到 `.screenshots/`，等待用户手动处理

### 页面异常

- 加载超时：30 秒后重试一次，再失败则停止
- 元素未找到：10 秒后重试一次，再失败则跳过
- 网络错误：15 秒后重试一次，再失败则停止
```

**模板变量替换**：
- macOS/Linux: `{{CHROME_PROFILE_PATH}}` → `~/.chrome-shared/.chrome-profile/`
- Windows: `{{CHROME_PROFILE_PATH}}` → `C:\Users\<用户名>\.chrome-shared\.chrome-profile\`

### 6. 写入项目级 `.mcp.json`

在**当前项目根目录**自动创建或更新 `.mcp.json`，写入 Playwright MCP 配置。

> MCP 服务配置必须放在项目级 `.mcp.json` 中才会生效，`~/.claude.json` 的顶层 `mcpServers` 对 MCP 启动无效。

如果 `.mcp.json` 已存在且包含其他 MCP 服务，保留已有配置，仅合并 `playwright` 条目。

**macOS / Linux** — 写入内容：

```json
{
  "mcpServers": {
    "playwright": {
      "type": "stdio",
      "command": "{{HOME}}/.claude/scripts/start-playwright-mcp.sh",
      "args": [],
      "env": {}
    }
  }
}
```

**Windows** — 写入内容：

```json
{
  "mcpServers": {
    "playwright": {
      "type": "stdio",
      "command": "powershell",
      "args": ["-File", "{{USERPROFILE}}\\.claude\\scripts\\start-playwright-mcp.ps1"],
      "env": {}
    }
  }
}
```

其中 `{{HOME}}` / `{{USERPROFILE}}` 替换为实际绝对路径。

确保 `.mcp.json` 已加入 `.gitignore`（路径含本机用户名，不应入库）。

### 7. 确保 `.mcp.json` 在 `.gitignore` 中

检查项目根目录的 `.gitignore`，如果没有忽略 `.mcp.json`，自动追加一行。

### 8. 自动允许 Playwright MCP 工具

检查用户级设置文件 `~/.claude/settings.json`，确保 `permissions.allow` 数组中包含 `"mcp__playwright__*"`。

如果不存在则追加。这样所有 Playwright MCP 工具调用不再需要逐次手动确认。

### 9. 验证

提示用户验证：

1. 重启 Claude Code（让 MCP 配置生效）
2. 在对话中使用任意 `mcp__playwright__*` 工具（如 `browser_navigate`）
3. 如果 Chrome 自动启动并导航成功，配置完成
4. 首次使用某平台需手动登录一次，之后所有项目共享登录态

### 输出格式

完成后输出清单：

```
Playwright 共享浏览器环境配置完成：

  [x] Chrome profile 目录：{{CHROME_PROFILE_PATH}}
  [x] 启动脚本：~/.claude/scripts/start-playwright-mcp.{{ext}}
  [x] 操作规范：~/.claude/rules/playwright.md
  [x] 项目 MCP 配置：.mcp.json
  [x] 工具权限：mcp__playwright__* 已加入 settings.json

下一步：
  1. 重启 Claude Code
  2. 首次使用需在浏览器中手动登录目标平台
```
