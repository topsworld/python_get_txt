#coding:utf-8
import  requests
import threading
from bs4 import BeautifulSoup
import re
import os
import time
import sys
req_head={
'Cache-Control':'private',
'CF-RAY':'373fbfa292760d3d-LAX',
'Connection':'keep-alive',
'Content-Type':'text/html; charset=utf-8',
'Date':'Sat, 24 Jun 2017 12:39:13 GMT',
'Server':'yunjiasu-nginx',
'Transfer-Encoding':'chunked',
'X-AspNet-Version':'2.0.50727',
'X-Powered-By':'ASP.NET'
}

req_header={
'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
'Accept-Encoding':'gzip, deflate',
'Accept-Language':'zh-CN,zh;q=0.8',
'Cookie':'__cfduid=d577ccecf4016421b5e2375c5b446d74c1499765327; UM_distinctid=15d30fac6beb80-0bdcc291c89c17-9383666-13c680-15d30fac6bfa28; CNZZDATA1261736110=1277741675-1499763139-null%7C1499763139; tanwanhf_9821=1; Hm_lvt_5ee23c2731c7127c7ad800272fdd85ba=1499612614,1499672399,1499761334,1499765328; Hm_lpvt_5ee23c2731c7127c7ad800272fdd85ba=1499765328; tanwanpf_9817=1; bdshare_firstime=1499765328088',
'Host':'www.qu.la',
'Proxy-Connection':'keep-alive',
'Referer':'http://www.qu.la/book/1265/765108.html',
'Upgrade-Insecure-Requests':'1',
'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.104 Safari/537.36'
}

req_url_base='http://www.qu.la/book/'

class myThread (threading.Thread):   #继承父类threading.Thread
    def __init__(self, threadID, counter,start_page):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.counter = counter
        self.start_page=start_page
    def run(self):                   #把要执行的代码写到run函数里面 线程在创建后会直接运行run函数
        #print("编号为1的小说")
        get_txt(self.counter,self.start_page)
        #print("Exiting")


threadLock = threading.Lock()
threads = []


def write_txt_intro(txt,start_page):
    fo = open("txt_intro{0:0>8}_{1:0>8}.txt".format(start_page,start_page+100), "ab+")
    try:
        fo.write(("*#*#{0:0>8}".format(txt['id'])+"\r\n").encode('UTF-8'))
        fo.write(('书籍名称：'+txt['title'] + "\r\n").encode('UTF-8'))
        fo.write(('书籍编号：{0:0>8}\r\n'.format(txt['id'])).encode('UTF-8'))
        fo.write((txt['author'] + "\r\n").encode('UTF-8'))
        fo.write((txt['update'] + "\r\n").encode('UTF-8'))
        fo.write((txt['lately'] + "\r\n").encode('UTF-8'))
        fo.write(("*******简介*******\r\n").encode('UTF-8'))
        fo.write(("\t" + txt['intro'] + "\r\n").encode('UTF-8'))
        fo.write(("******************\r\n").encode('UTF-8'))
        fo.write(("#*#*\r\n").encode('UTF-8'))
    finally:
        fo.close()

#小说下载函数
#id：小说编号
#字段介绍
# tetle：小说题目
# first_page：第一章页面
# txt_section：章节地址
# section_name：章节名称
# section_text：章节正文
# section_ct：章节页数
def get_txt(txt_id,start_page):
    txt={}
    txt['title']=''
    txt['id']=str(txt_id)
    try:
        #print("请输入需要下载的小说编号：")
        #txt['id']=input()
        req_url=req_url_base+ txt['id']+'/'                        #根据小说编号获取小说URL
        #print("小说编号："+txt['id'])
        res=requests.get(req_url,params=req_header)             #获取小说目录界面
        soups=BeautifulSoup(res.text,"html.parser")           #转化
        txt['title']=soups.select('#wrapper .box_con #maininfo #info h1')[0].text          #获取小说题目
        txt['author']=soups.select('#wrapper .box_con #maininfo #info p')
        txt['update']=txt['author'][2].text                                                       #获取小说最近更新时间
        txt['lately'] = txt['author'][3].text                                                     #获取最近更新章节名称
        txt['author']=txt['author'][0].text                                                       #获取小说作者
        txt['intro']=soups.select('#wrapper .box_con #maininfo #intro')[0].text.strip()            #获取小说简介
        print("编号："+'{0:0>8}   '.format(txt['id'])+  "小说名：《"+txt['title']+"》  开始下载。")
        #print("正在寻找第一章页面。。。")
        first_page=soups.select('#wrapper .box_con #list dl dd a')                          #获取小说所有章节信息
        section_ct=len(first_page)                                                                  #获取小说总章页面数
        first_page = first_page[0]['href'].split('/')[3]                                        #获取小说第一章页面地址
        print("小说章节页数："+str(section_ct))
        #print("第一章地址寻找成功："+ first_page)
        txt_section=first_page                                                                  #设置现在下载小说章节页面
        write_txt_intro(txt,start_page)
        fo = open('{0:0>8}'.format(txt['id'])+'-'+txt['title'] + '.txt.download', "ab+")         #打开小说文件
        fo.write((txt['title']+"\r\n").encode('UTF-8'))
        fo.write((txt['author'] + "\r\n").encode('UTF-8'))
        fo.write((txt['update'] + "\r\n").encode('UTF-8'))
        fo.write((txt['lately'] + "\r\n").encode('UTF-8'))
        fo.write(("*******简介*******\r\n").encode('UTF-8'))
        fo.write(("\t"+txt['intro'] + "\r\n").encode('UTF-8'))
        fo.write(("******************\r\n").encode('UTF-8'))
        while(1):
            try:
                r=requests.get(req_url+str(txt_section),params=req_header)                      #请求当前章节页面
                soup=BeautifulSoup(r.text,"html.parser")                                        #soup转换
                section_name=soup.select('#wrapper .content_read .box_con .bookname h1')[0]                             #获取章节名称
                section_text=soup.select('#wrapper .content_read .box_con #content')[0]
                for ss in section_text.select("script"):
                    ss.decompose()
                section_text=re.sub( '\s+', '\r\n\t', section_text.text).strip('\r\n')#获取章节文本
                txt_section=soup.select('#wrapper .content_read .box_con .bottem2 #A3')[0]['href']                      #获取下一章地址
                if(txt_section=='./'):                                                          #判断是否最后一章  最后一章则跳出循环
                    print("编号："+'{0:0>8}   '.format(txt['id'])+  "小说名：《"+txt['title']+"》 下载完成")
                    break
                fo.write(('\r'+section_name.text+'\r\n').encode('UTF-8'))                                #以二进制写入章节题目
                fo.write((section_text).encode('UTF-8'))                        #以二进制写入章节内容
                #print(txt['title']+' 章节：'+section_name.text+'     已下载')
                #print(section_text.text.encode('UTF-8'))
            except:
                print("编号："+'{0:0>8}   '.format(txt['id'])+  "小说名：《"+txt['title']+"》 章节下载失败，正在重新下载。")
        fo.close()
        os.rename('{0:0>8}'.format(txt['id'])+'-'+txt['title'] + '.txt.download', '{0:0>8}'.format(txt['id'])+'-'+txt['title'] + '.txt')
    except:
        fo_err = open('dowload.log', "ab+")
        try:
            fo_err.write(('['+time.strftime('%Y-%m-%d %X', time.localtime())+"]：编号：" + '{0:0>8}   '.format(txt['id']) + "小说名：《" + txt['title'] + "》 下载失败。\r\n").encode('UTF-8'))
            print('['+time.strftime('%Y-%m-%d %X', time.localtime())+"]：编号："+'{0:0>8}   '.format(txt['id'])+  "小说名：《"+txt['title']+"》 下载失败。")
            os.rename('{0:0>8}'.format(txt['id']) + '-' + txt['title'] + '.txt.download',
                  '{0:0>8}'.format(txt['id']) + '-' + txt['title'] + '.txt.error')
        except:
            fo_err.write(('['+time.strftime('%Y-%m-%d %X', time.localtime())+"]：编号："+'{0:0>8}   '.format(txt['id'])+"下载失败。\r\n").encode('UTF-8'))
            print('['+time.strftime('%Y-%m-%d %X', time.localtime())+"]：编号："+'{0:0>8}   '.format(txt['id'])+"下载失败。")
        finally:
            fo_err.close()

#批量获取txt  900-1000
def get_txts(start_page):
    print("当前起始页面："+str(start_page))
    print("正在创建下载任务。")
    for i in range(start_page, start_page+100):
        thread_one = myThread(i, str(i),start_page)
        thread_one.start()
        threads.append(thread_one)
    print("下载任务创建完成。")
    print("等待下载任务完成。。。")
    task_ct = len(threads)
    print('********************')
    i_ls_ct = 0
    while (1):
        run_task = 0
        for i in threads:
            if (i.isAlive()):
                run_task += 1
        # os.system('cls')
        # write('\b'+"总任务数：" + str(task_ct) + "  已完成任务数：" + str(task_ct - run_task)+"\r")
        if (i_ls_ct % 10 >= 4):
            print('{0:0>8}-{1:0>8} '.format(start_page,start_page+100)+"下载中："
                  + "*" * (int)((task_ct - run_task) / task_ct * 50) + "_" * (int)(
                run_task / task_ct * 50) + " /. 总数：" + str(task_ct) + "  已完成：" + str(task_ct - run_task), end="\r")
        else:
            print('{0:0>8}-{1:0>8} '.format(start_page,start_page+100)+"下载中："
                  + "*" * (int)((task_ct - run_task) / task_ct * 50) + "_" * (int)(
                run_task / task_ct * 50) + " \. 总数：" + str(task_ct) + "  已完成：" + str(
                task_ct - run_task), end="\r")
        if (run_task == 0):
            break
        time.sleep(.1)
        if (i_ls_ct > 100000):
            i_ls_ct = 0
        else:
            i_ls_ct += 1
            # print(i_ls_ct)
    print("所有下载任务已完成")
    time.sleep(2)
    os.system('cls' if os.name == 'nt' else "printf '\033c'")

#get_txt(764066)
if __name__=='__main__':
    #print("请输入需要下载的小说编号：")
    #txt_id = input()
    #get_txt(30176)
    # 创建新线程
    for i_ls in range(9,50):
        get_txts(i_ls*100)

#cd get_txt
#python get_txt.py