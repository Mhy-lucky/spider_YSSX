### 1. **准备服务器环境**

确保你的服务器上已安装 Python 3 和相关工具。

#### 1.1 **安装 Python 3**

首先，检查系统是否已安装 Python 3：

```bash
python3 --version
```

如果没有安装，可以通过以下命令进行安装：

**对于 Ubuntu/Debian 系统**：

```bash
sudo apt update
sudo apt install python3 python3-pip
```

**对于 CentOS/RHEL 系统**：

```bash
sudo yum install python3
```

#### 1.2 **安装 `pip` 和虚拟环境工具**

安装完 Python 后，确保 `pip` 工具已经安装：

```bash
pip3 --version
```

如果没有安装 `pip`，可以使用以下命令安装：

```bash
sudo apt install python3-pip  # 对于 Ubuntu 系统
sudo yum install python3-pip  # 对于 CentOS 系统
```

然后，安装 `virtualenv` 工具来创建虚拟环境（推荐）：

```bash
# 安装 virtualenv
sudo pip3 install virtualenv

# 创建虚拟环境
virtualenv venv

# 激活虚拟环境
source venv/bin/activate
```

### 2. **安装所需的 Python 库**

由于你没有 `requirements.txt` 文件，以下是手动安装所需的库：

```bash
pip install selenium chromedriver-autoinstaller argparse
```

* **`selenium`**：自动化浏览器操作，进行翻译。
* **`chromedriver-autoinstaller`**：自动安装与 Google Chrome 版本匹配的 ChromeDriver。
* **`argparse`**：用于解析命令行参数。

### 3. **安装和配置 Google Chrome 浏览器**

#### 3.1 **安装 Google Chrome 浏览器**

你需要在 Linux 系统上安装 **Google Chrome** 浏览器。以下是如何在 Ubuntu/Debian 系统上安装 Google Chrome 的步骤：

```bash
# 更新 apt 软件包列表
sudo apt update

# 安装 wget 工具（如果未安装）
sudo apt install wget

# 下载 Google Chrome 的 .deb 安装包
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb

# 安装下载的包
sudo dpkg -i google-chrome-stable_current_amd64.deb

# 如果遇到依赖问题，执行以下命令修复
sudo apt --fix-broken install
```

对于 **CentOS/RHEL** 系统，你可以参考 [Google Chrome 官方文档](https://www.google.com/chrome/) 进行安装。


### 4. **配置防火墙和端口**

如果你的服务器有防火墙，确保 **9222** 端口是开放的。因为 Chrome 浏览器会通过该端口进行远程调试。使用以下命令（适用于 Ubuntu/Debian）来打开该端口：

```bash
sudo ufw allow 9222
```

如果是 CentOS 系统，你可以使用 `firewalld` 进行端口开放：

```bash
sudo firewall-cmd --zone=public --add-port=9222/tcp --permanent
sudo firewall-cmd --reload
```


### 5. **运行脚本**

确保输入文件和输出文件路径正确后，可以使用以下命令来运行脚本：

```bash
python3 deepl_translation.py <input_file> <output_file> <source_lang> <target_lang>
```

例如，假设输入文件为 `input.txt`，输出文件为 `output.txt`，源语言为 `zh`，目标语言为 `en`，则可以执行以下命令：

```bash
python3 deepl_translation.py input.txt output.txt zh en
```

