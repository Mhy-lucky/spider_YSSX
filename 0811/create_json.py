import json

data = []

while True:
    user_input = input("请输入内容（输入 'exit' 结束）：")
    if user_input.lower() == 'exit':
        break
    data.append(user_input)

with open('output.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print("内容已保存到 output.json 文件。")