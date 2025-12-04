#!C:/Users/Deepak/AppData/Local/Programs/Python/Python311/python.exe
print("Content-Type: text/plain\r\n\r\n")

import pymysql, cgi, cgitb
cgitb.enable()

form = cgi.FieldStorage()
sender_id = form.getvalue("sender_id")
receiver_id = form.getvalue("receiver_id")
sender_type = form.getvalue("sender_type")
message_text = form.getvalue("message_text")

if not (sender_id and receiver_id and sender_type and message_text):
    print("Missing fields")
    exit()

try:
    con = pymysql.connect(host="localhost", user="root", password="", database="pet")
    cur = con.cursor()
    cur.execute("""INSERT INTO messages (sender_id, receiver_id, sender_type, message_text)
                   VALUES (%s, %s, %s, %s)""",
                (sender_id, receiver_id, sender_type, message_text))
    con.commit()
    con.close()
    print("OK")
except Exception as e:
    print(str(e))
