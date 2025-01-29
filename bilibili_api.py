import json, requests, chardet, re
from fake_useragent import UserAgent
from datetime import date



## request to bilibili api
# 随机产生请求头
ua = UserAgent()



# 对爬取的页面内容进行json格式处理
def getText(url):
    # 随机切换请求头
    res = requests.get(url = url, headers = {
        "accept-encoding": "gzip",  # gzip压缩编码  能提高传输文件速率
        "user-agent": ua.random
    })

    res.encoding = chardet.detect(res.content)['encoding']  # 统一字符编码
    res.encoding = 'utf-8'
    res = res.text
    data = json.loads(res)  # json格式化
    return data



def getBvNumbers(url : str):
    bv = re.search(r'BV\w+', url).group()

    if bv:
        print(bv)
        return bv
    else:
        print("Invalid Bilibili URL")



def getBiliInfor(video_url : str):
    bv = getBvNumbers(video_url)

    url_bv = f"https://api.bilibili.com/x/player/pagelist?bvid={bv}"
    response = getText(url_bv)

    cid = response['data'][0]['cid']  # get cid

    url_av = f"https://api.bilibili.com/x/web-interface/view?cid={cid}&bvid={bv}"
    response_av = getText(url_av)

    aid = response_av['data']['aid']  # get aid

    url_api = f"https://api.bilibili.com/x/web-interface/view?aid={aid}"
    response_api = getText(url_api)

    print(url_api)


    # return items
    return {
        "title": response_api['data']['title'],
        "description": response_api['data']['desc'],
        "release_date": date.fromtimestamp(response_api['data']['pubdate']).isoformat(),
        "uploader": response_api['data']['owner']['name'],
        "image_url": response_api['data']['pic'].replace("http:", "https:"),
        "url": f"bilibili.com/video/{bv}/",
        "duration": round(float(response_api['data']['duration']) / 60.0)
    }