# spider_YSSX
云上曲率公司爬虫实习
## All from myself：
①要爬取原图：需要先找到整张页面<a标签，然后跳转到具体的详情页面<img标签，下载(8-11成果) 一般会带有水印
②爬取缩略图：找到<img标签即可，不用跳转（8-12成果） 没有水印但是不清晰
③class_selector:a.xxxx class_name:xxxx

## 一个完整的 GitHub 工作流程，确保你可以：

1. **维护自己的代码仓库**（存放项目）
2. **写日志文档**（比如 `README.md`、开发日志）
3. **正确使用 Git 和 GitHub**（避免 PAT、权限等问题）


---

## **第一步：准备工作**

### 1. 安装 Git

* **Mac**（推荐直接用系统自带的 Git）：

  ```bash
  git --version
  ```

  如果没安装，会提示安装，点 **Install** 就好。

### 2. 注册 / 登录 GitHub

* [GitHub 官网](https://github.com) 注册账号（你已经有了：`Mhy-lucky`）。

---

## **第二步：生成并配置 PAT（Personal Access Token）**

因为 GitHub 取消了直接用密码推送代码，所以必须用 **PAT**。

### 1. 生成 PAT

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

## **第三步：在本地配置 Git**

### 1. 设置全局用户名和邮箱（必须和 GitHub 对应）

```bash
git config --global user.name "Mhy-lucky"
git config --global user.email "你的GitHub邮箱"
```

### 2. 删除旧的远程仓库绑定（你之前的关联可能有问题）

进入你的项目文件夹：

```bash
cd /路径/到/你的项目
git remote remove origin
```

---

## **第四步：创建 GitHub 仓库**

1. 登录 GitHub → 点击右上角 **+** → **New repository**
2. 填：

   * Repository name：`spider_YSSX`
   * 勾选 `Add a README file`（方便写日志）
3. 创建后 GitHub 会给你一个 **仓库地址**，形如：

   ```
   https://github.com/Mhy-lucky/spider_YSSX.git
   ```

---

## **第五步：关联本地项目到新仓库**

假设你项目文件夹是 `/Users/admin/spider_YSSX`

```bash
cd /Users/admin/spider_YSSX

# 初始化 Git 仓库（如果没有）
git init

# 添加远程仓库
git remote add origin https://github.com/Mhy-lucky/spider_YSSX.git
```

---

## **第六步：第一次提交并推送**

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

## **第七步：写日志文档**

### 1. 使用 README.md 记录说明

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

### 2. 提交日志更新

```bash
git add README.md
git commit -m "更新 README，添加开发日志"
git push
```

---

## **第八步：常用 Git 操作**

| 功能       | 命令                   |
| -------- | -------------------- |
| 查看当前状态   | `git status`         |
| 查看提交历史   | `git log --oneline`  |
| 添加文件到暂存区 | `git add 文件名`        |
| 提交       | `git commit -m "说明"` |
| 推送到远程仓库  | `git push`           |
| 拉取远程更新   | `git pull`           |

---

## **第九步：避免 PAT 每次都要输入**

如果不想每次输入用户名 + PAT，可以让 Git 记住：

```bash
git config --global credential.helper store
```

然后下一次输入后就会保存到本地。

---


