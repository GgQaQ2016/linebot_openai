from flask import Flask, request, abort, jsonify, session
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
import openai
import os
import traceback
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 初始化 Flask 應用程式
app = Flask(__name__)
app.secret_key = os.urandom(24)  # 用於 session 管理
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')

# LINE Bot 設定
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))

# OpenAI API 設定
openai.api_key = os.getenv("OPENAI_API_KEY")

# 助理 ID（請替換為您創建的助理 ID）
ASSISTANT_ID = "asst_w2rzWsGFa9tIbQtS93H2ZUgi"

def initialize_thread():
    """初始化對話串並存儲於 session"""
    if "thread_id" not in session:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."}
            ]
        )
        session["thread_id"] = response["id"]


def GPT_response_with_context(user_message):
    """使用 OpenAI 助理生成回應，並保留上下文"""
    try:
        initialize_thread()
        thread_id = session["thread_id"]

        # 將用戶訊息加入對話串
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": user_message}
            ],
            temperature=0.5,
            max_tokens=500,
            thread_id=thread_id
        )

        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"OpenAI API Error: {e}")
        return "抱歉，我無法處理您的請求，請稍後再試。"

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
    user_message = event.message.text
    try:
        # 使用 OpenAI 助理回應，並保留上下文
        assistant_response = GPT_response_with_context(user_message)
        echo = {"type": "text", "text": assistant_response or "抱歉，我沒有話可說了。"}

        # 回傳訊息給使用者
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=echo["text"]))
    except Exception as e:
        print(f"Error: {e}")
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="發生錯誤，請稍後再試。"))

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
