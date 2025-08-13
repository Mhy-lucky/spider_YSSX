#!/bin/bash

# 自动提交到 GitHub 的脚本
# 用法: ./gitpush.sh "提交说明"

# 先同步远程仓库，避免冲突
git pull

# 添加所有修改
git add .

# 提交（如果没写说明，就用默认文字）
if [ -z "$1" ]; then
    git commit -m "更新文件"
else
    git commit -m "$1"
fi

# 推送到远程仓库
git push -u origin main



