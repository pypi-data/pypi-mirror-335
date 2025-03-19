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


def get_photo_id_by_short_url(short_url):
    """
    从快手短连接获取视频id
    """
    # 获取跳转后的地址
    redirected_url = get_redirected_url(short_url)
    print(redirected_url)

    if redirected_url:

        match_photo_id = re.search(r"photoId=([^&]+)", redirected_url)
        if match_photo_id:
            return match_photo_id.group(1)

        match_photo = re.search(r"/photo/([^/?]+)", redirected_url)
        if match_photo:
            return match_photo.group(1)

        short_video = re.search(r"/short-video/([^/?]+)", redirected_url)
        if short_video:
            return short_video.group(1)
