#coding=utf-8
#!/usr/bin/python
import sys
sys.path.append('..') 
from base.spider import Spider
import json
import time
import base64


def second_to_time(a):
    #将秒数转化为 时分秒的格式
    if a < 3600:
        return time.strftime("%M:%S", time.gmtime(a))
    else:
        return time.strftime("%H:%M:%S", time.gmtime(a))

class Spider(Spider):  # 元类 默认的元类 type
    def getName(self):
        return "哔哩哔哩"
    def init(self,extend=""):
        print("============{0}============".format(extend))
        pass
    def isVideoFormat(self,url):
        pass
    def manualVideoCheck(self):
        pass
    def homeContent(self,filter):
        result = {}
        cateManual = {
            "动态":"动态",
            '历史记录':'历史记录',
            "热门":"热门",
            "排行榜":"排行榜",
            "zane妈":"zane妈",
            "相声小品": "相声小品",
            "林芊妤":"林芊妤",
            "Zard": "Zard",
            "玩具汽车": "玩具汽车",
            "儿童": "儿童",
            "幼儿": "幼儿",
            "儿童玩具": "儿童玩具",
            "昆虫": "昆虫",
            "动物世界": "动物世界",
            "纪录片": "纪录片",
            "搞笑": "搞笑",
            "假窗-白噪音": "窗+白噪音",
            "演唱会": "演唱会"
        }
        classes = []
        for k in cateManual:
            classes.append({
                'type_name':k,
                'type_id':cateManual[k]
            })
        result['class'] = classes
        if(filter):
            result['filters'] = self.config['filter']
        return result
    def homeVideoContent(self):
        result = {
            'list':[]
        }
        return result
    cookies = ''
    def getCookie(self):
        import requests
        import http.cookies
        #请在此输入 cookies
        raw_cookie_line = "buvid3=4EACEA62-1738-2499-7BD4-E14A8CF3062E54093infoc; b_nut=1667861954; i-wanna-go-back=-1; _uuid=10CBF8E88-88DF-2CA7-553B-1B9A285A3102158757infoc; buvid4=D8D5168E-DBA5-DBB3-D4EA-177D3940058059522-122110806-wmrIoPMDWijsLAkYRQhX/w%3D%3D; buvid_fp_plain=undefined; DedeUserID=429617357; DedeUserID__ckMd5=58f591cbe4b64558; rpdid=|()kYJ~m)Ru0J'uYY~)Yk|Yu; theme_style=light; nostalgia_conf=-1; b_lsid=4F946927_18457361FF1; b_ut=5; fingerprint=be3fab1635c4bfbf3cd92cc5a78721a8; SESSDATA=2a58ae02%2C1683463077%2C849da%2Ab2; bili_jct=ac2e50764bf43e4a5eadef19dcda2905; buvid_fp=2467d99d8522264426fa300d333a8f1e; sid=79wlt089; innersign=1; CURRENT_FNVAL=4048; CURRENT_QUALITY=112"
        simple_cookie = http.cookies.SimpleCookie(raw_cookie_line)
        cookie_jar = requests.cookies.RequestsCookieJar()
        cookie_jar.update(simple_cookie)
        return cookie_jar
    def get_dynamic(self,pg):
        result = {}
        if int(pg) > 1:
            return result
        offset = ''
        videos = []
        for i in range(0,10):
            url= 'https://api.bilibili.com/x/polymer/web-dynamic/v1/feed/all?timezone_offset=-480&type=all&page={0}&offset={1}'.format(pg,offset)
            rsp = self.fetch(url,cookies=self.getCookie())
            content = rsp.text
            jo = json.loads(content)
            if jo['code'] == 0:
                offset = jo['data']['offset']
                vodList = jo['data']['items']
                for vod in vodList:
                    if vod['type'] == 'DYNAMIC_TYPE_AV':
                        ivod = vod['modules']['module_dynamic']['major']['archive']
                        aid = str(ivod['aid']).strip()
                        title = ivod['title'].strip().replace("<em class=\"keyword\">","").replace("</em>","")
                        img =  ivod['cover'].strip()
                        remark = str(ivod['duration_text']).strip()
                        videos.append({
                            "vod_id":aid,
                            "vod_name":title,
                            "vod_pic":img,
                            "vod_remarks":remark
                        })
        result['list'] = videos
        result['page'] = pg
        result['pagecount'] = 9999
        result['limit'] = 90
        result['total'] = 999999
        return result

    def get_history(self,pg):
            result = {}
            url = 'http://api.bilibili.com/x/v2/history?pn=%s' % pg
            rsp = self.fetch(url,cookies=self.getCookie())
            content = rsp.text
            jo = json.loads(content)   #解析api接口,转化成json数据对象
            if jo['code'] == 0:

                videos = []
                vodList = jo['data']

                for vod in vodList:

                    if vod['duration'] > 0:   #筛选掉非视频的历史记录
                        aid = str(vod["aid"]).strip()   #获取 aid

                        #获取标题
                        title = vod["title"].replace("<em class=\"keyword\">", "").replace("</em>", "").replace("&quot;",
                                                                                                                '"')
                        #封面图片
                        img = vod["pic"].strip()

                        #获取已观看时间
                        if str(vod['progress'])=='-1':
                            process=str(second_to_time(vod['duration'])).strip()
                        else:
                            process = str(second_to_time(vod['progress'])).strip()
                        #获取视频总时长
                        total_time= str(second_to_time(vod['duration'])).strip()

                        #组合 已观看时间 / 总时长 ,赋值给 remark
                        remark = process+' / '+total_time


                        videos.append({
                            "vod_id": aid,
                            "vod_name": title,
                            "vod_pic": img,
                            "vod_remarks": remark

                        })
                result['list'] = videos
                result['page'] = pg
                result['pagecount'] = 9999
                result['limit'] = 90
                result['total'] = 999999
            return result

    def get_hot(self,pg):
        result = {}
        url= 'https://api.bilibili.com/x/web-interface/popular?ps=20&pn={0}'.format(pg)
        rsp = self.fetch(url,cookies=self.getCookie())
        content = rsp.text
        jo = json.loads(content)
        if jo['code'] == 0:
            videos = []
            vodList = jo['data']['list']
            for vod in vodList:
                aid = str(vod['aid']).strip()
                title = vod['title'].strip().replace("<em class=\"keyword\">","").replace("</em>","")
                img =  vod['pic'].strip()
                remark = str(vod['duration']).strip()
                videos.append({
                    "vod_id":aid,
                    "vod_name":title,
                    "vod_pic":img,
                    "vod_remarks":remark
                })
            result['list'] = videos
            result['page'] = pg
            result['pagecount'] = 9999
            result['limit'] = 90
            result['total'] = 999999
        return result
    def get_rank(self):
        result = {}
        url= 'https://api.bilibili.com/x/web-interface/ranking/v2?rid=0&type=all'
        rsp = self.fetch(url,cookies=self.getCookie())
        content = rsp.text
        jo = json.loads(content)
        if jo['code'] == 0:
            videos = []
            vodList = jo['data']['list']
            for vod in vodList:
                aid = str(vod['aid']).strip()
                title = vod['title'].strip().replace("<em class=\"keyword\">","").replace("</em>","")
                img =  vod['pic'].strip()
                remark = str(vod['duration']).strip()
                videos.append({
                    "vod_id":aid,
                    "vod_name":title,
                    "vod_pic":img,
                    "vod_remarks":remark
                })
            result['list'] = videos
            result['page'] = 1
            result['pagecount'] = 1
            result['limit'] = 90
            result['total'] = 999999
        return result
    def categoryContent(self,tid,pg,filter,extend):	
        result = {}
        if tid == "热门":
            return self.get_hot(pg=pg)
        if tid == "排行榜" :
            return self.get_rank()
        if tid == '动态':
            return self.get_dynamic(pg=pg)
        if tid == '历史记录':
            return self.get_history(pg=pg)
        url = 'https://api.bilibili.com/x/web-interface/search/type?search_type=video&keyword={0}&page={1}'.format(tid,pg)
        if len(self.cookies) <= 0:
            self.getCookie()
        rsp = self.fetch(url,cookies=self.getCookie())
        content = rsp.text
        jo = json.loads(content)
        if jo['code'] != 0:			
            rspRetry = self.fetch(url,cookies=self.getCookie())
            content = rspRetry.text		
        jo = json.loads(content)
        videos = []
        vodList = jo['data']['result']
        for vod in vodList:
            aid = str(vod['aid']).strip()
            title = tid + ":" + vod['title'].strip().replace("<em class=\"keyword\">","").replace("</em>","")
            img = 'https:' + vod['pic'].strip()
            remark = str(vod['duration']).strip()
            videos.append({
                "vod_id":aid,
                "vod_name":title,
                "vod_pic":img,
                "vod_remarks":remark
            })
        result['list'] = videos
        result['page'] = pg
        result['pagecount'] = 9999
        result['limit'] = 90
        result['total'] = 999999
        return result
    def cleanSpace(self,str):
        return str.replace('\n','').replace('\t','').replace('\r','').replace(' ','')
    def detailContent(self,array):
        aid = array[0]
        url = "https://api.bilibili.com/x/web-interface/view?aid={0}".format(aid)

        rsp = self.fetch(url,headers=self.header,cookies=self.getCookie())
        jRoot = json.loads(rsp.text)
        jo = jRoot['data']
        title = jo['title'].replace("<em class=\"keyword\">","").replace("</em>","")
        pic = jo['pic']
        desc = jo['desc']
        typeName = jo['tname']
        vod = {
            "vod_id":aid,
            "vod_name":title,
            "vod_pic":pic,
            "type_name":typeName,
            "vod_year":"",
            "vod_area":"bilidanmu",
            "vod_remarks":"",
            "vod_actor":jo['owner']['name'],
            "vod_director":jo['owner']['name'],
            "vod_content":desc
        }
        ja = jo['pages']
        playUrl = ''
        for tmpJo in ja:
            cid = tmpJo['cid']
            part = tmpJo['part']
            playUrl = playUrl + '{0}${1}_{2}#'.format(part,aid,cid)

        vod['vod_play_from'] = 'B站'
        vod['vod_play_url'] = playUrl

        result = {
            'list':[
                vod
            ]
        }
        return result
    def searchContent(self,key,quick):
        search = self.categoryContent(tid=key,pg=1,filter=None,extend=None)
        result = {
            'list':search['list']
        }
        return result
    def playerContent(self,flag,id,vipFlags):
        # https://www.555dianying.cc/vodplay/static/js/playerconfig.js
        result = {}

        ids = id.split("_")
        url = 'https://api.bilibili.com:443/x/player/playurl?avid={0}&cid=%20%20{1}&qn=112'.format(ids[0],ids[1])
        rsp = self.fetch(url,cookies=self.getCookie())
        jRoot = json.loads(rsp.text)
        jo = jRoot['data']
        ja = jo['durl']
        
        maxSize = -1
        position = -1
        for i in range(len(ja)):
            tmpJo = ja[i]
            if maxSize < int(tmpJo['size']):
                maxSize = int(tmpJo['size'])
                position = i

        url = ''
        if len(ja) > 0:
            if position == -1:
                position = 0
            url = ja[position]['url']

        result["parse"] = 0
        result["playUrl"] = ''
        result["url"] = url
        result["header"] = {
            "Referer":"https://www.bilibili.com",
            "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"
        }
        result["contentType"] = 'video/x-flv'
        return result

    config = {
        "player": {},
        "filter": {}
    }
    header = {}

    def localProxy(self,param):
        return [200, "video/MP2T", action, ""]
