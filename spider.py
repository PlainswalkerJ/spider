import urllib.request
import urllib.error
import re
import time
import random
from lxml import etree
import bs4
from selenium import webdriver
import openpyxl
import string
#在py3.6中，urllib2被拆分。
#目的:爬取wcl网页，获得萨格拉斯之墓史诗难度（M）下各个boss全球前100名承担输出任务的玩家的表现情况。并制成excel表格用于进一步数据处理。
#完成度：通过职业专精、boss名称穷举给出对应专精在各个boss下（史诗难度，可以改动写入英雄、普通难度）wcl的url，通过selenium和phantomjs联合使用，可以爬取包含有效信息的HTLM文件。
#可以根据网页文件解析出选择的天赋和装备，通过正则表达式筛选出橙装（如有需要，所有装备和天赋都可以进行筛选，只筛选橙装是为了减少工作量）得到装备名称的字符串对象。

def url_get(url):
    #测试通过。
    print("########################")
    print("Spider operational!")
    #my_headers=\
       # [{'User_Agent':'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0 '},{'User_Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko'}]
    #request=urllib.request.Request(url,headers=my_headers[random.randint(0,1)])
    #content=urllib.request.urlopen(request).read()
    #对于JS渲染的网页，以上方法爬取不能。
    driver = webdriver.PhantomJS("C:/phantomjs/bin/phantomjs.exe")
    driver.get(url)
    time.sleep(10)
    content = driver.page_source.encode('utf-8')
    time.sleep(10)
    print('Just finished!')
    return content

def save_data(data,filename):
    print('save %s.'%filename)
    with open(filename,'wb') as f:
        f.write(data)
    print('Data has been stored!')
    print("########################")
    #wb打开以二进制文件形式写入，若使用‘w’会报错。

def do_spider(url):
    html=url_get(url)
    xml = etree.HTML(html)
    class_specs=url[70:].split('&')
    bossname=xml.xpath('//*[@id="filter-boss-text"]')
    difficultyoption=xml.xpath('//*[@id="filter-difficulty-text"]')
    classes=xml.xpath('//*[@id="class-'+class_specs[0]+'"]')
    specs=xml.xpath('//*[@id="class-'+class_specs[0]+'-spec-'+class_specs[1][5:]+'"]')
    spec=specs[0].xpath('string(.)')
    boss_name=bossname[0].xpath('string(.)')
    difficulty=difficultyoption[0].xpath('string(.)')
    clas=classes[0].xpath('string(.)')
    filename=boss_name+'_'+difficulty+'_'+spec+'_'+clas+'.html'
    #################################################################
    wb = openpyxl.Workbook()
    ws=wb.active
    ws['A1'] = '玩家ID'
    ws['B1'] = 'DPS'
    ws['C1'] = '橙装1'
    ws['D1'] = '橙装2'
    for players in range(1,101):
     try:
        index=players
        idpath='//*[@id="row-'+url[46:50]+'-'+str(index)+'"]/td[2]/div/div[1]/a[2]'
        playerID = xml.xpath(idpath)
        #ID=str(playerID[0])
        ID=playerID[0].xpath('string(.)')
        dpspath='//*[@id="row-'+url[46:50]+'-'+str(index)+'"]/td[4]'
        playerDPS=xml.xpath(dpspath)
        DPS=playerDPS[0].xpath('string(.)')
        #DPS=str(playerDPS)

        playerGear=xml.xpath('//*[@id="row-'+url[46:50]+'-'+str(players)+'"]/script[2]/text()')
        #print(ID)
        ws['A'+str(players+1)]=str(ID)
        ws['B' + str(players + 1)] = str(re.findall('(?<=\t).+(?=\t)',DPS)[0])
        #print(DPS)
        #print(re.findall('(?<=\t).+(?=\t)',DPS))
        #print(str(playerGear[0]))
        gears=str(playerGear[0])
        GEAR=gears.split(';')
        count=0
        for line in range(0, len(GEAR)):
            #print(GEAR[line])
            #print(type(GEAR[line]))
            if re.findall(r'(?<=name: ").+?(?=", quality: "legendary")',GEAR[line]) != [] and count==0 :
                ws['C' + str(players + 1)] = str(re.findall(r'(?<=name: ").+?(?=", quality: "legendary")',GEAR[line])[0])
                count=1
            elif re.findall(r'(?<=name: ").+?(?=", quality: "legendary")',GEAR[line]) != [] and count==1 :
                ws['D' + str(players + 1)] = str(re.findall(r'(?<=name: ").+?(?=", quality: "legendary")', GEAR[line])[0])
                count=0
     except:
         players=players-1
         continue

    wb.save(boss_name+'_'+difficulty+'_'+spec+'_'+clas+'.xlsx')
    print('Workbook complete!')

              #print(str(re.findall(r'(?<=name: ").+?(?=", quality: "legendary")',GEAR[line])))






    #################################################################
    save_data(html,filename)

if __name__ == '__main__':
    classes=['DeathKnight','DemonHunter','Druid','Hunter','Mage','Monk','Paladin','Priest','Rogue','Shaman','Warlock','Warrior']
    spec=[['Frost','Unholy'],['Havoc'],['Balance','Feral'],['BeastMastery','Marksmanship','Survival']
         ,['Arcane','Fire','Frost'],['Windwalker'],['Retribution'],['Shadow'],['Assassination','Outlaw','Subtlety']
          ,['Elemental','Enhancement'],['Affliction','Demonology','Destruction'],['Arms','Fury']]
    boss=['2032','2048','2036','2037','2050','2054','2052','2038','2051']
    t=0
    for i in range(0,9):
         for k in range(0,12):
            for j in range(0,len(spec[k])):
                url = 'https://www.warcraftlogs.com/rankings/13#boss=' + boss[i] + '&difficulty=' + '5' + '&class=' + classes[k] + '&spec=' + spec[k][j]
                #try:
                do_spider(url)
                #except:
                 #do_spider(url)

                time.sleep(5)






