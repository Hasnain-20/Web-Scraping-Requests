from bs4 import BeautifulSoup
import grequests
import requests
import pandas as pd
import spacy


class PoliticoEU:

    def __init__(self, splat):
        self.headers = {
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Origin': 'https://www.politico.eu',
            'Referer': 'https://www.politico.eu/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
            'content-type': 'application/x-www-form-urlencoded',
            'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }
        self.keywords = ['Digital Market Act', 'Digital Services Act', 'GDPR', 'Data Privacy', 'Cybsersecurity', 'ePrivacy Regulation', 'Copyright Directive', 'Data Governance Act' , 'The Cybersecurity Act']
        self.keywords = [i.replace(" ","%20") for i in self.keywords]
        self.data = '{{"requests":[{{"indexName":"production_EU","params":"facets=%5B%22tagValues%22%5D&highlightPostTag=__%2Fais-highlight__&highlightPreTag=__ais-highlight__&maxValuesPerFacet=10&page={page}&query={keyword}&tagFilters="}}]}}'
        self.nlp = spacy.load('en_core_web_sm')

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
        self.nouns = []

    def searchKeywords(self):
        for key in self.keywords:
            print(key)
            for i in range(0,50):
                print(i,end=", ", flush=True)
                response = requests.post(
                    'https://a3cxkoqgf3-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(4.14.2)%3B%20Browser%20(lite)%3B%20instantsearch.js%20(4.47.0)%3B%20JS%20Helper%20(3.11.1)&x-algolia-api-key=138da0d7b154a5032735cfdcfda0e3cf&x-algolia-application-id=A3CXKOQGF3',
                    headers=self.headers,
                    data=self.data.format(page = i, keyword = key),
                ).json()
                if len(response['results'][0]['hits']) == 0:
                    print("no more")
                    break
                else:
                    for kk in range(len(response['results'][0]['hits'])):
                        self.keyUsed.append(key.replace("%20"," "))
                        self.newsPlatform.append(self.platform)
                    self.responses.append(response)
            print()

    def parseSearchResults(self):
        for resp in self.responses:
            dictt = resp['results'][0]
            for j in dictt['hits']:
                auths = j['authors']
                temp = []
                temp2 = []
                temp3 = []
                for aut in auths:
                    temp2.append(aut['url'].replace('author','staff'))
                    temp3.append(aut['url'])
                    temp.append(aut['name'])
                self.article_Url.append(j['url'])
                self.article_Title.append(j['title']['en'])
                self.urls.append(temp2)
                self.extract_Nouns(j['text']['en'].replace('&nbsp;',' '))
                if temp3:
                    if len(temp3)>1:
                        self.authors.append(temp)
                        self.authUrls.append(temp3)
                    else:
                        self.authUrls.append(temp3[0])
                        self.authors.append(temp[0])
                else:
                    self.authors.append("")
                    self.authUrls.append("")
                # print(article_Title[-1], authors[-1], urls[-1])
        print(len(self.urls))

    def extract_Nouns(self, text):
        doc = self.nlp(text)
        name = [ent.text for ent in doc.ents if ent.label_ == 'PERSON']
        # print(name)
        names = set()
        for n in name:
            names.add(n)
        self.nouns.append(names)

    def parseAuthors(self):
        kkk = 0
        for i in self.urls:
            reqs = (grequests.get(urrl, headers=self.headers) for urrl in i)
            respons = grequests.map(reqs)
            lis1 = []
            lis2 = []
            lis3 = []
            lis4 = []
            for resp in respons:
                print(kkk, " : ", resp.status_code, resp.url)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, 'html.parser')
                    try:
                        lis1.append(soup.select_one('.speaker__twitter-url')['href'])
                    except:
                        lis1.append("")
                    try:
                        lis2.append(self.decodeEmail(soup.select_one('.speaker__email>a')['href'].split("#")[-1]))
                    except:
                        lis2.append("")
                    try:
                        lis3.append(soup.select_one('.speaker__avatar>img')['src'])
                    except:
                        lis3.append("")
                    try:
                        lis4.append(soup.select_one('.speaker__intro').text.replace('\n',"").replace('\x0a',' '))
                    except:
                        lis4.append("")
                else:
                    lis1.append("")
                    lis2.append("")
                    lis3.append("")
                    lis4.append("")
            self.twitter.append(self.checker(lis1))
            self.email.append(self.checker(lis2))
            self.authorImg.append(self.checker(lis3))
            self.authorsBio.append(self.checker(lis4))
            kkk=kkk+1

    def checker(self, lis):
        if len(lis)==1:
            return lis[0]
        if not any(lis):
            return ""
        else:
            return lis

    def decodeEmail(self,fp):
        try:
            r = int(fp[:2],16)
            email = ''.join([chr(int(fp[i:i+2], 16) ^ r) for i in range(2, len(fp), 2)])
            return email
        except (ValueError):
            pass

    def runScrapper(self):
        self.searchKeywords()
        self.parseSearchResults()
        self.parseAuthors()
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
        print(len(self.nouns))
        df = pd.DataFrame({"Platform" : self.newsPlatform, "Article Title" : self.article_Title, "Article Url" : self.article_Url,
                            "Keyword" : self.keyUsed, "Authors Name": self.authors,"Authros Email" : self.email, 
                           "Authors Twitter" : self.twitter, "Authors Image" : self.authorImg, "Authors Bio" : self.authorsBio,
                           "Authors Page Url" : self.authUrls, "List of Nouns" : self.nouns})
        df.to_csv(f'{self.platform}.csv', encoding='utf-8-sig', index=False)
        return df

if __name__ == '__main__':
    platform = 'Politico'
    scrapper = PoliticoEU(platform)
    data = scrapper.runScrapper()