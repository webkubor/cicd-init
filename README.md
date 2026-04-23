# cicd-init

> 一行命令，为前端项目生成 GitLab CI / GitHub Actions 配置。

## 特性

- 🚀 **零配置** — 自动探测项目类型，无需手动配置
- 🔍 **智能检测** — 自动识别框架、包管理器、Node.js 版本
- 🎯 **双平台** — 支持 GitLab CI 和 GitHub Actions
- 🐳 **Docker** — 容器化运行，任意环境一键部署
- 📦 **零依赖** — 纯 Python 标准库，无需额外安装

## 自动检测

| 检测项 | 来源 |
|--------|------|
| Git 平台 | `git remote -v` → GitHub / GitLab（含自托管） |
| 包管理器 | lock 文件 → npm / yarn / yarn-berry / pnpm |
| 前端框架 | `package.json` → React / Vue / Angular / Next.js / Nuxt / Svelte |
| Node 版本 | `.nvmrc` / `.node-version` / `package.json` engines |
| 构建产物 | 框架 + Vite/CRA 推断 → `dist` / `build` / `.next` / `.output/public` |
| 可用脚本 | `package.json` scripts → lint / test / build / typecheck |

## 安装

### 方式一：pip install（推荐）

```bash
pip install git+https://github.com/webkubor/cicd-init.git
```

### 方式二：pipx 隔离安装

```bash
pipx install git+https://github.com/webkubor/cicd-init.git
```

### 方式三：从源码安装

```bash
git clone https://github.com/webkubor/cicd-init.git
cd cicd-init
make install          # 创建 venv 并安装
```

### 方式四：Docker

```bash
# 构建镜像
docker build -t cicd-init https://github.com/webkubor/cicd-init.git

# 使用（挂载项目目录）
docker run --rm -v $(pwd):/src cicd-init:latest init -d /src
```

### 方式五：一行命令部署到服务器

```bash
# pipx 方式（推荐）
curl -sL https://raw.githubusercontent.com/webkubor/cicd-init/main/scripts/deploy-server.sh | bash -s -- --method=pipx

# Docker 方式
curl -sL https://raw.githubusercontent.com/webkubor/cicd-init/main/scripts/deploy-server.sh | bash -s -- --method=docker

# venv 方式（安装到 /opt/cicd-init）
curl -sL https://raw.githubusercontent.com/webkubor/cicd-init/main/scripts/deploy-server.sh | bash -s -- --method=venv
```

## 使用

### 在你的前端项目根目录执行：

```bash
# 自动检测 git 远程仓库，生成对应平台的 CI 配置
cicd-init init

# 指定平台
cicd-init init --platform gitlab
cicd-init init --platform github

# 同时生成两个平台
cicd-init init --all

# 预览（不写入文件）
cicd-init init --dry-run

# 覆盖 Node.js 版本
cicd-init init --node-version 18
```

### Docker 使用：

```bash
docker run --rm -v $(pwd):/src cicd-init:latest init -d /src --dry-run
```

### 查看检测结果：

```bash
cicd-init detect
```

输出示例：

```json
{
  "framework": "react",
  "package_manager": "pnpm",
  "node_version": "20",
  "build_output": "dist",
  "scripts": {
    "lint": true,
    "test": true,
    "build": true,
    "typecheck": true
  },
  "git_platform": "github",
  "pm": {
    "install": "pnpm install --frozen-lockfile",
    "run": "pnpm run",
    "lockfile": "pnpm-lock.yaml",
    "gh_cache": "pnpm"
  },
  "run_prefix": "pnpm run"
}
```

## 生成的流水线

### GitLab CI (`.gitlab-ci.yml`)

```
install → typecheck → lint → test → build
                              ↗
                        (串行 stages)
                              ↘
```

- **install**: 安装依赖，缓存 node_modules
- **typecheck**: TypeScript 类型检查（如有 typecheck 脚本）
- **lint**: 代码检查
- **test**: 单元测试 + 覆盖率
- **build**: 构建，产出 artifact（保留 7 天）

### GitHub Actions (`.github/workflows/ci.yml`)

```
typecheck ─┐
lint ──────┤
test ──────┼──→ build → upload artifact
           │
       (并行执行)
```

- 相同的 stage 结构，使用 `needs` 实现并行
- 自动取消同一分支的旧流水线（concurrency）
- 支持 npm / yarn / pnpm 缓存

## 支持的框架

| 框架 | 构建产物 | 说明 |
|------|----------|------|
| React (Vite) | `dist` | 自动识别 vite.config |
| React (CRA) | `build` | 识别 react-scripts |
| Vue (Vite) | `dist` | |
| Vue (Nuxt) | `.output/public` | SSR 项目 |
| Angular | `dist` | 使用 @angular/core 识别 |
| Next.js | `.next` | SSR 项目 |
| Svelte / SvelteKit | `build` | |
| 通用 Vite | `dist` | 无框架绑定的 Vite 项目 |
| 通用 Webpack | `dist` | |

## 开发

```bash
# 安装
make install

# 测试（dry-run 在模拟项目上）
make test

# 构建 Docker
make docker
make docker-run DIR=/path/to/project

# 清理
make clean
```

## License

MIT
