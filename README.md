# cicd-init

> 一行命令，为前端项目自动生成 CI/CD 配置。不懂 CI/CD？没关系，跑一下就行。

## 🚀 60 秒上手

**第 1 步：安装（选一个）**

```bash
# 推荐：一行搞定（自动装 Python、pip、cicd-init）
curl -sL https://raw.githubusercontent.com/webkubor/cicd-init/main/install.sh | bash

# 或者用 pip
pip3 install git+https://github.com/webkubor/cicd-init.git

# 或者用 Docker
docker pull ghcr.io/webkubor/cicd-init
```

**第 2 步：在你的前端项目里跑**

```bash
cd 你的前端项目
cicd-init init
```

**搞定。** 提交代码，push 到 GitHub/GitLab，CI 自动跑起来。

---

## 📖 它干了什么？

自动探测你的项目：

| 探测项 | 怎么探测的 |
|--------|-----------|
| CI 平台 | `git remote` → GitHub / GitLab |
| 包管理器 | lock 文件 → npm / yarn / pnpm |
| 前端框架 | `package.json` 依赖 → React / Vue / Angular / Next.js / Nuxt / Svelte |
| Node 版本 | `.nvmrc` / `.node-version` / `package.json` engines |
| 构建命令 | `package.json` scripts → build |

然后自动生成对应的 CI 配置文件，你只需要 commit & push。

---

## 🎯 两种模式

### 极简模式（推荐新手）

```bash
cicd-init init --simple
```

只做两件事：**装依赖 → 构建**。生成的 CI 配置最干净，lint/test 以后再加。

### 完整模式（适合团队项目）

```bash
cicd-init init
```

包含完整的检查链：**typecheck → lint → test → build**，带覆盖率、artifacts、缓存。

---

## 📋 更多用法

```bash
# 看看它探测到了什么（不生成文件）
cicd-init detect

# 预览生成的配置（不写入文件）
cicd-init init --dry-run

# 强制指定平台
cicd-init init --platform gitlab
cicd-init init --platform github

# 同时生成两个平台
cicd-init init --all

# 覆盖 Node 版本
cicd-init init --node-version 18

# 指定其他项目目录
cicd-init init -d /path/to/project
```

### Docker 使用

```bash
docker run --rm -v $(pwd):/src ghcr.io/webkubor/cicd-init init -d /src --simple
```

---

## 🔧 生成的文件

| 平台 | 文件路径 |
|------|----------|
| GitHub Actions | `.github/workflows/ci.yml` |
| GitLab CI | `.gitlab-ci.yml` |

### 完整模式生成的流水线

```
typecheck ─┐
lint ──────┼──→ build → artifact
test ──────┘
```

- 并行执行 typecheck / lint / test，全部通过后构建
- 自动缓存 node_modules
- 构建产物保留 7 天

### 极简模式生成的流水线

```
install → build
```

- 干净利落，就这两步

---

## 🏗️ 服务器一键部署

```bash
# pipx 方式（推荐）
curl -sL https://raw.githubusercontent.com/webkubor/cicd-init/main/scripts/deploy-server.sh | bash -s -- --method=pipx

# Docker 方式
curl -sL https://raw.githubusercontent.com/webkubor/cicd-init/main/scripts/deploy-server.sh | bash -s -- --method=docker
```

---

## 🛠️ 开发

```bash
git clone https://github.com/webkubor/cicd-init.git
cd cicd-init
make install    # 创建 venv 并安装
make test       # 测试
make docker     # 构建 Docker 镜像
```

## License

MIT
