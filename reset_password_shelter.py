#!C:/Users/Deepak/AppData/Local/Programs/Python/Python311/python.exe
print("Content-Type: text/html\r\n\r\n")

import cgi, cgitb, pymysql, datetime

cgitb.enable()

form = cgi.FieldStorage()

# --- Database connection ---
con = pymysql.connect(host="localhost", user="root", password="", database="pet")
cur = con.cursor()

# --- Get token and password from form ---
token = form.getvalue("token")
token = token[0] if isinstance(token, list) else token

new_password = form.getvalue("Password")
new_password = new_password[0] if isinstance(new_password, list) else new_password

# --- Check if form is submitted ---
if form.getvalue("submit") and token and new_password:

    # Check if token exists and not expired (1 hour expiry)
    cur.execute("SELECT shelter_id, token_created FROM shelters WHERE reset_token=%s", (token,))
    row = cur.fetchone()

    if row:
        shelter_id, token_created = row
        if token_created is None:
            print("<script>alert('Invalid token.');window.location.href='shelter_login.py';</script>")
        else:
            # Check expiry
            token_age = datetime.datetime.now() - token_created
            if token_age.total_seconds() > 3600:  # 1 hour
                print(
                    "<script>alert('Token expired. Please request a new reset link.');window.location.href='shelter_login.py';</script>")
            else:
                # Update password and clear token
                cur.execute("UPDATE shelters SET password=%s, reset_token=NULL, token_created=NULL WHERE shelter_id=%s",
                            (new_password, shelter_id))
                con.commit()
                print(
                    "<script>alert('Password successfully updated!');window.location.href='shelter_login.py';</script>")
    else:
        print("<script>alert('Invalid token.');window.location.href='shelter_login.py';</script>")

# --- HTML Form ---
else:
    print(f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reset Password</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.7/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
    body {{ font-family: 'Segoe UI', sans-serif; background-color: #f8f9fa; }}
    .card {{ max-width: 450px; margin: 5% auto; border-radius: 15px; padding: 30px; }}
    </style>
    </head>
    <body>
    <div class="card shadow-sm">
      <h2 class="text-center text-primary mb-4">Reset Password</h2>
      <form method="post">
        <input type="hidden" name="token" value="{token}">
        <div class="mb-3">
          <label>New Password</label>
          <input type="password" class="form-control" name="Password" placeholder="Enter new password" required>
        </div>
        <div class="d-grid">
          <input type="submit" name="submit" class="btn btn-success btn-lg" value="Update Password">
        </div>
      </form>
    </div>
    </body>
    </html>
    """)

con.close()
