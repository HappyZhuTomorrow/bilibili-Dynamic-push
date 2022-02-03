# import imp
from importlib.resources import contents
from time import time
from unittest import result
from httpx import head
from numpy import result_type
import requests
import json
import time
class bilibili:
    def __init__(self):
        self.cookie = {
            "cookie": "填入账号的cookie"
        }
        self.head = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36"
        }


    #返回动态更新的uid
    def get_has_update(self):
        url = 'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/w_dyn_uplist?teenagers_mode=0'
        r = requests.get(url,cookies=self.cookie,headers=self.head)
        params = json.loads(r.text)

        uidList = []
        # nameList = []
        # print(params["data"])
        try:
            for i in params["data"]["items"]:
                if i['has_update'] == 1:
                    uidList.append(i['user_profile']['info']['uid'])
                # nameList.append(i['user_profile']['info']['uname'])
        except:
            pass
        return uidList


    def get_dym_one(self,uid):
        url = 'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/w_dyn_personal?host_uid={}&offset='.format(uid)

        r = requests.get(url,cookies=self.cookie,headers=self.head)
        params = json.loads(r.text)

        # print(params['data']['cards'][0])
        # print(params['data']['cards'][2])
        return params['data']['cards'][0]

    def get_dym_type(self,result):
        # 2 图片动态
        # 4 文字动态
        # 1 转发动态
        # 8 视频动态
        # result = self.get_dym_one(uid)
        # print(result['desc']['type'])
        return result['desc']['type']

    def isQuote(self,result):
        if self.get_dym_type(result) != 1:
            return 0
        else:
            params = json.loads(result['card'])
            originType = params['item']['orig_type']
            return originType

    # 处理得到的动态
    def handle_dym(self,dymType,result):
        dynamic_id = result['desc']['dynamic_id']
        if dymType == 1: #转发动态
            timestamp = result['desc']['timestamp'] #时间
            name = result['desc']['user_profile']['info']['uname'] #名字
            params = json.loads(result['card'])
            content = params['item']['content'] #动态内容
            originType = params['item']['orig_type'] #原动态类型
            origin = params['origin']
            # print(origin)
            if originType == 2: #转发的图片
                imgList = []
                origin = json.loads(origin)
                description = origin['item']['description'] #原动态文字
                for picture in origin['item']['pictures']:
                    imgList.append(picture['img_src']) #原动态图片的url
                originName = origin['user']['name']
                # print(originName)
                return timestamp,name,content,originName,description,imgList,dynamic_id

            if originType == 4:
                imgList = []
                origin = json.loads(origin)
                originName = origin['user']['uname']
                originCon = origin['item']['content'] 
                # print(f'{originName} {originCon}')
                return timestamp,name,content,originName,originCon,dynamic_id

            if originType == 8:
                origin = json.loads(origin)
                originVideoName = origin['owner']['name']
                originVideoInfo = origin['desc']
                originVideoPic = origin['pic']
                originVideoTile = origin['title']
                return timestamp,name,content,originVideoName,originVideoInfo,originVideoPic,originVideoTile,dynamic_id
                # print(originVideoName)
                # print(originVideoInfo)
                # print(originVideoPic)
                # print(originVideoTile)
                # print("origin=\n")
                # print(origin)
            
        elif dymType == 2:
            # print(result)
            timestamp = result['desc']['timestamp']
            imgDym = json.loads(result['card'])
           
            description = imgDym['item']['description']
            
            name = imgDym['user']['name']
            imgList = []
            for picture in imgDym['item']['pictures']:
                imgList.append(picture['img_src'])
            return timestamp,description,name,imgList,dynamic_id
            print(f'{description} {imgList} {name}')

        elif dymType == 4:
            # print(result['card'])
            contentDym = json.loads(result['card'])
            timestamp = contentDym['item']['timestamp']
            content = contentDym['item']['content']
            name = contentDym['user']['uname']
            return timestamp,content,name,dynamic_id
            print(f'{timestamp} {content} {name}')

        elif dymType == 8: #投稿视频
            timestamp = result['desc']['timestamp']
            card = json.loads(result['card'])
            VideoInfo = card['desc'] #视频简介
            VideoPic = card['pic']
            Videoname = card['owner']['name']
            VideoTitle = card['title']
            # print(VideoTitle)
            # print(VideoInfo)
            # print(Videoname)
            # print(VideoPic)
            # print(timestamp)
            return timestamp,VideoInfo,Videoname,VideoPic,VideoTitle,dynamic_id
            

    
    def timeChange(self,timestamp):
        timeArray = time.localtime(timestamp)
        nowTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        return nowTime

    def DymUrl(self,dynamic_id):
        return 'https://t.bilibili.com/{}'.format(dynamic_id)

    def run(self):
        while True:
            uidList = []
            uidList = self.get_has_update()
            if uidList is not None:
                for uid in uidList:
                    result = self.get_dym_one(uid)
                    dymType = self.get_dym_type(result)
                    imgList = []
                    if dymType == 1: #转发动态
                        originType = self.isQuote(result)
                        if originType == 2:
                            timestamp,name,content,originName,originContent,imgList,dynamic_id = self.handle_dym(dymType,result)
                            nowTime = self.timeChange(timestamp)
                            dymURL = self.DymUrl(dynamic_id)
                            # print(f'{nowTime} {name} {content} {originName} {originContent} {imgList} {dynamic_id}')
                            print(f'{name}转发了{originName}的动态:\n{nowTime}\n{content}\n原动态:\n{originContent}\n{imgList}\n{dymURL}')
                        elif originType == 4:
                            timestamp,name,content,originName,originContent,dynamic_id = self.handle_dym(dymType,result)
                            nowTime = self.timeChange(timestamp)
                            dymURL = self.DymUrl(dynamic_id)
                            # print(f'{nowTime} {name} {content} {originName} {originContent} {imgList} {dynamic_id}')
                            print(f'{name}转发了{originName}的动态:\n{nowTime}\n{content}\n原动态:\n{originContent}\n{imgList}\n{dymURL}')

                        elif originType == 8:
                            timestamp,name,content,originVideoName,originVideoInfo,originVideoPic,originVideoTile,dynamic_id = self.handle_dym(dymType,result)
                            nowTime = self.timeChange(timestamp)
                            dymURL = self.DymUrl(dynamic_id)
                            print(f'{name}转发了{originVideoName}的投稿:\n{nowTime}\n{content}\n原视频:\n{originVideoTile}\n{originVideoInfo}\n{originVideoPic}\n{dymURL}')
                    elif dymType == 2: #图片动态
                        timestamp,content,name,imgList,dynamic_id = self.handle_dym(dymType,result)
                        nowTime = self.timeChange(timestamp)
                        dymURL = self.DymUrl(dynamic_id)
                        # print(f'{nowTime} {content} {name} {imgList} {dynamic_id}')
                        print(f'{name}发表了动态:\n{nowTime}\n{content}\n{imgList}\n{dymURL}')
                    elif dymType == 4: #文字动态
                        timestamp,content,name,dynamic_id = self.handle_dym(dymType,result)
                        nowTime = self.timeChange(timestamp)
                        dymURL = self.DymUrl(dynamic_id)
                        # print(f'{nowTime} {content} {name} {dynamic_id}')
                        print(f'{name}发表了动态:\n{nowTime}\n{content}\n{dymURL}')
                    elif dymType == 8: #视频投稿
                        timestamp,VideoInfo,Videoname,VideoPic,VideoTitle,dynamic_id = self.handle_dym(dymType,result)
                        nowTime = self.timeChange(timestamp)
                        dymURL = self.DymUrl(dynamic_id)
                        print(f'{Videoname}投稿了新视频:\n{nowTime}\n{VideoTitle}\n{VideoInfo}\n{VideoPic}\n{dymURL}')
            # time.sleep(1)












            # uidList = []
            # nameList = []
            # uidList,nameList = self.get_has_update()
            # if uidList is not None:
            #     for uid in uidList:
            #         uid_index = uidList.index(uid)
            #         uname = nameList[uid_index] 
            #         result = self.get_dym_one(uid)
            #         params = json.loads(result['card'])
            #         content = params['item']['content']
            #         timeStamp = result['desc']['timestamp']
            #         timeArray = time.localtime(timeStamp)
            #         print(timeArray)
            #         nowTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
            #         print(f'{uname}发表了新动态:\n{nowTime}\n{content}')
            # time.sleep(1)


           
        
if __name__ == '__main__':
    bilibili().run()
    # bilibili().get_dym_one(23709126)
    # print(params)
    # bilibili().get_dym_type(bilibili().get_dym_one(23709126))
    # print(bilibili().isQuote(bilibili().get_dym_one(23709126)))
    # bilibili().handle_dym(1,bilibili().get_dym_one(23709126))
    
