#coding:utf-8
from __future__ import division 
import wx
import threading
import codecs
import urllib,urllib2,json,socket
import os.path
import time
codecs.register(lambda name: name == 'cp65001' and codecs.lookup('utf-8') or None)

class WorkerThread(threading.Thread):
    def __init__(self,window):
        threading.Thread.__init__(self)
        self.window=window
        self.select1 = self.window.choice1.GetSelection()
        self.select2 = self.window.choice2.GetSelection()
        self.select3 = self.window.choice3.GetSelections()
        self.width = self.window.tc1.Value
        self.height = self.window.tc2.Value
        self.timeout = self.window.tc3.Value
        self.page = self.window.tc4.Value
        self.savepath = self.window.tc5.Value
        
        self.retrytimes=10
        self.timeToQuit = threading.Event()
        self.timeToQuit.clear()
        
    def run(self):   
        wx.CallAfter(self.window.UpdateStatus,'开始下载'.decode('utf8'))
        self.download()
        wx.CallAfter(self.window.ThreadFinished)
    def stop(self):    
        self.timeToQuit.set()
        
    def download(self):
        if not self.select2==-1:
            if not os.path.exists(self.savepath):
                self.window.statusBar.SetStatusText('目录不存在，创建。'.decode('utf8'))
                os.mkdir(self.savepath)
                
            if self.select1==0:
                self.savepath=os.path.join(self.savepath,self.window.tag1[self.select2].decode('utf8'))
                if not os.path.exists(self.savepath):
                    self.window.statusBar.SetStatusText('目录不存在，创建。'.decode('utf8'))
                    os.mkdir(self.savepath)
                for selectIndex in self.select3:
                    newsavepath=os.path.join(self.savepath,self.window.tag2[self.select2][selectIndex].decode('utf8'))
                    if not os.path.exists(newsavepath):
                        self.window.statusBar.SetStatusText('目录不存在，创建。'.decode('utf8'))
                        os.mkdir(newsavepath)
                    self.downloadImage(newsavepath,urllib2.quote(self.window.tag1[self.select2]),urllib2.quote(self.window.tag2[self.select2][selectIndex]),urllib2.quote(''),self.page,self.timeout) 
         
            if self.select1==1:
                self.savepath=os.path.join(self.savepath,'壁纸'.decode('utf8'))
                if not os.path.exists(self.savepath):
                    self.window.statusBar.SetStatusText('目录不存在，创建。'.decode('utf8'))
                    os.mkdir(self.savepath)
                self.savepath=os.path.join(self.savepath,self.window.tag3[self.select2].decode('utf8'))
                if not os.path.exists(self.savepath):
                    self.window.statusBar.SetStatusText('目录不存在，创建。'.decode('utf8'))
                    os.mkdir(self.savepath)
                for selectIndex in self.select3:
                    newsavepath=os.path.join(self.savepath,self.window.tag4[self.select2][selectIndex].decode('utf8'))
                    if not os.path.exists(newsavepath):
                        self.window.statusBar.SetStatusText('目录不存在，创建。'.decode('utf8'))
                        os.mkdir(newsavepath)
                    self.downloadImage(newsavepath,urllib2.quote('壁纸'),urllib2.quote(self.window.tag3[self.select2]),urllib2.quote(self.window.tag4[self.select2][selectIndex]),self.page,self.timeout)    

    def downloadImage(self,directory,tag1,tag2,tag3,page,timeout):
        socket.setdefaulttimeout(int(timeout))
        i=1
        j=1
        p=30
        trytimes=0
        while i<int(page)+1:
            if self.timeToQuit.isSet():
                break
            url ='http://image.baidu.com/channel/listjson?fr=channel&tag1='+tag1+'&tag2='+tag2+'&tag3='+tag3+'&sorttype=0&pn='+str(p*i)+'&rn=30&ie=utf8&oe=utf-8'
            tag=str(urllib2.unquote(tag1)+'-'+urllib2.unquote(tag2)+'-'+urllib2.unquote(tag3)).decode('utf8')
            try:
                self.window.UpdateStatus(tag+' 加载json'.decode('utf8'))
                ipdata = urllib.urlopen(url).read()
            except IOError as ex:
                trytimes=trytimes+1
                self.window.UpdateStatus('%s 第 %s页无法获取 json。已经尝试了 %s次，最多尝试10次后放弃。'.decode('utf8') % (tag,i,trytimes) )
                if trytimes==self.retrytimes:
                    trytimes=0
                    i=i+1
                continue
            ipdata1 = json.loads(ipdata)
            if ipdata1['data']:
                for n in ipdata1['data']:
                    if self.timeToQuit.isSet():
                        break
                    if n and n['download_url']:
                        try:
                            dataimg = urllib.urlopen(n['download_url']).read()
                        except IOError as ex:
                            #if ex.message=="time out":
                            self.window.statusBar.SetStatusText('%s  第%s页  总第%s张  无法获取图片%s'.decode('utf8') % (tag,i,j,n['download_url']) )
                            continue
                        fPostfix = os.path.splitext(n['download_url'])[1]
                        if (fPostfix == '.png' or fPostfix == '.jpg' or fPostfix == '.PNG' or fPostfix == '.JPG' or fPostfix == '.GIF' or fPostfix == '.gif'):
                            filename = os.path.join(directory,os.path.basename(n['download_url']))
                        else:
                            filename=os.path.join(directory,os.path.basename(n['download_url']))+'.jpg'
                        try:
                            if not os.path.isfile(filename):
                                file_object = open(filename,'wb')
                                file_object.write(dataimg)
                                file_object.close()
                        except socket.timeout as ex:
                            #if ex.message=="timed out":
                            self.window.statusBar.SetStatusText('%s  第%s页  总第%s张 保存超时'.decode('utf8') % (tag,i,j) )
                            continue
                        #urllib.urlretrieve(n['download_url'],filename)
                        img = wx.Image(filename, wx.BITMAP_TYPE_ANY)
                        w = img.GetWidth()
                        h = img.GetHeight()
                        if w/h>1.05:
                            img2=img.Scale(420,420*h/w)
                        else:
                            img2=img.Scale(400*w/h,400)
                        try:
                            self.window.myImage.SetBitmap(wx.Image('bitmaps\\default.jpg', wx.BITMAP_TYPE_ANY).ConvertToBitmap()) 
                            self.window.myImage.SetBitmap(img2.ConvertToBitmap()) 
                            self.window.statusBar.SetStatusText('%s  第%s页  总第%s张 下载成功'.decode('utf8') % (tag,i,j) )
                        except wx.PyDeadObjectError as e:
                            self.stop()
                        j +=1
            else:
                break
            i +=1
        self.window.num += j
        
class DownloadWindow(wx.Window):
    def __init__(self, parent, ID):
        wx.Window.__init__(self, parent,ID)
        
class DownloadFrame(wx.Frame):
    def __init__(self, parent):
        self.threads = []
        wx.Frame.__init__(self, parent, -1, "百度图片下载器".decode('utf8'),style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX,size=(800,450))
        self.icon = wx.Icon('bitmaps\\download.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(self.icon)  
        self.font = wx.Font(20, wx.SWISS,wx.NORMAL,wx.NORMAL)
        self.statusBar=wx.StatusBar(self);
        self.statusBar.SetStatusText('欢迎使用百度图片下载器'.decode('utf8'))
        self.SetStatusBar(self.statusBar)
        self.starttime=time.time()
        self.Bind(wx.EVT_CLOSE,self.OnCloseWindow)
        self.num=0
        self.tag1=[] 
        self.tag2=[]
        self.tag3=[]
        self.tag4=[]
        
        #图片
        self.tag1.append('明星')
        self.tag2.append(['全部','刘亦菲','姚笛','钟汉良','刘诗诗','范冰冰','少女时代','宋茜','高圆圆','张根硕','杨幂','王力宏','张歆艺','吴奇隆','柳岩','唐嫣','金贤重','张雨绮','汤唯','周迅','孙俪','Angelababy','五月天','李准基','朴有天','韩庚','林志玲','林峰','东方神起','Hebe','钟欣桐'])
        
        self.tag1.append('美女')
        self.tag2.append(['全部','性感','写真','比基尼','白富美','宅男必备','嫩萝莉','有沟必火','高雅大气很有范','腐女','御姐','不能直视','清纯','诱惑','人体艺术','校花','丝袜美腿','模特','妹子','网络美女','长发','足球宝贝','小清新','西洋美人','气质','古典美女','非主流','车模','短发'])
        
        self.tag1.append('搞笑')
        self.tag2.append(['全部','搞笑','ps大神','熊孩子','雷人','校园也疯狂','暴走漫画','搞笑人物','重口味','标语招牌','内涵图片','搞笑动物','神感悟','搞笑漫画','创意趣图','爆笑瞬间','搞笑表情','恶搞','趣味','错觉','微段子','猎奇','搞笑明星','文字截图'])
        
        self.tag1.append('摄影')
        self.tag2.append(['全部','风景','人像','光影','lomo','静物','原创','黑白','时尚','唯美','微距','摄影师','国家地理','城市建筑','生态摄影','人文纪实','水下摄影','摄影器材','创意摄影','室内摄影'])
        
        self.tag1.append('动漫')
        self.tag2.append(['全部','海贼王','火影忍者','日本漫画','动漫人物','漫画','死神','二次元','妖精尾巴','手办','名侦探柯南','神奇宝贝','哆啦A梦','卡通形象','圣斗士','动画','cosplay','古风','原画','手绘','场景','犬夜叉','银魂','七龙珠','灌篮高手','使命召唤','仙剑5','魔兽世界','高达','生化危机'])
        
        self.tag1.append('宠物')
        self.tag2.append(['全部','喵星人','萌货','狗狗','猫叔','哈士奇','宠物鼠','萨摩耶','泰迪','博美','金毛'])
        
        self.tag1.append('设计')
        self.tag2.append(['全部','平面设计','室内设计','产品设计','建筑设计','素材','原创设计','设计效果图','经典设计','雕塑','海报','包装','插画','灵感','手绘','icon','创意设计','UI','logo','GUI','banner','web','APP','字体','网页','色彩','美术绘画','视觉','博物馆','设计素材','艺术','字体设计','排版','配色'])
        
        self.tag1.append('旅游')
        self.tag2.append(['全部','美景','印象','建筑','国外旅游','国内旅游','爱琴海','雪山','温泉','海滩','自然风光','瀑布','荷花','蓝天','日出','峡谷','马尔代夫','香港','西藏','新疆','云南','丽江','鼓浪屿','法国','马来西亚','韩国','日本','英国','德国','泰国','台湾','美国','上海','九寨沟','古镇','瑞士','西湖','普吉岛','威尼斯','三亚','乌镇','马德里','夏威夷'])
        
        self.tag1.append('汽车')
        self.tag2.append(['全部',' 名车','跑车','兰博基尼','豪车','宝马','保时捷','奥迪','摩托','老爷车','概念车','奔驰','阿斯顿.马丁','汽车周边'])
        
        self.tag1.append('家居')
        self.tag2.append(['全部','家装','装饰','阳台','书房','儿童家居','台灯','茶几','卫浴','沙发','室内','装修','家具','陶瓷','礼物','创意','家居生活','样板间','卧室','别墅','客厅','时尚家居','收纳','床品套件','床头柜','灯','创意家居'])
        
        self.tag1.append('素材')
        self.tag2.append(['全部','海报设计','广告设计','展板模板','DM宣传单','名片卡片','画册设计','其他设计','企业LOGO标志','女性人物','其他模版','国内广告设计','交通工具','菜单菜谱','中文模版','生活素材','春节','背景底纹','背景素材','房地产广告','其他模版','花纹花边','公共标识标志','人物','VI设计'])
        
        self.tag1.append('人文')
        self.tag2.append(['全部','绘画书法','传统文化','宗教信仰','国画','舞蹈音乐','油画','山水画','书法','国画山水','中国风','花鸟画','山水风景画','美术绘画'])
        
        self.tag1.append('动物')
        self.tag2.append(['全部','野生动物','昆虫','鸟类','海洋生物','鱼类','家禽家畜'])
        
        self.tag1.append('信息图')
        self.tag2.append(['全部','互联网','营销','数据','图表','电商'])
        
        #壁纸
        self.tag3.append('风景')
        self.tag4.append(['全部','自然风光','花草植物','国外风光','唯美意境','旅游风光','海底世界','冰天雪地','山水相映','海滩沙滩','璀璨星空'])
        
        self.tag3.append('美女')
        self.tag4.append(['全部','写真','美腿','欧美','性感','模特','可爱','日韩写真','清新','动漫美女','车模'])
        
        self.tag3.append('浪漫爱情')
        self.tag4.append([''])
        
        self.tag3.append('明星')
        self.tag4.append(['全部','欧美明星','少女时代','刘亦菲','东方神起','钟汉良','刘诗诗','金贤重','吴尊','张根硕','杨幂','Super Junior','张馨予','蔡依林','景甜','范冰冰','高圆圆'])
         
        self.tag3.append('小清新')
        self.tag4.append([''])
        
        self.tag3.append('名车')
        self.tag4.append(['全部','概念车','奥迪','跑车','兰博基尼','宝马','奔驰','法拉利','劳斯莱斯','迈凯轮','阿斯顿·马丁','路虎','玛莎拉蒂'])
        
        self.tag3.append('影视')
        self.tag4.append(['全部','欧美影视','港台影视','大陆影视','日韩影视'])
        
        self.tag3.append('游戏')
        self.tag4.append(['全部','魔兽世界','仙剑'])
        
        self.tag3.append('动漫')
        self.tag4.append(['全部','火影忍者','海贼王','死神','银魂'])
        
        self.tag3.append('创意')
        self.tag4.append(['全部','广告创意','精美设计','极简','三维立体'])
        
        self.tag3.append('温馨家居')
        self.tag4.append([''])

        self.tag3.append('炫丽多彩')
        self.tag4.append([''])
        
        self.tag3.append('极简')
        self.tag4.append([''])
        
        self.tag3.append('唯美意境')
        self.tag4.append([''])
        
        self.tag3.append('花草植物')
        self.tag4.append([''])
        
        self.tag3.append('写真')
        self.tag4.append([''])
        
        self.tag3.append('高清宽屏')
        self.tag4.append([''])
        
        self.tag3.append('微软壁纸')
        self.tag4.append([''])
        
        self.tag3.append('护眼壁纸')
        self.tag4.append([''])
        
        self.tag3.append('动物宠物')
        self.tag4.append([''])
        
        self.tag3.append('海底世界')
        self.tag4.append([''])
        
        self.tag3.append('苹果壁纸')
        self.tag4.append([''])
        
        self.tag3.append('璀璨星空')
        self.tag4.append([''])
        
        self.tag3.append('三维立体')
        self.tag4.append([''])
        
        self.tag3.append('正能量')
        self.tag4.append([''])
        
        self.tag3.append('卡通')
        self.tag4.append([''])
        
        self.tag3.append('手绘素描')
        self.tag4.append([''])
        
        self.tag3.append('体育')
        self.tag4.append([''])
        
        self.tag3.append('军事')
        self.tag4.append([''])
        
        self.tag3.append('可爱儿童')
        self.tag4.append([''])
        
        self.tag3.append('夏季清凉')
        self.tag4.append([''])
        self.createPanel()
        
    def createPanel(self):
        panel = wx.Panel(self)
        panel.SetBackgroundColour('white')  
        box = wx.BoxSizer(wx.HORIZONTAL)
        
        boxLeft=wx.BoxSizer(wx.VERTICAL)
        
        choice1List = ['图片'.decode('utf8'),'壁纸'.decode('utf8')]  
        self.choice1=wx.Choice(panel, -1, (150,20),choices=choice1List)  
        self.Bind(wx.EVT_CHOICE, self.Select1Changed,self.choice1)
        boxLeft.Add(self.choice1,flag=wx.EXPAND | wx.ALL,border=10)
        
        choice2List = [''] 
        self.choice2 = wx.Choice(panel, -1,  (150, 280), choices=choice2List)  
        self.Bind(wx.EVT_CHOICE, self.Select2Changed,self.choice2)
        boxLeft.Add(self.choice2,flag=wx.EXPAND | wx.ALL,border=10)
        
        img = wx.Image("bitmaps\\default.jpg", wx.BITMAP_TYPE_ANY)
        
        img2=img.Scale(420,400)
        self.myImage = wx.StaticBitmap(panel, -1,wx.BitmapFromImage(img2))
        boxLeft.Add(self.myImage,flag=wx.EXPAND | wx.ALL,border=10)
        
        box.Add(boxLeft)
        
        boxCenter=wx.BoxSizer(wx.VERTICAL)
        
        choice3List = [''] 
        self.choice3 = wx.ListBox(panel, -1, (0, 0), (120, 390), choice3List,wx.LB_MULTIPLE)  
        boxCenter.Add(self.choice3,flag=wx.EXPAND | wx.ALL,border=10)
        
        box.Add(boxCenter)
        
        boxRight=wx.BoxSizer(wx.VERTICAL)
        
        st1 = wx.StaticText(panel,label='Width:')
        boxRight.Add(st1,flag=wx.RIGHT,border=8) 
        self.tc1 = wx.TextCtrl(panel,-1,'0',size=(60,-1))
        boxRight.Add(self.tc1,proportion=1)
        
        boxRight.Add((-1,14))
        
        st2 = wx.StaticText(panel,label='Height:')
        boxRight.Add(st2,flag=wx.RIGHT,border=8) 
        self.tc2 = wx.TextCtrl(panel,-1,'0',size=(60,-1))
        boxRight.Add(self.tc2,proportion=1)
        
        boxRight.Add((-1,14))
        
        st3 = wx.StaticText(panel,label='Timeout:')
        boxRight.Add(st3,flag=wx.RIGHT,border=8) 
        self.tc3 = wx.TextCtrl(panel,-1,'15',size=(60,-1))
        boxRight.Add(self.tc3,proportion=1)
        
        boxRight.Add((-1,14))
        
        st4 = wx.StaticText(panel,label='Page:')
        boxRight.Add(st4,flag=wx.RIGHT,border=8) 
        self.tc4 = wx.TextCtrl(panel,-1,'10',size=(60,-1))
        boxRight.Add(self.tc4,proportion=1)
        
        boxRight.Add((-1,14))
        
        st5 = wx.StaticText(panel,label='Path:')
        boxRight.Add(st5,flag=wx.RIGHT,border=8) 
        self.tc5 = wx.TextCtrl(panel,-1,'d:\\pictures\\',size=(150,-1))
        self.tc5.SetInsertionPoint(-1) 
        boxRight.Add(self.tc5,proportion=1)
        
        boxRight.Add((-1,14))
        
        self.btnStart=wx.Button(panel,label='开始'.decode('utf8'))
        boxRight.Add(self.btnStart,proportion=1)
        self.Bind(wx.EVT_BUTTON, self.Start,self.btnStart)
        
        boxRight.Add((-1,12))
        
        self.btnStop=wx.Button(panel,label='停止'.decode('utf8'))
        self.btnStop.Enable(False)
        boxRight.Add(self.btnStop,proportion=1)
        self.Bind(wx.EVT_BUTTON, self.Stop,self.btnStop)
        
        box.Add(boxRight,flag=wx.LEFT|wx.RIGHT|wx.TOP,border=10)
        
        self.Bind(wx.EVT_CLOSE,  self.OnCloseWindow)
        
        panel.SetSizer(box)
            
    def Select1Changed(self,event):
        self.choice3.Clear()
        self.choice2.Clear()
        select1=self.choice1.GetSelection()
        if select1==0:
            for select in self.tag1:
                self.choice2.Append(select.decode('utf8'),None)
        if select1==1:
            for select in self.tag3:
                self.choice2.Append(select.decode('utf8'),None)
        
    def Select2Changed(self,event):
        self.choice3.Clear()
        select1=self.choice1.GetSelection()
        select2=self.choice2.GetSelection()
        if select1==0:
            for select in self.tag2[int(select2)]:
                self.choice3.Append(select.decode('utf8'),None)
        if select1==1:
            for select in self.tag4[int(select2)]:
                self.choice3.Append(select.decode('utf8'),None)
            
    def Start(self,event):
        self.num=0
        self.starttime=time.time()
        self.thread = WorkerThread(self)
        self.thread.start()
        self.btnStart.Enable(False)
        self.btnStop.Enable(True)
    
    def UpdateStatus(self,msg):
        self.statusBar.SetStatusText(msg)
        
    def ThreadFinished(self):
        self.endtime=time.time()
        self.btnStart.Enable(True)
        self.btnStop.Enable(False)
        taketime=int(self.endtime-self.starttime)
        self.statusBar.SetStatusText('欢迎使用百度图片下载器，刚才的总共花费时间 %s 秒，共下载%s张'.decode('utf8') % (str(taketime),str(self.num-1)))
            
    #点击stop    
    def Stop(self,event):
        self.thread.stop()
    #关闭窗口    
    def OnCloseWindow(self,event):
        self.Stop(event)
        self.DestroyChildren()
        event.Skip()
            
class MainApp(wx.App):
    def OnInit(self):
        self.frame = DownloadFrame(None)
        self.frame.Show(True)
        self.SetTopWindow(self.frame)
        return True        
if __name__ == '__main__':
    app = MainApp(0)
    app.MainLoop()
