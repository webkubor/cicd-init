#!/usr/bin/env bash
# ============================================================
#  cicd-init 一键安装脚本
#  用法: curl -sL https://raw.githubusercontent.com/webkubor/cicd-init/main/install.sh | bash
# ============================================================
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

info()  { echo -e "${CYAN}👉 $1${NC}"; }
ok()    { echo -e "${GREEN}✅ $1${NC}"; }
warn()  { echo -e "${YELLOW}⚠️  $1${NC}"; }
fail()  { echo -e "${RED}❌ $1${NC}"; exit 1; }

echo ""
echo -e "${CYAN}════════════════════════════════════════${NC}"
echo -e "${CYAN}   cicd-init 安装器${NC}"
echo -e "${CYAN}════════════════════════════════════════${NC}"
echo ""

# ── 1. 检查/安装 Python3 ──
info "检查 Python 3 ..."
if command -v python3 &>/dev/null; then
    PY_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    PY_MAJOR=$(python3 -c "import sys; print(sys.version_info.major)")
    PY_MINOR=$(python3 -c "import sys; print(sys.version_info.minor)")
    if [ "$PY_MAJOR" -ge 3 ] && [ "$PY_MINOR" -ge 8 ]; then
        ok "Python $PY_VER 已就绪"
    else
        warn "Python 版本过低 ($PY_VER), 需要 3.8+"
        NEED_PY=true
    fi
else
    NEED_PY=true
fi

if [ "${NEED_PY:-false}" = true ]; then
    info "正在安装 Python 3 ..."
    if command -v brew &>/dev/null; then
        brew install python3
    elif command -v apt-get &>/dev/null; then
        sudo apt-get update -qq && sudo apt-get install -y -qq python3 python3-pip
    elif command -v yum &>/dev/null; then
        sudo yum install -y python3 python3-pip
    elif command -v apk &>/dev/null; then
        sudo apk add python3 py3-pip
    else
        fail "无法自动安装 Python，请手动安装 Python 3.8+ 后重试"
    fi
    ok "Python 3 安装完成"
fi

# ── 2. 检查/安装 pip ──
if ! python3 -m pip --version &>/dev/null 2>&1; then
    info "正在安装 pip ..."
    if command -v apt-get &>/dev/null; then
        sudo apt-get install -y -qq python3-pip
    elif command -v yum &>/dev/null; then
        sudo yum install -y python3-pip
    elif command -v apk &>/dev/null; then
        sudo apk add py3-pip
    else
        python3 -m ensurepip --default-pip 2>/dev/null || \
        curl -sS https://bootstrap.pypa.io/get-pip.py | python3
    fi
fi

# ── 3. 安装 cicd-init ──
info "正在安装 cicd-init ..."
if command -v pipx &>/dev/null; then
    pipx install git+https://github.com/webkubor/cicd-init.git --force
    ok "通过 pipx 安装成功"
elif command -v pip3 &>/dev/null; then
    pip3 install --user git+https://github.com/webkubor/cicd-init.git
    ok "通过 pip3 --user 安装成功"
    # 确保 ~/.local/bin 在 PATH
    if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc" 2>/dev/null || true
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.zshrc" 2>/dev/null || true
        export PATH="$HOME/.local/bin:$PATH"
        warn "已将 ~/.local/bin 加入 PATH，请重新打开终端或执行: source ~/.zshrc"
    fi
else
    python3 -m pip install --user git+https://github.com/webkubor/cicd-init.git
    ok "安装成功"
fi

# ── 4. 验证 ──
echo ""
if command -v cicd-init &>/dev/null; then
    VERSION=$(cicd-init --version 2>/dev/null || echo "unknown")
    ok "cicd-init $VERSION 安装成功！"
else
    # 尝试直接找
    FOUND=$(python3 -m pip show cicd-init 2>/dev/null | head -1) || true
    if [ -n "$FOUND" ]; then
        warn "cicd-init 已安装但不在 PATH 中"
        warn "请重新打开终端，或执行: export PATH=\"\$HOME/.local/bin:\$PATH\""
    else
        fail "安装失败，请手动运行: pip3 install git+https://github.com/webkubor/cicd-init.git"
    fi
fi

echo ""
echo -e "${CYAN}════════════════════════════════════════${NC}"
echo -e "${GREEN}  🎉 开始使用:${NC}"
echo ""
echo -e "  ${YELLOW}cd 你的前端项目目录${NC}"
echo -e "  ${YELLOW}cicd-init init${NC}"
echo ""
echo -e "  搞定！CI 配置已自动生成 🚀"
echo -e "${CYAN}════════════════════════════════════════${NC}"
echo ""
