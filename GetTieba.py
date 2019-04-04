import requests
from lxml import etree
from urllib import parse
import re

class Tieba:
    '贴吧爬虫，负责爬取该吧中帖子的tid'
    def __init__(self,name):
        self.name=name
        strName=parse.quote(name) # 对吧名进行url编码
        self.url='http://tieba.baidu.com/f?kw='+strName+'&ie=utf-8'

    def getBaseInfo(self):
        '爬取该吧的基础信息'
        r=requests.get(self.url)
        html=etree.HTML(r.content.decode('UTF-8'))

        pages=html.xpath('//*[@id="frs_list_pager"]/a[11]/@href')[0] #获取该吧总共有多少页
        pn_r='&pn=[0-9]*'
        pn_c=re.compile(pn_r)
        pn=pn_c.findall(pages)[0][4:]

        baseInfo={
            'pn':pn
        }

        return baseInfo
    
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