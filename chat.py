#!C:/Users/Deepak/AppData/Local/Programs/Python/Python311/python.exe
print("Content-Type: text/html\r\n\r\n")

import cgi
import cgitb
import pymysql
import sys, io

# Enable debugging
cgitb.enable(display=1)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

form = cgi.FieldStorage()

# Safely get single values (not lists)
def get_first_value(field):
    val = form.getvalue(field)
    if isinstance(val, list):
        return val[0]
    return val

user_id = get_first_value("user_id")
shelter_id = get_first_value("shelter_id")
sender_type = get_first_value("sender_type")
message_text = get_first_value("message_text")

con = pymysql.connect(host="localhost", user="root", password="", database="pet")
cur = con.cursor()

# --- If message sent ---
if message_text:
    receiver_type = "shelter" if sender_type == "user" else "user"
    receiver_id = shelter_id if sender_type == "user" else user_id

    cur.execute("""
        INSERT INTO messages (sender_id, receiver_id, sender_type, message_text, sent_at)
        VALUES (%s, %s, %s, %s, NOW())
    """, (user_id if sender_type == "user" else shelter_id,
          receiver_id, sender_type, message_text))
    con.commit()

# --- Fetch messages between user and shelter ---
cur.execute("""
    SELECT sender_id, sender_type, message_text, sent_at 
    FROM messages 
    WHERE (sender_id=%s AND receiver_id=%s)
       OR (sender_id=%s AND receiver_id=%s)
    ORDER BY sent_at ASC
""", (user_id, shelter_id, shelter_id, user_id))

messages = cur.fetchall()
con.close()

# --- HTML Output ---
print(f"""
<html>
<head>
<title>Chat - PetAdopt</title>
<meta charset="UTF-8">
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
  height:100%;
  width:250px;
  position:fixed;
  top:0;
  left:-250px;
  background-color:#05b1ef;
  overflow-x:hidden;
  transition:0.3s;
  padding-top:60px;
  z-index:1100;
}}
.sidebar a {{
  padding:12px 20px;
  text-decoration:none;
  font-size:18px;
  display:block;
  color:#01080f;
}}
.sidebar a:hover {{ background-color:#5a94ce; color:white; }}
.sidebar .submenu {{ padding-left:30px; }}
.sidebar-heading {{
  font-size:14px;
  text-transform:uppercase;
  padding:15px 20px 5px;
  color:#acc6e0;
}}
.overlay {{ position:fixed; top:0; left:0; width:100%; height:100%; background: rgba(0,0,0,0.5); display:none; z-index:1050; }}
#mainContent {{ margin-left:0; transition: margin-left 0.3s; }}
@media (min-width: 769px) {{ #mainContent.content-shift {{ margin-left:250px; }} }}

.chat-container {{
    width: 60%; margin: 50px auto; background: #fff;
    border-radius: 10px; padding: 20px;
    box-shadow: 0 0 10px rgba(0,0,0,0.1);
}}
.message {{
    padding: 10px 15px; margin: 5px 0; border-radius: 10px; max-width: 75%;
}}
.user {{ background-color: #cce5ff; align-self: flex-end; text-align: right; }}
.shelter {{ background-color: #d4edda; align-self: flex-start; text-align: left; }}
.chat-box {{ display: flex; flex-direction: column; gap: 5px; }}
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
       <li class="nav-item"><a class="nav-link" href="pet_list_user.py?user_id={user_id}">Adoption</a></li>
       <li class="nav-item"><a class="nav-link" href="care_dash_user.py?user_id={user_id}">Care Resources</a></li>
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
    <li><a class="nav-link" href="dashboard.py?user_id={user_id}"><i class="bi bi-house me-2"></i> Dashboard</a></li>
    <li><a class="nav-link" href="profile_manage.py?user_id={user_id}"><i class="bi bi-person-circle me-2"></i> Profile Management</a></li>
    <li><a class="nav-link" href="pet_list_user.py?user_id={user_id}"><i class="bi bi-heart me-2"></i> Pet Adoption</a></li>
    <li><a class="nav-link" href="care_dash_user.py?user_id={user_id}"><i class="bi bi-journal-medical me-2"></i> Care Resources</a></li>
    <li><a class="nav-link" href="chat.py?user_id={user_id}"><i class="bi bi-chat-dots me-2"></i> Communication</a></li>
    <li><a class="nav-link" href="#"><i class="bi bi-gear me-2"></i> Settings</a></li>
  </ul>
</nav>

<div class="overlay" id="overlay"></div>

<!-- Main Content -->
<div id="mainContent">
<div class='chat-container'>
<h3 class='text-center text-primary'>User–Shelter Chat</h3>
<div class='chat-box'>
""")

for msg in messages:
    sender_class = "user" if msg[1] == "user" else "shelter"
    print(f"<div class='message {sender_class}'>{msg[2]}<br><small>{msg[3]}</small></div>")

print(f"""
</div>
<form method='post'>
    <input type='hidden' name='user_id' value='{user_id}'>
    <input type='hidden' name='shelter_id' value='{shelter_id}'>
    <input type='hidden' name='sender_type' value='{sender_type}'>
    <div class='input-group mt-3'>
        <input type='text' name='message_text' class='form-control' placeholder='Type your message...' required>
        <button type='submit' class='btn btn-primary'>Send</button>
    </div>
</form>
</div>
</div>

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
overlay.addEventListener('click', () => {{
  sidebar.style.left='-250px';
  overlay.style.display='none';
}});
</script>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.7/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
""")
