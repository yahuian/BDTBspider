import requests
from lxml import etree
import re
import csv

class Tiezi:
    '''帖子爬虫，负责爬每个贴子的数据'''

    def __init__(self,tid,pn):
        '''http://tieba.baidu.com/p/tid?pn=1 tid为帖子编号，pn为页码'''
        self.tid=tid
        self.pn=pn
    
    def getBaseInfo(self):
        '''获取该贴的基础信息'''
        url='http://tieba.baidu.com/p/'+str(self.tid)+'?pn='+str(self.pn) #构建帖子的url
        r=requests.get(url)
        html=etree.HTML(r.content.decode('UTF-8')) # 将请求得到的内容转化为xpath可处理的html格式
        title=html.xpath('//*[@id="j_core_title_wrap"]/div[2]/h1/text()')[0] # 某个贴子的标题
        responsNum=html.xpath('//*[@id="thread_theme_5"]/div[1]/ul/li[2]/span[1]/text()')[0] # 回复贴的个数
        pages=html.xpath('//*[@id="thread_theme_5"]/div[1]/ul/li[2]/span[2]/text()')[0] # 该贴的页数
        divs=html.xpath('//*[@id="j_p_postlist"]/div') # divs集合的元素是<Element div at 0x3316fa8>，每一个div都是一层楼，所有的信息都在里面
        baseInfo={
            "html":html,
            "title":title,
            "responseNum":responsNum,
            "pages":pages,
            "divs":divs
        }
        return baseInfo

    def getFloorBaseInfo(self,div):
        '''获取每层楼的基本数据'''
        userName=div.xpath('./div[2]/ul/li[@class="d_name"]/a//text()')[0] # 发帖人
        text=div.xpath('./div[3]/div[1]/cc/div[2]//text()') # 每层楼的内容
        data_field=div.xpath('./@data-field')[0] # 该楼层的相关信息都在div标签的data-field属性里面
        byte=data_field.encode('UTF-8') # 将lxml.etree._ElementUnicodeResult类型转为为bytes类型
        string=str(byte,'UTF-8') # 将 bytes类型转为string

        # 构建正则表达式
        post_id_r='"post_id":[0-9]*,'
        post_no_r='"post_no":[0-9]*'  # 楼层号
        date_r='"date":"[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}"' # 发帖时间 
        comment_num_r='"comment_num":[0-9]*,' # 回复数量，后面确定楼中楼是否翻页大有帮助

        # 编译这段正则表达式
        date_c=re.compile(date_r)
        post_no_c=re.compile(post_no_r)
        post_id_c=re.compile(post_id_r)
        comment_num_c=re.compile(comment_num_r)
        
        # 得到目标字符串，并简单截取来清洗格式
        date=date_c.findall(string)[0][8:-1]
        post_no=post_no_c.findall(string)[0][10:]
        post_id=post_id_c.findall(string)[0][10:]
        comment_num=int(comment_num_c.findall(string)[0][14:-1])

        # 计算楼中楼被分为几页，每页显示10条数据,0页表示没有回复,即没有楼中楼
        if comment_num==0:
            lzlPage=0
        elif comment_num<=10:
            lzlPage=1
        elif comment_num % 10==0:
            lzlPage=int(comment_num/10)
        else:
            lzlPage=int(comment_num/10)+1

        FloorBaseInfo={
            "userName":userName,
            "text":text,
            "date":date,
            "post_no":post_no, # 以上全部是本楼的信息

            "post_id":post_id, # 它用来构建楼中楼的url
            "lzlPage":lzlPage  # 楼中楼有几页
        }
        return FloorBaseInfo

    def getLZLInfor(self,pid,page):
        '''获取楼中楼特定页的数据'''
        # 构建楼中楼消息的url地址，并爬取数据
        lzlUrl='http://tieba.baidu.com/p/comment?tid='+str(self.tid)+'&pid='+str(pid)+'&pn='+str(page)
        r_lzl=requests.get(lzlUrl)
        root=etree.HTML(r_lzl.content.decode('UTF-8'))

        infoList=[]

        lis=root.xpath('//li') # 每一个li都代表一条评论
        for i in range(0,len(lis)-1):
            r_text=lis[i].xpath('./div[@class="lzl_cnt"]')[0].xpath('string(.)').replace(' ','') # 回复的评论信息

            r_list=r_text.split(':',1)
            user1=r_list[0]
            
            # 提取时间
            time_r='[0-9]{4}-[0-9]*-[0-9]*:[0-9]*回复'
            time_c=re.compile(time_r)
            time=time_c.findall(r_list[1])[0] # 此时的格式位'2019-3-2319:04回复'
            time1=time[0:-2] # 切除'回复'
            date=time1[0:-5]+' '+time1[-5:] # 格式化发帖时间

            r_text1=r_list[1].replace(time,'') # 该串中只有评论内容或者是user2+评论内容

            if(r_text1[0:2]=='回复'):
                s=r_text1.split(':',1)
                try:
                    user2=s[0][2:]
                    context=s[1]
                except IndexError:
                    user2=''
                    context=r_text1
            else:
                user2=''
                context=r_text1
            
            tempDir={
                'user1':user1,
                'user2':user2,
                'context':context,
                'date':date
            }
            infoList.append(tempDir)
            
        return infoList

# main函数
pre = Tiezi('5214401882',1) # 初始化一个帖子
preInfo=pre.getBaseInfo() # 帖子基本信息

for pn in range(1,int(preInfo['pages'])+1):
    page=Tiezi('5214401882',pn)
    baseInfo=page.getBaseInfo()

    '''
    print('标题：',baseInfo['title'])
    print('回复数：',baseInfo['responseNum'])
    print('页数：',baseInfo['pages'])
    #print('楼层：',baseInfo['divs'],len(baseInfo['divs']),"个")
    '''

    # 写入csv文件
    infoDir={'user1':'','user2':'','context':'','date':''}
    fileName=preInfo['title'].replace('.','')
    with open(fileName+'.csv','a',newline='',encoding='utf-8-sig') as csvfile:
        w=csv.DictWriter(csvfile,fieldnames=infoDir)
        w.writeheader()

        for e in baseInfo['divs']:
            FloorBaseInfo=page.getFloorBaseInfo(e) # 每层楼的基本信息

            #print('用户名：',FloorBaseInfo['userName'])
            #print('内容：',FloorBaseInfo['text'])
            #print('时间：',FloorBaseInfo['date'])
            #print('楼层：',FloorBaseInfo['post_no'])
            
            w.writerow({
                'user1':FloorBaseInfo['userName'],
                'user2':'',
                'context':FloorBaseInfo['text'],
                'date':FloorBaseInfo['date']
            })

            # 楼中楼
            if FloorBaseInfo['lzlPage']!=0:
                for i in range(1,FloorBaseInfo['lzlPage']+1):
                    lzlInfo=page.getLZLInfor(FloorBaseInfo['post_id'],i)
                    for j in lzlInfo:
                        w.writerow({
                            'user1':j['user1'],
                            'user2':j['user2'],
                            'context':j['context'],
                            'date':j['date']
                        })
            w.writerow({})
            print(FloorBaseInfo['post_no'],'楼成功写入文件') # 每层楼

    print(pn,'页成功写入文件') # 帖子的某页

print(fileName,'成功写入文件') # 整个帖子