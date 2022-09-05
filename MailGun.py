import requests
import csv
import pymysql
import os
import urllib.request

def connect_db_broadcast():
    conn = pymysql.connect(host='remotemysql.com', user='dITUFnLCTX', password='zUP8IcUnxt', db='dITUFnLCTX')
    return conn

def blastMsg(pesan, email):
    requests.post(
        "https://api.mailgun.net/v3/sykescp.xyz/messages",
        auth=("api", "9b3a8f0e2f1bb1c0df1b405bc99cb851-4b1aa784-b0397ba9"),
        data = {
            "from": "Smara <smara@sykescp.xyz>",
            "to":email,
            "subject":"Pesan Tanpa File Attachment",
            "text": pesan
            })

def blastFile(link, nama, email):
    urllib.request.urlretrieve(link, nama)
    requests.post(
        "https://api.mailgun.net/v3/sykescp.xyz/messages",
        auth=("api", "9b3a8f0e2f1bb1c0df1b405bc99cb851-4b1aa784-b0397ba9"),
        files=[("attachment", (nama, open(nama,"rb").read()))],
        data = {
            "from": "Smara <smara@sykescp.xyz>",
            "to":email,
            "subject":"Pesan dengan File Attachment",
            "text": "Ini email dengan attachment",
            })
    os.remove(nama)

while(1):
    db_broadcast = connect_db_broadcast()
    cursor_broadcast = db_broadcast.cursor()

    sql_select = "SELECT * FROM tb_outbox WHERE flag=1"
    cursor_broadcast.execute(sql_select)
    
    results = cursor_broadcast.fetchall()

    if(cursor_broadcast.rowcount==0):
        print("Tidak ada pesan/ file yang ingin dikirim.")
    else:
        print("Terdapat pesan yang ingin dikirim.")
        emails = []
        with open(r"listemail.csv", encoding='UTF-8') as f:
            rows = csv.reader(f)
            next(rows, None)
            for row in rows:
                email = {}
                email = row[0]
                emails.append(email)

        for data in results:
            if(data[2]=="msg"):
                print("-----PESAN TANPA ATTACHMENT-----")
                print("Mengirim pesan dengan ID = ", data[0])
                print("Isi pesan = ", data[1])
                for email in emails:
                    print("Mengirim pesan kepada email = ", email)
                    blastMsg(data[1], email)

            else:
                print("-----PESAN DENGAN ATTACHMENT-----")
                print("Mengirim pesan dengan ID = ", data[0])
                print("URL attachment = ", data[1])
                print("Nama file = ", data[7])
                for email in emails:
                    print("Mengirim pesan kepada email = ", email)
                    blastFile(data[1], data[7], email)
            
            sql = "UPDATE tb_outbox SET flag = %s WHERE id_outbox = %s"
            val = (2, data[0])
            cursor_broadcast.execute(sql, val)
            db_broadcast.commit()