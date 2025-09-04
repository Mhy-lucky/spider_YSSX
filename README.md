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
* ⑤先写好一个爬虫小框架（比如固定的内容可以爬到翻译的结果），再去扩充其他的部分，不要一口吃成个大胖子，能成功运行的小demo单独保存成文件，一步一步得到final文件
* ⑥** GPT解决不了问题的时候上CSDN，棒啊！**
* ⑦对于翻译框等限制字数要求的，看清楚是字符数还是单词数（DeepL）
* ⑧chrome_options.add_argument("--window-size=1920,1080")  # ✅ 无头模式必加，防止加载不完整
* ⑨使用引擎URL参数直接选择语言，避免下拉框点击失败。（比如对于谷歌翻译：url = f"https://translate.google.com/?sl=auto&tl={TARGET_LANG}&text={encoded_text}&op=translate"）

5.反爬总结
* ①安全验证无法跳过，也无法解决（小牛翻译）
* ②翻译请求由前端JS监听输入事件触发，模拟点击输入内容无法触发翻译（Slate.js 编辑器）（火山翻译/腾讯翻译君）
* ③本地可跑，服务器上刷新一下就会导致timeout(google翻译)




## 二、📝 爬虫需求模板（Page Object 模式）
帮我写一个脚本，模拟点击https://fanyi.qq.com/，
选择源语言和目标语言，点击语言选择框<div class="tea-dropdown__header tea-dropdown-default"><div class="tea-dropdown__value">英语</div><i class="tea-icon tea-icon-arrowdown" role="img" aria-label="arrowdown"></i></div>；
然后选择语言，各语言结构<ul class="tea-list"><li class="">英语</li><li class="">繁体中文</li><li class="">法语</li><li class="">德语</li><li class="">俄语</li><li class="">土耳其语</li><li class="">西班牙语</li><li class="">日语</li><li class="">韩语</li><li class="">越南语</li><li class="">印尼语</li><li class="">马来西亚语</li></ul>；
然后输入需要翻译的内容，输入框结构<div class="tea-textarea-group" style="width: 100%;"><textarea placeholder="输入文本内容" class="tea-textarea font-size-22 size-full-width" maxlength="2000" style="height: 99px;">今天天气很好
我喜欢
希望明天天气也好</textarea><label class="tea-textarea__label">19 / 2000</label></div>；
提取翻译内容，翻译框结构<div class="target-text-box not-show" style="height: 99px;"><div class="target-text-list">today the weather is very good</div><div class="target-text-list">I like</div><div class="target-text-list">I hope the weather will be fine tomorrow</div></div>；
然后把原文本和翻译文本按照def append_to_file(pairs):
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        for original, translated in pairs:
            f.write(f"{original}\t{translated}\n")这种格式保存  一条一行

___
