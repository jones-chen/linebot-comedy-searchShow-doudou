# 導入模組
import os
from flask import Flask, request, abort
import linebot
from linebot.exceptions import InvalidSignatureError
from linebot.models import *

# 自寫函式
from model.respond import *
from model.data import *
from model.data import *

# 1. 設定 Line Bot 參數
# (1) CHANNEL_ACCESS_TOKEN：用於驗證身份的 Line Bot 通行證
CHANNEL_ACCESS_TOKEN = '0w1WPuXcFUtupRkvlstdcnVh8a1QxgSVH7WENnttPYeOYZ/gUk9Q/bW8WwWsrrbE/rGUwxS2QWMkfsqJxk8IJUGQufo5lekJSBHABkFvn3zG1mBtlYMYCOQquSK8eaGlVBtfLH8e6Xq+62E27ejkWQdB04t89/1O/w1cDnyilFU='
# (2) Channel Secret：用於簽名驗證的 Line Bot 金鑰
CHANNEL_SECRET = '7e794f2eb21b74ab2c59c36f572905c0'
# (3) 用於發送訊息
line_bot_api = linebot.LineBotApi(CHANNEL_ACCESS_TOKEN)
# (4) 用於處理 Webhook 事件
handler = linebot.WebhookHandler(CHANNEL_SECRET)

# 2. 設定主程式
# (1) 建立 Flask 應用程式
app = Flask(__name__)
# (2) 啟動應用程式
if __name__ == "__main__":    
    port = int(os.environ.get('PORT', 5000))     
    app.run(host='0.0.0.0', port=port)

# 從自寫函式取變數(model/data.py)
city_dict = generate_city_dict()
city_with_activity = city_dict.keys() #有活動的城市清單
city_month_dict = generate_city_month_dict(city_dict) #有活動的月份清單


# 確認訪問成功
@app.route('/', methods=['POST'])
def home():
    return "Welcome to the Comedy Search Show!"

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # 簽名，handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# Line Bot 收到的訊息事件，根據訊息內容進行不同的回應。
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = '' #原訊息清空
    user_input = event.message.text #取得用戶訊息
    user_input = user_input.replace('臺', '台')  #修正
    match user_input:
        # 收到'/',而且是'地點+月份'，回傳該地點與該月份的活動清單
        case input if '/' in input and checkCityMonthFormat(input):
            city, month = input.split('/')
            if city in city_with_activity and month in city_month_dict[city]:
                message = send_city_activity(city_month_dict[city][month])
            else:
                message = TextSendMessage(text=f'唉呀，{city} 在 {month} 沒有喜劇活動喔！')
            
        # 收到'/',而且是['推薦', '隨機推薦', '隨機']，回傳該地點與該月份的活動清單
        case input if '/' in input and checkCityRecommendFormat(input):
            city, recommend = input.split('/')
            if city in city_with_activity:
                activity = random_city_recommend_activity(city_dict[city])
                message = send_recommend_activity(activity)
            else:
                message = TextSendMessage(text=f'唉呀，{city} 最近沒有喜劇活動喔！')
                
        # 收到‘有’喜劇活動的'地點'，回傳該地點的活動
        case input if input in city_with_activity:
            message = send_city_activity(city_dict[input])

        # 收到‘沒有’喜劇活動的'地點'，回傳沒有喜劇活動
        case input if input in tw_city_list:
            message = TextSendMessage(text=f'唉呀，{input} 最近沒有喜劇活動喔！')
            
        # 說到'推薦', '隨機推薦', '隨機，回傳活動
        case input if any(['推薦', '隨機推薦', '隨機'] in input) :
            activity = random_recommend_activity()
            message = send_recommend_activity(activity)
        
        # 說到'逗逗'，回傳one punch line
        case input if '逗逗' in input:
            one_liner = random_one_liner()
            text_message = send_one_liner(one_liner)
            message = TextSendMessage(text=text_message)
        
        # 其他
        case _:
            return
    
    # 回傳訊息
    line_bot_api.reply_message(event.reply_token, message)



# 處理使用者追蹤帳號的事件
@handler.add(FollowEvent)
def handle_follow(event):
    message = TextSendMessage(
        text='喵喵喵～朕想去看喜劇，姑且讓你這卑微的人類告訴我，想去哪個城市看表演吧!\n(๑ↀᆺↀ๑)✧')
    line_bot_api.reply_message(event.reply_token, message)

# 處理使用者加入群組的事件
@handler.add(JoinEvent)
def handle_join(event):
    message = TextSendMessage(
        text='喵喵喵～朕想去看喜劇，姑且讓你們這些卑微的人類告訴我，想去哪個城市看表演吧!\n(๑ↀᆺↀ๑)✧')
    line_bot_api.reply_message(event.reply_token, message)

# 回傳訊息
@handler.add(PostbackEvent)
def handle_postback(event):
    message = TextSendMessage(
        text='告訴我吧，卑微的人類～你想查詢的城市，如:[台北]，我還可以篩選月份，如:[台北/七月] <(๑ↀVↀ๑)>')
    line_bot_api.reply_message(event.reply_token, message)

