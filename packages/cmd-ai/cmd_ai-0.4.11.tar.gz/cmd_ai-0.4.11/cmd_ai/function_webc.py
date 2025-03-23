#!/usr/bin/env python3

from cmd_ai import config
from cmd_ai.version import __version__
import json

"""

##
{
  "name": "get_weather",
  "description": "Determine weather or weather prediction in Czech Republic ",
  "parameters": {
    "type": "object",
    "properties": {
      "time": {
        "type": "string",
        "description": "today, tomorrow"
      }
    },
    "required": [
      "time"
    ]
  }
}

#### return json

{"weather":" Počasí přes den (07-24): > Zpočátku skoro jasno až polojasno, zejména na Moravě a severovýchodě Čech místy mlhy, i mrznoucí. Postupně od severozápadu přibývání oblačnosti a později v severozápadní polovině území místy déšť, i mrznoucí, a nad 1000 m i sněžení. Nejvyšší teploty 6 až 10 °C, při slabém větru kolem 4 °C, zejména na střední Moravě a severovýchodě Čech, v 1000 m na horách kolem 5 °C. Mírný jihozápadní až západní vítr 3 až 7 m/s, místy s nárazy kolem 15 m/s. Zejména na severovýchodě Čech a na Moravě vítr jen slabý proměnlivý do 3 m/s."}

"""

from googlesearch import search

from fire import Fire
import datetime as dt
import requests
from bs4 import BeautifulSoup
from bs4.element import Comment

# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from webdriver_manager.chrome import ChromeDriverManager

# from webdriver_manager.firefox import GeckoDriverManager

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from subprocess import getoutput

from console import fg


def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


def fetch_url_content(url):
    print("D...  requesting", url)
    response = requests.get(url)
    cont = []
    res=""
    if response.status_code == 200:
        print("D...  response is OK")
        soup = BeautifulSoup(response.text, 'html.parser')
        texts = soup.findAll(string=True)
        visible_texts = filter(tag_visible, texts)
        print(visible_texts)
        for i in visible_texts:
            i = i.strip()
            if len(i)==0: continue
            cont.append(i)
        res =  "\n".join(cont)
        return json.dumps(  {"url_content":res } , ensure_ascii=False)  # MUST OUTPUT FORMAT

    else:
        return json.dumps(  {"url_content":res } , ensure_ascii=False)  # MUST OUTPUT FORMAT
        #return f"Error: Unable to fetch the URL. Status code: {response.status_code}"


# def get_google_urls(searchstring):
#     pool = search( searchstring, num_results=5)
#     urls = []
#     cont = []
#     for i in pool:
#         urls.append(i)
#     urls = list(set(urls))
#     for i in urls:
#         #cont.append("# URL ADDRESS:")
#         cont.append(i)
#     res = cont#"\n".join( cont)

#     # must return json for GPT
#     return json.dumps(  {"urls":res } , ensure_ascii=False)  # MUST OUTPUT FORMAT



if __name__=="__main__":
    Fire(fetch_url_content)
