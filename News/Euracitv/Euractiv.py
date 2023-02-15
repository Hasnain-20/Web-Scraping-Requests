import math
from bs4 import BeautifulSoup
import grequests
import requests
import pandas as pd

class Euractiv:

    def __init__(self, splat, url):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
            "Accept-Encoding": "*",
            "Connection": "keep-alive"
        }
        self.url = url
        self.keywords = ['Digital Market Act', 'Digital Services Act', 'GDPR', 'Data Privacy', 'Cybsersecurity', 'ePrivacy Regulation', 'Copyright Directive', 'Data Governance Act' , 'The Cybersecurity Act']
        self.keywords = [i.replace(" ","+") for i in self.keywords]

        self.platform = splat
        self.newsPlatform = []
        self.responses = []
        self.authors = []
        self.article_Title = []
        self.email = []
        self.twitter = []
        self.urls = []
        self.authorImg = []
        self.keyUsed = []
        self.authUrls = []
        self.article_Url = []
        self.authorsBio = []

    def searchKeywords(self):
        print("Searching")
        for key in self.keywords:
            print(key)
            print(url+'?s='+key)
            resp = requests.get(url+'?s='+key, headers=self.headers)
            soup = BeautifulSoup(resp.text, 'html.parser')
            links = soup.select('h3>a')
            self.responses.extend(link['href'] for link in links)
            for kk in range(len(links)):
                self.keyUsed.append(key.replace("+"," "))
            print(len(self.responses))
            items = int(soup.select_one('h4.text-center').text.split(" ")[0])
            pages = math.ceil(items/24)
            if pages > 1:
                urls = [url + f'page/{j}/?s=' for j in range(2,pages+1)]
                urls = [urll + key for urll in urls]
                reqs = (grequests.get(urrl, headers=self.headers) for urrl in urls)
                responses = grequests.map(reqs, size=20)
                for resp in responses:
                    print(resp.url)
                    soupp = BeautifulSoup(resp.text,'html.parser')
                    links = soupp.select('h3>a')
                    self.responses.extend(link['href'] for link in links)
                    for kk in range(len(links)):
                        self.keyUsed.append(key.replace("+"," "))
                print(len(self.responses))

    def parseSearchResults(self):
        print("Parcing Search Results")
        # reqs = (grequests.get(url, headers=self.headers) for url in self.responses)
        # responses = grequests.map(reqs, size=24)
        kkk = 0
        # for resp in responses:
        for i in self.responses:
            resp = requests.get(i, headers=self.headers)
            print(kkk, " : ", resp.status_code, resp.url)
            if resp.status_code == 200:    
                soup = BeautifulSoup(resp.text, 'html.parser')
                # print(resp.url)
                self.newsPlatform.append(self.platform)
                self.article_Url.append(resp.url)
                # print(soup.select_one('.ea-post-title>h1').text)
                self.article_Title.append(soup.select_one('.ea-post-title>h1').text)
                # print(soup.select_one('p>.author')['href'])
                id = soup.select('p>.author')
                if len(id)>2:
                    lis1 = []
                    lis2 = []
                    lis3 = []
                    lis4 = []
                    lis5 = []
                    lis6 = []
                    for idd in id:
                        if 'euractiv' in idd.text.lower():
                            continue
                        liss = self.parseAuthors(idd['id'])
                        lis1.append(idd.text)
                        lis2.append(liss[1])
                        lis3.append(liss[2])
                        lis4.append(liss[3])
                        lis5.append(liss[4])
                        lis6.append(idd['href'])

                    self.authors.append(lis1)
                    self.authorsBio.append(self.checker(lis2))
                    self.twitter.append(self.checker(lis3))
                    self.email.append(self.checker(lis4))
                    self.authorImg.append(self.checker(lis5))
                    self.authUrls.append(lis6)
                # print(id)
                elif len(id)==0:
                    self.authors.append("")
                    self.authorsBio.append("")
                    self.twitter.append("")
                    self.email.append("")
                    self.authorImg.append("")
                    self.authUrls.append("")
                else:
                    liss = self.parseAuthors(id[0]['id'])
                    self.authors.append(id[0].text)
                    self.authorsBio.append(liss[1])
                    self.twitter.append(liss[2])
                    self.email.append(liss[3])
                    self.authorImg.append(liss[4])
                    self.authUrls.append(id[0]['href'])
                kkk = kkk + 1
            else:
                self.keyUsed.pop(kkk)

    def checker(self, lis):
        if len(lis)==1:
            return lis[0]
        if not any(lis):
            return ""
        else:
            return lis

    def parseAuthors(self,id):
        data = {
                'action': 'author_info',
                'id': id,
            }
        author_details = requests.post('https://www.euractiv.com/wp-admin/admin-ajax.php', headers=self.headers, data=data)
        if len(author_details.text) > 50:
            soup2 = BeautifulSoup(author_details.text, 'html.parser')
            lis1 = soup2.select_one('h5.card-title').text
            # print(soup2.select_one('h5.card-title').text)
            try:
                lis2 = soup2.select_one('p.card-text').text
                # print(soup2.select_one('p.card-text').text)
            except:
                lis2 = ""
            social = soup2.select('div.social-icons>a')
            lis3 = social[1]['href']
            lis4 = social[0]['href'].split('mailto:')[-1]
            # print(social[1]['href'])
            # print(social[0]['href'].split('mailto:'))
            lis5 = soup2.select_one('.card-img')['src']
            # print(soup2.select_one('.card-img')['src'])
            # print()
        else:
            lis1 = ""
            lis2 = ""
            lis3 = ""
            lis4 = ""
            lis5 = ""
        return lis1, lis2, lis3, lis4, lis5

    def runScrapper(self):
        self.searchKeywords()
        self.parseSearchResults()
        return self.makeCSV()
    
    def makeCSV(self):
        print(len(self.article_Title))
        print(len(self.authors))
        print(len(self.twitter))
        print(len(self.email))
        print(len(self.authorImg))
        print(len(self.keyUsed))
        print(len(self.newsPlatform))
        print(len(self.article_Url))
        print(len(self.authUrls))
        print(len(self.authorsBio))
        df = pd.DataFrame({"Platform" : self.newsPlatform, "Article Title" : self.article_Title, "Article Url" : self.article_Url,
                            "Keyword" : self.keyUsed, "Authors Name": self.authors,"Authros Email" : self.email, 
                           "Authors Twitter" : self.twitter, "Authors Image" : self.authorImg, "Authors Bio" : self.authorsBio,
                           "Authors Page Url" : self.authUrls})
        df.to_csv(f'{self.platform}.csv', encoding='utf-8-sig', index=False)
        return df

if __name__ == '__main__':
    platform = 'EURACTIV'
    url = 'https://www.euractiv.com/'
    scrapper = Euractiv(platform,url)
    data = scrapper.runScrapper()