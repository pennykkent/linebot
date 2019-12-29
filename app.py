from flask import Flask, request, abort

import urllib.request, json
import requests
from bs4 import BeautifulSoup

import os
import sys
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

app = Flask(__name__)

ACCESS_TOKEN= os.environ['ACCESS_TOKEN']
SECRET= os.environ['CHANNEL_SECRET']

# Channel Access Token
line_bot_api = LineBotApi(ACCESS_TOKEN)
# Channel Secret
handler = WebhookHandler(CHANNEL_SECRET)

pm_site = {}

@app.route("/")
def hello_world():
    return "歡迎使用此LINE BOT"


# 監聽所有來自 /callback 的 Post Request
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
        abort(400)
    return 'OK'

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
#     _message = TextSendMessage(text='Nice to meet you!')
#     _message = TextSendMessage(text=(event.source.user_id)) #reply userid
#     line_bot_api.reply_message(event.reply_token, _message)  
    # message = TextSendMessage(text=event)
#     print(event)

    msg = event.message.text
    _low_msg = msg.lower()
    
    _token = msg.strip().split(" ")
    _low_token = _token[0].lower()
    
    # query THU courses
    if '課程' in _token[0] or '課表' in _token[0]:
        cls_list = getCls(_token[1])
        for cls in cls_list:
            _message = TextSendMessage(text=cls)	#reply course
            line_bot_api.reply_message(event.reply_token, _message)
#            line_bot_api.push_message(event.source.user_id, TextSendMessage(text='123'))
    elif '誠品' in _token[0] or '書單' in _token[0]:
        bookls = find_bookls(_token[1])
        _message = TextSendMessage(text=bookls)	#reply course
        line_bot_api.reply_message(event.reply_token, _message)
    elif '空氣' in _token[0] or 'pm2' in _low_token:
        # query PM2.5
        for _site in pm_site:
            if _site == _token[1]:
                _message = TextSendMessage(text=pm_site[_site]) #reply pm2.5 for the site
                line_bot_api.reply_message(event.reply_token, _message)
                break;
    elif '!h' in _token[0] or '!help' in _token[0]:
        _message = TextSendMessage(text="請輸入:課程, 誠品, 空氣 + <關鍵字>")
        line_bot_api.reply_message(event.reply_token, _message)
	
def find_bookls(kw):
    with open("ESLITE.json",'r') as load_f:
        load_dict = json.load(load_f)
    x = load_dict['items']
    ans = ()
    for i in x:
        #if i['title'] == "title":
        if i['title'].find(str(kw))== -1:
            pass
#             print("")
        else:
            ans= (i['title']+i['link'])
#             print (i['title'], i['link'])
    return ans

def loadPMJson():
    with urllib.request.urlopen("http://opendata2.epa.gov.tw/AQI.json") as url:
        data = json.loads(url.read().decode())
        for ele in data:
            pm_site[ele['SiteName']] = ele['PM2.5']

def eyny_movie():
    target_url = 'http://www.eyny.com/forum-205-1.html'
    print('Start parsing eynyMovie....')
    rs = requests.session()
    res = rs.get(target_url, verify=False)
    soup = BeautifulSoup(res.text, 'html.parser')
    content = ''
    for titleURL in soup.select('.bm_c tbody .xst'):
        if pattern_mega(titleURL.text):
            title = titleURL.text
            if '11379780-1-3' in titleURL['href']:
                continue
            link = 'http://www.eyny.com/' + titleURL['href']
            data = '{}\n{}\n\n'.format(title, link)
            content += data
    return content
        
            
import os
if __name__ == "__main__":
    # load PM2.5 records
    loadPMJson()
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
