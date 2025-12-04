#!C:/Users/Deepak/AppData/Local/Programs/Python/Python311/python.exe
print("Content-Type: text/html\r\n\r\n")
import os

# Optional: Clear session or cookies here if you have login tracking
# Example for cookie (if using):
# print("Set-Cookie: admin_logged_in=; expires=Thu, 01 Jan 1970 00:00:00 GMT\r\n")

# Redirect to login page
print('<script>window.location.href="admin_login.py";</script>')
