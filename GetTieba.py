import requests
from lxml import etree
from urllib import parse
import re

class Tieba:
    '贴吧爬虫，负责爬取该吧中的相关信息'
    def __init__(self,name):
        self.name=name
        strName=parse.quote(name) # 对吧名进行url编码
        self.url='http://tieba.baidu.com/f?kw='+strName+'&ie=utf-8'

    def getBaseInfo(self):
        '爬取该吧的基础信息'
        r=requests.get(self.url)
        html=etree.HTML(r.content.decode('UTF-8'))

        pages=html.xpath('//*[@id="frs_list_pager"]/a[11]/@href')[0] # 获取该吧总共有多少页
        pn_r='&pn=[0-9]*'
        pn_c=re.compile(pn_r)
        pn=pn_c.findall(pages)[0][4:]

        members=html.xpath('//*[@class="card_num"]/span/span[2]/text()')[0]# 获取本吧的关注者数量

        baseInfo={
            'pn':pn,
            'nums':members
        }

        return baseInfo

    def getMembersInfo(self,pn):
        '获取本吧会员信息'
        gbkUrl=parse.quote(self.name,encoding='gbk') # 对吧名进行gbk编码
        url='http://tieba.baidu.com/bawu2/platform/listMemberInfo?word='+gbkUrl+'&pn='+str(pn)
        r=requests.get(url)
        html=etree.HTML(r.content.decode('gbk'))
        users=html.xpath('//*[@id="container"]/div[3]/span') # 用户相关信息在sapn中
        
        membersInfo=[]

        for e in users:
            href=e.xpath('./a/@href')[0]
            userUrl='http://tieba.baidu.com'+href # 构建用户主页链接
            res=requests.get(userUrl)

            try:
                root=etree.HTML(res.content.decode('utf-8'))
            except UnicodeDecodeError: # 已被删除的用户
                userInfo=['用户名:删除','吧龄：','发帖：','']
                sex=2
            else:
                userInfo=root.xpath('//*[@id="userinfo_wrap"]/div[2]/div[3]/div//text()') # 用户的相关信息
                try:
                    userSex=root.xpath('//*[@id="userinfo_wrap"]/div[2]/div[3]/div/span[1]/@class')[0] # 性别
                except IndexError: # 已经被屏蔽的用户
                    userInfo=['用户名:屏蔽','吧龄：','发帖：','']
                    sex=2
                else:
                    if userSex[26:]=='male':
                        sex=1
                    if userSex[26:]=='female':
                        sex=0

            userName=userInfo[0][4:] # 用户名
            years=userInfo[1][3:]    # 吧龄
            ties=userInfo[2][3:]     # 发帖数

            temp={
                'name':userName,
                'years':years,
                'ties':ties,
                'sex':sex
            }

            membersInfo.append(temp)

        return membersInfo

    def getTieInfo(self,pn):
        '爬取每一页帖子的回复数，标题，tid'
        url=self.url+'&pn='+str(pn)
        r=requests.get(url)

        html=etree.HTML(r.content.decode('UTF-8'))
        li=html.xpath('//*[@id="thread_list"]/li') # 一个li标签就是一个帖子
        
        if pn==0:
            index=1 # 第0页有置顶帖子，从li[1]开始才是普通帖子
        else:
            index=0 # 
        
        infoList=[]

        for i in range(index,len(li)):
            reply_num=li[i].xpath('./div/div[1]')[0].xpath('string(.)') # 某贴的回复数
            title=li[i].xpath('./div/div[2]/div[1]/div[1]/a[1]/@title')[0] # 某贴的标题
            tid=li[i].xpath('./div/div[2]/div[1]/div[1]/a[1]/@href')[0][3:] # 某贴的tid

            tempDir={
                'reply_num':int(reply_num),
                'title':title,
                'tid':tid
            }
            infoList.append(tempDir)

        return infoList