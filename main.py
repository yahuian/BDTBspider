from GetTieba import Tieba
from GetTiezi import Tiezi
import csv

# 用户输入要爬的吧名即可
tieba=Tieba('北京工业大学吧') #注意不要输入'吧'字

#---------------------------------------------------------#
baseInfo=tieba.getBaseInfo()
print('吧名:',tieba.name)
print('尾页id:',baseInfo['pn'])
'''
# 将整个吧的帖子信息写入csv文件
infoDir={'回复数':'','标题':'','Tid':''}
with open(tieba.name+'吧.csv','a',newline='',encoding='utf-8-sig') as csvfile:
    w=csv.DictWriter(csvfile,fieldnames=infoDir)
    w.writeheader()
    for i in range(0,int(baseInfo['pn'])+50,50): #获取整个吧的信息
        TieInfo=tieba.getTieInfo(i) #获取每一页的贴子信息
        for e in TieInfo:
            w.writerow({
                '回复数':e['reply_num'],
                '标题':e['title'],
                'Tid':e['tid']
            })
        print('...')
        w.writerow({})
        print(i,' 成功写入文件')
'''

# 从csv文件中读取tid，爬取每个帖子的具体信息
with open(tieba.name+'.csv','r',encoding='utf-8-sig') as csvfile:
    reader = csv.reader(csvfile)
    column2 = [row[2] for row in reader]
    #csv文件的第一行是属性名Tid,所以range从第二行开始
    for i in range(406,406): # 不要一次性遍历所有的tid,可以尝试每次爬几十个帖
        if(column2[i]!=''):
            tid=column2[i]
    
        pre = Tiezi(tid,1) # 初始化一个帖子
        preInfo=pre.getBaseInfo() # 帖子基本信息

        for pn in range(1,int(preInfo['pages'])+1):
            page=Tiezi(tid,pn)
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