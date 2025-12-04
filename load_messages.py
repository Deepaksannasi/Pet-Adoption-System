#!C:/Users/Deepak/AppData/Local/Programs/Python/Python311/python.exe
print("Content-Type: text/html\r\n\r\n")

import pymysql, cgi, cgitb
cgitb.enable()

form = cgi.FieldStorage()
user_id = form.getvalue("user_id")
shelter_id = form.getvalue("shelter_id")

con = pymysql.connect(host="localhost", user="root", password="", database="pet")
cur = con.cursor()

cur.execute("""
    SELECT sender_id, sender_type, message_text, sent_at 
    FROM messages 
    WHERE (sender_id=%s AND receiver_id=%s) OR (sender_id=%s AND receiver_id=%s)
    ORDER BY sent_at ASC
""", (user_id, shelter_id, shelter_id, user_id))

rows = cur.fetchall()
con.close()

for sender_id, sender_type, msg, sent in rows:
    if sender_type == 'user':
        print(f"<div class='d-flex justify-content-end'><div class='message sent'>{msg}</div></div>")
    else:
        print(f"<div class='d-flex justify-content-start'><div class='message received'>{msg}</div></div>")
