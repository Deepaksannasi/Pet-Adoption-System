#!C:/Users/Deepak/AppData/Local/Programs/Python/Python311/python.exe
print("content-type:text/html \r\n\r\n")
import cgi
import cgitb
import pymysql
import smtplib


cgitb.enable()

form = cgi.FieldStorage()
con = pymysql.connect(host="localhost", user="root", password="", database="pet")
cur = con.cursor()

print("""
<form method="post">
<input type="text" name="empmailid" placeholder="enter your email">
<input type="password" name="password" placeholder="enter password">   
<input type="submit" name="send" value="send mail">
</form>""")

sub=form.getvalue("send")
empmailid=form.getvalue("empmailid")
password=form.getvalue("password")
if sub!=None:
    formadd='deepaknavin321@gmail.com'
    password2='awoa dsrw annu vkon'
    toadd=empmailid
    subject="""Regarding content"""
    body=f"this is your empid:{empmailid}\npassword:{password}"
    msg=f"""Subject:{subject}\n\n{body}"""
    server=smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo()
    server.starttls()
    server.login(formadd,password2)
    server.sendmail(formadd,toadd,msg)
    server.quit()
    print("""
    <script>
    alert("the mail will be sended sucessfully")
    </script>
      """)
