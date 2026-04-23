#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# cicd-init 服务器部署脚本
# 用法:
#   curl -sL https://raw.githubusercontent.com/webkubor/cicd-init/main/scripts/deploy-server.sh | bash
#   或下载后: bash deploy-server.sh [OPTIONS]
#
# 选项:
#   --method=pipx    使用 pipx 安装（推荐）
#   --method=docker  使用 Docker
#   --method=venv    使用 Python venv
#   --prefix=/usr/local  安装前缀（仅 venv 模式）
#   --force          强制重新安装
# ============================================================

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

REPO="webkubor/cicd-init"
BRANCH="main"
METHOD="${1:---method=pipx}"

# Parse args
for arg in "$@"; do
  case $arg in
    --method=*) METHOD="${arg#*=}" ;;
    --prefix=*) PREFIX="${arg#*=}" ;;
    --force) FORCE=true ;;
  esac
done

info()  { echo -e "${GREEN}[✓]${NC} $*"; }
warn()  { echo -e "${YELLOW}[!]${NC} $*"; }
fail()  { echo -e "${RED}[✗]${NC} $*"; exit 1; }

check_python() {
  if command -v python3 &>/dev/null; then
    python3 --version
    return 0
  fi
  fail "Python 3 未安装。请先安装: apt install python3 / yum install python3 / apk add python3"
}

check_docker() {
  if command -v docker &>/dev/null; then
    docker --version
    return 0
  fi
  fail "Docker 未安装。请先安装 Docker。"
}

install_pipx() {
  info "检测 pipx..."
  if ! command -v pipx &>/dev/null; then
    warn "pipx 未安装，正在安装..."
    if command -v apt &>/dev/null; then
      sudo apt install -y pipx
    elif command -v yum &>/dev/null; then
      sudo yum install -y pipx
    elif command -v apk &>/dev/null; then
      sudo apk add py3-pipx
    else
      python3 -m pip install --user pipx
    fi
    pipx ensurepath
  fi
  info "使用 pipx 安装 cicd-init..."
  pipx install "git+https://github.com/${REPO}.git@${BRANCH}" ${FORCE:+--force}
  info "安装完成! 运行 cicd-init --help 验证"
}

install_venv() {
  local PREFIX="${PREFIX:-/opt/cicd-init}"
  info "使用 venv 安装到 ${PREFIX}..."
  sudo git clone -b "$BRANCH" "https://github.com/${REPO}.git" "$PREFIX/src" ${FORCE:+--force} 2>/dev/null || \
    (cd "$PREFIX/src" && sudo git pull)
  sudo python3 -m venv "$PREFIX/venv"
  sudo "$PREFIX/venv/bin/pip" install -q "$PREFIX/src"
  # Symlink to PATH
  sudo ln -sf "$PREFIX/venv/bin/cicd-init" /usr/local/bin/cicd-init
  info "安装完成! 运行 cicd-init --help 验证"
}

install_docker() {
  info "使用 Docker 安装..."
  check_docker
  docker build -t cicd-init "https://github.com/${REPO}.git#${BRANCH}"
  # Create alias
  DOCKER_ALIAS='cicd-init(){ docker run --rm -v "$(pwd):/src" cicd-init:latest "$@"; }'
  if [ -f ~/.bashrc ]; then
    grep -qF 'cicd-init()' ~/.bashrc || echo "$DOCKER_ALIAS" >> ~/.bashrc
  fi
  if [ -f ~/.zshrc ]; then
    grep -qF 'cicd-init()' ~/.zshrc || echo "$DOCKER_ALIAS" >> ~/.zshrc
  fi
  info "安装完成! 重新加载 shell 后运行 cicd-init --help"
  info "或直接运行: docker run --rm -v \$(pwd):/src cicd-init:latest init -d /src"
}

echo ""
echo "=============================="
echo "  cicd-init 服务器部署"
echo "  仓库: github.com/${REPO}"
echo "=============================="
echo ""

case "$METHOD" in
  pipx)
    check_python
    install_pipx
    ;;
  venv)
    check_python
    install_venv
    ;;
  docker)
    install_docker
    ;;
  *)
    echo "用法: $0 --method=[pipx|venv|docker] [--prefix=/path] [--force]"
    echo ""
    echo "  pipx   - 用户级隔离安装（推荐）"
    echo "  venv   - 系统级安装到 /opt/cicd-init"
    echo "  docker - Docker 容器运行"
    exit 1
    ;;
esac

echo ""
cicd-init --help
