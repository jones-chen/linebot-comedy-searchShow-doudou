# 喜劇搜秀(Linebot Comedy Search Show) - 逗逗(Doudou)
Taiwan Comedy Linebot A chatbot on LINE (messaging app) that recommends standup comedy shows in Taiwan. Created as the final project for ccClub 2023 www.ccclub.io/.

<div align="center">
<img src="https://i.imgur.com/wf6J7ce.jpg" width="960" height="540" style="text-align: center;"/>
</div>

## 壹、功能介紹(Features)
[Project Slide](https://docs.google.com/presentation/d/1Bj_b4GeBqU_jhvex0vaPfGd4CKuCPVxwyS7NsXVndyY/edit#slide=id.g22e9cb41ed0_0_1782)
本功能使用 Flask 和 Line Bot SDK 的基本結構，用於建立一個 Line Bot。
透過建立 喜劇lineBot，讓使用者透過機器人取得近期的喜劇演出資訊。並且可以根據 地點/月份，將活動塞選出來。 



## 貳、使用說明(How to use)
(一) 加入LINE好友
* 方法一：輸入 @005czwos
* 掃描QRcode：
<img src="https://github.com/jones-chen/Linebot-comedy-doudou/blob/main/image/LineAddFriend.png?raw=true" width=144 height="144">

(二) 取得推薦活動
1. 輸入「地點」
2. 輸入「月份」
3. 輸入「地點/月份」
4. 輸入「隨機推薦」

<div style="white-space: nowrap;" align="center">
<img src="https://github.com/jones-chen/Linebot-comedy-doudou/blob/main/image/Feature-LocalMonth.gif?raw=true" width=250 display=inline>
<img src="https://github.com/jones-chen/Linebot-comedy-doudou/blob/main/image/Feature-RandomRecommond.gif?raw=true" width=250 display=inline>
</div>

(三) 看笑話
1. 輸入其他內容
<div align="center">
<img src="https://github.com/jones-chen/Linebot-comedy-doudou/blob/main/image/Feature-RandomJoke.gif?raw=true" width=250>
</div>

## 參、環境建置與需求 (prerequisites)

## 肆、安裝與執行步驟 (installation and execution)

## 伍、程式設計核心流程概念
### (一) 建立喜劇活動資料庫 - 爬蟲、例行活動
1. 執行 crawler 資料夾內的 comedy_crawler.py 爬蟲程式
2. 爬蟲程式將爬取 [活動通(Accupass)](https://www.accupass.com/)、[KKTIX](https://kktix.com/) 兩大平台的"喜劇"搜尋結果。
3. 透過 白名單(whiteList) 與 黑名單(blackList) 將爬蟲結果優化，過濾相關的喜劇活動。
4. 同時爬取建立好的 [例行性喜劇活動](https://reurl.cc/RzQ4YZ)
5. 將整理好的活動，放置 [google Sheet的 Database-Total中。](https://reurl.cc/GAlV5p)
### (二) 建立LINE BOT
1. 建立 LINE BOT 機器人 Channel
2. 使用 LINE Simulator 建立呈現模板
### (三) 建立 FLASK、上架PaaS
1. 用 Flask 撰寫 app.py ，建立Line的路由
2. 撰寫 資料庫篩選邏輯
(1) 讀取 google Sheet的 Database 
(2) 將已發生的活動排除 
(3) 撰寫隨機推薦公式

## 陸、檔案介紹
1. crawler資料夾：存放爬蟲會需要用到的程式碼。
2. requirements.txt：告訴PaaS會使用到的模組。
3. app.py：主程式，運行linebot的路由。
4. data.py：將活動篩選的判斷邏輯。
5. repond.py：活動回覆公式。
6. credentials.json：授權data.py爬取 google sheet API 的授權文件。