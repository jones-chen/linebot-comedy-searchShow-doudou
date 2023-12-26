from linebot.models import *

# 生成一張活動卡片
def send_recommend_activity(activity):
    json_file = generate_activity_json(activity['img src'], activity['theme'], activity['location'], activity['duration'], activity['link'])

    try:
        recommend_message = FlexSendMessage(
            alt_text='逗逗推薦你喜劇\no(ↀ∀ↀ*)o',
            contents=json_file
        )
    except:
        recommend_message = TextSendMessage(text='唉呀...出了點問題耶～')

    return recommend_message

# 送出多張活動卡片，最多12個張
def send_city_activity(city_activity_list):
    # 若只有一個活動，則用上面函式
    if len(city_activity_list) == 1:
        activity = city_activity_list[0]
        city_message = send_recommend_activity(activity)
        return city_message
    
    # 若超過12個活動，只取前12個
    elif len(city_activity_list) > 12:
        city_activity_list = city_activity_list[:12]

    # 將活動內容整理成訊息
    json_file = [generate_activity_json(activity['img src'], activity['theme'], activity['location'], activity['duration'], activity['link']) for activity in city_activity_list]
    flex_contents = {"type": "carousel", "contents": json_file}

    try:
        city_message = FlexSendMessage(
            alt_text='逗逗帶你看喜劇\n\(= ↀωↀ =)/',
            contents=flex_contents
        )
    except:
        city_message = TextSendMessage(text='唉呀...出了點問題耶～')

    return city_message

# 生成卡片的Json圖像參數
def generate_activity_json(pic_url, title, place, date, link):
    return {
        "type": "bubble",
        "hero": {
                "type": "image",
                "url":  pic_url,
                "size": "full",
                "aspectRatio": "20:13",
                "aspectMode": "fit",
                "backgroundColor": "#444444"
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                    {
                        "type": "text",
                        "text": title,
                        "weight": "bold",
                        "size": "lg"
                    },
                {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "lg",
                        "spacing": "sm",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "Place",
                                        "color": "#aaaaaa",
                                        "size": "sm",
                                        "flex": 1
                                    },
                                    {
                                        "type": "text",
                                        "text": place,
                                        "wrap": True,
                                        "color": "#666666",
                                        "size": "sm",
                                        "flex": 5
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "Date",
                                        "color": "#aaaaaa",
                                        "size": "sm",
                                        "flex": 1
                                    },
                                    {
                                        "type": "text",
                                        "text": date,
                                        "wrap": True,
                                        "color": "#666666",
                                        "size": "sm",
                                        "flex": 5
                                    }
                                ]
                            }
                        ]
                        }
            ]
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [
                    {
                        "type": "button",
                        "style": "link",
                        "height": "sm",
                        "action": {
                            "type": "uri",
                            "label": "點擊查看",
                            "uri": link
                        }
                    }
            ],
            "flex": 0
        }
    }

# One Line Punch文字內容
def send_one_liner(one_liner):
    name = one_liner['name'] #來源人
    sentence = one_liner['one_liner'] #句子
    fb = one_liner['fb']
    ig = one_liner['ig']
    
    text = f'「{sentence}」- {name}\nFB: {fb}\nIG: {ig}' #整合送出結果

    return text