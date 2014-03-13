#encoding:utf-8
'''
Created on 2013-6-28
处理图片的方法
@author: zhaoliang
'''
import Image,ImageEnhance,ImageDraw
import os,os.path
from pinyin import PinYin
import codecs
import datetime
codecs.register(lambda name: name == 'cp65001' and codecs.lookup('utf-8') or None)

stand_width=480
'''
调整图片大小，以宽度480为基准，参数为目录，如d:\\baidu
'''
def resizeImage(imagePath):
    new_path = imagePath +'_new'
    if not os.path.exists(new_path):
        os.mkdir(new_path)
    for root, dirs, files in os.walk(imagePath):
        for f in files:
            fp = os.path.join(root, f)
            img = Image.open(fp)
            (x,y) = img.size 
            x_s = stand_width 
            y_s = y * x_s / x 
            out = img.resize((x_s,y_s),Image.ANTIALIAS) 
            fp=new_path+'\\'+f
            out.save(fp)
            print(fp)

'''
清理图片，以宽度500为准，删除宽度不够500的，同时删除大小小于10k（被损坏）的图片
'''
def deleteSmall(imagePath):
    for file in os.listdir(imagePath):
        targetFile = os.path.join(imagePath,file) 
        if os.path.isfile(targetFile): 
            size=os.path.getsize(targetFile)
            if(size<10240):
                os.remove(targetFile)
                continue
            fp = open(targetFile,'rb')
            img=Image.open(fp)
            (x,y) = img.size 
            fp.close()
            if(x<stand_width):
                print(targetFile+' '+str(x)+':'+str(y))
                os.remove(targetFile)

'''
递归处理目录下的图片，根据大小比较，去掉重复
'''             
def differ(imagePath):
    starttime = datetime.datetime.now()
    fileSizeArray=[]
    for file in os.listdir(imagePath):
        targetFile = os.path.join(imagePath,file) 
        if os.path.isfile(targetFile): 
            size=os.path.getsize(targetFile)
            fileSizeArray.append([size,targetFile,file])
    #print(fileSizeArray)
    fileSizeArray.sort()
    x=0
    for x in range(0,len(fileSizeArray)-1):
        y=x+1
        if(y>len(fileSizeArray)):
            break
        while(fileSizeArray[x][0]==fileSizeArray[y][0] and y<len(fileSizeArray)):
            try:
                os.remove(fileSizeArray[y][1])
            except WindowsError as e:
                print('file is not exist'+e.args[0])
            y=y+1
            print('---------------------')
    endtime = datetime.datetime.now()
    print('get picture sizes takes '+ str((endtime-starttime).seconds) + ' seconds,' + str(len(fileSizeArray)) )  
    
                  

dir='d:\\pictures\\'
for i in os.walk(dir):
    print(i[0])
    deleteSmall(i[0])
    differ(i[0])
