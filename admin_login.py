#!C:/Users/Deepak/AppData/Local/Programs/Python/Python311/python.exe
print("Content-Type: text/html\r\n\r\n")

import cgi, cgitb, pymysql, sys, io, html
cgitb.enable(display=1)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

form = cgi.FieldStorage()
username = form.getvalue("username", "").strip()
password = form.getvalue("password", "").strip()
error_msg = ""

# --- If form submitted ---
if username and password:
    try:
        # --- DB connection ---
        con = pymysql.connect(host="localhost", user="root", password="", database="pet")
        cur = con.cursor()
        cur.execute("SELECT * FROM admin_users WHERE username=%s AND password=%s", (username, password))
        admin = cur.fetchone()
        con.close()

        if admin:
            # --- Redirect to admin dashboard ---
            print(f"""
            <script>
                alert('Login successful!');
                window.location.href='admin_dash.py';
            </script>
            """)
            sys.exit()
        else:
            error_msg = "Invalid username or password!"
    except Exception as e:
        error_msg = f"Database error: {str(e)}"

# --- HTML Login Form ---
print(f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Admin Login - PetAdopt</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.7/dist/css/bootstrap.min.css" rel="stylesheet">
<link href="https://cdn.jsdelivr.net/npm/bootstrap-icons/font/bootstrap-icons.css" rel="stylesheet">
<style>
body {{ font-family: 'Segoe UI', sans-serif; background-color: #f8f9fa; }}

.navbar {{
  background-color: #343a40;
  padding: 0.8rem 1rem;
}}

.navbar-brand {{
  font-weight: 600;
  color: #ffffff !important;
  letter-spacing: 0.5px;
}}

.navbar-nav .nav-link {{
  color: #ffffff !important;
  font-size: 16px;
  margin-right: 15px;
  transition: color 0.3s, background-color 0.3s;
}}

.navbar-nav .nav-link:hover {{
  color: #05b1ef !important;
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 8px 12px;
}}

.navbar-toggler {{
  border-color: rgba(255, 255, 255, 0.3);
}}

.navbar-toggler-icon {{
  filter: invert(1);
}}

.card {{
  border-radius: 15px;
  max-width: 450px;
  margin: 5% auto;
  padding: 30px;
  box-shadow: 0 0 15px rgba(0,0,0,0.2);
}}

h2 {{ text-align:center; margin-bottom:20px; color:#0d6efd; }}

.error {{ color:red; text-align:center; margin-bottom:10px; }}

@media (max-width: 576px) {{
  .card {{ padding:20px; margin:10% auto; }}
}}
</style>
</head>
<body>

<!-- Navbar -->
<nav class="navbar navbar-expand-lg navbar-dark">
  <div class="container">
    <a class="navbar-brand fw-bold ms-3" href="#">PetAdopt</a>
    <div class="collapse navbar-collapse">
      <ul class="navbar-nav ms-auto">
       <li class="nav-item"><a class="nav-link" href="home.py">Home</a></li>
       <li class="nav-item"><a class="nav-link" href="pet_list_user.py">Adoption</a></li>
       <li class="nav-item"><a class="nav-link" href="care_dash.py">Care Resources</a></li>
       <li class="nav-item"><a class="nav-link" href="#">Shelters</a></li>
       <li class="nav-item"><a class="nav-link" href="user_login.py">Login</a></li>
      </ul>
    </div>
  </div>
</nav>

<div class="card shadow-sm">
    <h2>Admin Login</h2>
    {f'<div class="error">{html.escape(error_msg)}</div>' if error_msg else ''}
    <form method="post">
        <div class="mb-3">
            <label>Username</label>
            <input type="text" name="username" class="form-control" placeholder="Enter your UserName" required value="{html.escape(username)}">
        </div>
        <div class="mb-3">
            <label>Password</label>
            <input type="password" name="password" class="form-control" placeholder="Enter your Password" required>
        </div>
        <div class="d-grid mt-3">
          <button type="submit" class="btn btn-primary btn-lg">Login</button>
        </div>
    </form>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.7/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
""")
