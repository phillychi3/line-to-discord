from discord_webhook import DiscordWebhook
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from flask import Flask, request, abort
import logging
from linebot.models import *
import json
import os

FORMAT = '[SYNC] %(asctime)s %(levelname)s: %(message)s'
logger = logging.getLogger('sync')
logger.setLevel(logging.INFO)

handler = logging.FileHandler('sync.log', encoding='utf-8')
handler.setFormatter(logging.Formatter(FORMAT))
logger.addHandler(handler)

hdr = logging.StreamHandler()
hdr.setFormatter(logging.Formatter(FORMAT))
logger.addHandler(hdr)


app = Flask(__name__)

if not os.path.isfile('set.json'):
    set = {"access": "access_token", "secret": "secret_key"}
    with open('set.json', 'w') as f:
        json.dump(set, f)
    exit()


with open('set.json', 'r') as f:
    set = json.load(f)

linebotapi = LineBotApi(set["access"])
handler = WebhookHandler(set["secret"])




@app.route("/callback", methods=['POST'])
def callback():
    sing = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, sing)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text
    logger.info(f'Line: {msg}')
    webhook = DiscordWebhook(set['webhook'],username="Line",content=msg)
    webhook.execute()

if __name__ == '__main__':
    app.run()
