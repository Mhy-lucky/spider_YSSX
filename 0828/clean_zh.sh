#!/bin/bash
# 高效清洗小说文件：删除生僻字/错字行 + 半句行
INPUT="/data1/to_hongyao/data.zh"
OUTPUT="/data1/to_hongyao/data_clean.zh"
PROGRESS_INTERVAL=1000000

awk -v interval=$PROGRESS_INTERVAL 'BEGIN{
    # 允许的字符：中文、数字、常用中文标点
    valid="^[一-龥，。！？；：“”‘’（）【】——、…0-9[:space:]]+$"
    # 允许的结尾标点：句号/问号/感叹号/双引号
    end="[。！？”]$"
    total=0; kept=0
}
{
    total++
    text=$0
    # 非法字符
    if (text !~ valid) next
    # 结尾不完整
    if (text !~ end) next
    # 保留
    print text
    kept++
    if (total % interval == 0) {
        printf("[seen] %d lines, [kept] %d lines\n", total, kept) > "/dev/stderr"
    }
}
END{
    printf("完成 ✅ 总行数: %d, 保留: %d, 删除: %d\n", total, kept, total-kept) > "/dev/stderr"
}' "$INPUT" > "$OUTPUT"
