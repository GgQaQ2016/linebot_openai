from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
import openai 

import os
import traceback



# 初始化 Flask 應用程式
app = Flask(__name__)
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')

# LINE Bot 設定
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))

# OpenAI API 初始化
openai.api_key = os.getenv('OPENAI_API_KEY')
client = openai (api_key=openai.api_key)
ASSISTANT_ID = "asst_w2rzWsGFa9tIbQtS93H2ZUgi"

# OpenAI 助理初始化對話串
sessions = {}

def init_openai_thread(user_id):
    """初始化 OpenAI 助理對話串"""
    if user_id not in sessions:
        thread = client.beta.threads.create()
        sessions[user_id] = thread.id
    return sessions[user_id]

def get_openai_response(user_id, message):
    """向 OpenAI 助理發送訊息並獲取回應"""
    thread_id = init_openai_thread(user_id)

    # 新增用戶訊息到對話串
    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=message
    )

    # 建立 Run 來獲取助理回應
    run = client.beta.threads.runs.create(thread_id=thread_id, assistant_id=ASSISTANT_ID)

    # 輪詢直到完成
    while True:
        run_status = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
        if run_status.status == "completed":
            break

    # 取得回應並格式化
    messages = client.beta.threads.messages.list(thread_id=thread_id)
    response = messages.data[-1].content
    return response

# 監聽所有來自 /callback 的 POST Request
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# 處理用戶訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    user_message = event.message.text

    try:
        # 使用 OpenAI 助理回應
        assistant_response = get_openai_response(user_id, user_message)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=assistant_response))
    except Exception as e:
        print(traceback.format_exc())
        error_message = "發生錯誤，請稍後再試！"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=error_message))

# 處理 Postback
@handler.add(PostbackEvent)
def handle_postback(event):
    print(event.postback.data)

# 歡迎訊息
@handler.add(MemberJoinedEvent)
def welcome(event):
    uid = event.joined.members[0].user_id
    gid = event.source.group_id
    profile = line_bot_api.get_group_member_profile(gid, uid)
    name = profile.display_name
    message = TextSendMessage(text=f'{name} 歡迎加入')
    line_bot_api.reply_message(event.reply_token, message)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
