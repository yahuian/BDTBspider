# 所需知识
1. 首先研究贴子的HTML结构，看看你要爬的数据都在什么位置，建议使用chrome的审查元素功能。
2. requests库只用到了requests.get('url')来获取网站源码,快速入门请看[requests官方文档](http://docs.python-requests.org/zh_CN/latest/)
3. lxml.etree库只用到了etree.HTML('str')来将str格式化为HTML，进而使用xpath来查找想要的元素。快速入门请看[xpath菜鸟教程](http://www.runoob.com/xpath/xpath-tutorial.html)，建议百度多搜搜相关资料，搞清楚绝对路径和相对路径。chrome审查元素功能下，右键相应的元素，选择copy，可以拿到该元素的xpath路径。
4. python也用到了最基本的语法，有什么不会的可以边百度边写。