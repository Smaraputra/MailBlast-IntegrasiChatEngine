import os
import pymysql
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty
from telethon.tl.types import InputPeerUser
from telethon.errors.rpcerrorlist import PeerFloodError
import requests
import time
import csv
import urllib.request

api_id = 4416225
api_hash = 'a28a9d0459ca40fb6bbf31543cab12e3'
phone = '+6282237396688'

app = Flask(__name__)

line_bot_api = LineBotApi('7w2rRXITa3fzCg6FhWKQAmk6mXHOQITTXdL9m6PRKUubymP7WPeL0nUQN/GffloSSSCLxrERYIKn1soNHVBDustxIg04cCfihyyCsmkpcYVXMkj0G3IoGOpn9E4Gu7J7fjWhPKlCmr3pIa8gjuwMEAdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('6cbc91fde5d41d85aab40b89a1a31769')

def connect_db_broadcast():
    conn = pymysql.connect(host='remotemysql.com', user='dITUFnLCTX', password='zUP8IcUnxt', db='dITUFnLCTX')
    return conn

@app.route("/callback", methods=['POST'])
def callback():
    # Get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # Get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # Handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

def bc():
    db_broadcast = connect_db_broadcast()
    cursor_broadcast = db_broadcast.cursor()

    sql_select = "SELECT * FROM tb_outbox WHERE flag_line=1"
    cursor_broadcast.execute(sql_select)

    results = cursor_broadcast.fetchall()

    if(cursor_broadcast.rowcount==0):
        print("Tidak ada pesan/ file yang ingin dikirim.")
    else:
        print("Terdapat pesan yang ingin dikirim.")
        print("-----Broadcast Via Line-----")
        users = ["U1f54465dcd28ccdaa1b6adad58efb990", "Uaa75a27dafd2c17b5b91d4ddb524d329", "U422a78c07a6aa11f7da1f9411fcfd417"]

        for data in results:
            if data[2] == "msg":
                print("***Memulai broadcast dengan pesan = ", data[1])
                for user in users:
                    try:
                        print("- Mengirim pesan kepada :", user)
                        line_bot_api.push_message(user, TextSendMessage(text=data[1]))
                        print("- Menungu {} detik".format(4))
                        time.sleep(4)
                    except Exception as e:
                        print("Error:", e)
                        print("Menungu {} detik".format(4))
                        time.sleep(4)
            sql = "UPDATE tb_outbox SET flag_line = %s WHERE id_outbox = %s"
            val = (2, data[0])
            cursor_broadcast.execute(sql, val)
            db_broadcast.commit()

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    db_broadcast = connect_db_broadcast()
    cursor_broadcast = db_broadcast.cursor()
    PESAN = event.message.text
    if(PESAN=="!bc"):
        bc()
    else:
        balasan = "Pesan yang ingin anda broadcast = " + PESAN
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=balasan))
        sql = "INSERT INTO tb_outbox (out_msg, type, flag, flag_tele, flag_line, tgl) VALUES (%s, %s, %s, %s, %s, CURDATE())"
        val = (PESAN, "msg", 1, 1, 1)
        cursor_broadcast.execute(sql, val)
        db_broadcast.commit()

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

