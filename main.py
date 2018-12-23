import gzip
import json
from urllib.request import build_opener

import re

opener = build_opener()
opener.addheaders.clear()
opener.addheaders.append(("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.80 Safari/537.36"))

url = "https://www.bilibili.com/av{}"

if __name__ == "__main__":
    av = input("input av number(both av170001 and 170001 are OJBK):")
    if av.startswith("av"):
        av = av[2:]
    response = opener.open(url.format(av)).read()
    response = gzip.decompress(response).decode()
    data = re.findall("__INITIAL_STATE__=\{.*\:\{.*\:.*\}\};", response)

    try:
        data = json.loads(data.pop()[18:-1])
    except Exception as e:
        print("Failed to get lyrics")
        raise e

    data = data["videoData"]["subtitle"]["list"]
    if not data:
        print("No subtitle")
        exit(0)
    for i in data:
        print("{}/{}: \n\tauthor: {}\n\turl: {}".format(i["lan"], i["lan_doc"], i["author"]["name"], i["subtitle_url"]))
        subtitle = json.loads(opener.open(i["subtitle_url"]).read().decode())
        with open(f"{av}.lrc", "w", encoding="utf-8") as f:
            author = i["author"]["name"]
            if author:
                f.write("[by:{}]\n".format(author))
            for i in subtitle["body"]:
                start_time = i["from"]
                end_time = i["to"]
                content = i["content"]
                f.write("[{:02d}:{:02d}.{:02d}]{}\n".format(int(start_time / 60), int(start_time % 60), int((start_time - int(start_time)) * 100), content))
            print("saved as {}.lrc".format(av))
