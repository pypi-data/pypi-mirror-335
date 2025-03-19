import re
import urllib.parse
import json
from typing import Optional, Union
from time import localtime, strftime
from aiohttp import ClientSession
import sys
import getopt
import logging
import os
import yaml
from datetime import datetime, date
from kirara_ai.logger import get_logger
logger = get_logger("ApiCollection")


useage = 'python index.py -u <url>'
headers = {
    'method': 'GET',
    'Cookie': 'buvid3=1CC3009A-D423-3E55-F787-661CDC57058E73946infoc; b_nut=1720767173; CURRENT_FNVAL=4048; _uuid=F86C6842-C7EB-6DE10-22E6-ACC92431BC3807849infoc; buvid_fp=f8c4348644e6844a0ac6128231f40ede; rpdid=0zbfVGqEbt|1bwImssKW|31|3w1Ssa9h; header_theme_version=CLOSE; enable_web_push=DISABLE; DedeUserID=492252146; DedeUserID__ckMd5=03dfbe33ea9429e6; hit-dyn-v2=1; home_feed_column=5; browser_resolution=1920-919; buvid4=FA5A18D7-96A3-C425-AB7F-FFA9AB4D06C665297-022052116-fLHoGoJcONkYlgID3yMzYQ%3D%3D; share_source_origin=COPY; bsource=share_source_copy_link; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NDI0NDcwMzEsImlhdCI6MTc0MjE4Nzc3MSwicGx0IjotMX0.0IANz4xY_TBRtW-ma-GcnSJl3OIxtwhlmeN0Oy5gLow; bili_ticket_expires=1742446971; SESSDATA=2e255e80%2C1757739834%2Cfaf4c%2A31CjAl_03BcmzWqfmsl4Ra7wk7X4rqcq3K4a9hAhlmIO1mpud1OFH-88xXORl_62JrKrISVkNyYWRyel9RYTQ4SGJsQllYdVRpaVptNV9EY3B1My1vbFJWTmQzMlQ2RDFlbm9fbEd5dGt6ZGdqVmtFOC1JZXk5Qm5pVXFldlEtWVR4OFhFRklpTFNRIIEC; bili_jct=a21be0cdc359e2a6d89dccc3ee90d4dc; sid=6p1ji7fo; b_lsid=528AE27F_195A3225938',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9',
    'cache-control': 'max-age=0',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.25 Mobile Safari/537.36',
}
analysis_stat = {}  # group_id : last_vurl
# 使用默认配置
blacklist = []
analysis_display_image = False
analysis_display_image_list = []
trust_env = False


current_dir = os.path.dirname(os.path.abspath(__file__))
video_ids_file = os.path.join(current_dir, "bilibili_video_ids.yaml")
def _load_video_ids():
    """从YAML文件加载视频ID记录"""
    try:
        today = str(date.today())
        if os.path.exists(video_ids_file):
            with open(video_ids_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
                # 检查是否是今天的数据
                if data.get('date') == today:
                    return data.get('video_ids', {})

        # 如果文件不存在、数据为空或日期不是今天，创建新的空记录
        empty_data = {
            'date': today,
            'video_ids': {}
        }
        with open(video_ids_file, 'w', encoding='utf-8') as f:
            yaml.safe_dump(empty_data, f, allow_unicode=True)
        return empty_data['video_ids']
    except Exception as e:
        logger.error(f"Failed to load video IDs: {e}")
        return {}
def _save_video_ids():
    """保存视频ID记录到YAML文件"""
    try:
        data = {
            'date': str(date.today()),
            'video_ids': video_ids
        }
        # 确保目录存在
        os.makedirs(os.path.dirname(video_ids_file), exist_ok=True)
        # 使用 'w' 模式覆盖写入文件
        with open(video_ids_file, 'w', encoding='utf-8') as f:
            yaml.safe_dump(data, f, allow_unicode=True)
    except Exception as e:
        logger.error(f"Failed to save video IDs: {e}")

video_ids = {}
video_ids = _load_video_ids()



# 手动搜视频标题
async def search_bilibili_video_by_title(title,sender):

    async with ClientSession(trust_env=trust_env, headers=headers) as session:
        vurl = await search_bili_by_title(sender,title, session)
        msg = await bili_keyword(vurl, session)
    try:
        return msg
    except:
        # 避免简介有风控内容无法发送
        logger.warning(f"{msg}\n此次解析可能被风控，尝试去除简介后发送！")
        msg = re.sub(r"简介.*", "", msg)
        return msg

# on_rex判断不到小程序信息

async def rex_bilibili(text):
    if re.search(r"(b23.tv)|(bili(22|23|33|2233).cn)", text, re.I):
        # 提前处理短链接，避免解析到其他的
        text = await b23_extract(text)
    patterns = r"(\.bilibili\.com)|(^(av|cv)(\d+))|(^BV([a-zA-Z0-9]{10})+)|(\[\[QQ小程序\]哔哩哔哩\])|(QQ小程序&amp;#93;哔哩哔哩)|(QQ小程序&#93;哔哩哔哩)"
    match = re.compile(patterns, re.I).search(text)
    if match:
        async with ClientSession(trust_env=trust_env, headers=headers) as session:
            msg = await bili_keyword(text, session)
        if msg:
            try:
                return msg
            except:
                # 避免简介有风控内容无法发送
                logger.warning(f"{msg}\n此次解析可能被风控，尝试去除简介后发送！")
                msg = re.sub(r"简介.*", "", msg)
                return msg


async def bili_keyword(text: str, session: ClientSession
) -> str:
    try:
        # 提取url
        url, page, time_location = extract(text)
        # 如果是小程序就去搜索标题
        if not url:
            if title := re.search(r'"desc":("[^"哔哩]+")', text):
                vurl = await search_bili_by_title(title[1], session)
                if vurl:
                    url, page, time_location = extract(vurl)

        # 获取视频详细信息
        msg, vurl = "", ""
        if "view?" in url:
            msg, vurl = await video_detail(
                url, page=page, time_location=time_location, session=session
            )
        elif "bangumi" in url:
            msg, vurl = await bangumi_detail(url, time_location, session)
        elif "xlive" in url:
            msg, vurl = await live_detail(url, session)
        elif "article" in url:
            msg, vurl = await article_detail(url, page, session)
        elif "dynamic" in url:
            msg, vurl = await dynamic_detail(url, session)


    except Exception as e:
        msg = "bili_keyword Error: {}".format(type(e))
    return msg


async def b23_extract(text):
    b23 = re.compile(r"b23.tv/(\w+)|(bili(22|23|33|2233).cn)/(\w+)", re.I).search(
        text.replace("\\", "")
    )
    url = f"https://{b23[0]}"
    async with ClientSession(trust_env=trust_env) as session:
        async with session.get(url) as resp:
            return str(resp.url)


def extract(text: str):
    try:
        url = ""
        # 视频分p
        page = re.compile(r"([?&]|&amp;)p=\d+").search(text)
        # 视频播放定位时间
        time = re.compile(r"([?&]|&amp;)t=\d+").search(text)
        # 主站视频 av 号
        aid = re.compile(r"av\d+", re.I).search(text)
        # 主站视频 bv 号
        bvid = re.compile(r"BV([A-Za-z0-9]{10})+", re.I).search(text)
        # 番剧视频页
        epid = re.compile(r"ep\d+", re.I).search(text)
        # 番剧剧集ssid(season_id)
        ssid = re.compile(r"ss\d+", re.I).search(text)
        # 番剧详细页
        mdid = re.compile(r"md\d+", re.I).search(text)
        # 直播间
        room_id = re.compile(r"live.bilibili.com/(blanc/|h5/)?(\d+)", re.I).search(text)
        # 文章
        cvid = re.compile(
            r"(/read/(cv|mobile|native)(/|\?id=)?|^cv)(\d+)", re.I
        ).search(text)
        # 动态
        dynamic_id_type2 = re.compile(
            r"(t|m).bilibili.com/(\d+)\?(.*?)(&|&amp;)type=2", re.I
        ).search(text)
        # 动态
        dynamic_id = re.compile(r"(t|m).bilibili.com/(\d+)", re.I).search(text)
        if bvid:
            url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid[0]}"
        elif aid:
            url = f"https://api.bilibili.com/x/web-interface/view?aid={aid[0][2:]}"
        elif epid:
            url = (
                f"https://bangumi.bilibili.com/view/web_api/season?ep_id={epid[0][2:]}"
            )
        elif ssid:
            url = f"https://bangumi.bilibili.com/view/web_api/season?season_id={ssid[0][2:]}"
        elif mdid:
            url = f"https://bangumi.bilibili.com/view/web_api/season?media_id={mdid[0][2:]}"
        elif room_id:
            url = f"https://api.live.bilibili.com/xlive/web-room/v1/index/getInfoByRoom?room_id={room_id[2]}"
        elif cvid:
            page = cvid[4]
            url = f"https://api.bilibili.com/x/article/viewinfo?id={page}&mobi_app=pc&from=web"
        elif dynamic_id_type2:
            url = f"https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/get_dynamic_detail?rid={dynamic_id_type2[2]}&type=2"
        elif dynamic_id:
            url = f"https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/get_dynamic_detail?dynamic_id={dynamic_id[2]}"
        return url, page, time
    except Exception:
        return "", None, None


async def search_bili_by_title(sender: str, title: str, session: ClientSession) -> str:
    mainsite_url = "https://www.bilibili.com"
    search_url = f"https://api.bilibili.com/x/web-interface/wbi/search/all/v2?keyword={urllib.parse.quote(title)}"

    # set headers
    async with session.get(mainsite_url) as resp:
        assert resp.status == 200

    async with session.get(search_url) as resp:
        result = (await resp.json())["data"]["result"]
    for i in result:
        if i.get("result_type") != "video" :
            continue
        # 只返回第一个结果
        if sender not in video_ids:
            video_ids[sender] = []
        for videoDate in i["data"]:
            logger.debug(videoDate["id"])
            logger.debug(video_ids[sender])
            if not videoDate["id"] in video_ids[sender]:
                video_ids[sender].append(videoDate["id"])
                _save_video_ids()
                return videoDate.get("arcurl")


# 处理超过一万的数字
def handle_num(num: int):
    if num > 10000:
        num = f"{num / 10000:.2f}万"
    return num


async def video_detail(url: str, session: ClientSession, **kwargs):
    try:
        async with session.get(url) as resp:
            res = (await resp.json()).get("data")
            if not res:
                return "解析到视频被删了/稿件不可见或审核中/权限不足", url
        vurl = f"https://www.bilibili.com/video/av{res['aid']}"
        vurl = await getRealUrl(vurl,session)
        title = f"\n标题：{res['title']}\n"
        cover = f"封面：{res['pic']}\n"
        if page := kwargs.get("page"):
            page = page[0].replace("&amp;", "&")
            p = int(page[3:])
            if p <= len(res["pages"]):
                vurl += f"?p={p}"
                part = res["pages"][p - 1]["part"]
                if part != res["title"]:
                    title += f"小标题：{part}\n"
        if time_location := kwargs.get("time_location"):
            time_location = time_location[0].replace("&amp;", "&")[3:]
            if page:
                vurl += f"&t={time_location}"
            else:
                vurl += f"?t={time_location}"
        pubdate = strftime("%Y-%m-%d %H:%M:%S", localtime(res["pubdate"]))
        tname = f"类型：{res['tname']} | UP：{res['owner']['name']} | 日期：{pubdate}\n"
        stat = f"播放：{handle_num(res['stat']['view'])} | 弹幕：{handle_num(res['stat']['danmaku'])} | 收藏：{handle_num(res['stat']['favorite'])}\n"
        stat += f"点赞：{handle_num(res['stat']['like'])} | 硬币：{handle_num(res['stat']['coin'])} | 评论：{handle_num(res['stat']['reply'])}\n"
        desc = f"简介：{res['desc']}"
        desc_list = desc.split("\n")
        desc = "".join(i + "\n" for i in desc_list if i)
        desc_list = desc.split("\n")
        if len(desc_list) > 4:
            desc = desc_list[0] + "\n" + desc_list[1] + "\n" + desc_list[2] + "……"
        mstext = "".join([cover,f"直链：{vurl}", title, tname, stat, desc])
        return mstext, vurl
    except Exception as e:
        msg = "视频解析出错--Error: {}".format(type(e))
        return msg, None


async def bangumi_detail(url: str, time_location: str, session: ClientSession):
    try:
        async with session.get(url) as resp:
            res = (await resp.json()).get("result")
            if not res:
                return None, None
        cover = f"封面：{res['cover']}\n"
        title = f"番剧：{res['title']}\n"
        desc = f"{res['newest_ep']['desc']}\n"
        index_title = ""
        style = "".join(f"{i}," for i in res["style"])
        style = f"类型：{style[:-1]}\n"
        evaluate = f"简介：{res['evaluate']}\n"
        if "season_id" in url:
            vurl = f"https://www.bilibili.com/bangumi/play/ss{res['season_id']}"
        elif "media_id" in url:
            vurl = f"https://www.bilibili.com/bangumi/media/md{res['media_id']}"
        else:
            epid = re.compile(r"ep_id=\d+").search(url)[0][len("ep_id=") :]
            for i in res["episodes"]:
                if str(i["ep_id"]) == epid:
                    index_title = f"标题：{i['index_title']}\n"
                    break
            vurl = f"https://www.bilibili.com/bangumi/play/ep{epid}"
        if time_location:
            time_location = time_location[0].replace("&amp;", "&")[3:]
            vurl += f"?t={time_location}"
        mstext = "".join([f"{cover}\n", f"{vurl}\n", title, index_title, desc, style, evaluate])
        return mstext, vurl
    except Exception as e:
        msg = "番剧解析出错--Error: {}".format(type(e))
        msg += f"\n{url}"
        return msg, None


async def live_detail(url: str, session: ClientSession):
    try:
        async with session.get(url) as resp:
            res = await resp.json()
            if res["code"] != 0:
                return None, None
        res = res["data"]
        uname = res["anchor_info"]["base_info"]["uname"]
        room_id = res["room_info"]["room_id"]
        title = res["room_info"]["title"]
        cover = res["room_info"]["cover"]
        live_status = res["room_info"]["live_status"]
        lock_status = res["room_info"]["lock_status"]
        parent_area_name = res["room_info"]["parent_area_name"]
        area_name = res["room_info"]["area_name"]
        online = res["room_info"]["online"]
        tags = res["room_info"]["tags"]
        watched_show = res["watched_show"]["text_large"]
        vurl = f"https://live.bilibili.com/{room_id}\n"
        if lock_status:
            lock_time = res["room_info"]["lock_time"]
            lock_time = strftime("%Y-%m-%d %H:%M:%S", localtime(lock_time))
            title = f"[已封禁]直播间封禁至：{lock_time}\n"
        elif live_status == 1:
            title = f"[直播中]标题：{title}\n"
        elif live_status == 2:
            title = f"[轮播中]标题：{title}\n"
        else:
            title = f"[未开播]标题：{title}\n"
        up = f"主播：{uname}  当前分区：{parent_area_name}-{area_name}\n"
        watch = f"观看：{watched_show}  直播时的人气上一次刷新值：{handle_num(online)}\n"
        if tags:
            tags = f"标签：{tags}\n"
        if live_status:
            player = f"独立播放器：https://www.bilibili.com/blackboard/live/live-activity-player.html?enterTheRoom=0&cid={room_id}"
        else:
            player = ""
        mstext = "".join([cover,vurl, title, up, watch, tags, player])
        return mstext, vurl
    except Exception as e:
        msg = "直播间解析出错--Error: {}".format(type(e))
        return msg, None


async def article_detail(url: str, cvid: str, session: ClientSession):
    try:
        async with session.get(url) as resp:
            res = (await resp.json()).get("data")
            if not res:
                return None, None
        images = res["origin_image_urls"]
        vurl = f"https://www.bilibili.com/read/cv{cvid}"
        title = f"标题：{res['title']}\n"
        up = f"作者：{res['author_name']} (https://space.bilibili.com/{res['mid']})\n"
        view = f"阅读数：{handle_num(res['stats']['view'])} "
        favorite = f"收藏数：{handle_num(res['stats']['favorite'])} "
        coin = f"硬币数：{handle_num(res['stats']['coin'])}"
        share = f"分享数：{handle_num(res['stats']['share'])} "
        like = f"点赞数：{handle_num(res['stats']['like'])} "
        dislike = f"不喜欢数：{handle_num(res['stats']['dislike'])}"
        desc = view + favorite + coin + "\n" + share + like + dislike + "\n"
        mstext = "".join([images,title, up, desc, vurl])
        return mstext, vurl
    except Exception as e:
        msg = "专栏解析出错--Error: {}".format(type(e))
        return msg, None


async def dynamic_detail(url: str, session: ClientSession):
    try:
        async with session.get(url) as resp:
            res = (await resp.json())["data"].get("card")
            if not res:
                return None, None
        card = json.loads(res["card"])
        dynamic_id = res["desc"]["dynamic_id"]
        vurl = f"https://t.bilibili.com/{dynamic_id}\n"
        if not (item := card.get("item")):
            return "动态不存在文字内容", vurl
        if not (content := item.get("description")):
            content = item.get("content")
        content = content.replace("\r", "\n")
        if len(content) > 250:
            content = content[:250] + "......"
        images = (
            item.get("pictures", [])
            if analysis_display_image or "dynamic" in analysis_display_image_list
            else []
        )
        if images:
            images = images
        else:
            pics = item.get("pictures_count")
            if pics:
                content += f"\nPS：动态中包含{pics}张图片"
        if origin := card.get("origin"):
            jorigin = json.loads(origin)
            short_link = jorigin.get("short_link")
            if short_link:
                content += f"\n动态包含转发视频{short_link}"
            else:
                content += f"\n动态包含转发其他动态"
        imageUrls = "\n".join(images)
        content = content+f"\n{imageUrls}"+f"\n{vurl}"

        return content, vurl
    except Exception as e:
        msg = "动态解析出错--Error: {}".format(type(e))
        return msg, None
async def getArgs(argv):
    if len(argv) == 0:
        print(useage)
        sys.exit(2)
    url = ''
    try:
        opts, args = getopt.getopt(argv, "hu:", ["url="])
    except getopt.GetoptError:
        print(useage)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(useage)
            sys.exit()
        elif opt in ("-u", "--url"):
            url = arg
    return {
        'url': url,
    }

# 获取真实地址
async def getRealUrl(url: str, session: ClientSession):
    parse = urllib.parse.urlparse(url)
    host = parse.netloc
    if 'bilibili.com' not in host:
        print('url host wrong, ' + url)
    path = parse.path
    scheme = parse.scheme

    # 更新headers中的host、path和scheme
    headers['authority'] = host
    headers['path'] = path
    headers['scheme'] = scheme
    html = ""
    async with session.get(url, headers=headers) as resp:
        html = await resp.text()
    pattern = r'"url":"(.*?)","'
    # 查找所有匹配项
    matches = re.findall(pattern, html)
    # 处理找到的每个URL
    for rurl in matches:
        # 将 /u002F 替换为 /
        decoded_url = rurl.replace('\\u002F', '/')
        decoded_url = decoded_url.replace('&amp;', '&')
        if "mp4" not in decoded_url:
            continue
        print(decoded_url)
        return decoded_url
    return url
