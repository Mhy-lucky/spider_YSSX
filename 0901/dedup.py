# 去重脚本：删除文件中的重复行，并保持原有顺序
def remove_duplicate_lines(input_file, output_file):
    seen = set()
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8') as outfile:
        for line in infile:
            if line not in seen:
                seen.add(line)
                outfile.write(line)

if __name__ == "__main__":
    input_path = "/Users/admin/Desktop/coding/0904/urls.txt"   # 输入文件
    output_path = "output.txt" # 去重后的输出文件
    remove_duplicate_lines(input_path, output_path)
    print(f"去重完成！结果已保存到 {output_path}")
