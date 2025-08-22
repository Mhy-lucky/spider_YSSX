#!/bin/bash
INPUT_FILE="/data1/to_hongyao/chinese_web_novel.zh"
TMP_DIR="/home/maohongyao/tmp_clean_parts"
BLOCK_LINES=50000000
MAX_PROCS=8
OUTPUT_FILE="/home/maohongyao/data_clean.zh"

# 创建临时目录
mkdir -p "$TMP_DIR"
cd "$TMP_DIR" || exit 1

# 拆分文件到临时目录
echo "📦 拆分大文件，每块 $BLOCK_LINES 行..."
split -l $BLOCK_LINES "$INPUT_FILE" part_

PARTS=(part_*)
TOTAL_PARTS=${#PARTS[@]}
echo "🔹 总块数: $TOTAL_PARTS"

# 获取总行数
TOTAL_LINES=0
for f in "${PARTS[@]}"; do
    LINES=$(wc -l < "$f")
    TOTAL_LINES=$((TOTAL_LINES + LINES))
done
echo "📏 总行数估算: $TOTAL_LINES"

# 并行清洗
echo "🚀 启动并行清洗..."
for f in "${PARTS[@]}"; do
    OUT_FILE="${f}_clean"
    python /home/maohongyao/pro/code/clean/clean_novel.py "$f" "$OUT_FILE" &
    while [ $(jobs -r | wc -l) -ge $MAX_PROCS ]; do
        sleep 2
    done
done

# 等待所有进程完成
wait
echo "✅ 所有块清洗完成"

# 合并清洗结果
cat part_*_clean > "$OUTPUT_FILE"

# 去重
sort -u "$OUTPUT_FILE" -o "$OUTPUT_FILE"

# 清理临时文件
rm -f part_* part_*_clean

echo "🎉 清洗完成，最终文件: $OUTPUT_FILE"
