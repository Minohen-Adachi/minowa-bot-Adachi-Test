import os
import random

import requests
from bs4 import BeautifulSoup
from flask import Flask, abort, request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (MessageEvent, SourceUser, TextMessage,
                            TextSendMessage, VideoMessage, VideoSendMessage)

app = Flask(__name__)

# 環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)


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


# ランダム返信用のリスト
randomResList = []

# random.txtから名言を読み込む
with open('random.txt', 'r') as f:
    # 一列ごとに読み込む
    for line in f:
        # 改行文字の削除
        stripedLine = line.rstrip()
        randomResList.append(stripedLine)

# keyと一致する入力ならvalueを出力する用の辞書
resDictionary = {
    "死ぬこと以外は": "かすり傷",
    "読書という": "荒野",
    "たった一人の": "熱狂"
}


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    # メッセージが送られてきたときの処理

    # 辞書に含まれるものは特定の言葉を返す
    for key, value in resDictionary.items():
        # keyが含まれていてvalueが含まれていないとき
        if key in event.message.text and value not in event.message.text:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=value))
            break

    # 勝算というフレーズが入っていたとき
    if '勝算' in event.message.text:
        # user名を取得
        if isinstance(event.source, SourceUser):
            profile = line_bot_api.get_profile(event.source.user_id)
            # user名
            name = profile.display_name
            # 「(user名)の勝算！」と返却する。
            reply = '{0}の勝算！'.format(name)
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=reply))

    # 2.0というフレーズが入っていたとき
    elif '2.0' in event.message.text:
        # user名を取得
        if isinstance(event.source, SourceUser):
            profile = line_bot_api.get_profile(event.source.user_id)
            # user名
            name = profile.display_name
            # 「(user名)の勝算！」と返却する。
            reply = '{0}2.0'.format(name)
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=reply))

    # 箕輪編集室の情報を返却
    elif '箕輪編集室' == event.message.text:
        r = requests.get("https://camp-fire.jp/projects/view/34264")
        soup = BeautifulSoup(r.content, "html.parser")
        # 箕輪編集室の現在のパトロン数
        numOfMember = soup.select("strong.number")[0].getText()
        # 箕輪編集室の現在の空き人数
        num = 0
        for i in soup.select("div.limited.rfloat"):
            # OUT OF STOCK でないとき
            if '残り' in i.getText():
                n = i.getText().replace('残り：', '').replace('人まで', '')
                num += int(n)
        if num == 0:
            line_bot_api.reply_message(
                event.reply_token, [
                    TextSendMessage(
                        text='箕輪編集室はこちら。'), TextSendMessage(
                        text='https://camp-fire.jp/projects/view/34264'), TextSendMessage(
                        text='現在{0}です。満員御礼！' .format(
                            numOfMember, num))])
        else:
            line_bot_api.reply_message(
                event.reply_token, [
                    TextSendMessage(
                        text='箕輪編集室はこちら。'), TextSendMessage(
                        text='https://camp-fire.jp/projects/view/34264'), TextSendMessage(
                        text='現在{0}です。{1}人空きがあります。' .format(
                            numOfMember, num))])

    # 箕輪編集室の情報を返却
    elif '箕輪大陸' == event.message.text:
        r = requests.get("https://camp-fire.jp/projects/view/83596")
        soup = BeautifulSoup(r.content, "html.parser")
        # 箕輪大陸の支援総額
        sum = soup.select("strong.number")[0].getText()
        n_str = sum.replace('円', '').replace(',', '')
        achievementRate = int(n_str) * 100 / 3000000
        achievementRate = int(achievementRate)

        line_bot_api.reply_message(
            event.reply_token, [
                TextSendMessage(
                    text='箕輪大陸はこちら。'), TextSendMessage(
                    text='https://camp-fire.jp/projects/view/83596'), TextSendMessage(
                    text='現在の支援総額は、{0}です。達成率は、{1}%です。' .format(
                        sum, achievementRate))])

    elif 'ドークショ' in event.message.text or 'ドクショ' in event.message.text or\
            'コウヤ' in event.message.text:
        messages = [
            TextSendMessage(
                text='ドークショドクショドークショ コウヤ（＾Ｏ＾）') for i in range(4)]
        messages.append(TextSendMessage(text='ドークショドクショデジッセンダ（＾Ｏ＾）'))
        line_bot_api.reply_message(
            event.reply_token,
            messages)
    # 箕輪編集室公式SNS情報を返す
    elif 'sns' == event.message.text.lower():
        line_bot_api.reply_message(
            event.reply_token, [
                TextSendMessage(
                    text='https://twitter.com/minowa_et'), TextSendMessage(
                    text='https://www.instagram.com/minohen/')])

    else:
        # 特定の単語が入っていなければリストからランダムで返信する
        reply = random.choice(randomResList)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply))


if __name__ == "__main__":
    # app.run()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
