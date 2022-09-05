from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
import requests
import time
import telebot
import asyncio
import pymysql
import json
import os
from flask import Flask, request, abort

PESAN : str

app = Flask(__name__)

def connect_db_broadcast():
    conn = pymysql.connect(host='remotemysql.com', user='dITUFnLCTX', password='zUP8IcUnxt', db='dITUFnLCTX')
    return conn

db_broadcast = connect_db_broadcast()
cursor_broadcast = db_broadcast.cursor()

def start(update, context):
    print("User memasukkan command start.")
    update.message.reply_text('Selamat datang. Silahkan ketikan pesan yang ingin anda broadcast!')
    
def help(update, context):
    print("User memasukkan command help.")
    update.message.reply_text('Ketikan pesan yang ingin anda broadcast!')

def echo(update, context):
    global PESAN
    PESAN = update.message.text
    print("-----Pesan Broadcast Baru Terdeteksi-----")
    print("User memasukkan pesan broadcast = ", PESAN)
    balas= "Pesan yang ingin anda broadcast = " + PESAN
    update.message.reply_text(balas)
    print('Menyimpan pesan broadcast kedalam database.')
    sql = "INSERT INTO tb_outbox (out_msg, type, flag, flag_tele, flag_line,tgl) VALUES (%s, %s, %s, %s, %s,CURDATE())"
    val = (PESAN, "msg", 1, 1)
    cursor_broadcast.execute(sql, val)
    db_broadcast.commit()
    print('-----Selesai-----')
    # print('Menyimpan kedalam file pesan.')
    # with open("pesan.csv","w",encoding='UTF-8') as f:
    #     writer = csv.writer(f,delimiter=",",lineterminator="\n")
    #     writer.writerow(['Pesan'])
    #     writer.writerow([PESAN])

def downloaderfile(update, context):
    global PESAN
    URL = context.bot.get_file(update.message.document)
    PESAN = update.message.caption
    nama = os.path.basename(URL.file_path)
    print("-----File Broadcast Baru Terdeteksi-----")
    print("User memasukkan file broadcast = ", PESAN)
    print("URL file = ", URL.file_path)
    print('Menyimpan file broadcast kedalam database.')
    sql = "INSERT INTO tb_outbox (out_msg, type, flag, flag_tele, flag_line, tgl, nama_file) VALUES (%s, %s, %s, %s, %s,CURDATE(), %s)"
    val = (URL.file_path, PESAN, 1, 1, 1,nama)
    cursor_broadcast.execute(sql, val)
    db_broadcast.commit()
    print('-----Selesai-----')

def bot():
    print("-----Bot Telegram Aktif!-----")
    print("Gunakan fitur chat dengan bot telegram untuk memasukkan pesan dan melakukan broadcast!")
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
    updater = Updater("1721191189:AAE84MPtxIVHVZWu4fD2b9BYGJ-jlt7-w1w", use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(MessageHandler(Filters.text, echo))
    dp.add_handler(MessageHandler(Filters.document, downloaderfile))
    updater.start_polling()
    updater.idle()
    
if __name__ == "__main__":
    bot()