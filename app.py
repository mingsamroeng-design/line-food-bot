from flask import Flask, request

from linebot.v3.webhook import WebhookHandler
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
)
from linebot.v3.exceptions import InvalidSignatureError

from config import (
    LINE_CHANNEL_ACCESS_TOKEN,
    LINE_CHANNEL_SECRET,
    PORT,
)

app = Flask(__name__)

configuration = Configuration(
    access_token=LINE_CHANNEL_ACCESS_TOKEN
)

handler = WebhookHandler(
    LINE_CHANNEL_SECRET
)


@app.route("/")
def home():
    return "Ming Food Bot is running!"


@app.route("/callback", methods=["POST"])
def callback():

    signature = request.headers.get(
        "X-Line-Signature", ""
    )

    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)

    except InvalidSignatureError:
        return "Invalid signature", 400

    except Exception as e:
        print(e)
        return "Internal Server Error", 500

    return "OK"


@handler.add(
    MessageEvent,
    message=TextMessageContent
)
def handle_message(event):

    with ApiClient(configuration) as api_client:

        line_bot_api = MessagingApi(api_client)

        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    TextMessage(
                        text=f"คุณพิมพ์ว่า: {event.message.text}"
                    )
                ],
            )
        )


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=PORT,
        debug=True,
    )