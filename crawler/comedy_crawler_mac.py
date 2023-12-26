from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import urllib.parse as up
import time, json, requests, gspread
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from oauth2client.service_account import ServiceAccountCredentials
def API2GSheet():
    # 上傳Google Sheet，設定Google Sheet的名稱和JSON檔案的路徑
    # 網址 https://docs.google.com/spreadsheets/d/1HzQhihET7Brr0XrWDUrBXyOyYCRMD7g_TazBfa46kv0/edit#gid=0
    sheet_name = '喜劇Bot_DB'
    json_file_path = 'credentials.json'

    # 連接到Google Sheets API
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(json_file_path, scope)
    client = gspread.authorize(credentials)

    # 開啟Google Sheet
    spreadsheet  = client.open(sheet_name)
    return spreadsheet 
    
def UploadGSheet(spreadsheet, df, tabName):
    # 開啟Google Sheet
    worksheet = spreadsheet.worksheet(tabName)

    # 清除Google Sheet中的所有內容
    worksheet.clear()

    # 更新Google Sheet
    worksheet.update([df.columns.values.tolist()] + df.values.tolist())

def ReadGSheet(tabName):
    # 開啟Google Sheet
    spreadsheet = API2GSheet()
    worksheet = spreadsheet.worksheet(tabName)
    listData = worksheet.get_all_records()
    return listData

def checkSystem(checkStr):   #取得喜劇元素關鍵字

    # 檢查黑名單
    with open('blackListWords.txt',"r",encoding="utf-8") as file_in:
        blackWordsList = file_in.read().split("\n")
    for blackWord in blackWordsList :
        if blackWord in checkStr :
            return False
    
    # 檢查白名單
    with open('whiteListWords.txt',"r",encoding="utf-8") as file_in:
        whiteWordsList = file_in.read().split("\n")
    for whiteWord in whiteWordsList :
        if whiteWord in checkStr :
            return True

def startSelenium():
    myOptions = Options()
    myOptions.add_argument("--start-maximized")  # 最大化窗口
    myOptions.chrome_executable_path = 'ChromeDriverManager().install()'
    browser = webdriver.Chrome(options= myOptions) #執行selenium瀏覽器
    return browser


    # # 設置 Chrome WebDriver 的路徑
    # ChromeDriverPath = Service('path_to_chromedriver')

    # # 設置 Chrome WebDriver 的選項
    # myOptions = Options()
    # # myOptions.add_argument('--headless')  # 在背景執行 Chrome，不顯示視窗

    # # 創建 Chrome WebDriver
    # browser  = webdriver.Chrome(service=ChromeDriverPath, options=myOptions)
    # return browser

def accupassCrawler():
    # 啟動Selenium
    browser = startSelenium()

    # 進入網頁
    keyword = '喜劇' #stand up comedy
    kw_URLcode=up.quote_plus(keyword)
    url = f'https://www.accupass.com/search?q={kw_URLcode}'
    browser.get(url)
    #等待載入
    time.sleep(3)

    #瀑布流，載入活動卡資料
    for times in range(10): #小資料測試區 2 or 30
        browser.execute_script(f'window.scrollTo(0, 800*{times})')   #代表Javascripe 的語言
        time.sleep(0.5)

    #取得活動卡列表
    card_class = 'Events-cf521f18-grid-item'
    card_list = browser.find_elements(By.CLASS_NAME,card_class)
    # print(f'card_list: {card_list}')

    #從活動卡，逐一取得資料
    outputDictionary = []
    filterDic = []
    for card_count in range(len(card_list)) :
        try:
            #theme
            theme_xpath = f'//*[@id="content"]/div/div[1]/main/section/div/div[{card_count+1}]/div/div/div/div/div/div[1]/a/p'
            theme = browser.find_element(By.XPATH,theme_xpath).get_attribute("textContent")
            
            #location
            location_xpath = f'//*[@id="content"]/div/div[1]/main/section/div/div[{card_count+1}]/div/div/div/div/div/div[2]/a/span'
            location = browser.find_element(By.XPATH,location_xpath).get_attribute("textContent")[0:2]
            # print(location)
            
            #time
            time_xpath = f'//*[@id="content"]/div/div[1]/main/section/div/div[{card_count+1}]/div/div/div/div/div/div[1]/p'
            duration = browser.find_element(By.XPATH,time_xpath).get_attribute("textContent")
            #種類一：2023.07.01 (六) 15:00 - 07.15 (六) 16:10
            #種類二：2023.07.02 (日) 14:00 -  15:30
            startDate = duration.split('-')[0].split(' ')[0].replace('.','-')
            showYear = startDate.split('-')[0]
            startTime = duration.split('-')[0].split(' ')[2]
            
            #有些有日期、有些沒日期
            EndDuration = duration.split('-')[1]
            if '(' in EndDuration or ')' in EndDuration :#有日期
                endDate = EndDuration.split(' ')[1].replace('.','-') #08-19
                if len(endDate.split('-')) == 2 :
                    endDate = f'{showYear}-{endDate}'
            else: #沒日期
                endDate = startDate
            endTime = EndDuration.split(' ')[-1]
            # print(duration,startDate,startTime, endDate, endTime)
            
            #img
            img_xpath = f'//*[@id="content"]/div/div[1]/main/section/div/div[{card_count+1}]/div/div/div/div/a/div/img'
            imgSrc = str(browser.find_element(By.XPATH,img_xpath).get_attribute("data-src"))
            # print(imgSrc)

            #link
            link_xpath = f'//*[@id="content"]/div/div[1]/main/section/div/div[{card_count+1}]/div/div/div/div/div/div[1]/a'
            link = browser.find_element(By.XPATH,link_xpath).get_attribute('href') 
            # print(link)
            
            #跨頁爬蟲
            idNumber = link.split('/')[4]
            subUrl = f'https://api.accupass.com/v3/events/{idNumber}'
            response = requests.get(subUrl)
            response.encoding = 'utf-8'
            responseDic = json.loads(response.text)  # 先轉”字串”,在變json
            # print(f'responseDic:\n{responseDic}')
            
            # 取得主辦人
            organizerTitle = responseDic['organizer']['title'].lower()
            # print(organizerTitle)
            
            # 取得Hashtags
            tags = responseDic['tags']
            tagNames = []
            for tag in tags :
                tagName = tag['name'].lower()
                tagNames = tagNames + [tagName]
            # print(tagNames)
            
            #確認是否為喜劇元素(標題、主辦單位、tag)
            checkStr = theme.lower() + organizerTitle + str(tagNames)
            if checkSystem(checkStr) : 
                #符合喜劇元素
                print(f'Accupass - {theme}')
                #建立Csv列表  
                outputDictionary.append({'theme': theme,
                'location':location,
                'duration':duration,
                'startDate':startDate,
                'startTime':startTime,
                'endDate':endDate,
                'endTime':endTime,
                'img src' :imgSrc,
                'link':link,
                'organizer':organizerTitle,
                'tags':str(tagNames)})
            else:
                #不符合喜劇元素  
                print(f'不符合 - Accupass - {theme}')
                filterDic.append({'theme': theme,
                'location':location,
                'duration':duration,
                'startDate':startDate,
                'startTime':startTime,
                'endDate':endDate,
                'endTime':endTime,
                'img src' :imgSrc,
                'link':link,
                'organizer':organizerTitle,
                'tags':str(tagNames)})
                
        except Exception:
            # print('進入fall')
            break
        
    df_output = pd.DataFrame(outputDictionary)
    print(df_output)
    df_output = df_output.sort_values(by=['startDate'],ascending=[True]) 
    # print(df_output)
    
    return df_output, filterDic

def KktixCrawler_host():
    # Parse the RSS feed
    feed_url = "https://comedyclub.kktix.cc/events.atom?locale=zh-TW"
    feed = feedparser.parse(feed_url)

    # Prepare CSV file
    csv_filename = "comedy_events.csv"
    outputDictionary = []
    csv_header = ["theme", "location", "date", "time", "img src", "link", "organizer", "tags"]
    csv_rows = []

    # Get current date
    current_date = datetime.now().date()

    # Extract event information
    for entry in feed.entries:
        theme = entry.title

        # Extract location
        location_data = entry.content[0]
        location_value = location_data["value"]
        location_parts = location_value.split(" / ")
        location = location_parts[-1][:2] if len(location_parts) > 1 else ""

        date = entry.published.split("T")[0]
        time_parts = location_value.split("：")
        time = time_parts[1].split("(+0800)")[0]

        link = entry.link

        # Check if the event date is on or after the current date
        event_date = datetime.strptime(date, "%Y-%m-%d").date()
        if event_date >= current_date:

            # Get the img src
            response = requests.get(link)
            soup = BeautifulSoup(response.content, "html.parser")
            img_div = soup.find("div", class_="og-banner")
            img_src = img_div.img["src"] if img_div and img_div.img else ""

            organizer = entry.author
            if isinstance(entry.author, dict) and "name" in entry.author:
                organizer = entry.author["name"]

            tags = []
            if "tags" in entry:
                if isinstance(entry.tags, list):
                    tags = [tag.term for tag in entry.tags]

            # Append the event information to CSV rows
            csv_rows.append([theme, location, date, time, img_src, link, organizer, tags])
            
            outputDictionary.append({'theme': theme,
            'location':location,
            'duration':'-',
            'startDate':date,
            'startTime':time,
            'endDate':'-',
            'endTime':'-',
            'img src' :img_src,
            'link':link,
            'organizer':organizer,
            'tags':str(tags)})

    # Write the event information to CSV file
    with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(csv_header)
        writer.writerows(csv_rows)

    print(f"Scraping completed. The data has been saved to '{csv_filename}'.")

def KktixCrawler_search():
    outputDictionary = []
    filterDic = [] 
    allSellEvents = [] #從page1 ~ page100 的活動
    # 指定目標網址
    urlCode = '%E5%96%9C%E5%8A%87'
    for page in range(1,30) : #小資料測試區 2 or 30
        url = f"https://kktix.com/events?page={page}&search={urlCode}"  # 替換成你要爬取的網址
        print(f'KKTIX-第{page}頁')
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        # 當下頁面的所有活動元素
        viewEvents = soup.find_all("li", class_="type-view") #檢視活動(多場活動)
        sellEvents = soup.find_all("li", class_="type-selling") #開賣中
        allSellEvents = allSellEvents + sellEvents
        events = viewEvents + sellEvents
        if len(events) == 0 :
            break
    
    # 逐一處理每個活動元素
    for event in allSellEvents:
        # 標題
        theme = event.find("h2").text.strip()
        # 圖片
        imgSrc = event.find("img")['src']
        # 連結
        link = event.find("a")['href']
        
        # 跨頁爬蟲
        response = requests.get(link)
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 時間
        duration = ''
        try:
            info = soup.find("div",class_='event-info')     
            timezones = info.find_all("span",class_='timezoneSuffix')
        except Exception: #有可能再section裡面
            info = soup.find("section",class_='event-info')
            timezones = info.find_all("span",class_='timezoneSuffix')
            
        n=0
        for timezone in timezones:
            duration = duration + ' - '*n + timezone.text.strip()
            n=1
        startDate = duration.split('(')[0].replace('/','-')
        startTime = duration.split(') ')[1].split('(')[0]
        duration = duration.replace('(+0800)','').replace('/','.').replace('周','')
        
        # 地點
        locationElement = info.find("i",class_='fa fa-map-marker')
        location_all  = locationElement.next_sibling.text.strip()
        location  = location_all.split('/ ')[1][0:2]
        
        # 主辦單位
        organizerElement = info.find("i",class_='fa fa-sitemap')
        organizer  = organizerElement.next_sibling.text.strip()
        
        #確認是否為喜劇元素(標題、主辦單位、tag)
        checkStr = theme.lower() + organizer 
        if checkSystem(checkStr) :
            print(f'KKTIX - {theme}')
            #符合喜劇元素，建立Csv列表  
            outputDictionary.append({'theme': theme,
            'location':location,
            'duration':duration,
            'startDate':startDate,
            'startTime':startTime,
            'endDate':'-',
            'endTime':'-',
            'img src' :imgSrc,
            'link':link,
            'organizer':organizer,
            'tags':'-'})
        else:
            #不符合喜劇元素  
            print(f'不符合 - KKTIX - {theme}')
            filterDic.append({'theme': theme,
            'location':location,
            'duration':duration,
            'startDate':startDate,
            'startTime':startTime,
            'endDate':'-',
            'endTime':'-',
            'img src' :imgSrc,
            'link':link,
            'organizer':organizer,
            'tags':'-'})
   
    df_output = pd.DataFrame(outputDictionary)
    df_output = df_output.sort_values(by=['startDate'],ascending=[True]) 
    # print(df_output)
    
    return df_output, filterDic

        
# 零、連接到G-SheetAPI
spreadsheet = API2GSheet()
# 一、取得活動清單
# (1-1)Accupass活動資料庫
print("1. 進行爬蟲...")
df_accupass, filterDic_Accupass = accupassCrawler() 
UploadGSheet(spreadsheet, df_accupass,'Accupass(updating)') #更新到線上
df_accupass.to_csv(f'output/accupass_output.csv',encoding="utf_8_sig", index=False) #線下存檔
print("(1-1) Accupass活動資料庫 已成功更新到 線上/線下資料夾！")

# (1-2)KKTIX活動資料庫
df_KKTIX, filterDic_KKTIX = KktixCrawler_search()
UploadGSheet(spreadsheet, df_KKTIX,'KKTIX(updating)') #更新到線上
df_KKTIX.to_csv(f'output/KKTIX_output.csv',encoding="utf_8_sig", index=False) #線下存檔
print("(1-2) KKTIX活動資料庫 已成功更新到 線上/線下資料夾！")

# (1-3)G-sheet例行活動 
#人力更新網址：https://docs.google.com/spreadsheets/d/1HzQhihET7Brr0XrWDUrBXyOyYCRMD7g_TazBfa46kv0/edit#gid=1645301951
# df_routing = pd.DataFrame(ReadGSheet('Routing(manual maintain)'))
# print(df_routing)
# print("(1-3) 已取得例行活動！")

# # # 二、組合，並上傳至 G-Sheet
df_accupass = pd.DataFrame(ReadGSheet('Accupass(updating)'))
df_KKTIX = pd.DataFrame(ReadGSheet('KKTIX(updating)'))
df_routing = pd.DataFrame(ReadGSheet('Routing(manual maintain)'))

print("2. 進行組合...")
print("(2-1) Total 組合...")
df_Total = pd.concat([df_accupass, df_KKTIX, df_routing], ignore_index=True)
df_Total = df_Total.sort_values(by=['startDate'],ascending=[True]) 
df_Total.to_csv(f'output/Total_output.csv',encoding="utf_8_sig", index=False) #線下存檔
UploadGSheet(spreadsheet, df_Total,'Total') #更新到線上
print(df_Total)

print("(2-2) Filter 組合...")
filterDic_Accupass = pd.DataFrame.from_dict(filterDic_Accupass)
filterDic_KKTIX = pd.DataFrame.from_dict(filterDic_KKTIX)
df_filter = pd.concat([filterDic_Accupass, filterDic_KKTIX], ignore_index=True)
print(f'df_filter:{df_filter}')

if df_filter.empty:
    df_filter = pd.DataFrame({'theme': '','location':'','duration':'','startDate':'','startTime':'','endDate':'','endTime':'','img src' :'','link':'','organizer':'','tags':''}, index=[0])
df_filter = df_filter.sort_values(by=['startDate'], ascending=[True])
df_filter.to_csv(f'output/Filter_output.csv',encoding="utf_8_sig", index=False) #線下存檔
UploadGSheet(spreadsheet, df_filter,'Filter') #更新到線上
print(df_filter)

print("3. 完成 - 所有活動資料庫 已成功更新到 線上/線下資料夾！")