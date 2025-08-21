# 📝 DeepL Selenium 自动翻译脚本部署指南（Linux）

## 前提条件

* Linux 系统
* Python 3.10+
* 网络可访问 `https://www.deepl.com/translator`
* 待翻译文件，例如 `input.txt`
* 版本相匹配的Chrome和chromedriver
* 先登录服务器
  
---

# 版本 1️⃣：有 sudo 权限

适合可以用 `sudo` 安装软件和系统依赖的用户。

## 1. 安装 Python3 和 pip

```bash
sudo apt update
sudo apt install -y python3 python3-pip unzip wget
```

## 2. 安装 Google Chrome

```bash
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install -y ./google-chrome-stable_current_amd64.deb
google-chrome --version
```

## 3. 安装 ChromeDriver

1. 查询 Chrome 主版本号：

```bash
google-chrome --version
```

2. 下载对应版本的 ChromeDriver：

```bash
wget https://chromedriver.storage.googleapis.com/<CHROME_MAJOR_VERSION>.0.XXXX/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
sudo mv chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver
chromedriver --version
```

> `<CHROME_MAJOR_VERSION>` 和 `XXXX` 替换为对应 ChromeDriver 完整版本号，可参考 [ChromeDriver 官网](https://chromedriver.chromium.org/downloads)。

## 4. 创建 Python 虚拟环境并安装依赖

```bash
python3 -m venv deepl_env
source deepl_env/bin/activate
pip install --upgrade pip
pip install selenium
```

## 5. 配置脚本路径

修改脚本：

```python
options.binary_location = "/usr/bin/google-chrome"
Service("/usr/local/bin/chromedriver")
INPUT_FILE = "input.txt"
OUTPUT_FILE = "deepl_trans.txt"
```
* 一定要在脚本上上传自己环境下的正确路径，OUTPUT_FILE 可以不配置路径，运行后会自动生成

## 6. 运行脚本

```bash
source deepl_env/bin/activate
python deepl.py
```

* 在home运行：python deepl.py的绝对路径；cd进入deepl.py同一文件夹下运行：python deepl.py 即可
* 脚本会监控 `input.txt` 并写入 `deepl_trans.txt`

---

# 版本 2️⃣：没有 sudo 权限（使用 conda）

适合没有系统安装权限，但可以用 conda 管理 Python 环境的用户。

## 1. 安装 Miniconda / Anaconda

* 下载 Miniconda：

```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
```

* 按提示安装到用户目录，例如 `$HOME/miniconda3`
* 初始化 conda：

```bash
source $HOME/miniconda3/bin/activate
```

## 2. 创建 conda 环境

```bash
conda create -n deepl_env python=3.10 -y
conda activate deepl_env
```

## 3. 安装 Selenium

```bash
pip install selenium
```

## 4. 安装 Chrome 和 ChromeDriver 到用户目录

1. 下载 Chrome portable：

```bash
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
dpkg -x google-chrome-stable_current_amd64.deb $HOME/chrome
```

* Chrome 路径示例：

```text
$HOME/chrome/opt/google/chrome/chrome
```

2. 下载 ChromeDriver：

```bash
wget https://chromedriver.storage.googleapis.com/<CHROME_MAJOR_VERSION>.0.XXXX/chromedriver_linux64.zip
unzip chromedriver_linux64.zip -d $HOME/chrome
chmod +x $HOME/chrome/chromedriver
```

## 5. 配置脚本路径

修改脚本：

```python
options.binary_location = "/home/user/chrome/opt/google/chrome/chrome"
Service("/home/user/chrome/chromedriver")
INPUT_FILE = "/home/user/pro/code/deepl/input.txt"
OUTPUT_FILE = "/home/user/pro/code/deepl/deepl_trans.txt"
```
* 一定要在脚本上上传自己环境下的正确路径，OUTPUT_FILE 可以不配置路径，运行后会自动生成

## 6. 运行脚本

```bash
conda activate deepl_env
python /home/user/pro/code/deepl/deepl_translate.py
```

* 在home运行：python deepl.py的绝对路径；cd进入deepl.py同一文件夹下运行：python deepl.py 即可
* 脚本会自动监控 `input.txt` 并写入 `deepl_trans.txt`

---

# ⚠️ 注意事项（两种版本都需要）

1. **网络访问**：DeepL 页面需要外网访问
2. **浏览器权限**：（安装好之后要运行下面这两条指令，不然没有权限）

```bash
chmod +x /home/user/chrome/chromedriver
chmod +x /home/user/chrome/opt/google/chrome/chrome
```

4. **依赖系统库**（仅有 sudo 可用时安装）：

```bash
sudo apt install -y fonts-liberation libappindicator3-1 libnss3 lsb-release xdg-utils
```

5. **浏览器自动关闭**：脚本捕获 `KeyboardInterrupt` 后会自动关闭 Chrome

---


# 一键部署脚本示例

保存为 `setup_deepl_env.sh` 并赋予可执行权限：

```bash
chmod +x setup_deepl_env.sh
```

```bash
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
```

---

### 🔹 使用方法

#### 有 sudo 权限

```bash
sudo ./setup_deepl_env.sh
source $DEEPL_DIR/python_env/bin/activate
python deepl_translate.py
```

#### 无 sudo 权限（使用 conda）

```bash
./setup_deepl_env.sh
source $HOME/miniconda3/bin/activate
conda activate deepl_env
python deepl_translate.py
```

---

这个一键部署脚本会自动：

* 判断权限
* 安装系统依赖或 conda 环境
* 下载 Chrome + ChromeDriver 并设置权限
* 创建 Python 环境并安装 Selenium

---


