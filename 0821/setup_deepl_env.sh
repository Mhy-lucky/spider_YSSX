#!/bin/bash
# 一键部署 DeepL Selenium 翻译环境
# 版本：2025-08
# 用法：
# sudo ./setup_deepl_env.sh   # 有 sudo 权限
# ./setup_deepl_env.sh        # 无 sudo 权限，需 conda

echo "============================="
echo "DeepL Selenium 一键部署脚本"
echo "============================="

# ---------------- 用户配置 ----------------
DEEPL_DIR="$HOME/deepl_env_setup"
CHROME_DIR="$HOME/chrome"
INPUT_FILE="$HOME/deepl/input.txt"
OUTPUT_FILE="$HOME/deepl/deepl_trans.txt"
CHROME_VERSION="115.0.5790.170"   # 可根据需求修改
CHROMEDRIVER_VERSION="115.0.5790.170"

# ---------------- 检查 sudo ----------------
if sudo -n true 2>/dev/null; then
    echo "检测到 sudo 权限 ✅"
    SUDO=true
else
    echo "未检测到 sudo ❌，将使用用户目录 + conda 部署"
    SUDO=false
fi

# ---------------- 创建工作目录 ----------------
mkdir -p "$DEEPL_DIR"
mkdir -p "$CHROME_DIR"
mkdir -p "$(dirname "$INPUT_FILE")"
mkdir -p "$(dirname "$OUTPUT_FILE")"

# ---------------- 有 sudo 权限版本 ----------------
if [ "$SUDO" = true ]; then
    echo ">> 安装系统依赖和 Python3"
    sudo apt update
    sudo apt install -y python3 python3-pip wget unzip fonts-liberation libappindicator3-1 libnss3 lsb-release xdg-utils

    echo ">> 安装 Google Chrome"
    wget -O "$DEEPL_DIR/chrome.deb" https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
    sudo apt install -y "$DEEPL_DIR/chrome.deb"

    echo ">> 安装 ChromeDriver"
    wget -O "$DEEPL_DIR/chromedriver.zip" "https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip"
    unzip "$DEEPL_DIR/chromedriver.zip" -d "$DEEPL_DIR"
    sudo mv "$DEEPL_DIR/chromedriver" /usr/local/bin/
    sudo chmod +x /usr/local/bin/chromedriver

    echo ">> 创建虚拟环境"
    python3 -m venv "$DEEPL_DIR/python_env"
    source "$DEEPL_DIR/python_env/bin/activate"
    pip install --upgrade pip
    pip install selenium

    echo "✅ 有 sudo 权限版本部署完成"

# ---------------- 无 sudo 权限版本 ----------------
else
    echo ">> 安装 Miniconda（如果未安装）"
    if [ ! -d "$HOME/miniconda3" ]; then
        wget -O "$DEEPL_DIR/Miniconda.sh" https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
        bash "$DEEPL_DIR/Miniconda.sh" -b -p "$HOME/miniconda3"
    fi
    source "$HOME/miniconda3/bin/activate"

    echo ">> 创建 conda 环境"
    conda create -n deepl_env python=3.10 -y
    conda activate deepl_env
    pip install --upgrade pip
    pip install selenium

    echo ">> 下载 Chrome portable"
    wget -O "$DEEPL_DIR/chrome.deb" https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
    dpkg -x "$DEEPL_DIR/chrome.deb" "$CHROME_DIR"

    echo ">> 下载 ChromeDriver"
    wget -O "$DEEPL_DIR/chromedriver.zip" "https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip"
    unzip "$DEEPL_DIR/chromedriver.zip" -d "$CHROME_DIR"
    chmod +x "$CHROME_DIR/chromedriver"
    chmod +x "$CHROME_DIR/opt/google/chrome/chrome"

    echo "✅ 无 sudo 权限版本部署完成"
fi

# ---------------- 提示完成 ----------------
echo "===================================="
echo "部署完成 ✅"
echo "输入文件路径: $INPUT_FILE"
echo "输出文件路径: $OUTPUT_FILE"
echo "Chrome 路径:"
if [ "$SUDO" = true ]; then
    echo "  /usr/bin/google-chrome"
    echo "ChromeDriver 路径: /usr/local/bin/chromedriver"
else
    echo "  $CHROME_DIR/opt/google/chrome/chrome"
    echo "ChromeDriver 路径: $CHROME_DIR/chromedriver"
fi
echo "请在脚本中更新 INPUT_FILE 和 OUTPUT_FILE 路径"
echo "===================================="