#!C:/Users/Deepak/AppData/Local/Programs/Python/Python311/python.exe
print("content-type:text/html \r\n\r\n")
import cgi
import cgitb
import pymysql
import os

cgitb.enable()
con = pymysql.connect(host="localhost", user="root", password="", database="pet")
cur = con.cursor()
form = cgi.FieldStorage()


print(f"""
      <form method="post">
      <input type="password" name="pass" placeholder="Enter password">
      <input type="submit" name="sub" value="Change Password">
      </form>
      """)
submit=form.getvalue("sub");
if submit!=None:
    password=form.getvalue("pass")
    q=f"""update care_resource set password='{password}' where organization_name='petss'"""
    cur.execute(q)
    con.commit()
    print("""
    <script>
    alert("password changed successfully")
    </script>
    """)
