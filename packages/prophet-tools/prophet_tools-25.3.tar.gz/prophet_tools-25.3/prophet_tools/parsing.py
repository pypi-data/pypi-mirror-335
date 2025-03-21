import json
from prophet_tools.terminal import *

def get_json_cookies_and_headers(filepath: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    with open(filepath, 'r') as file:
        cookies = json.load(file)
    cookies_dict = {cookie['name']: cookie['value'] for cookie in cookies}

    return cookies_dict, headers

def get_cookies_from_txt(cookies_path):
    import os
    if not os.path.exists(cookies_path):
        raise KeyError('Файл кукис не найден')
    with open(cookies_path, 'r', encoding='utf-8') as file:
        txt = file.read()

    cookies = {}

    lines = txt.splitlines()
    for line in lines:
        cookie = line.split('	')
        name = cookie[0]
        data = cookie[1]
        cookies[name] = data

    return cookies

def download_from_youtube(link):
    from pytube import YouTube

    class Link:
        def __init__(s, link) -> None:
            s.type = link.type
            s.res = int(link.resolution[0:-1]) if link.resolution else 0
            s.fps = link.fps if hasattr(link, 'fps') else 0
            s.size = link.filesize
            s.url = link.url

    def get_max_video_quality(links):
        less_or_1080 = []
        for link in links:
            if link.res <= 1080 and link.res != 0:
                less_or_1080.append(link)

        best_quality_links = []
        max_res = max([link.res for link in less_or_1080])
        for link in less_or_1080:
            if link.res == max_res:
                best_quality_links.append(link)

        max_size = max([link.size for link in best_quality_links])
        for link in best_quality_links:
            if link.size == max_size:
                return link

    yt = YouTube(link)
    try:
        streams = yt.fmt_streams
    except:
        raise ConnectionError(print_in_color("Can't download", red=True, dont_print=True))

    possible_links = []
    for stream in streams:
        possible_links.append(Link(stream))

    best_video_link = get_max_video_quality(possible_links)
    print('best')

if __name__ == "__main__":
    download_from_youtube('https://www.youtube.com/watch?v=OkvQFZFX00s')