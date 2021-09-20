from nonebot import *
import json
from random import randint
import requests,random,os,json,re
from hoshino import Service,R,priv,util
from hoshino.typing import MessageSegment,CQEvent, HoshinoBot
from hoshino.util import FreqLimiter,pic2b64
from urllib.request import urlopen
from urllib.parse import urlencode
import hoshino
import asyncio
import time
import urllib
import string
import random
import hashlib
import math
import requests
import os
from  PIL  import   Image,ImageFont,ImageDraw
from io import BytesIO
import io
import base64
from PIL import Image

# Github-@lulu666lulu https://github.com/Azure99/GenshinPlayerQuery/issues/20
# '''
# {body:"",query:{"action_ticket": undefined, "game_biz": "hk4e_cn”}}
# 对应 https://api-takumi.mihoyo.com/binding/api/getUserGameRolesByCookie?game_biz=hk4e_cn //查询米哈游账号下绑定的游戏(game_biz可留空)
# {body:"",query:{"uid": 12345(被查询账号米哈游uid)}}
# 对应 https://api-takumi.mihoyo.com/game_record/app/card/wapi/getGameRecordCard?uid=
# {body:"",query:{'role_id': '查询账号的uid(游戏里的)' ,'server': '游戏服务器'}}
# 对应 https://api-takumi.mihoyo.com/game_record/app/genshin/api/index?server= server信息 &role_id= 游戏uid
# {body:"",query:{'role_id': '查询账号的uid(游戏里的)' , 'schedule_type': 1(我这边只看到出现过1和2), 'server': 'cn_gf01'}}
# 对应 https://api-takumi.mihoyo.com/game_record/app/genshin/api/spiralAbyss?schedule_type=1&server= server信息 &role_id= 游戏uid
# {body:"",query:{game_id: 2(目前我知道有崩坏3是1原神是2)}}
# 对应 https://api-takumi.mihoyo.com/game_record/app/card/wapi/getAnnouncement?game_id=    这个是公告api
# b=body q=query
# 其中b只在post的时候有内容，q只在get的时候有内容
# '''

#源码来源于https://github.com/Womsxd/YuanShen_User_Info
sv = Service('ysInfo', visible=True, manage_priv=priv.ADMIN, enable_on_default=True)
bot = get_bot()

mhyVersion = "2.11.1"
salt = "xV8v4Qu54lUKrEYFZkJhB8cuOh9Asafs" # Github-@lulu666lulu
client_type = "5"
cache_Cookie = "_guid=227471054.4257066864067721000.1628484833057.5515; UM_distinctid=17b29428fe228d-0d6360bb6f1442-45410429-1fa400-17b29428fe3231; _ga=GA1.2.339487481.1628484836; _MHYUUID=507874ae-f95c-4c23-810e-60f599a8cc59; CNZZDATA1275023096=1275660519-1628482653-%7C1630894650; _gid=GA1.2.735750044.1630897505; ltoken=UAGB86gbitmCEqJkNTZZoFZebAOjQ3hrhtLOP54T; ltuid=5755149; cookie_token=NnxS3r5YpFkuXSLI7oMy3GuhNcgALlIMeWrm5HnI; account_id=5755149; monitor_count=7" #自行获取

FILE_PATH = os.path.dirname(__file__)
FONTS_PATH = os.path.join(FILE_PATH,'fonts')
FONTS_PATH = os.path.join(FONTS_PATH,'sakura.ttf')

def get_duanluo(text):
    txt = Image.new('RGBA', (600, 800), (255, 255, 255, 0))
    draw = ImageDraw.Draw(txt)
    # 所有文字的段落
    duanluo = ""
    max_width = 600
    # 宽度总和
    sum_width = 0
    # 几行
    line_count = 1
    # 行高
    line_height = 0
    for char in text:
        width, height = draw.textsize(char, font)
        sum_width += width
        if sum_width > max_width: # 超过预设宽度就修改段落 以及当前行数
            line_count += 1
            sum_width = 0
            duanluo += '\n'
        duanluo += char
        line_height = max(height, line_height)
    if not duanluo.endswith('\n'):
        duanluo += '\n'
    return duanluo, line_height, line_count

def split_text(content):
    # 按规定宽度分组
    max_line_height, total_lines = 0, 0
    allText = []
    for text in content.split('\n'):
        duanluo, line_height, line_count = get_duanluo(text)
        max_line_height = max(line_height, max_line_height)
        total_lines += line_count
        allText.append((duanluo, line_count))
    line_height = max_line_height
    total_height = total_lines * line_height
    drow_height = total_lines * line_height
    return allText, total_height, line_height, drow_height

def __md5__(text):
    _md5 = hashlib.md5()
    _md5.update(text.encode())
    return _md5.hexdigest()

def __get_ds__(query, body=None):
    if body:
        body = json.dumps(body)
    n = salt
    i = str(int(time.time()))
    r = str(random.randint(100000, 200000))
    q = '&'.join([f'{k}={v}' for k, v in query.items()])
    c = __md5__("salt=" + n + "&t=" + i + "&r=" + r + '&b=' + (body or '') + '&q=' + q)
    return i + "," + r + "," + c

def request_data(uid = 0, api='index', character_ids=None):
    server = 'cn_gf01'
    if uid[0] == "5":
        server = 'cn_qd01'

    headers = {
        'Accept': 'application/json, text/plain, */*',
        "User-Agent":"Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) miHoYoBBS/2.11.1",
        "Referer": "https://webstatic.mihoyo.com/",
        "x-rpc-app_version": mhyVersion,
        "x-rpc-client_type": client_type,
        "DS": "",
        'Cookie': cache_Cookie
    }

    params = {"role_id": uid, "server": server}

    json_data = None
    fn = requests.get
    base_url = 'https://api-takumi.mihoyo.com/game_record/app/genshin/api/%s'
    url = base_url % api + '?'
    if api == 'index':
        url += urlencode(params)
    elif api == 'spiralAbyss':
        params['schedule_type'] = '1'
        url += urlencode(params)
    elif api == 'character':
        url = 'https://api-takumi.mihoyo.com/game_record/app/genshin/api/character'
        fn = requests.post
        json_data = {"character_ids": character_ids,"role_id": uid, "server": server}
        print(json_data)
        params = {}

    headers['DS'] = __get_ds__(params, json_data)
    res = fn(url=url, headers=headers, json=json_data)
    return res.text



def GetInfo(Uid, ServerID):
    req = requests.get(
        url="https://api-takumi.mihoyo.com/game_record/app/genshin/api/index?server=" + ServerID + "&role_id=" + Uid,
        headers={
            'Accept': 'application/json, text/plain, */*',
            'DS': DSGet("role_id=" + Uid + "&server=" + ServerID),
            'Origin': 'https://webstatic.mihoyo.com',
            'x-rpc-app_version': mhyVersion,
            'User-Agent': 'Mozilla/5.0 (Linux; Android 9; Unspecified Device) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/39.0.0.0 Mobile Safari/537.36 miHoYoBBS/2.2.0',
            'x-rpc-client_type': client_type,
            'Referer': 'https://webstatic.mihoyo.com/app/community-game-records/index.html?v=6',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,en-US;q=0.8',
            'X-Requested-With': 'com.mihoyo.hyperion',
            "Cookie": cache_Cookie
        }
    )
    return req.text

def GetBaseInfo(MysId, ServerID):
    req = requests.get(
        url="https://api-takumi.mihoyo.com/game_record/card/wapi/getGameRecordCard?&uid=" + MysId,
        headers={
            'Accept': 'application/json, text/plain, */*',
            'DS': DSGet("role_id=" + Uid + "&server=" + ServerID),
            'Origin': 'https://webstatic.mihoyo.com',
            'x-rpc-app_version': mhyVersion,
            'User-Agent': 'Mozilla/5.0 (Linux; Android 9; Unspecified Device) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/39.0.0.0 Mobile Safari/537.36 miHoYoBBS/2.2.0',
            'x-rpc-client_type': client_type,
            'Referer': 'https://webstatic.mihoyo.com/app/community-game-records/index.html?v=6',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,en-US;q=0.8',
            'X-Requested-With': 'com.mihoyo.hyperion',
            "Cookie": cache_Cookie
        }
    )
    return req.text
    
def GetCharacter(Uid, ServerID, Character_ids):
    try:
        req = requests.post(
            url = "https://api-takumi.mihoyo.com/game_record/app/genshin/api/character",
            headers = {
                'Accept': 'application/json, text/plain, */*',
                'DS': DSGet("role_id=" + Uid + "&server=" + ServerID),
                'Origin': 'https://webstatic.mihoyo.com',
                "Cookie": cache_Cookie,#自己获取
                'x-rpc-app_version': mhyVersion,
                'User-Agent': 'Mozilla/5.0 (Linux; Android 9; Unspecified Device) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/39.0.0.0 Mobile Safari/537.36 miHoYoBBS/2.2.0',
                'x-rpc-client_type': client_type,
                'Referer': 'https://webstatic.mihoyo.com/app/community-game-records/index.html?v=6',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'zh-CN,en-US;q=0.8',
                'X-Requested-With': 'com.mihoyo.hyperion'
            },
            json = {"character_ids": Character_ids ,"role_id": Uid ,"server": ServerID }
        )
        return (req.text)
    except:
        print ("访问失败，请重试！")
        #sys.exit (1)
        return

def GetSpiralAbys(Uid, ServerID, Schedule_type):
    try:
        req = requests.get(
            url = "https://api-takumi.mihoyo.com/game_record/app/genshin/api/spiralAbyss?schedule_type=" + Schedule_type + "&server="+ ServerID +"&role_id=" + Uid,
            headers = {
                'Accept': 'application/json, text/plain, */*',
                'DS': DSGet("role_id=" + Uid + "&server=" + ServerID),
                'Origin': 'https://webstatic.mihoyo.com',
                "Cookie": cache_Cookie,#自己获取
                'x-rpc-app_version': mhyVersion,
                'User-Agent': 'Mozilla/5.0 (Linux; Android 9; Unspecified Device) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/39.0.0.0 Mobile Safari/537.36 miHoYoBBS/2.2.0',
                'x-rpc-client_type': client_type,
                'Referer': 'https://webstatic.mihoyo.com/app/community-game-records/index.html?v=6',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'zh-CN,en-US;q=0.8',
                'X-Requested-With': 'com.mihoyo.hyperion'
            }
        )
        return (req.text)
    except:
        print ("访问失败，请重试！")
        #sys.exit (1)
        return    

def calcStringLength(text):
    # 令len(str(string).encode()) = m, len(str(string)) = n
    # 字符串所占位置长度 = (m + n) / 2
    # 但由于'·'属于一个符号而非中文字符所以需要把长度 - 1
    if re.search('·', text) is not None:
        stringlength = int(((str(text).encode()) + len(str(text)) - 1) / 2)
    elif re.search(r'[“”]', text) is not None:
        stringlength = int((len(str(text).encode()) + len(str(text))) / 2) - 2
    else:
        stringlength = int((len(str(text).encode()) + len(text)) / 2)

    return stringlength


def spaceWrap(text, flex=10):
    stringlength = calcStringLength(text)

    return '%s' % (str(text)) + '%s' % (' ' * int((int(flex) - stringlength)))


def elementDict(text, isOculus=False):
    elementProperty = str(re.sub(r'culus_number$', '', text)).lower()
    elementMastery = {
        "anemo": "风",
        "pyro": "火",
        "geo": "岩",
        "electro": "雷",
        "cryo": "冰",
        "hydro": "水",
        "dendro": "草",  # https://genshin-impact.fandom.com/wiki/Dendro
        "none": "无",
    }
    try:
        elementProperty = str(elementMastery[elementProperty])
    except KeyError:
        elementProperty = "草"
    if isOculus:
        return elementProperty + "神瞳"
    elif not isOculus:
        return elementProperty + "属性"




def JsonAnalysis(JsonText,Uid, ServerID, level, nickname):
    data = json.loads(JsonText)
    if data["retcode"] != 0:
        if data["retcode"] == 10001:
            os.remove("cookie.txt")
            return "Cookie错误/过期，请重置Cookie"
        return (
                "Api报错，返回内容为：\r\n"
                + JsonText + "\r\n出现这种情况可能是UID输入错误 or 不存在"
        )
    else:
        pass
    msg_list = []
    Character_Info = f'UID{Uid} 的信息为：\n'
    Character_Info += "人物：\n"
    msg_list.append(Character_Info)
    name_length = []
    Character_List = data["data"]["avatars"]
    Character_ids = []
    for i in Character_List:
        
        Character_ids +=  [i["id"]]
        name_length.append(calcStringLength(i["name"]))
    dataC = json.loads(request_data(uid=Uid, api='character', character_ids=Character_ids))
    Character_datas = dataC["data"]["avatars"]
    namelength_max = int(max(name_length))
    
    #获取角色数量，计算输出图片长度
    characternum = data["data"]["stats"]["avatar_number"]
    need_middle = math.ceil(characternum/6)
    middle_height = need_middle*390
    img_height = middle_height+1024
    #命之座及好感度
    PLAYER = os.path.join(FILE_PATH,'player_info')
    FETTER = os.path.join(FILE_PATH,'fetter')
    #背景图片初始化
    IMG_PATH = os.path.join(FILE_PATH,'images')
    im = Image.new("RGB", (1454, img_height), (255, 255, 255))
    #头部背景图片插入
    base_img1 = os.path.join(IMG_PATH,'ysinfo_top.png')
    dtimg1 = Image.open(base_img1)
    dtbox1 = (0, 0)
    im.paste(dtimg1, dtbox1)
    #插入标题图片
    base_img2 = os.path.join(IMG_PATH,'ysinfo_center.png')
    dtimg2 = Image.open(base_img2)
    dtbox2 = (0, 837)
    im.paste(dtimg2, dtbox2)
    #插入角色部分背景
    base_img = os.path.join(IMG_PATH,'ysinfo_back.png')
    dtimg = Image.open(base_img)
    for num in range(need_middle):
        dtheight = 937 + int(num) * 390
        dtbox = (0, dtheight)
        im.paste(dtimg, dtbox)
    #插入底部背景
    base_img3 = os.path.join(IMG_PATH,'ysinfo_bottom.png')
    dtimg3 = Image.open(base_img3)
    dtbox3 = (0, img_height-100)
    im.paste(dtimg3, dtbox3)
    
    #插入尘歌壶3个洞天
    #翠黛峰
    base_img_c = os.path.join(IMG_PATH,'翠黛峰.png')
    dtimg_c = Image.open(base_img_c).convert('RGBA')
    dtimg_c = dtimg_c.resize((188, 188))
    dtbox_c = (1140, 116)
    im.paste(dtimg_c, dtbox_c, mask=dtimg_c.split()[3])
    #罗浮洞
    base_img_l = os.path.join(IMG_PATH,'罗浮洞.png')
    dtimg_l = Image.open(base_img_l).convert('RGBA')
    dtimg_l = dtimg_l.resize((188, 188))
    dtbox_l = (1140, 319)
    im.paste(dtimg_l, dtbox_l, mask=dtimg_l.split()[3])
    #清琼岛
    base_img_q = os.path.join(IMG_PATH,'清琼岛.png')
    dtimg_q = Image.open(base_img_q).convert('RGBA')
    dtimg_q = dtimg_q.resize((188, 188))
    dtbox_q = (1140, 522)
    im.paste(dtimg_q, dtbox_q, mask=dtimg_q.split()[3])
    
    #插入查询者信息
    #插入昵称、uid、随机角色头像
    #随机获取有的角色的一个头像,插入背景
    picid = random.sample(Character_ids,1)
    picname = str(picid[0])+'.png'
    base_img_t = os.path.join(IMG_PATH,picname)
    dtimg_t = Image.open(base_img_t).convert('RGBA')
    dtimg_t = dtimg_t.resize((213, 213))
    dtbox_t = (70, 53)
    im.paste(dtimg_t, dtbox_t, mask=dtimg_t.split()[3])
    
    draw = ImageDraw.Draw(im)
    #插入UID
    line = "UID:"+str(Uid)
    font = ImageFont.truetype(FONTS_PATH, 22)
    w, h = draw.textsize(line, font=font)
    draw.text(((753 - w) / 2, 113), line, font=font, fill = (0, 158, 61))
    #插入昵称
    font = ImageFont.truetype(FONTS_PATH, 34)
    w, h = draw.textsize(nickname, font=font)
    draw.text(((753 - w) / 2, 143), nickname, font=font, fill = (0, 0, 0))
    
    #插入等级
    if level>0:
        if level < 20:
            wordlevel = 0
        else:
            wordlevel = math.floor( ( level - 15 ) / 5 )
    else:
        level = '/'
        wordlevel = '/'
    line = str(level)+"级"
    font = ImageFont.truetype(FONTS_PATH, 42)
    w, h = draw.textsize(line, font=font)
    draw.text(((1774 - w) / 2, 122), line, font=font, fill = (255, 255, 255))
    
    #插入世界等级
    line = "世界等级"+str(wordlevel)
    font = ImageFont.truetype(FONTS_PATH, 22)
    w, h = draw.textsize(line, font=font)
    draw.text(((1774 - w) / 2, 170), line, font=font, fill = (255, 255, 255))
    
    font = ImageFont.truetype(FONTS_PATH, 32)
    #活跃天数　　
    line = str(data["data"]["stats"]["active_day_number"])
    draw.text((305, 296), line, font=font, fill = (255, 255, 255))
    #成就
    line = str(data["data"]["stats"]["achievement_number"])
    draw.text((305, 344), line, font=font, fill = (255, 255, 255))
    #角色数量
    line = str(data["data"]["stats"]["avatar_number"])
    draw.text((305, 392), line, font=font, fill = (255, 255, 255))
    #深渊
    if data["data"]["stats"]["spiral_abyss"] != "-":
        line=data["data"]["stats"]["spiral_abyss"]
    else:
        line="没打"
    draw.text((305, 440), line, font=font, fill = (255, 255, 255))
    
    #普通宝箱　　
    line = str(data["data"]["stats"]["common_chest_number"])
    draw.text((620, 296), line, font=font, fill = (255, 255, 255))
    #精致
    line = str(data["data"]["stats"]["exquisite_chest_number"])
    draw.text((620, 344), line, font=font, fill = (255, 255, 255))
    #珍贵
    line = str(data["data"]["stats"]["precious_chest_number"])
    draw.text((620, 392), line, font=font, fill = (255, 255, 255))
    #华丽
    line = str(data["data"]["stats"]["luxurious_chest_number"])
    draw.text((620, 440), line, font=font, fill = (255, 255, 255))
    
    #风神曈　　
    line = str(data["data"]["stats"]["anemoculus_number"])
    draw.text((925, 296), line, font=font, fill = (255, 255, 255))
    #岩
    line = str(data["data"]["stats"]["geoculus_number"])
    draw.text((925, 344), line, font=font, fill = (255, 255, 255))
    #雷
    line = str(data["data"]["stats"]["electroculus_number"])
    draw.text((925, 392), line, font=font, fill = (255, 255, 255))
    
    font = ImageFont.truetype(FONTS_PATH, 26)
    Area_list = data["data"]["world_explorations"]
    for i in Area_list:
        if i["type"] == "Reputation":
            if i["name"]=='蒙德':
                #蒙德
                line = spaceWrap(str(i["exploration_percentage"] / 10).replace("100.0", "100"), 4)+'%'
                draw.text((400, 546), line, font=font, fill = (255, 255, 255))
                line = "Lv."+spaceWrap(str(i["level"]), 2)
                draw.text((400, 595), line, font=font, fill = (255, 255, 255))
            elif i["name"]=='璃月':
                #璃月
                line = spaceWrap(str(i["exploration_percentage"] / 10).replace("100.0", "100"), 4)+'%'
                draw.text((400, 699), line, font=font, fill = (255, 255, 255))
                line = "Lv."+spaceWrap(str(i["level"]), 2)
                draw.text((400, 749), line, font=font, fill = (255, 255, 255))
            elif i["name"]=='稻妻':
                #稻妻
                line = spaceWrap(str(i["exploration_percentage"] / 10).replace("100.0", "100"), 4)+'%'
                draw.text((915, 691), line, font=font, fill = (255, 255, 255))
                line = "Lv."+spaceWrap(str(i["level"]), 2)
                draw.text((915, 728), line, font=font, fill = (255, 255, 255))
        else:
            if i['name']=='龙脊雪山':
                line = spaceWrap(str(i["exploration_percentage"] / 10).replace("100.0", "100"), 4)+'%'
                draw.text((915, 546), line, font=font, fill = (255, 255, 255))
        if len(i["offerings"]) != 0:
            if i["offerings"][0]["name"]=='神樱眷顾':
                line = "Lv." + spaceWrap(str(i["offerings"][0]["level"]), 2)
                draw.text((915, 764), line, font=font, fill = (255, 255, 255))
            elif i["offerings"][0]["name"]=='忍冬之树':
                line = "Lv." + spaceWrap(str(i["offerings"][0]["level"]), 2)
                draw.text((915, 595), line, font=font, fill = (255, 255, 255))
    
    #尘歌壶
    if len(data["data"]["homes"]) != 0:
        Home_List = data["data"]["homes"]
        line = "尘歌壶 Lv."+ str(Home_List[0]["level"])
        font = ImageFont.truetype(FONTS_PATH, 30)
        w, h = draw.textsize(line, font=font)
        draw.text(((2474 - w) / 2, 75), line, font=font, fill = (255, 255, 255))
        
        #尘歌壶3个洞天
        homeworld_list = []
        #有解锁的洞天
        for i in Home_List:
            homeworld_list.append(i["name"])
            if i['name']=='翠黛峰':
                line = i['name']
                font = ImageFont.truetype(FONTS_PATH, 30)
                w, h = draw.textsize(line, font=font)
                draw.text(((2474 - w) / 2, 165), line, font=font, fill = (242, 196, 127))
                
                line = "洞天等级"
                font = ImageFont.truetype(FONTS_PATH, 30)
                w, h = draw.textsize(line, font=font)
                draw.text(((2474 - w) / 2, 203), line, font=font, fill = (250, 245, 207))
                
                line = i['comfort_level_name']
                font = ImageFont.truetype(FONTS_PATH, 24)
                w, h = draw.textsize(line, font=font)
                draw.text(((2474 - w) / 2, 232), line, font=font, fill = (255, 255, 255))
            elif i['name']=='罗浮洞':
                line = i['name']
                font = ImageFont.truetype(FONTS_PATH, 30)
                w, h = draw.textsize(line, font=font)
                draw.text(((2474 - w) / 2, 368), line, font=font, fill = (242, 196, 127))
                
                line = "洞天等级"
                font = ImageFont.truetype(FONTS_PATH, 30)
                w, h = draw.textsize(line, font=font)
                draw.text(((2474 - w) / 2, 406), line, font=font, fill = (250, 245, 207))
                
                line = i['comfort_level_name']
                font = ImageFont.truetype(FONTS_PATH, 24)
                w, h = draw.textsize(line, font=font)
                draw.text(((2474 - w) / 2, 435), line, font=font, fill = (255, 255, 255))
            elif i['name']=='清琼岛':
                line = i['name']
                font = ImageFont.truetype(FONTS_PATH, 30)
                w, h = draw.textsize(line, font=font)
                draw.text(((2474 - w) / 2, 571), line, font=font, fill = (242, 196, 127))
                
                line = "洞天等级"
                font = ImageFont.truetype(FONTS_PATH, 30)
                w, h = draw.textsize(line, font=font)
                draw.text(((2474 - w) / 2, 609), line, font=font, fill = (250, 245, 207))
                
                line = i['comfort_level_name']
                font = ImageFont.truetype(FONTS_PATH, 24)
                w, h = draw.textsize(line, font=font)
                draw.text(((2474 - w) / 2, 638), line, font=font, fill = (255, 255, 255))
        #未解锁的洞天
        if '翠黛峰' not in homeworld_list:
            line = '翠黛峰'
            font = ImageFont.truetype(FONTS_PATH, 30)
            w, h = draw.textsize(line, font=font)
            draw.text(((2474 - w) / 2, 165), line, font=font, fill = (242, 196, 127))
            
            line = "洞天等级"
            font = ImageFont.truetype(FONTS_PATH, 30)
            w, h = draw.textsize(line, font=font)
            draw.text(((2474 - w) / 2, 203), line, font=font, fill = (250, 245, 207))
            
            line = '未解锁'
            font = ImageFont.truetype(FONTS_PATH, 24)
            w, h = draw.textsize(line, font=font)
            draw.text(((2474 - w) / 2, 232), line, font=font, fill = (255, 255, 255))
        if '罗浮洞' not in homeworld_list:
            line = '罗浮洞'
            font = ImageFont.truetype(FONTS_PATH, 30)
            w, h = draw.textsize(line, font=font)
            draw.text(((2474 - w) / 2, 368), line, font=font, fill = (242, 196, 127))
            
            line = "洞天等级"
            font = ImageFont.truetype(FONTS_PATH, 30)
            w, h = draw.textsize(line, font=font)
            draw.text(((2474 - w) / 2, 406), line, font=font, fill = (250, 245, 207))
            
            line = '未解锁'
            font = ImageFont.truetype(FONTS_PATH, 24)
            w, h = draw.textsize(line, font=font)
            draw.text(((2474 - w) / 2, 435), line, font=font, fill = (255, 255, 255))
        if '清琼岛' not in homeworld_list:
            line = '清琼岛'
            font = ImageFont.truetype(FONTS_PATH, 30)
            w, h = draw.textsize(line, font=font)
            draw.text(((2474 - w) / 2, 571), line, font=font, fill = (242, 196, 127))
            
            line = "洞天等级"
            font = ImageFont.truetype(FONTS_PATH, 30)
            w, h = draw.textsize(line, font=font)
            draw.text(((2474 - w) / 2, 609), line, font=font, fill = (250, 245, 207))
            
            line = '未解锁'
            font = ImageFont.truetype(FONTS_PATH, 24)
            w, h = draw.textsize(line, font=font)
            draw.text(((2474 - w) / 2, 638), line, font=font, fill = (255, 255, 255))
            
        #摆设
        line = "摆件:" + str(Home_List[0]["item_num"])
        font = ImageFont.truetype(FONTS_PATH, 26)
        w, h = draw.textsize(line, font=font)
        draw.text(((2474 - w) / 2, 730), line, font=font, fill = (255, 255, 255))
        #最大仙力
        line = '仙力:' + str(Home_List[0]["comfort_num"])
        font = ImageFont.truetype(FONTS_PATH, 26)
        w, h = draw.textsize(line, font=font)
        draw.text(((2474 - w) / 2, 770), line, font=font, fill = (255, 255, 255))
    else:
        line = '翠黛峰'
        font = ImageFont.truetype(FONTS_PATH, 30)
        w, h = draw.textsize(line, font=font)
        draw.text(((2474 - w) / 2, 165), line, font=font, fill = (242, 196, 127))
        
        line = "洞天等级"
        font = ImageFont.truetype(FONTS_PATH, 30)
        w, h = draw.textsize(line, font=font)
        draw.text(((2474 - w) / 2, 203), line, font=font, fill = (250, 245, 207))
        
        line = '未解锁'
        font = ImageFont.truetype(FONTS_PATH, 24)
        w, h = draw.textsize(line, font=font)
        draw.text(((2474 - w) / 2, 232), line, font=font, fill = (255, 255, 255))

        line = '罗浮洞'
        font = ImageFont.truetype(FONTS_PATH, 30)
        w, h = draw.textsize(line, font=font)
        draw.text(((2474 - w) / 2, 368), line, font=font, fill = (242, 196, 127))
        
        line = "洞天等级"
        font = ImageFont.truetype(FONTS_PATH, 30)
        w, h = draw.textsize(line, font=font)
        draw.text(((2474 - w) / 2, 406), line, font=font, fill = (250, 245, 207))
        
        line = '未解锁'
        font = ImageFont.truetype(FONTS_PATH, 24)
        w, h = draw.textsize(line, font=font)
        draw.text(((2474 - w) / 2, 435), line, font=font, fill = (255, 255, 255))

        line = '清琼岛'
        font = ImageFont.truetype(FONTS_PATH, 30)
        w, h = draw.textsize(line, font=font)
        draw.text(((2474 - w) / 2, 571), line, font=font, fill = (242, 196, 127))
        
        line = "洞天等级"
        font = ImageFont.truetype(FONTS_PATH, 30)
        w, h = draw.textsize(line, font=font)
        draw.text(((2474 - w) / 2, 609), line, font=font, fill = (250, 245, 207))
        
        line = '未解锁'
        font = ImageFont.truetype(FONTS_PATH, 24)
        w, h = draw.textsize(line, font=font)
        draw.text(((2474 - w) / 2, 638), line, font=font, fill = (255, 255, 255))
        
        #摆设
        line = "摆件:0"
        font = ImageFont.truetype(FONTS_PATH, 26)
        w, h = draw.textsize(line, font=font)
        draw.text(((2474 - w) / 2, 730), line, font=font, fill = (255, 255, 255))
        #最大仙力
        line = '仙力:0'
        font = ImageFont.truetype(FONTS_PATH, 26)
        w, h = draw.textsize(line, font=font)
        draw.text(((2474 - w) / 2, 770), line, font=font, fill = (255, 255, 255))
    
    zb_list = []
    for l in range(need_middle):
        for i in range(6):
            zb_list.append([l,i])
    
    jishu = 0
    ICON_PATH = os.path.join(FILE_PATH,'icon')
    for i in Character_datas:
        #937 390xl 50 200 30 230xi
        #计算位置
        z_left = 50+230*zb_list[jishu][1]
        z_top = 937+390*zb_list[jishu][0]
        #插入底图
        base_img = os.path.join(IMG_PATH,'card_content.png')
        dtimg = Image.open(base_img).convert('RGBA')
        dtbox = (z_left, z_top)
        im.paste(dtimg, dtbox, mask=dtimg.split()[3])
        
        weapon = i["weapon"]
        if i["name"] == "旅行者":
            if i["image"].find("UI_AvatarIcon_PlayerGirl") != -1:
                name = str("荧")
            elif i["image"].find("UI_AvatarIcon_PlayerBoy") != -1:
                name = str("空")
            else:
                name = str("旅行者")
        else:
            name = str(i["name"])
        
        #插入角色头像
        picname = str(name) +".png"
        icon_name = os.path.join(ICON_PATH,picname)
        try:
            img = Image.open(icon_name).convert('RGBA')
        except FileNotFoundError:
            urllib.request.urlretrieve(i['icon'], icon_name)
            img = Image.open(icon_name).convert('RGBA')
        img = img.resize((200, 200))
        dtbox = (z_left, z_top)
        im.paste(img, dtbox, mask=img.split()[3])
        
        
        #插入角色命座
        line = str(i["actived_constellation_num"])
        i_con = Image.open(os.path.join(PLAYER, f'命之座{line}.png'))
        i_con = i_con.resize((43, 43))
        mz_left = z_left + 158
        mz_top = z_top
        mzbox = (mz_left, mz_top)
        im.paste(i_con, mzbox, mask=i_con.split()[3])
        
        #插入角色属性
        elementname = str(i["element"]) +".png"
        element_img = os.path.join(IMG_PATH,elementname)
        eleimg = Image.open(element_img).convert('RGBA')
        eleimg = eleimg.resize((30, 30))
        ele_left = z_left + 5
        els_top = z_top + 7
        elebox = (ele_left, els_top)
        im.paste(eleimg, elebox, mask=eleimg.split()[3])
        
        #插入角色姓名
        line = str(name)
        font = ImageFont.truetype(FONTS_PATH, 26)
        w, h = draw.textsize(line, font=font)
        name_max_width = (z_left+100)*2
        name_top = z_top + 215
        draw.text(((name_max_width - w) / 2, name_top), line, font=font, fill = (0, 0, 0))
        
        #插入角色等级
        line = 'Lv.' + spaceWrap(str(i["level"]), 2)
        font = ImageFont.truetype(FONTS_PATH, 26)
        level_left = z_left + 28
        level_top = z_top + 250
        draw.text((level_left, level_top), line, font=font, fill = (0, 0, 0))
        
        #插入角色好感度
        line = str(i["fetter"])
        i_fet = Image.open(os.path.join(FETTER, f'好感度{line}.png'))
        i_fet = i_fet.resize((45, 45))
        fetter_left = z_left + 135
        fetter_top = z_top + 242
        fetterbox = (fetter_left, fetter_top)
        im.paste(i_fet, fetterbox, mask=i_fet.split()[3])
        
        #插入武器图片
        weaponname = str(weapon["name"]) +".png"
        weapon_name = os.path.join(ICON_PATH,weaponname)
        try:
            weapon_img = Image.open(weapon_name).convert('RGBA')
        except FileNotFoundError:
            urllib.request.urlretrieve(weapon['icon'], weapon_name)
            weapon_img = Image.open(weapon_name).convert('RGBA')
        weapon_img = weapon_img.resize((60, 60))
        weapon_left = z_left + 9
        weapon_top = z_top + 283
        weaponbox = (weapon_left, weapon_top)
        im.paste(weapon_img, weaponbox, mask=weapon_img.split()[3])
        
        #插入武器名称
        line = str(weapon["name"])
        font = ImageFont.truetype(FONTS_PATH, 18)
        weaponname_left = z_left + 73
        weaponname_top = z_top + 291
        draw.text((weaponname_left, weaponname_top), line, font=font, fill = (0, 0, 0))
        
        #插入武器等级精炼
        line = 'Lv.' + str(weapon["level"]) + " 精炼." + str(weapon["affix_level"])
        font = ImageFont.truetype(FONTS_PATH, 18)
        weaponlv_left = z_left + 73
        weaponlv_top = z_top + 320
        draw.text((weaponlv_left, weaponlv_top), line, font=font, fill = (0, 0, 0))
        
        jishu = jishu + 1
        
    bio  = io.BytesIO()
    im.save(bio, format='PNG')
    base64_str = 'base64://' + base64.b64encode(bio.getvalue()).decode()
    mes  = f"[CQ:image,file={base64_str}]"
    return mes


    
@sv.on_prefix(['原神信息','米游社查询','原神查询'])
async def genshin(bot, ev: CQEvent):
    uid = ev.message.extract_plain_text()
    sender = ev.sender
    msg = str(ev)
    if not re.fullmatch('[0-9]*', uid):
        await bot.send(ev, uid, at_sender=True)
        return
    uid = uid.lstrip('0')
    if not uid:
        await bot.send(ev, '请输入原神信息uid或米游社ID 如：原神信息100692770', at_sender=True)
        sv.logger.info('原神uid不对')
        return
    level = 0
    nickname = sender["card"] or sender["nickname"]
    # if '米游社' in msg:
        # userinfo = json.loads(GetBaseInfo(uid))
        # gamelist = userinfo['data']['list']
        # for item in gamelist:
            # if item['game_id']==2:
                # uid = item['game_role_id']
                # level = item['level']
                # nickname = item['nickname']
                # break
        # if int(level)<1:
            # await bot.send(ev, '米游社ID有误！\n请检查输入的米游社ID是否绑定了原神账号！', at_sender=True)
            # return
    # else:
        # if (len(uid) != 9):
            # userinfo = json.loads(GetBaseInfo(uid))
            # gamelist = userinfo['data']['list']
            # for item in gamelist:
                # if item['game_id']==2:
                    # uid = item['game_role_id']
                    # level = item['level']
                    # nickname = item['nickname']
                    # break
            # if int(level)<1:
                # await bot.send(ev, 'UID有误！\n请检查输入的UID是否正确！', at_sender=True)
                # return
    if (len(uid) == 9):
        if (uid[0] == "1"):
            sv.logger.info('原神查询uid中')
            await bot.send(ev,'原神查询uid中')
            mes = JsonAnalysis(request_data(uid=uid), uid, "cn_gf01", level, nickname)
            await bot.send(ev, mes, at_sender=True)
            #await bot.send_group_forward_msg(group_id=ev['group_id'], messages=tas_list)
        elif (uid[0] == "5"):
            sv.logger.info('原神查询uid中')
            mes = JsonAnalysis(request_data(uid=uid), uid, "cn_qd01", level, nickname)
            await bot.send(ev, mes, at_sender=True)
            #await bot.send_group_forward_msg(group_id=ev['group_id'], messages=tes_list)
        else:
            sv.logger.info('原神uid不对')
            await bot.send(ev, 'UID输入有误！\n请检查UID是否为国服UID！', at_sender=True)
    else:
        sv.logger.info('原神uid不对')
        await bot.send(ev, 'UID长度有误！\n请检查输入的UID是否为9位数！', at_sender=True)

@sv.on_prefix('原神深渊')
async def genshin(bot: HoshinoBot, ev: CQEvent):
    args = ev.message.extract_plain_text().split()
    if len(args) == 1:
        uid = ev.message.extract_plain_text()
        Schedule_type = "1"
    elif len(args) ==2:
        uid = args[1]
        if args[0] == '本期':
            Schedule_type = "1"
        elif args[0] == '上期':
            Schedule_type = "2"
        else:
            await bot.finish(ev,'请重新输入', at_sender=True)
    else:
        await bot.finish(ev,'请重新输入', at_sender=True)
    if not re.fullmatch('[0-9]*', uid):
        await bot.send(ev, uid, at_sender=True)
        return
    uid = uid.lstrip('0')
    if not uid:
        await bot.send(ev, '请输入 原神深渊+（本期或上期）+uid （注：不加默认本期） \n如：原神深渊 100692770', at_sender=True)
        sv.logger.info('原神uid不对')
        return
    if (len(uid) == 9):
        if (uid[0] == "1"):
            sv.logger.info('原神深渊查询中')
            await bot.send(ev,'原神深渊查询中')
            SpiralAbysInfo = JsonSpiralAbys(GetSpiralAbys(uid ,"cn_gf01" ,Schedule_type), Schedule_type)
            sv.logger.info('原神深渊查询成功')
            tas_list = []
            msg_text = f'UID{uid} (官服)的深渊信息为：\r\n{SpiralAbysInfo}'
            n = ImgText(msg_text)
            mes = n.draw_text()
            data = {
                "type": "node",
                "data": {
                    "name": "imhy",
                    "uin": "2093936907",
                    "content":mes
                        }
                    }
            tas_list.append(data)
            await bot.send(ev, mes, at_sender=True)
            #await bot.send_group_forward_msg(group_id=ev['group_id'], messages=tas_list)
        elif (uid[0] == "5"):
            sv.logger.info('原神深渊查询中')
            SpiralAbysInfo = JsonSpiralAbys(GetSpiralAbys(uid ,"cn_gf01"), Schedule_type)
            sv.logger.info('原神深渊查询成功')
            tes_list = []
            msg_text = f'UID{uid} (官服)的深渊信息为：\r\n{SpiralAbysInfo}'
            n = ImgText(msg_text)
            mes = n.draw_text()
            data = {
                "type": "node",
                "data": {
                    "name": "imhy",
                    "uin": "2093936907",
                    "content":mes
                        }
                    }
            tes_list.append(data)
            await bot.send(ev, mes, at_sender=True)
            #await bot.send_group_forward_msg(group_id=ev['group_id'], messages=tes_list)
        else:
            sv.logger.info('原神uid不对')
            await bot.send(ev, 'UID输入有误！\n请检查UID是否为国服UID！', at_sender=True)
    else:
        sv.logger.info('原神uid不对')
        await bot.send(ev, 'UID长度有误！\n请检查输入的UID是否为9位数！', at_sender=True)