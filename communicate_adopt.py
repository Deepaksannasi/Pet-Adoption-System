#!C:/Users/Deepak/AppData/Local/Programs/Python/Python311/python.exe
print("Content-Type: text/html\r\n\r\n")

import cgi, cgitb, pymysql, html, sys, io
cgitb.enable(display=1)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

form = cgi.FieldStorage()

# --- Get parameters safely ---
logged_id = form.getvalue("user_id")
if isinstance(logged_id, list):
    logged_id = logged_id[0]

to_id = form.getvalue("to_id")
if isinstance(to_id, list):
    to_id = to_id[0]

message = form.getvalue("message", "")

# --- Check login ---
if not logged_id:
    print("<h3 style='color:red;text-align:center;'>Please login first.</h3>")
    exit()

# --- DB connection ---
con = pymysql.connect(host="localhost", user="root", password="", database="pet")
cur = con.cursor()

# --- Handle sending message ---
if form.getvalue("send") and message and to_id:
    try:
        cur.execute(
            "INSERT INTO messages (sender_id, receiver_id, message) VALUES (%s,%s,%s)",
            (logged_id, to_id, message)
        )
        con.commit()
    except Exception as e:
        print(f"<script>alert('Error sending message: {str(e)}');window.history.back();</script>")

# --- Fetch logged-in user info ---
cur.execute("SELECT full_name FROM user_reg WHERE user_id=%s", (logged_id,))
me = cur.fetchone()
me_name = me[0] if me else "User"

# --- Fetch list of shelters user can chat with ---
cur.execute("""
    SELECT DISTINCT s.shelter_id, s.organization_name
    FROM shelters s
    JOIN pets p ON s.shelter_id = p.shelter_id
    JOIN adoptions a ON p.pet_id = a.Pet_ID
    WHERE a.User_ID = %s
""", (logged_id,))
partners = cur.fetchall()

# --- Fetch chat history ---
chat_history = []
partner_name = ""
if to_id:
    cur.execute("SELECT organization_name FROM shelters WHERE shelter_id=%s", (to_id,))
    partner = cur.fetchone()
    partner_name = partner[0] if partner else "Unknown"

    cur.execute("""
        SELECT sender_id, receiver_id, message, timestamp
        FROM messages
        WHERE (sender_id=%s AND receiver_id=%s) OR (sender_id=%s AND receiver_id=%s)
        ORDER BY timestamp ASC
    """, (logged_id, to_id, to_id, logged_id))
    chat_history = cur.fetchall()

# --- HTML Output ---
print(f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Chat - PetAdopt</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.7/dist/css/bootstrap.min.css" rel="stylesheet">
<link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css" rel="stylesheet">
<style>
body {{ font-family:'Segoe UI'; background:#f8f9fa; transition: margin-left 0.3s; }}
.navbar {{ background-color:#343a40; padding:0.8rem 1rem; }}
.navbar-brand {{ font-weight:600; color:#fff !important; letter-spacing:0.5px; }}
.navbar-nav .nav-link {{ color:#fff !important; margin-right:15px; transition:0.3s; }}
.navbar-nav .nav-link:hover {{ color:#05b1ef !important; background: rgba(255,255,255,0.1); border-radius:8px; padding:8px 12px; }}
.hamburger {{ font-size:1.5rem; cursor:pointer; position:fixed; top:15px; left:15px; z-index:1200; color:white; }}
.sidebar {{
      height: 100%;
      width: 250px;
      position: fixed;
      top: 0;
      left: -250px;
      background-color: #05b1ef;
      overflow-x: hidden;
      transition: 0.3s;
      padding-top: 60px;
      z-index: 1100;
    }}
    .sidebar a {{
      padding: 12px 20px;
      text-decoration: none;
      font-size: 18px;
      display: block;
      color: #01080f;
    }}
    .sidebar a:hover {{ background-color: #5a94ce; color: white; }}
    .sidebar .submenu {{ padding-left: 30px; }}
    .sidebar-heading {{
      font-size: 14px;
      text-transform: uppercase;
      padding: 15px 20px 5px;
      color: #acc6e0;
    }}
.overlay {{ position:fixed; top:0; left:0; width:100%; height:100%; background: rgba(0,0,0,0.5); display:none; z-index:1050; }}
#mainContent {{ margin-left:0; transition: margin-left 0.3s; }}
.content {{ padding:20px; }}
.chat-box {{ height:400px; overflow-y:auto; border:1px solid #ccc; padding:15px; background:white; }}
.msg-sent {{ text-align:right; color:#0d6efd; }}
.msg-recv {{ text-align:left; color:#198754; }}
@media (min-width: 769px) {{ #mainContent.content-shift {{ margin-left:250px; }} }}
</style>
</head>
<body>

<!-- Navbar -->
<nav class="navbar navbar-expand-lg navbar-dark">
  <div class="container">
    <span class="hamburger" id="hamburger">&#9776;</span>
    <a class="navbar-brand fw-bold ms-3" href="#">PetAdopt</a>
    <div class="collapse navbar-collapse">
      <ul class="navbar-nav ms-auto">
       <li class="nav-item"><a class="nav-link" href="home.py">Home</a></li>
       <li class="nav-item"><a class="nav-link" href="pet_list_user?user_id={logged_id}.py">Adoption</a></li>
       <li class="nav-item"><a class="nav-link" href="care_dash_user?user_id={logged_id}.py">Care Resources</a></li>
       <li class="nav-item"><a class="nav-link" href="user_login.py">Login</a></li>
      </ul>
    </div>
  </div>
</nav>

<!-- Sidebar -->
<nav id="sidebar" class="sidebar p-0">
  <div class="pt-4 text-center">
    <h4 class="mb-4" style="color:white;">PetAdopt</h4>
  </div>
  <ul class="nav flex-column">
    <li><a class="nav-link" href="dashboard.py?user_id={logged_id}"><i class="bi bi-house me-2"></i> Dashboard</a></li>
    <li><a class="nav-link" href="profile_manage.py?user_id={logged_id}"><i class="bi bi-person-circle me-2"></i> Profile Management</a></li>
    <li><a class="nav-link" href="pet_list_user.py?user_id={logged_id}"><i class="bi bi-heart me-2"></i> Pet Adoption</a></li>
    <li><a class="nav-link" href="search_view.py?user_id={logged_id}"><i class="bi bi-search me-2"></i> Search & View Pets</a></li>
    <li><a class="nav-link" href="care_dash_user.py?user_id={logged_id}"><i class="bi bi-journal-medical me-2"></i> Care Resources</a></li>
    <li><a class="nav-link" href="communicate_adopt.py?user_id={logged_id}"><i class="bi bi-gear me-2"></i> Communicate Adopt</a></li>
    <li><a class="nav-link" href="#"><i class="bi bi-gear me-2"></i> Settings</a></li>
  </ul>
</nav>

<!-- Main Content -->
<div id="mainContent" class="container-fluid content">
<div class="row">
<div class="col-md-3">
<h4>Available Shelters</h4>
<ul class="list-group">
""")

if partners:
    for pid, pname in partners:
        active = "active" if str(pid) == str(to_id) else ""
        print(f"<li class='list-group-item {active}'><a href='communicate_adopt.py?user_id={logged_id}&to_id={pid}'>{pname}</a></li>")
else:
    print("<li class='list-group-item'>No shelters available</li>")

print("</ul></div><div class='col-md-9'>")

if to_id:
    print(f"<h4>Chat with {partner_name}</h4>")
    print("<div class='chat-box mb-3'>")
    for sender, receiver, msg, ts in chat_history:
        if str(sender) == str(logged_id):
            print(f"<div class='msg-sent'><b>Me:</b> {html.escape(msg)}<br><small>{ts}</small></div>")
        else:
            print(f"<div class='msg-recv'><b>{partner_name}:</b> {html.escape(msg)}<br><small>{ts}</small></div>")
    print("</div>")

    print(f"""
<form method="post">
<input type="hidden" name="user_id" value="{logged_id}">
<input type="hidden" name="to_id" value="{to_id}">
<div class="input-group">
<input type="text" name="message" class="form-control" placeholder="Type a message..." required>
<button type="submit" name="send" class="btn btn-primary">Send</button>
</div>
</form>
""")
else:
    print("<h4>Select a shelter from the left to start chatting.</h4>")

print("</div></div></div>")

# --- Sidebar toggle script ---
print(f"""
<script>
const hamburger = document.getElementById('hamburger');
const sidebar = document.getElementById('sidebar');
const mainContent = document.getElementById('mainContent');
const overlay = document.getElementById('overlay');

hamburger.addEventListener('click', () => {{
  const isOpen = sidebar.style.left === '0px';
  sidebar.style.left = isOpen ? '-250px' : '0px';
  if(window.innerWidth > 768) {{ mainContent.classList.toggle('content-shift'); }}
  else {{ overlay.style.display = isOpen ? 'none' : 'block'; }}
}});
overlay.addEventListener('click', () => {{ sidebar.style.left='-250px'; overlay.style.display='none'; }});
</script>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.7/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
""")

con.close()
