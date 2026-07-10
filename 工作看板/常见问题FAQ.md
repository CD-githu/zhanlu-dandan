# 开发常见问题 FAQ

## 概述

本文档收集了工作看板项目开发过程中的常见问题和解决方案。

---

## 环境配置问题

### Q1: Node.js 版本不兼容怎么办？

**问题描述**：运行 `npm install` 或 `npm run tauri:dev` 时提示 Node 版本太低。

**解决方案**：
```bash
# 检查当前版本
node --version

# 如果版本低于 18.0，使用 nvm 升级
nvm install 20
nvm use 20

# 或者直接从官网下载安装最新 LTS 版本
# https://nodejs.org/
```

**说明**：Tauri 2.x 需要 Node.js 18.0 或更高版本。

---

### Q2: Rust 安装失败怎么办？

**问题描述**：运行 `cargo install tauri-cli` 时安装失败。

**解决方案**：

**Windows**：
```powershell
# 下载并运行 rustup-init.exe
# https://www.rust-lang.org/tools/install

# 安装后重新打开 PowerShell
rustc --version
```

**macOS**：
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env
```

**Linux (Ubuntu/Debian)**：
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env

# 安装必要的构建工具
sudo apt update
sudo apt install build-essential
```

---

### Q3: Windows 上编译失败，提示缺少 C++ 构建工具

**问题描述**：编译 Rust 项目时提示 "link.exe not found"

**解决方案**：
1. 下载并安装 Visual Studio C++ Build Tools
2. 下载地址：https://visualstudio.microsoft.com/visual-cpp-build-tools/
3. 安装时选择 "Desktop development with C++" 工作负载

**快速安装命令**：
```powershell
# 使用 winget 安装（推荐）
winget install Microsoft.VisualStudio.2022.BuildTools --override "--wait --passive --add ProductLang=en-us --add Microsoft.VisualStudio.Workload.VCTools;includeRecommended"
```

---

### Q4: macOS 上编译失败，提示缺少命令行工具

**问题描述**：编译时提示 "xcrun: error: invalid active developer path"

**解决方案**：
```bash
# 安装 Xcode Command Line Tools
xcode-select --install

# 如果已经安装但路径错误
sudo xcode-select --switch /Library/Developer/CommandLineTools
```

---

## Tauri 问题

### Q5: Tauri 命令无法找到？

**问题描述**：运行 `tauri` 命令时提示 "command not found"

**解决方案**：

**全局安装**：
```bash
npm install -g @tauri-apps/cli
```

**或者使用 npx**：
```bash
npx tauri dev
npx tauri build
```

**或者使用 cargo**：
```bash
cargo install tauri-cli
cargo tauri dev
```

---

### Q6: Tauri 开发服务器无法启动？

**问题描述**：运行 `npm run tauri:dev` 时无法启动或白屏。

**解决方案**：

1. **检查端口被占用**：
```bash
# Windows
netstat -ano | findstr :5173

# Linux/macOS
lsof -i :5173

# 如果被占用，修改 vite.config.ts 中的端口
server: {
  port: 5174 // 改为其他端口
}
```

2. **检查前端是否正常**：
```bash
# 先单独测试前端
npm run dev

# 确认前端正常后，再启动 Tauri
npm run tauri:dev
```

3. **清除缓存**：
```bash
# 清除 Vite 缓存
rm -rf node_modules/.vite

# 重新安装依赖
rm -rf node_modules
npm install
```

---

### Q7: 窗口大小不正确？

**问题描述**：Tauri 窗口太小或太大。

**解决方案**：修改 `src-tauri/tauri.conf.json`：

```json
{
  "tauri": {
    "windows": [
      {
        "title": "工作看板",
        "width": 1280,
        "height": 800,
        "minWidth": 800,
        "minHeight": 600,
        "resizable": true,
        "fullscreen": false
      }
    ]
  }
}
```

---

## Vue 开发问题

### Q8: Vite 启动报错 "Cannot find module @vitejs/plugin-vue"？

**问题描述**：运行 `npm run dev` 时报错找不到模块。

**解决方案**：
```bash
# 重新安装依赖
rm -rf node_modules package-lock.json
npm install

# 或者单独安装缺失的依赖
npm install @vitejs/plugin-vue -D
```

---

### Q9: TypeScript 类型错误 "无法找到模块"？

**问题描述**：导入 `@/components/xxx` 时提示找不到模块。

**解决方案**：

1. **检查 tsconfig.json 配置**：
```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  }
}
```

2. **检查 vite.config.ts 配置**：
```typescript
resolve: {
  alias: {
    '@': resolve(__dirname, 'src')
  }
}
```

3. **重启 TypeScript 服务器**：
- VS Code: `Cmd+Shift+P` -> "TypeScript: Restart TS Server"

---

### Q10: Element Plus 组件样式不生效？

**问题描述**：Element Plus 组件显示但没有样式。

**解决方案**：

1. **检查导入**：
```typescript
// main.ts
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css' // 必须导入样式

app.use(ElementPlus)
```

2. **检查 vite.config.ts**：
```typescript
import ElementPlus from 'vite-plugin-element-plus'

plugins: [
  vue(),
  ElementPlus()
]
```

3. **如果 SCSS 变量不生效**，添加配置：
```javascript
import { defineConfig } from 'vite'
import ElementPlus from 'vite-plugin-element-plus'

export default defineConfig({
  // ...
  css: {
    preprocessorOptions: {
      scss: {
        additionalData: '@use "@/styles/variables.scss" as *;'
      }
    }
  }
})
```

---

## 数据库问题

### Q11: Prisma 迁移失败 "Failed to connect to database"？

**问题描述**：运行 `npx prisma migrate dev` 时连接数据库失败。

**解决方案**：

1. **检查 schema.prisma**：
```prisma
datasource db {
  provider = "sqlite"
  url      = "file:./workboard.db"
}
```

2. **创建 prisma 目录**：
```bash
mkdir -p prisma
```

3. **删除旧的数据库文件**：
```bash
rm -f workboard.db
rm -rf prisma/migrations
```

4. **重新初始化**：
```bash
npx prisma init --datasource-provider sqlite
npx prisma migrate dev --name init
npx prisma generate
```

---

### Q12: Prisma Client 生成失败？

**问题描述**：运行 `npx prisma generate` 时失败。

**解决方案**：

```bash
# 清除 Prisma 缓存
rm -rf node_modules/.prisma

# 重新安装 Prisma
npm install prisma @prisma/client

# 重新生成
npx prisma generate
```

---

### Q13: 数据库字段更新不生效？

**问题描述**：修改 schema.prisma 后，查询时没有新字段。

**解决方案**：

1. **运行迁移**：
```bash
npx prisma migrate dev --name add_new_field
```

2. **重新生成 Prisma Client**：
```bash
npx prisma generate
```

3. **重启开发服务器**：
```bash
npm run tauri:dev
```

---

## 构建打包问题

### Q14: 构建时出现证书错误 (macOS)？

**问题描述**：运行 `npm run tauri build` 时提示代码签名错误。

**解决方案**：

**临时方案**（仅用于测试）：
```bash
# 在 tauri.conf.json 中禁用签名
{
  "bundle": {
    "macOS": {
      "signingIdentity": null
    }
  }
}
```

**正式方案**：
1. 在 Mac 上创建签名证书
2. 在 `tauri.conf.json` 中配置：
```json
{
  "bundle": {
    "macOS": {
      "signingIdentity": "Developer ID Application: Your Name (TEAM_ID)",
      "entitlements": null,
      "providerShortName": "TEAM_ID"
    }
  }
}
```

---

### Q15: Windows 构建时 NSIS 打包失败？

**问题描述**：构建时报错 "Failed to create NSIS installer"

**解决方案**：

1. **检查 tauri.conf.json**：
```json
{
  "bundle": {
    "targets": ["msi"], // 改用 MSI 代替 NSI
    "windows": {
      "webviewInstallMode": {
        "type": "embedBootstrapper"
      }
    }
  }
}
```

2. **安装 WiX Toolset**：
```powershell
winget install WiX.Toolset
```

---

### Q16: Linux 构建时缺少依赖？

**问题描述**：构建时报错缺少 `libwebkit2gtk` 等依赖。

**解决方案**：

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install libwebkit2gtk-4.0-dev \
  build-essential \
  curl \
  wget \
  file \
  libssl-dev \
  libgtk-3-dev \
  libayatana-appindicator3-dev \
  librsvg2-dev

# Fedora
sudo dnf install webkit2gtk4.0-devel \
  openssl-devel \
  curl \
  wget \
  file \
  libappindicator-gtk3-devel \
  librsvg2-devel

# Arch Linux
sudo pacman -Syu
sudo pacman -S webkit2gtk \
  base-devel \
  curl \
  wget \
  file \
  openssl \
  appmenu-gtk-module \
  libappindicator-gtk3 \
  librsvg
```

---

## AI 集成问题

### Q17: AI 请求超时？

**问题描述**：调用 AI API 时超时。

**解决方案**：

```typescript
// 在 AI 服务中添加超时配置
async function generateSummary(request: AISummaryRequest) {
  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), 60000) // 60秒超时

  try {
    const response = await fetch(config.apiUrl, {
      signal: controller.signal,
      // ...
    })
    clearTimeout(timeoutId)
    return response.json()
  } catch (error) {
    clearTimeout(timeoutId)
    throw new Error('AI 请求超时，请检查网络或增加超时时间')
  }
}
```

---

### Q18: 内网 AI API 无法访问？

**问题描述**：配置内网 API 地址后无法访问。

**解决方案**：

1. **检查地址格式**：
```typescript
// 正确格式
const apiUrl = "http://192.168.1.100:8000/v1"
const apiUrl = "http://localhost:8000/v1"

// 错误格式
const apiUrl = "192.168.1.100:8000/v1" // 缺少协议
const apiUrl = "http://192.168.1.100:8000/v1/" // 结尾不要斜杠
```

2. **检查网络连接**：
```bash
# 测试连接
curl http://192.168.1.100:8000/v1/models

# 检查防火墙规则
# Windows
netsh advfirewall firewall add rule name="Allow AI API" dir=in action=allow protocol=tcp localport=8000

# Linux/macOS
sudo ufw allow 8000
```

3. **检查 Tauri 权限**（`tauri.conf.json`）：
```json
{
  "tauri": {
    "allowlist": {
      "http": {
        "all": true,
        "request": true
      }
    }
  }
}
```

---

## 性能问题

### Q19: 应用启动慢？

**问题描述**：启动 Tauri 应用需要 10 秒以上。

**解决方案**：

1. **优化依赖加载**：
```typescript
// 使用懒加载
const WorkflowView = defineAsyncComponent(() =>
  import('@/views/Workflow.vue')
)
```

2. **优化数据库查询**：
```rust
// 添加索引
CREATE INDEX idx_task_status ON tasks(status);
CREATE INDEX idx_task_type ON tasks(type);
```

3. **禁用不必要的开发工具**：生产构建时自动禁用

---

### Q20: 内存占用过高？

**问题描述**：应用运行一段时间后内存占用持续增长。

**解决方案**：

1. **检查内存泄漏**：
```javascript
// 组件卸载时清理
onUnmounted(() => {
  // 清理定时器
  clearInterval(timerId)

  // 清理事件监听
  window.removeEventListener('resize', handler)
})
```

2. **使用虚拟滚动**：
```vue
<template>
  <el-table-v2
    :columns="columns"
    :data="largeData"
    :width="700"
    :height="400"
    fixed
  />
</template>
```

3. **优化 Pinia 状态管理**：
```typescript
// 使用 unref 清理不再使用的响应式数据
function clearCache() {
  tasks.value = []
  cache.clear()
}
```

---

## 调试问题

### Q21: 如何在 Tauri 中查看 Rust 日志？

**解决方案**：

```rust
use log::info;

fn main() {
    // 初始化日志
    pretty_env_logger::init();

    tauri::Builder::default()
        .setup(|app| {
            info!("Application started");
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

**查看日志**：
- 开发环境：直接在终端看到
- 生产环境：配置文件位置见 `tauri.conf.json` 中的 `config` 字段

---

### Q22: 如何在浏览器中调试前端？

**解决方案**：

**开发环境**：
```bash
npm run tauri:dev
# 会自动打开开发者工具
```

**手动打开开发者工具**：
```typescript
const { openDevTools } = window.__TAURI__.window
openDevTools()
```

或修改 `tauri.conf.json`：
```json
{
  "tauri": {
    "windows": [{
      "devtools": true
    }]
  }
}
```

---

## 其他问题

### Q23: 路由刷新后 404？

**问题描述**：刷新页面时显示 "Cannot GET /tasks"

**解决方案**：使用 hash 模式路由：

```typescript
// router/index.ts
import { createRouter, createWebHashHistory } from 'vue-router'

export const router = createRouter({
  history: createWebHashHistory(), // 使用 hash 模式
  routes
})
```

---

### Q24: 如何处理多语言？

**解决方案**：使用 Vue I18n：

```bash
npm install vue-i18n
```

```typescript
// main.ts
import { createI18n } from 'vue-i18n'
import zh from './locales/zh-CN.json'
import en from './locales/en-US.json'

const i18n = createI18n({
  locale: 'zh-CN',
  fallbackLocale: 'en-US',
  messages: { 'zh-CN': zh, 'en-US': en }
})

app.use(i18n)
```

---

### Q25: 如何实现主题切换？

**解决方案**：

```typescript
// store/theme.ts
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  const theme = ref<'light' | 'dark' | 'auto'>('auto')

  function setTheme(newTheme: 'light' | 'dark' | 'auto') {
    theme.value = newTheme
    localStorage.setItem('theme', newTheme)
    applyTheme(newTheme)
  }

  function applyTheme(thm: 'light' | 'dark' | 'auto') {
    const isDark = thm === 'dark' || (thm === 'auto' && window.matchMedia('(prefers-color-scheme: dark)').matches)
    document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light')
  }

  return { theme, setTheme, applyTheme }
})
```

---

## 获取帮助

如果以上 FAQ 没有解决你的问题：

1. 查看官方文档：
   - [Tauri 文档](https://tauri.app/)
   - [Vue 3 文档](https://vuejs.org/)
   - [Element Plus 文档](https://element-plus.org/)

2. 搜索已有 Issue：
   - [Tauri GitHub Issues](https://github.com/tauri-apps/tauri/issues)
   - [Vue GitHub Issues](https://github.com/vuejs/core/issues)

3. 提问时请提供：
   - 操作系统及版本
   - Node.js 版本
   - Rust 版本
   - 完整的错误信息
   - 复现步骤
   - 相关代码片段

---

## 常用调试命令

```bash
# 检查环境
node --version
npm -v
rustc --version
cargo --version
cargo tauri --version

# 清理并重新安装
rm -rf node_modules
rm -rf src-tauri/target
npm install

# 数据库相关
npx prisma studio          # 打开数据库可视化工具
npx prisma migrate dev     # 运行迁移
npx prisma generate        # 生成 Prisma Client

# 构建相关
npm run build              # 构建前端
npm run tauri:build        # 构建应用

# 调试相关
npm run tauri:dev          # 启动开发环境
npm run dev                # 仅启动前端开发服务器
```

希望这些 FAQ 对你有帮助！
