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





___
## 二、GitHub学习成果
___
### 个人
一个完整的 GitHub 工作流程，确保你可以：

1. **维护自己的代码仓库**（存放项目）
2. **写日志文档**（比如 `README.md`、开发日志）
3. **正确使用 Git 和 GitHub**（避免 PAT、权限等问题）


---

### **第一步：准备工作**

#### 1. 安装 Git

* **Mac**（推荐直接用系统自带的 Git）：

  ```bash
  git --version
  ```

  如果没安装，会提示安装，点 **Install** 就好。

#### 2. 注册 / 登录 GitHub

* [GitHub 官网](https://github.com) 注册账号（你已经有了：`Mhy-lucky`）。

---

### **第二步：生成并配置 PAT（Personal Access Token）**

因为 GitHub 取消了直接用密码推送代码，所以必须用 **PAT**。

#### 1. 生成 PAT

1. 登录 GitHub → 点击右上角头像 → **Settings**
2. 左侧找到 **Developer settings**
3. 点击 **Personal access tokens → Tokens (classic)**
4. 点 **Generate new token → Generate new token (classic)**
5. 勾选权限：

   * `repo`（仓库读写）
   * `workflow`（可选，运行 CI）
6. 设置有效期（比如 90 天 / 无限制）
7. **生成后**，一定要把它复制下来保存（生成页面关掉就看不到了）。

---

### **第三步：在本地配置 Git**

#### 1. 设置全局用户名和邮箱（必须和 GitHub 对应）

```bash
git config --global user.name "Mhy-lucky"
git config --global user.email "你的GitHub邮箱"
```

#### 2. 删除旧的远程仓库绑定（如果之前有绑定过）

进入你的项目文件夹：

```bash
cd /路径/到/你的项目
git remote remove origin
```

---

### **第四步：创建 GitHub 仓库**

1. 登录 GitHub → 点击右上角 **+** → **New repository**
2. 填：

   * Repository name：`spider_YSSX`
   * 勾选 `Add a README file`（方便写日志）
3. 创建后 GitHub 会给你一个 **仓库地址**，形如：

   ```
   https://github.com/Mhy-lucky/spider_YSSX.git
   ```

---

### **第五步：关联本地项目到新仓库**

假设你项目文件夹是 `/Users/admin/spider_YSSX`

```bash
cd /Users/admin/spider_YSSX

# 初始化 Git 仓库（如果没有）
git init

# 添加远程仓库
git remote add origin https://github.com/Mhy-lucky/spider_YSSX.git
```

---

### **第六步：第一次提交并推送**

```bash
# 添加所有文件
git add .

# 提交记录（写清楚提交说明）
git commit -m "第一次提交，上传项目"

# 推送到 main 分支
git push -u origin main
```

系统会提示：

```
Username for 'https://github.com':
```

* 输入 **GitHub 用户名**（`Mhy-lucky`）

```
Password for 'https://Mhy-lucky@github.com':
```

* 粘贴 **PAT**（虽然看不到输入内容，但是已经粘贴进去了，按回车即可）

---

### **第七步：写日志文档**

#### 1. 使用 README.md 记录说明

在项目根目录新建文件：

```bash
touch README.md
```

写内容：

```markdown
# spider_YSSX
这是我的爬虫项目。

## 开发日志
- 2025-08-12: 初始化项目并提交到 GitHub
- 2025-08-13: 完善数据抓取模块
```

#### 2. 提交日志更新

```bash
git add README.md
git commit -m "更新 README，添加开发日志"
git push
```

---

### **第八步：常用 Git 操作**

| 功能       | 命令                   |
| -------- | -------------------- |
| 查看当前状态   | `git status`         |
| 查看提交历史   | `git log --oneline`  |
| 添加文件到暂存区 | `git add 文件名`        |
| 提交       | `git commit -m "说明"` |
| 推送到远程仓库  | `git push`           |
| 拉取远程更新   | `git pull`           |

---

### **第九步：避免 PAT 每次都要输入**

如果不想每次输入用户名 + PAT，可以让 Git 记住：

```bash
git config --global credential.helper store
```

然后下一次输入后就会保存到本地。

---
### **第十步：日常操作： 已经建立并且关联好远程仓库之后，后续需要上传新的文件或者之前的文件内容有修改时：**
1. git pull origin main --rebase   # 先拉取远程最新代码
2. git add .                       # 添加修改
3. git commit -m "更新说明"         # 提交修改
4. git push origin main            # 推送到远程
___

### 团队协作
---

#### 团队Git协作超简洁小贴士

1. **克隆仓库**
   每个人先从远程仓库复制代码到本地：
   `git clone <仓库地址>`

2. **创建功能分支**
   切换主分支拉最新，建一个专属功能分支：

   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/你的功能名
   ```

3. **日常开发和提交**
   在自己的功能分支写代码，分批提交：

   ```bash
   git add .
   git commit -m "简洁明了的改动说明"
   ```

4. **保持功能分支更新**
   每次开发前，从主分支拉最新合并进功能分支，避免冲突：

   ```bash
   git checkout main
   git pull origin main
   git checkout feature/你的功能名
   git merge main  # 或 git rebase main
   ```

5. **推送功能分支**
   把本地功能分支代码推送到远程仓库：
   `git push origin feature/你的功能名`

6. **发起Pull Request（PR）**
   在GitHub网页端，从功能分支请求合并到主分支，等待团队审核。

7. **代码审核与修改**
   审核人提出建议后，继续在功能分支修改并推送更新。

8. **合并代码**
   审核通过，合并功能分支到主分支，完成后删除功能分支。

9. **更新本地主分支**
   合并后，大家都拉取最新主分支代码继续开发：

   ```bash
   git checkout main
   git pull origin main
   ```

10. **冲突解决**
    出现冲突时，手动修改冲突文件，保存后：

    ```bash
    git add 冲突文件
    git rebase --continue  # 或 git commit
    ```

---

##### 额外小贴士

* 提交信息写清楚，方便别人理解。
* 不直接在主分支开发，保护主分支稳定。
* 功能完成再合并，避免主分支出现不稳定代码。
* 代码规范团队约定，保持一致。
* 定期清理不需要的分支，保持仓库整洁。


---

## 三、📝 Selenium 爬虫元素定位与自动化操作完整笔记

在使用 Selenium 做爬虫或网页自动化时，**元素定位**和**动态页面操作**是核心步骤。元素定位不准确或操作不当，可能导致爬虫失败、翻译/数据获取错误，或触发安全验证。

---

### 1️⃣ 元素定位原则

1. **尽量精确定位**

   * 直接定位到目标元素，避免在中间层元素上重复操作。
   * 示例：如果要点击“提交按钮”，不要先定位整个表单再在里面找，除非必须。

2. **从外到里 vs 直接定位**

   * **从外到里**：先定位父容器，再在容器内查找子元素。

     * 优点：减少同类元素重复冲突。
     * 缺点：步骤多，可能增加 `stale element` 错误。
     * 适用场景：动态生成页面或存在多个同类元素。
   * **直接定位**：用精确选择器（ID、类名、XPath 等）直接找到目标元素。

     * 优点：简洁、快速。
     * 缺点：页面结构变化时可能失效。
     * 适用场景：结构固定、唯一性强的元素。

3. **选择最稳定的定位方式**

   * 尽量避免依赖 `nth-child` 或过长 XPath。
   * 优先顺序：`ID > class > CSS > XPath`。

---

### 2️⃣ 常用元素定位方式

| 方法               | 示例                                                                                | 特点                            |
| ---------------- | --------------------------------------------------------------------------------- | ----------------------------- |
| **ID**           | `driver.find_element(By.ID, "username")`                                          | 唯一性高，快速，稳定                    |
| **Class**        | `driver.find_element(By.CLASS_NAME, "login-button")`                              | 若多个同类元素，可用 `find_elements` 遍历 |
| **Tag**          | `driver.find_element(By.TAG_NAME, "input")`                                       | 一般配合容器限定                      |
| **CSS Selector** | `driver.find_element(By.CSS_SELECTOR, "div.container > button.submit")`           | 灵活，支持组合父子关系、类名、ID             |
| **XPath**        | `driver.find_element(By.XPATH, "//div[@class='container']//button[text()='提交']")` | 强大，支持文本/属性匹配，但过长易失效           |

---

### 3️⃣ 父子元素定位技巧

1. **先定位父元素，再定位子元素**

```python
container = driver.find_element(By.CLASS_NAME, "dropdown")
button = container.find_element(By.TAG_NAME, "button")
```

2. **直接定位子元素**

```python
button = driver.find_element(By.CSS_SELECTOR, ".dropdown > button")
```

**总结**：

* 父子定位更安全，减少重复元素干扰；
* 直接定位更简洁，但要保证唯一性。

---

### 4️⃣ 元素状态判断（显式等待）

```python
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# 元素可见
elem = WebDriverWait(driver, 10).until(
    EC.visibility_of_element_located((By.ID, "submit"))
)

# 元素可点击
elem = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.ID, "submit"))
)

# 动态文本变化
import time
start_time = time.time()
while time.time() - start_time < 10:
    text = elem.text.strip()
    if text:
        break
    time.sleep(0.2)
```

---

### 5️⃣ 不同类型元素操作方式

| 元素类型        | 定位方法                 | 操作方式 / 注意事项                               |
| ----------- | -------------------- | ----------------------------------------- |
| 按钮 Button   | id / class / XPath   | 点击 `click()`，必要时滚动到视野 `move_to_element()` |
| 输入框 Input   | id / name / CSS      | 清空 `clear()` → 输入 `send_keys()`           |
| 图片 Image    | XPath / CSS / alt 属性 | 获取 `src` 属性，用于展示或验证码                      |
| 下拉菜单 Select | CSS / XPath          | 点击下拉 → 等待选项出现 → 点击选项                      |
| 动态文本或结果     | CSS / XPath          | 获取 `text`，等待异步更新                          |
| 弹窗 / 验证码    | CSS / XPath          | 可能需人工操作或特殊处理                              |

---

### 6️⃣ 动态页面 & 安全验证处理逻辑

* 操作可能触发 **安全验证**（如图形验证码）
* 点击语言或按钮未生效时：

  1. 下拉点击目标语言
  2. 检测是否成功切换
  3. 若未生效 → 提示人工完成安全验证 → 再次点击语言
  4. 循环直到成功
* 注意：每次操作前检查元素可点击，防止 `stale element` 异常

---

### 7️⃣ 完整流程图
<img width="774" height="486" alt="截屏2025-08-15 17 53 11" src="https://github.com/user-attachments/assets/6dcc5a1d-3f6d-42f0-9451-997797f9fbe2" />
<img width="771" height="560" alt="截屏2025-08-15 17 53 34" src="https://github.com/user-attachments/assets/ec7b8ede-2573-46da-a8ea-a285ec0ac3ed" />

---

### 8️⃣ 特殊提示

1. **循环操作语言选择**

   * 点击语言未生效 → 循环下拉 → 点击 → 等待 → 提示人工安全验证 → 再点击

2. **验证码 / 安全验证**

   * 自动化时可能触发图形验证码
   * 无法完全自动化识别时，只能循环提示人工完成或使用 OCR

3. **避免常见异常**

   * `StaleElementReferenceException` → 元素刷新后引用失效 → 重新定位
   * `NoSuchElementException` → 元素未渲染或选择器错误 → 使用显式等待和检查选择器

4. **操作顺序**

   1. 定位元素
   2. 等待元素可见 / 可点击
   3. 执行操作（点击/输入）
   4. 检查是否生效
   5. 循环处理安全验证 / 异常
   6. 获取最终结果

---

✅ **核心总结**

* 定位元素时，**稳定性优先**，唯一性次之，简洁性再次
* 动态页面优先 **显式等待 + 父子定位**
* 静态页面可直接 CSS/XPath 定位
* 安全验证出现时，循环操作直到成功再获取结果
* 不同元素类型有不同操作方式（按钮 / 输入框 / 下拉 / 图片 / 弹窗）

---






