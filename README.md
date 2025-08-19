# spider_YSSX
云上曲率公司爬虫实习

___
## 一、All from myself：
___
1. 要爬取原图：
   需要先找到<a标签（而不是<div标签）一般就表示这张图片本身了，然后find_elements即可找到页面上的所有图片，再跳转到具体的详情页面<img标签，find_element,下载(8-11成果), 一般会带有水印
<img width="1194" height="495" alt="截屏2025-08-12 19 21 40" src="https://github.com/user-attachments/assets/a5ad4c38-8743-4d45-a19e-3bb393195168" />

2. 爬取缩略图：
   找到<img标签即可，不用跳转（8-12成果,没有水印但是不清晰

3. 区别: class_selector:a.xxxx class_name:xxxx

4.爬虫小贴士
* ①无论是否需要无头模式，在没有得到结果之前都不要无头，实时看到进程找元素定位是否有错误
* ②元素定位首先使用确定的，如id,class等，能直接定位就不要一层一层找，不要使用过长Xpath
* ③使用Page Object
* ④元素定位时，一定要全屏去找，打开网之后进入全屏去进行某些元素的定位

5.反爬总结
* ①安全验证无法跳过，也无法解决（小牛翻译）
* ②翻译请求由前端JS监听输入事件触发，模拟点击输入内容无法触发翻译（Slate.js 编辑器）（火山翻译）






## 三、
---

## 四、📝 爬虫需求模板（Page Object 模式）
请尽量完整填写，越详细越准确：
网站基本信息
网站 URL：
登录/权限要求（有/无，是否需要账号密码）：
是否有验证码 / 安全验证（图形/滑块/其他）：
目标数据
需要爬取的主要信息类型（文本 / 图片 /文件 / 下拉选项 等）：
具体字段（如标题、内容、作者、发布时间 等）：
需要保存的格式（CSV / Excel / JSON / 数据库）：
目标页面结构
页面是静态还是动态渲染（AJAX/JS）：
是否存在分页 / 滚动加载 / 下拉刷新：
是否需要翻页 / 无限滚动：
操作需求
是否需要模拟点击按钮 / 下拉菜单 / 选择选项：
是否需要输入文本（搜索框 / 登录 / 筛选）：
是否需要循环操作（比如循环选择多个下拉项或翻页）：
元素定位信息
是否能提供主要元素的 ID / class / CSS / XPath：
对于复杂页面，是否希望采用父子元素定位：
需要显式等待的元素（可见 / 可点击 / 已存在）：
其他要求
是否要求 无头模式（Headless）运行：
是否需要日志 / 异常处理 / 重试机制：
是否有特殊操作（如下载文件、截图、验证码人工提示）：

___
## 五、服务器跑代码，安装 Conda 并创建 Python 环境笔记
___

### 1️⃣ 登录服务器

```bash
ssh h29
```

登录后，会看到类似：

```
[maohongyao@localhost ~]$
```

---

### 2️⃣ 服务器未安装 Conda 时的一条命令安装脚本

```bash
ssh h29 "bash -c '\
# 下载并安装 Miniconda
wget -O ~/Miniconda3-latest-Linux-x86_64.sh https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
bash ~/Miniconda3-latest-Linux-x86_64.sh -b -p ~/miniconda3 && \
# 使用国内镜像，避免 TOS 和下载慢
~/miniconda3/bin/conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/ && \
~/miniconda3/bin/conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/ && \
# 接受官方 TOS
~/miniconda3/bin/conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main && \
~/miniconda3/bin/conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r && \
# 创建 Python 3.10 环境
~/miniconda3/bin/conda create -n myenv python=3.10 -y || true && \
# 安装依赖
~/miniconda3/bin/conda run -n myenv pip install selenium requests -i https://pypi.tuna.tsinghua.edu.cn/simple && \
# 验证 Python 和 Selenium
~/miniconda3/bin/conda run -n myenv python -c \"import sys; print(\\\"Python version:\\\", sys.version)\" && \
~/miniconda3/bin/conda run -n myenv python -c \"import selenium; print(\\\"Selenium version:\\\", selenium.__version__)\" && \
# 运行你的 Python 脚本
~/miniconda3/bin/conda run -n myenv python your_script.py\
'"
```

> 替换 `your_script.py` 为你自己的脚本路径

---

### 3️⃣ 服务器已安装 Conda 时的一条命令脚本

```bash
ssh h29 "bash -c '\
# 使用国内镜像
~/miniconda3/bin/conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/ && \
~/miniconda3/bin/conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/ && \
# 接受官方 TOS
~/miniconda3/bin/conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main && \
~/miniconda3/bin/conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r && \
# 创建 Python 3.10 环境（已存在不会报错）
~/miniconda3/bin/conda create -n myenv python=3.10 -y || true && \
# 安装依赖
~/miniconda3/bin/conda run -n myenv pip install selenium requests -i https://pypi.tuna.tsinghua.edu.cn/simple && \
# 验证 Python 和 Selenium
~/miniconda3/bin/conda run -n myenv python -c \"import sys; print(\\\"Python version:\\\", sys.version)\" && \
~/miniconda3/bin/conda run -n myenv python -c \"import selenium; print(\\\"Selenium version:\\\", selenium.__version__)\" && \
# 运行你的 Python 脚本
~/miniconda3/bin/conda run -n myenv python your_script.py\
'"
```

---

### 4️⃣ 安装完成后的验证

```bash
# 查看 Python 版本
python --version

# 查看 Selenium 版本
python -c "import selenium; print(selenium.__version__)"
```

* Python 应该是你指定的版本（如 3.10.18）
* Selenium 应该可以正常导入（如 4.35.0）

---

### 5️⃣ 后台运行脚本示例

```bash
~/miniconda3/bin/conda run -n myenv nohup python your_script.py > output.log 2>&1 &
```

---

### 6️⃣ 登录服务器后继续使用 Conda 环境

```bash
source ~/miniconda3/bin/activate
conda activate myenv
```

然后就可以直接运行你的 Python 脚本。

---

### 7️⃣ 常见问题与解决方法

| 问题                                                      | 原因        | 解决方法                                                 |
| ------------------------------------------------------- | --------- | ---------------------------------------------------- |
| 安装报 `--More--`                                          | 安装许可证分页显示 | 使用 `-b` 无交互安装，或按空格回车继续                               |
| 安装路径有空格报错 `Cannot install into directories with spaces` | 路径不合法     | 选择无空格路径，例如 `~/miniconda3`                            |
| 激活 Conda 报错 `No such file or directory`                 | 路径写错      | 使用 `source ~/miniconda3/bin/activate`                |
| 创建环境报 `EnvironmentNameNotFound`                         | 环境不存在     | 先用 `conda info --envs` 查看，再创建新环境                     |
| pip 下载超时                                                | 网络问题      | 使用国内镜像：`-i https://pypi.tuna.tsinghua.edu.cn/simple` |

---

### 8️⃣ 优点

* 一键完成安装、环境创建、依赖安装、版本验证和脚本运行
* 支持国内镜像加速下载
* 不需要管理员权限
* 可直接后台运行脚本

#####  ps:
1.已经新建好了环境，每次需要从服务器进入环境时：
* source ~/miniconda3/bin/activate
* conda activate myenv
2.已经上传到服务器上的文件、文件夹，文件内容/文件夹内容在本地有改动的同步方法：
* 在本地终端输入rsync -avz --progress "/Users/admin/Desktop/爬虫实习/0814/" h29:/home/maohongyao/0814/

---







