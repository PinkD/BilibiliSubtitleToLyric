import gzip
import json
import argparse
import sys
from urllib.request import build_opener

import re

url = "https://www.bilibili.com/av{}"

opener = build_opener()
opener.addheaders.clear()
opener.addheaders.append(("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.80 Safari/537.36"))
argParser = argparse.ArgumentParser()
argParser.add_argument("av", help="av number, both av170001 and 170001 are OK")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        argParser.print_help()
        sys.exit(1)
    argParser = argParser.parse_args()
    av = argParser.av
    if av.startswith("av"):
        av = av[2:]
    response = opener.open(url.format(av)).read()
    response = gzip.decompress(response).decode()
    data = re.findall("__INITIAL_STATE__={.*:{.*:.*}.*};", response)

    try:
        data = json.loads(data.pop()[18:-1])
    except IndexError as e:
        print("Failed to get lyrics, the first run may fail, please run again to see if this happens again")
        exit(1)
    else:
        data = data["videoData"]["subtitle"]["list"]
        if not data:
            print(f"No subtitle for av{av}")
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
