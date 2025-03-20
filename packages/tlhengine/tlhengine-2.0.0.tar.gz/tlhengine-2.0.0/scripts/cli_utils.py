#!/usr/bin/python3

# here is a function to convert normal url to jsdelivr url
# https://github.com/tianlianghai/test_branch/blob/main/README.md
# the target url is
# https://cdn.jsdelivr.net/gh/tianlianghai/test_branch@main/README.md
import argparse
import sys
print("using interpreter", sys.executable)  
def convert_to_jsdelivr_url(url):
    if url.startswith("https://github.com"):
        url = url.replace("https://github.com", "https://cdn.jsdelivr.net/gh")
        url = url.replace("/blob/", "@")
        return url
    # https://raw.githubusercontent.com/tianlianghai/picgo_save/main/save/image-20240715182206559.png
    if url.startswith("https://raw.githubusercontent.com"):
        url = url.replace("https://raw.githubusercontent.com", "https://cdn.jsdelivr.net/gh")
        url = url.replace("/main/", "@main/")
        return url
    
# use this as a cli with argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert normal url to jsdelivr url")
    parser.add_argument("url", help="The url to convert")
    args = parser.parse_args()
    print(convert_to_jsdelivr_url(args.url))