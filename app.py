
from flask import Flask, request, abort
import json
from modules.config_manager import config

from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
    FlexMessage,
    FlexContainer
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)

app = Flask(__name__)

configuration = Configuration(access_token=config.linebot_access_token)
handler = WebhookHandler(config.linebot_access_secret)

def get_carousel_template(results):
    contents = []
    for result in results.values():
        content_bubble = get_bubble_item(result)
        contents.append(content_bubble)
    
    return {
        "type": "carousel",
        "contents": contents
    }

def get_rate_contents(rate):
    if isinstance(rate, str):
        rate = round(float(rate), 1)
    
    rate_list = []
    
    for idx in range(1, 6):
        url = "https://developers-resource.landpress.line.me/fx/img/"
        url = url + "review_gold_star_28.png" if idx <= rate else url + "review_gray_star_28.png"
        rate_list.append({
            "type": "icon",
            "size": "sm",
            "url": url
        })
    
    rate_list.append({
            "type": "text",
            "text": f"{rate}",
            "size": "sm",
            "color": "#999999",
            "margin": "md",
            "flex": 0
    })
    
    return rate_list
    

def get_bubble_item(cource_data):
    relative = cource_data['relative']
    if isinstance(relative, str):
        relative = round(float(relative), 1)
    
    return {
        "type": "bubble",
        "hero": {
            "type": "image",
            "url": cource_data.get('image', "https://developers-resource.landpress.line.me/fx/img/01_1_cafe.png"),
            "size": "full",
            "size": "full",
            "aspectRatio": "20:13",
            "aspectMode": "cover",
            "action": {
                "type": "uri",
                "uri": cource_data['link']
            }
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": cource_data['cource'],
                    "weight": "bold",
                    "size": "md"
                },
                {
                    "type": "box",
                    "layout": "baseline",
                    "margin": "md",
                    "contents": get_rate_contents(cource_data['rate'])
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
                                    "text": "相似距離",
                                    "color": "#AAAAAA",
                                    "size": "xs",
                                    "flex": 2
                                },
                                {
                                    "type": "text",
                                    "text": f"{relative}",
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
                                    "text": "分類",
                                    "color": "#AAAAAA",
                                    "size": "sm",
                                    "flex": 1
                                },
                                {
                                    "type": "text",
                                    "text": cource_data['category'],
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
                                    "text": "老師",
                                    "color": "#AAAAAA",
                                    "size": "sm",
                                    "flex": 1
                                },
                                {
                                    "type": "text",
                                    "text": cource_data['teacher'],
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
                                    "text": "總時長",
                                    "color": "#AAAAAA",
                                    "size": "sm",
                                    "flex": 1
                                },
                                {
                                    "type": "text",
                                    "text": cource_data['duration'],
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
                                    "text": "價格",
                                    "color": "#aaaaaa",
                                    "size": "sm",
                                    "flex": 1
                                },
                                {
                                    "type": "text",
                                    "text": f"$ {cource_data['price']}",
                                    "wrap": True,
                                    "color": "#FFDD00",
                                    "size": "sm",
                                    "flex": 5,
                                    "weight": "bold"
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
                    "label": "COURCE",
                    "uri": cource_data['link']
                    }
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [],
                    "margin": "sm"
                }
            ],
            "flex": 0
        }
    }

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        
        text = event.message.text.strip()
        
        #* 根據回覆內容作條件判斷
        if text == "功能":
            reply_text = "請輸入你遇到的困難，我可以幫你做課程推薦，提問格式如下:\n請推薦 __你的問題__"
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=reply_text)]
                )
            )
        
        elif text.startswith("請推薦") or text.startswith("Please recommand"):
            question = text.split("請推薦")[-1].strip() or text.split("Please recommand")[-1].strip()
            reply_text = f"你輸入的問題是: {question}"
            
            result_dict = config.recommendation(question)
            carousel_json = get_carousel_template(result_dict)
            carousel_str = json.dumps(carousel_json)
            
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[FlexMessage(alt_text="推薦課程",
                                          contents=FlexContainer.from_json(carousel_str))]
                )
            )
            
        else:
            reply_text = "輸入格式不符，格式如下\n請推薦 __你的問題__"
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=reply_text)]
                )
            )
            

if __name__ == "__main__":
    app.run()