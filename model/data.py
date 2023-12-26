from google.oauth2.service_account import Credentials
import gspread
import random
import datetime
from collections import defaultdict

# 1. 讀取工作表(Total、One_Liner)
# https://docs.google.com/spreadsheets/d/1HzQhihET7Brr0XrWDUrBXyOyYCRMD7g_TazBfa46kv0/edit#gid=0
# (1) 設定認證憑證
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = Credentials.from_service_account_file("model/credentials.json", scopes=scope)
client = gspread.authorize(credentials)
# (2) 開啟 Google Sheets 檔案
sheetsName = '喜劇Bot_DB'
spreadsheet = client.open(sheetsName)
# (3) 讀取表單
totalSheet = spreadsheet.worksheet('Total')
total_activity_data = totalSheet.get_all_records()
oneLinerSheet = spreadsheet.worksheet('One_liner')
one_liner_data = oneLinerSheet.get_all_records()

# 2. 建立轉換字典
month_convert_dict = {'01': '一月', '02': '二月', '03': '三月', '04': '四月', '05': '五月','06': '六月', 
                      '07': '七月', '08': '八月', '09': '九月', '10': '十月', '11': '十一月', '12': '十二月'}

tw_city_list = ['台北', '新北', '基隆', '桃園', '新竹', '苗栗', '台中', '彰化', '雲林',
                '南投', '嘉義', '台南', '高雄', '屏東', '台東', '花蓮', '宜蘭', '澎湖', '金門', '馬祖']

# 該活動是否要列入計算，回傳True, False（開始日期還沒到or結束日期還沒到)
def isActivityValid(activity, today):
    start_date = datetime.datetime.strptime(activity['startDate'], '%Y-%m-%d').date()
    end_date = datetime.datetime.strptime(activity['endDate'], '%Y-%m-%d').date() if activity['endDate'] != '-' else None
    return start_date >= today or (end_date != None and end_date >= today)

# 建立可用的活動清單
def generateValidActivity():
    today = datetime.date.today()
    valid_activity = [activity for activity in total_activity_data if isActivityValid(activity, today)]
    return valid_activity

# 建立可用的活動清單
valid_activity_list = generateValidActivity()

# 隨機回傳一個活動
def random_recommend_activity():
    activity = random.choice(valid_activity_list)
    return activity

# 隨機回傳一個該縣市的活動
def random_city_recommend_activity(activity_lst):
    activity = random.choice(activity_lst)
    return activity

# 隨機回傳一個笑話
def random_one_liner():
    one_liner = random.choice(one_liner_data)
    return one_liner

# 確認是否為 城市/月份這個格式，回傳True、False
def checkCityMonthFormat(input):
    city, month = input.split('/')
    if city in tw_city_list and month in month_convert_dict.values():
        return True
    else:
        return False

# 檢查用戶輸入的格式
def checkCityRecommendFormat(input):
    city, recommend = input.split('/')
    keywords = ['推薦', '隨機推薦', '隨機']
    if city in tw_city_list and any(keyword in recommend for keyword in keywords):
        return True
    else:
        return False

# 建立現有活動的縣市清單
def generate_city_dict():
    # city_dict = {"台北：[row1, row2]"}
    city_dict = {}

    # 取得尚未舉辦的活動清單
    for row in valid_activity_list:
        location = row['location'].replace('臺', '台') #統一中文大小寫
        if location not in city_dict.keys(): 
            city_dict[location] = [row]
        else:
            city_dict[location].append(row)
    return city_dict

# 建立該月份活動清單
def generate_city_month_dict(city_dict):
    city_month_dict = defaultdict(dict)

    for key, value in city_dict.items():
        for activity in value:
            start_month = month_convert_dict[activity['startDate'][5:7]]
            end_month = month_convert_dict[activity['endDate']
                                           [5:7]] if activity['endDate'] != '-' else None

            if end_month == None or start_month == end_month:
                if start_month not in city_month_dict[key]:
                    city_month_dict[key][start_month] = [activity]
                else:
                    city_month_dict[key][start_month].append(activity)
            elif end_month != None and start_month != end_month:
                if start_month not in city_month_dict[key]:
                    city_month_dict[key][start_month] = [activity]
                elif start_month in city_month_dict[key]:
                    city_month_dict[key][start_month].append(activity)
                elif end_month not in city_month_dict[key]:
                    city_month_dict[key][end_month] = [activity]
                elif end_month in city_month_dict[key]:
                    city_month_dict[key][end_month].append(activity)

    return city_month_dict
