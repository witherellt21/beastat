import urllib.request
import requests
import sys
from lxml import etree

def format_pandas_http_request(*, url:str) -> str:
    # opener = urllib.request.build_opener()
    # opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    # response = opener.open(url)
    # return response
    # response = requests.get(url, headers = {'User-agent': 'your bot 0.1', 'Accept-Encoding': 'identity'})
    # print(response.headers)
    # # print(dir(response))
    # print(type(response.content.decode()))
    # # sys.exit()

    # return etree.HTML(response.content)
    return url
