input_file = '/home/maohongyao/pro/code/clean/data_clean.zh'
output_file = '/data1/to_hongyao/data_clean.zh'

with open(input_file, 'r', encoding='utf-8') as fin, \
     open(output_file, 'a', encoding='utf-8') as fout:  # 'a' 追加模式

    for line in fin:
        # 如果这一行是有问题的那行，直接跳过
        if line.strip() == '150718963':  # 精确匹配整行
            continue
        fout.write(line)

print("处理完成 ✅，已删除问题行并写入:", output_file)
