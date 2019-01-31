# -*- coding:utf-8 -*-
import requests
import threading
from queue import Queue
import re
import time
from proxy_helper import Proxy_helper
from bs4 import BeautifulSoup
import pymysql
from mysqlConfig import MysqlConfig
from userAgents import userAgents


class Spider(threading.Thread):
    def __init__(self, threadName, url_queue, validip_que):
        threading.Thread.__init__(self)
        self.daemon = True
        self.mysqlConfig=MysqlConfig
        self.url_queue = url_queue
        self.validip_que = validip_que
        self.userAgents =userAgents
        self.productPageRequestCount=0
        self.count = 0

    def run(self):
        print("%s开始启动" % (self.name))
        self.connectMysql()
        self.initializeMysql()
        while not self.url_queue.empty():
            url = self.url_queue.get()
            self.getListHtml(url)
            self.url_queue.task_done()

    def connectMysql(self):
        try:
            self.mysqlClient = pymysql.connect(
                host=self.mysqlConfig.host,
                port=self.mysqlConfig.port,
                user=self.mysqlConfig.user,
                passwd=self.mysqlConfig.password,
                database=self.mysqlConfig.database,
                use_unicode=True
            )
            print("数据库连接成功")
        except Exception as e:
            print("数据库连接失败")

    def initializeMysql(self):
        with open("initialize.sql", 'r', encoding='utf-8') as fd:
            sqlStr=fd.read()
            sqlCommands = sqlStr.split(';')
            for command in sqlCommands:
                if command!="":
                    try:
                        self.mysqlClient.cursor().execute(command)
                        # print("成功执行一条sql指令")
                    except Exception as msg:
                        pass
                        # print(msg)

            print('数据库初始化成功!')

    def getListHtml(self,url,repeat_count=0):
        headers = {
            "Accept": "text/html,application/xhtml+xmmysqlClientl,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Referer": "%s" % (url),
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "%s" % (self.userAgents[self.count % 17])
        }
        validip = self.validip_que.get()
        proxy = {'http': validip}
        try:
            response = requests.get(url, proxies=proxy, headers=headers, timeout=5)
            if response.status_code == 200:
                self.validip_que.put(validip)
                response.encoding = "euc-kr"
                soup = BeautifulSoup(response.text, "lxml")
                a_list = list(set(soup.select("td b a")))
                for a in a_list:
                    arc_url = "http://cellbank.snu.ac.kr/" + a.get("href")
                    self.getArticleHtml(arc_url,url)
            else:
                repeat_count += 1
                if repeat_count < 4:
                    print("%s列表页下载失败，正在进行第%d次重新下载!" % (url, repeat_count))
                    self.getListHtml(url,headers,repeat_count)
                else:
                    print("%s列表页下载失败" % (url))
                    self.sqlInsertFailedListUrl(url)
        except BaseException as e:
            print("代理IP连接超时")
            self.validip_que.get(validip)

    def getArticleHtml(self, arc_url,list_url,repeat_count=0):
        headers={
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Host": "cellbank.snu.ac.kr",
            "Pragma": "no-cache",
            "Referer": list_url,
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "%s" % (self.userAgents[self.productPageRequestCount % 17])
        }
        validip = self.validip_que.get()
        proxy = {'http': validip}
        try:
            response = requests.get(arc_url,proxies=proxy,timeout=5)
            if response.status_code == 200:
                self.validip_que.put(validip)
                response.encoding = "euc-kr"
                soup = BeautifulSoup(response.text, 'lxml')
                KCLBNo_search = re.search(r'KCLB No[\S\s\\s\r\n]{0,}?#ffffff>[\s\r\n]{0,}([\S\s]*?)</td>', response.text, re.I)
                Name_search = re.search(r'<td bgcolor=#F0F9FF align=center>[\s\r\n]{0,}Name[\S\s\\s\r\n]{0,}?#ffffff>[\s\r\n]{0,}([\S\s]*?)</td>',response.text, re.I)
                Distributibility_search = re.search(r'Distributibility[\S\s\\s\r\n]{0,}?#ffffff>[\s\r\n]{0,}([\S\s]*?)</td>',response.text, re.I)
                CellLineSTRProfile_search = re.search(r'Cell Line STR<br>Profile[\S\s\\s\r\n]{0,}?#ffffff>[\s\r\n]{0,}([\S\s]*?)<Tumorigenecity/td>', response.text, re.I)
                Origin_search = re.search(r'Origin[\S\s\\s\r\n]{0,}?#ffffff>[\s\r\n]{0,}([\S\s]*?)</td>', response.text, re.I)
                Species_search = re.search(r'Species[\S\s\\s\r\n]{0,}?#ffffff>[\s\r\n]{0,}([\S\s]*?)</td>', response.text, re.I)
                Strain_search = re.search(r'Strain[\S\s\\s\r\n]{0,}?#ffffff>[\s\r\n]{0,}([\S\s]*?)</td>', response.text, re.I)
                VirusSusceptibilit_search = re.search(r'Virus Susceptibility[\S\s\\s\r\n]{0,}?#ffffff>[\s\r\n]{0,}([\S\s]*?)</td>', response.text, re.I)
                VirusResistance_search = re.search(r'Virus Resistance[\S\s\\s\r\n]{0,}?#ffffff>[\s\r\n]{0,}([\S\s]*?)</td>',response.text, re.I)
                Reversetranscritase_search = re.search(r'Reverse transcritase[\S\s\\s\r\n]{0,}?#ffffff>[\s\r\n]{0,}([\S\s]*?)</td>', response.text, re.I)
                Tumorigenecity_search = re.search(r'Tumorigenecity[\S\s\\s\r\n]{0,}?#ffffff>[\s\r\n]{0,}([\S\s]*?)</td>',response.text, re.I)
                Isoenzyme_search = re.search(r'Isoenzyme[\S\s\\s\r\n]{0,}?#ffffff>[\s\r\n]{0,}([\S\s]*?)</td>', response.text,re.I)
                Karyology_search = re.search(r'Karyology[\S\s\\s\r\n]{0,}?#ffffff>[\s\r\n]{0,}([\S\s]*?)</td>', response.text,re.I)
                CellularMorphology_search = re.search(r'Cellular morphology[\S\s\\s\r\n]{0,}?#ffffff>[\s\r\n]{0,}([\S\s]*?)</td>', response.text, re.I)
                Production_search = re.search(r'Production[\S\s\\s\r\n]{0,}?#ffffff>[\s\r\n]{0,}([\S\s]*?)</td>', response.text,re.I)
                Histocompatibility_search = re.search(r'Histocompatibility[\S\s\\s\r\n]{0,}?#ffffff>[\s\r\n]{0,}([\S\s]*?)</td>', response.text, re.I)
                GrowthPattern_search = re.search(r'Growth pattern[\S\s\\s\r\n]{0,}?#ffffff>[\s\r\n]{0,}([\S\s]*?)</td>',response.text, re.I)
                Histopathology_search = re.search(r'Histopathology[\S\s\\s\r\n]{0,}?#ffffff>[\s\r\n]{0,}([\S\s]*?)</td>',response.text, re.I)
                Differentiation_search = re.search(r'Histopathology[\S\s\\s\r\n]{0,}?#ffffff>[\s\r\n]{0,}([\S\s]*?)</td>',response.text, re.I)
                FreezingMedia_search = re.search(r'Freezing media[\S\s\\s\r\n]{0,}?#ffffff>[\s\r\n]{0,}([\S\s]*?)</td>',response.text, re.I)
                OriginalMedia_search = re.search(r'Original media[\S\s\\s\r\n]{0,}?#ffffff>[\s\r\n]{0,}([\S\s]*?)</td>',response.text, re.I)
                KCLBMedia_search = re.search(r'KCLB media[\S\s\\s\r\n]{0,}?#ffffff>[\s\r\n]{0,}([\S\s]*?)</td>', response.text,re.I)
                Depositor_search = re.search(r'Depositor[\S\s\\s\r\n]{0,}?#ffffff>[\s\r\n]{0,}([\S\s]*?)</td>', response.text,re.I)
                Subculture_search = re.search(r'Subculture[\S\s\\s\r\n]{0,}?#ffffff>[\s\r\n]{0,}([\S\s]*?)</td>', response.text,re.I)
                References_search = re.search(r'References[\S\s\\s\r\n]{0,}?#ffffff>[\s\r\n]{0,}([\S\s]*?)</td>', response.text,re.I)
                Note_search = re.search(r'Note[\S\s\\s\r\n]{0,}?#ffffff>[\s\r\n]{0,}([\S\s]*?)</td>', response.text, re.I)
                Hit_search = re.search(r'Hit[\S\s\\s\r\n]{0,}?#ffffff>[\s\r\n]{0,}([\S\s]*?)</td>', response.text, re.I)
                SplitRatio_search = re.search(r'Split ratio[\S\s\\s\r\n]{0,}?#ffffff>[\s\r\n]{0,}([\S\s]*?)</td>',response.text, re.I)
                MediaChange_search = re.search(r'Media change[\S\s\\s\r\n]{0,}?#ffffff>[\s\r\n]{0,}([\S\s]*?)</td>',response.text, re.I)
                KCLBNo = KCLBNo_search.group(1).replace('\r\n','').rstrip() if KCLBNo_search else ""
                Name = Name_search.group(1).replace('\r\n','').rstrip() if Name_search else ""
                Distributibility = Distributibility_search.group(1).replace('\r\n','').rstrip() if Distributibility_search else ""
                CellLineSTRProfile = CellLineSTRProfile_search.group(1).replace('\r\n','').rstrip() if CellLineSTRProfile_search else ""
                Origin = Origin_search.group(1).replace('\r\n','').rstrip() if Origin_search else ""
                Species = Species_search.group(1).replace('\r\n','').rstrip() if Species_search else ""
                Strain = Strain_search.group(1).replace('\r\n','').rstrip() if Strain_search else ""
                VirusSusceptibilit = VirusSusceptibilit_search.group(1).replace('\r\n','').rstrip() if VirusSusceptibilit_search else ""
                VirusResistance = VirusResistance_search.group(1).replace('\r\n','').rstrip() if VirusResistance_search else ""
                Reversetranscritase = Reversetranscritase_search.group(1).replace('\r\n','').rstrip() if Reversetranscritase_search else ""
                Tumorigenecity = Tumorigenecity_search.group(1).replace('\r\n','').rstrip() if Tumorigenecity_search else ""
                Isoenzyme = Isoenzyme_search.group(1).replace('\r\n','').rstrip() if Isoenzyme_search else ""
                Karyology = Karyology_search.group(1).replace('\r\n','').rstrip() if Karyology_search else ""
                CellularMorphology = CellularMorphology_search.group(1).replace('\r\n','').rstrip() if CellularMorphology_search else ""
                Production = Production_search.group(1).replace('\r\n','').rstrip() if Production_search else ""
                Histocompatibility = Histocompatibility_search.group(1).replace('\r\n','').rstrip() if Histocompatibility_search else ""
                GrowthPattern = GrowthPattern_search.group(1).replace('\r\n','').rstrip() if GrowthPattern_search else ""
                Histopathology = Histopathology_search.group(1).replace('\r\n','').rstrip() if Histopathology_search else ""
                Differentiation = Differentiation_search.group(1).replace('\r\n','').rstrip() if Differentiation_search else ""
                FreezingMedia = FreezingMedia_search.group(1).replace('\r\n','').rstrip() if FreezingMedia_search else ""
                OriginalMedia = OriginalMedia_search.group(1).replace('\r\n','').rstrip() if OriginalMedia_search else ""
                KCLBMedia = KCLBMedia_search.group(1).replace('\r\n','').rstrip() if KCLBMedia_search else ""
                Depositor = Depositor_search.group(1).replace('\r\n','').rstrip() if Depositor_search else ""
                Subculture = Subculture_search.group(1).replace('\r\n','').rstrip() if Subculture_search else ""
                References = References_search.group(1).replace('\r\n','').rstrip() if References_search else ""
                Note = Note_search.group(1).replace('\r\n','').rstrip() if Note_search else ""
                Hit = Hit_search.group(1).replace('\r\n','').rstrip() if Hit_search else ""
                SplitRatio = SplitRatio_search.group(1).replace('\r\n','').rstrip() if SplitRatio_search else ""
                MediaChange = MediaChange_search.group(1).replace('\r\n','').rstrip() if MediaChange_search else ""
                #  print("{}\nKCLBNo:{}\nName:{}\nDistributibility:{}\nCellLineSTRProfile:{} \
                # \nOrigin:{}\nSpecies:{}\nStrain:{}\nVirusSusceptibilit:{}\nVirusResistance:{} \
                # \nReversetranscritase:{}\nTumorigenecity:{}\nIsoenzyme:{}\nKaryology:{}\
                # \nCellularMorphology:{}\nProduction:{}\nHistocompatibility:{}\nGrowthPattern:{}\
                # nHistopathology:{}\nDifferentiation:{}\nFreezingMedia:{}\nOriginalMedia:{}\nKCLBMedia:{}\
                # \n Depositor:{}\nSubculture:{}\n References:{}\nNote:{}\n Hit:{}\n SplitRatio:{} \
                # \nMediaChange:{}\n".format(arc_url, KCLBNo, Name, Distributibility, CellLineSTRProfile, \
                #  Origin, Species, Strain, VirusSusceptibilit, VirusResistance, Reversetranscritase,\
                #  Tumorigenecity, Isoenzyme, Karyology, CellularMorphology,Production, Histocompatibility,\
                #  GrowthPattern, Histopathology, Differentiation,FreezingMedia, OriginalMedia,KCLBMedia, \
                #  Depositor, Subculture, References, Note, Hit,SplitRatio, MediaChange))
                self.sqlInsertProduction(tuple(dict(zip(["KCLBNo","Name","Distributibility","CellLineSTRProfile",\
                 "Origin","Species","Strain","VirusSusceptibilit","VirusResistance","Reversetranscritase",
                 "Tumorigenecity","Isoenzyme","Karyology","CellularMorphology",\
                 "Production","Histocompatibility","GrowthPattern","Histopathology",\
                 "Differentiation","FreezingMedia","OriginalMedia","KCLBMedia","Depositor",\
                  "Subculture","References","Note","Hit","SplitRatio","MediaChange"], \
                  [KCLBNo,Name,Distributibility,CellLineSTRProfile,\
                 Origin,Species,Strain,VirusSusceptibilit,VirusResistance,Reversetranscritase,
                 Tumorigenecity,Isoenzyme,Karyology,CellularMorphology,\
                 Production,Histocompatibility,GrowthPattern,Histopathology,\
                 Differentiation,FreezingMedia,OriginalMedia,KCLBMedia,Depositor,\
                 Subculture,References,Note,Hit,SplitRatio,MediaChange])).values()),arc_url)
            else:
                 repeat_count += 1
                 if repeat_count<4:
                    print("%s产品页下载失败，正在进行第%d次重新下载!"%(arc_url,repeat_count))
                    self.getArticleHtml(arc_url,list_url,repeat_count)
                 else:
                    print("%s产品页下载失败" % (arc_url))
                    self.sqlInsertFailedArcUrl(arc_url)
        except BaseException as e:
            print("代理IP连接超时")
            self.validip_que.get(validip)
        finally:
            self.productPageRequestCount+=1

    def sqlInsertProduction(self, values,url):
        global sql
        sql = """INSERT IGNORE INTO cellbank_production(KCLBNo,ProductName,Distributibility,CellLineSTRProfile,\
Origin,Species,Strain,VirusSusceptibilit,VirusResistance,Reversetranscritase,
Tumorigenecity,Isoenzyme,Karyology,CellularMorphology,\
Production,Histocompatibility,GrowthPattern,Histopathology,\
Differentiation,FreezingMedia,OriginalMedia,KCLBMedia,Depositor,\
Subculture,Reference,Note,Hit,SplitRatio,MediaChange) VALUES {}""".format(values)
        if self.mysqlClient.cursor().execute(sql):
            self.mysqlClient.commit()
            print("成功插入一条记录")
        else:
            print("数据插入失败")
            self.sqlInsertFailedArcUrl(url)

    def sqlInsertFailedArcUrl(self, url):
        global sql
        sql = """INSERT IGNORE INTO cellbank_failed_arc_url(url) VALUES ('{}')""".format(url)
        # print(sql)
        self.mysqlClient.cursor().execute(sql)
        self.mysqlClient.commit()
        print("成功处理一个列表:%s" % (url))


    def sqlInsertFailedListUrl(self, url):
        global sql
        sql = """INSERT IGNORE INTO cellbank_failed_arc_url(url) VALUES ('{}')""".format(url)
        # print(sql)
        self.mysqlClient.cursor().execute(sql)
        self.mysqlClient.commit()
        print("成功处理一个列表:%s" % (url))


    def addPoidList(self, poiId_list_string):
        global sql
        sql = """INSERT IGNORE INTO meituan_poId_list(poiId_list_string) VALUES ("{}")""".format(poiId_list_string)
        self.mysqlClient.cursor().execute(sql)
        self.mysqlClient.commit()
        print("成功添加poiId到数据库")


def main():
    # 开启多线程采集代理IP，并放置于代理IP的队列ipproxy_que里
    ip_que = Queue(1200)
    validip_que = Queue(1200)
    ipCheckoutThreadMount = 7
    ipCollectThreadMount = 2
    dataCollectThreadMount = 5
    proxy_helper = Proxy_helper(ip_que, validip_que, ipCheckoutThreadMount, ipCollectThreadMount)
    proxy_helper.run()
    time.sleep(5)
    url_list = ["http://cellbank.snu.ac.kr/english/sub/catalog.php?start=%d&page=species&CatNo=60&qry_char=a" % (
                (index - 1) * 10) for index in range(1, 63)]
    url_que = Queue(300)
    for arc_url in url_list:
        url_que.put(arc_url)

    for i in range(dataCollectThreadMount):
        worker = Spider("数据采集线程%d" % (i), url_que, validip_que)
        worker.start()
        print("数据采集线程%d开启" % (i))

    url_que.join()


if __name__ == "__main__":
    main()
