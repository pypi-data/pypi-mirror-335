import re

import requests
from requests.adapters import HTTPAdapter

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    'Connection': 'close',
}

# 创建一个重试策略
retry_strategy = requests.adapters.Retry(
    total=3,  # 允许的重试总次数，优先于其他计数
    read=3,  # 重试读取错误的次数
    connect=3,  # 重试多少次与连接有关的错误（请求发送到远程服务器之前引发的错误）
    backoff_factor=1,  # 休眠时间： {backoff_factor} * (2 ** ({重试总次数} - 1))
    # status_forcelist=[403, 408, 500, 502, 504],  # 强制重试的状态码
)

# 创建一个自定义的适配器，应用重试策略
adapter = HTTPAdapter(max_retries=retry_strategy)


def get_redirected_url(short_url):
    # 应用自定义的适配器
    session = requests.Session()
    session.keep_alive = False
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    response = session.get(short_url, headers=HEADERS, allow_redirects=True)
    final_url = response.url
    return final_url


def get_video_id_by_short_url(short_url):
    """
    从抖音短连接获取视频id
    """

    # 获取跳转后的地址
    redirected_url = get_redirected_url(short_url)
    print(redirected_url)

    if redirected_url:
        # 使用正则表达式提取视频id：寻找 '/video/' 后面跟随的一串数字
        match = re.search(r'/video/(\d+)', redirected_url)
        if match:
            video_id = match.group(1)
            return video_id

        # 匹配 '/note/' 后面的内容
        match_note = re.search(r"/note/([^/?]+)", redirected_url)
        if match_note:
            return match_note.group(1)

        # 使用正则表达式提取modal_id
        match_modal_id = re.search(r'modal_id=(\d+)', redirected_url)
        if match_modal_id:
            return match_modal_id.group(1)


def get_iframe_data_by_video_id(video_id):
    """
    该接口用于通过视频 VideoID 获取 IFrame 代码。视频 VideoID 可以通过 PC 端视频播放地址中获取
    该接口无需申请权限。

    注意：
    该接口以 https://open.douyin.com/ 开头
    请求地址
    GET /api/douyin/v1/video/get_iframe_by_video

    docs: https://developer.open-douyin.com/docs/resource/zh-CN/dop/develop/openapi/video-management/douyin/iframe-player/get-iframe-by-video
    """
    url = f"https://open.douyin.com/api/douyin/v1/video/get_iframe_by_video?video_id={video_id}"
    response = requests.get(url, )
    if response.status_code == 200:
        response_data = response.json()
        data = response_data["data"]
        # print(url, response_data)
        return data
    else:
        response.raise_for_status()
        print("get_iframe_data_by_video_id Error:", response.status_code)
        return None
