#!C:/Users/Deepak/AppData/Local/Programs/Python/Python311/python.exe
print("Content-Type: text/html\r\n\r\n")

import cgi, cgitb, pymysql, random, string, smtplib, ssl, datetime
from email.message import EmailMessage

cgitb.enable()
form = cgi.FieldStorage()

# --- Database connection ---
con = pymysql.connect(host="localhost", user="root", password="", database="pet")
cur = con.cursor()

# --- Helper: generate token ---
def generate_token(length=50):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# --- Helper: send email ---
def send_email(to_email, subject, body):
    sender_email = "deepaknavin321@gmail.com"          # your Gmail
    sender_password = "uwoz tzql phkx hjho"  # Gmail App Password

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = to_email
    msg.set_content(body)

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"<script>alert('Email sending failed: {str(e)}');</script>")
        return False

# --- LOGIN ---
if form.getvalue("login"):
    email = form.getvalue("Email").strip()
    password = form.getvalue("Password").strip()
    cur.execute("SELECT shelter_id, password, organization_name FROM shelters WHERE email=%s", (email,))
    row = cur.fetchone()
    if row:
        shelter_id, db_password, org_name = row
        if password == db_password:
            print(f"<script>alert('Login Successful. Welcome {org_name}');window.location.href='shelter_dash.py?shelter_id={shelter_id}';</script>")
        else:
            print("<script>alert('Incorrect password');window.history.back();</script>")
    else:
        print("<script>alert('Email not registered');window.history.back();</script>")

# --- FORGOT PASSWORD ---
elif form.getvalue("forgot"):
    email = form.getvalue("Email").strip()
    cur.execute("SELECT shelter_id FROM shelters WHERE email=%s", (email,))
    row = cur.fetchone()
    if row:
        shelter_id = row[0]
        token = generate_token()
        cur.execute("UPDATE shelters SET reset_token=%s, token_created=%s WHERE shelter_id=%s",
                    (token, datetime.datetime.now(), shelter_id))
        con.commit()
        reset_link = f"http://localhost/deepak/reset_password.py?token={token}"  # update to online URL later
        body = f"Hello!\n\nClick the link below to reset your password:\n{reset_link}\n\nIf you didn't request this, ignore."
        if send_email(email, "PetAdopt Shelter Password Reset", body):
            print("<script>alert('Password reset link sent to your email');window.location.href='shelter_login.py';</script>")
    else:
        print("<script>alert('Email not found');window.history.back();</script>")

# --- HTML FORM with Navbar ---
print("""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Shelter Login</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.7/dist/css/bootstrap.min.css" rel="stylesheet">
<style>
body { font-family: 'Segoe UI', sans-serif; background-color: #f8f9fa; }
.card { border-radius: 15px; max-width: 450px; margin: 5% auto; padding: 30px; }
/* Navbar Styling */
.navbar { background-color: #343a40; padding: 0.8rem 1rem; }
.navbar-brand { font-weight: 600; color: #ffffff !important; letter-spacing: 0.5px; }
.navbar-nav .nav-link { color: #ffffff !important; font-size: 16px; margin-right: 15px; transition: color 0.3s, background-color 0.3s; }
.navbar-nav .nav-link:hover { color: #05b1ef !important; background-color: rgba(255, 255, 255, 0.1); border-radius: 8px; padding: 8px 12px; }
.navbar-toggler { border-color: rgba(255, 255, 255, 0.3); }
.navbar-toggler-icon { filter: invert(1); }
@media (max-width: 992px) {
  .navbar-nav { text-align: center; background-color: #343a40; padding: 10px 0; }
  .navbar-nav .nav-link { margin-right: 0; padding: 10px; display: block; }
}
</style>
</head>
<body>

<!-- Navbar -->
<nav class="navbar navbar-expand-lg navbar-dark">
  <div class="container">
    <a class="navbar-brand fw-bold" href="#">PetAdopt</a>
    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
      <span class="navbar-toggler-icon"></span>
    </button>
    <div class="collapse navbar-collapse" id="navbarNav">
      <ul class="navbar-nav ms-auto">
        <li class="nav-item"><a class="nav-link" href="home.py">Home</a></li>
        <li class="nav-item"><a class="nav-link" href="pet_list_user.py">Adoption</a></li>
        <li class="nav-item"><a class="nav-link" href="care_dash_admin.py">Care Resources</a></li>
        <li class="nav-item"><a class="nav-link" href="#">Shelters</a></li>
        <li class="nav-item"><a class="nav-link" href="shelter_login.py">Login</a></li>
      </ul>
    </div>
  </div>
</nav>

<div class="card shadow-sm">
  <h2 class="text-center text-primary mb-4">Shelter Login</h2>
  <form method="post">
    <div class="mb-3">
      <label>Email</label>
      <input type="email" class="form-control" name="Email" required>
    </div>
    <div class="mb-3">
      <label>Password</label>
      <input type="password" class="form-control" name="Password" required>
    </div>
    <div class="d-grid mb-2">
      <input type="submit" name="login" class="btn btn-primary btn-lg" value="Login">
    </div>
    <div class="text-center">
      <a href="#" onclick="document.getElementById('forgotForm').style.display='block';return false;">Forgot Password?</a>
    </div>
  </form>

  <form id="forgotForm" method="post" style="display:none;margin-top:15px;">
    <div class="mb-3">
      <label>Enter your registered Email</label>
      <input type="email" class="form-control" name="Email" required>
    </div>
    <div class="d-grid">
      <input type="submit" name="forgot" class="btn btn-warning" value="Send Reset Link">
    </div>
  </form>

  <p class="mt-3 text-center">Don't have an account? <a href="shelter_reg.py">Register</a></p>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.7/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
""")

con.close()
