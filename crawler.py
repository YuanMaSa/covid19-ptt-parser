import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime

URL = "https://www.ptt.cc/bbs/Gossiping/search"
TYPE = ["新聞", "爆卦"]
KEY = ["疫情", "指揮中心", "確診", "新冠", "疫苗", "醫院", "本土"]
PAGES = 50

payload = {
'from': '/bbs/Gossiping/index.html',
'yes': 'yes'
}
news_d = {}


class PttCrawler:
    def __init__(self, url=URL, keyword=KEY):
        self.url = url
        self.keyword = keyword
        self.articleIndex = 1
        self.rs = requests.session()      
        self.passWarning()
        for t in TYPE:
            self.startSearching(f"{URL}index.html", t)


    def __str__(self):
        return f"{self.keyword}"
    
    def passWarning(self):
        self.rs.post('https://www.ptt.cc/ask/over18',data = payload)

    def startSearching(self, url, articleType):
        res = self.rs.get(url, params={'q': articleType})
        soup = BeautifulSoup(res.text, "html.parser")
        startingIndex = 1

        for i in range(1, PAGES):
            newUrl = f"{URL}?page={startingIndex}&q={articleType}"
            print(newUrl)
            self.getPageArticles(newUrl, articleType)
            startingIndex += 1
            
        print(news_d)

        for k, v in sorted(news_d.items(), key=lambda x: x[1]["trending"], reverse=True):
            print(v)
            print(v["link"])

        # self.articleIndex = 1


    def getPageArticles(self, url, newsType):
        res = self.rs.get(url)
        soup = BeautifulSoup(res.text, "html.parser")
        
        for i in soup.find_all("div", {"class": "r-ent"}):
            d = i.find("div", {"class": "date"})
            l = i.find("div", {"class": "title"}).a
            # select today's news
            
            if self.isCurDate(d.text) and l is not None:
                title = i.select('.title')[0].text.strip()
                link = l["href"]
                trending = i.select('.nrec')[0].text

                if self.hasKeyword(title) and self.getTrending(trending) > 20:
                    print(title)
                    self.insertData(
                        self.articleIndex, title, link, d.text.strip(), int(trending), newsType)
                    self.articleIndex += 1
    
    def insertData(self, index, title, link, date, trending, newsType):
        newData = {
            "title": title,
            "type": newsType,
            "link": f"https://www.ptt.cc/{link}",
            "date": date,
            "trending": trending
        }
        
        news_d[index] = newData
        

    def getPageIndex(self, data):
        target = data.find_all("a", {"class": "btn wide"})
        for i in target:
            if i.text == "‹ 上頁":
                target_id = i["href"].split("/")[-1].split(".")[0]
            
        target_id = re.sub(r"[a-zA-z]+", "", target_id)
                
        return target_id

    
    def isCurDate(self, d):
        curDate = datetime.now().strftime("%-m/%d")
        return curDate == d.strip(" ")
    
    def getTrending(self, t):
        if not re.match('[0-9]', t):
            return 0

        return int(t)
    
    def hasKeyword(self, t):
        if "RE" in t or "Re" in t:
            return False

        for k in self.keyword:
            if re.search(k, t):
                return True
        return False