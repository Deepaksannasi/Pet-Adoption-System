#!C:/Users/Deepak/AppData/Local/Programs/Python/Python311/python.exe
print("Content-Type: text/html\r\n\r\n")

import sys, io, cgi, cgitb, pymysql, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
cgitb.enable()

# --- Get Shelter ID and Action ---
form = cgi.FieldStorage()
shelter_id = form.getvalue("shelter_id") or ""
action = form.getvalue("action") or ""

if not shelter_id:
    print("<h2 style='text-align:center; color:red;'>Access Denied: Please provide a valid Shelter ID.</h2>")
    exit()

# --- DB Connection ---
try:
    con = pymysql.connect(host="localhost", user="root", password="", database="pet")
    cur = con.cursor()
except Exception as e:
    print(f"<h2>Database Connection Error: {e}</h2>")
    exit()

# --- Handle Status Update ---
if action == "update_status":
    adoption_id = form.getvalue("adoption_id")
    new_status = form.getvalue("status")
    if adoption_id and new_status:
        cur.execute("UPDATE adoptions SET status=%s WHERE Adoption_ID=%s", (new_status, adoption_id))
        con.commit()
        print(f'<script>window.location.href="{os.path.basename(__file__)}?shelter_id={shelter_id}";</script>')

# --- Get Shelter Name ---
cur.execute("SELECT organization_name FROM shelters WHERE shelter_id=%s", (shelter_id,))
shelter_data = cur.fetchone()
shelter_name = shelter_data[0] if shelter_data else "Shelter"

# --- Check if 'contact' column exists ---
cur.execute("SHOW COLUMNS FROM user_reg")
columns = [col[0] for col in cur.fetchall()]
has_contact = "contact" in columns

# --- Fetch Adoption Requests ---
if has_contact:
    query = """
        SELECT a.Adoption_ID, u.full_name, u.email, u.contact, 
               p.name, p.breed, a.status, a.Submission_Date
        FROM adoptions a
        LEFT JOIN user_reg u ON a.User_ID = u.user_id
        LEFT JOIN pets p ON a.Pet_ID = p.pet_id
        WHERE a.Shelter_ID=%s
        ORDER BY a.Submission_Date DESC
    """
else:
    query = """
        SELECT a.Adoption_ID, u.full_name, u.email, 
               p.name, p.breed, a.status, a.Submission_Date
        FROM adoptions a
        LEFT JOIN user_reg u ON a.User_ID = u.user_id
        LEFT JOIN pets p ON a.Pet_ID = p.pet_id
        WHERE a.Shelter_ID=%s
        ORDER BY a.Submission_Date DESC
    """
cur.execute(query, (shelter_id,))
requests = cur.fetchall()

current_page = os.path.basename(__file__)

# ---------------- HTML OUTPUT ----------------
print(f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Adoption Tracking - {shelter_name}</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.7/dist/css/bootstrap.min.css" rel="stylesheet">
<link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css" rel="stylesheet">
<style>
body {{ font-family: 'Segoe UI', sans-serif; background: #f8f9fa; transition: margin-left 0.3s; }}
.navbar {{ background: #343a40; }}
.navbar-brand {{ color:white !important; font-weight:bold; }}

.navbar-nav .nav-link {{ color:white !important; }}
.navbar-nav .nav-link:hover {{ color:#05b1ef !important; }}
.sidebar {{ height: 100%; width: 250px; position: fixed; top: 0; left: -250px; background-color: #05b1ef; overflow-x: hidden; transition:0.3s; padding-top: 60px; color:white; z-index:1100; }}
.sidebar a {{ padding: 12px 20px; text-decoration:none; font-size:18px; display:block; color:#01080f; }}
.sidebar a:hover {{ background-color:#5a94ce; color:white; }}
.hamburger {{ font-size:1.5rem; cursor:pointer; position:fixed; top:15px; left:15px; z-index:1200; color:white; }}
.overlay {{ position:fixed; top:0; left:0; width:100%; height:100%; background: rgba(0,0,0,0.5); display:none; z-index:1050; }}
#mainContent {{ transition: margin-left 0.3s; }}
@media (min-width:769px) {{ .content-shift {{ margin-left:250px !important; }} }}
.badge-status {{ font-size: 0.9rem; color:white; padding:5px 10px; border-radius:10px; }}
.table thead th {{ background: #007bff; color:white; }}
.table tbody tr:hover {{ background-color: #007bff; }}
#searchInput {{ margin-bottom:20px; max-width:400px; border-radius:25px; padding:10px 20px; border:1px solid #ccc; }}
</style>
</head>
<body>

<!-- Navbar -->
<nav class="navbar navbar-expand-lg navbar-dark">
  <div class="container">
    <span class="hamburger" id="hamburger">&#9776;</span>
    <a class="navbar-brand fw-bold ms-3" href="#">{shelter_name}</a>
    <ul class="navbar-nav ms-auto">
      <li class="nav-item"><a class="nav-link" href="home.py?shelter_id={shelter_id}">Home</a></li>
      <li class="nav-item"><a class="nav-link" href="pet_list.py?shelter_id={shelter_id}">Add Pet</a></li>
      <li class="nav-item"><a class="nav-link" href="shelter_dash.py?shelter_id={shelter_id}">Dashboard</a></li>
      <li class="nav-item"><a class="nav-link" href="logout.py">Logout</a></li>
    </ul>
  </div>
</nav>

<div class="overlay" id="overlay"></div>

<!-- Sidebar -->
<nav id="sidebar" class="sidebar p-0">
<div class="pt-4">
<h4 class="text-center mb-4">{shelter_name}</h4>
<ul class="nav flex-column">
<li><a href="shelter_dash.py?shelter_id={shelter_id}" class="nav-link"><i class="bi bi-house"></i> Dashboard</a></li>
<li><a href="pet_list.py?shelter_id={shelter_id}" class="nav-link"><i class="bi bi-card-list"></i> Pet Listings</a></li>
<li><a href="{current_page}?shelter_id={shelter_id}" class="nav-link active"><i class="bi bi-clipboard-check"></i> Adoption Tracking</a></li>
<li><a href="chat_shelter.py?shelter_id={shelter_id}" class="nav-link"><i class="bi bi-chat-dots"></i> Communicate</a></li>
 <li>
        <a href="profile_manage_shelter.py?shelter_id={shelter_id}" class="nav-link {'active' if 'adopt_track.py' in current_page else ''}">
          <i class="bi bi-clipboard-check"></i> Profile Management
        </a>
      </li>
</ul>
</div>
</nav>

<div id="mainContent" class="container my-5">
<h1 class="text-center text-primary mb-4"><i class="bi"></i>Adoption Tracking</h1>

<div class="card p-4">
<input type="text" id="searchInput" class="form-control" placeholder=" Search by User, Pet, or Breed...">
<div class="table-responsive ">
<table class="table table-bordered table-hover align-middle" id="requestsTable">
<thead class="table-dark">

<tr>
<th>ID</th><th>User Name</th><th>Email</th>""")

if has_contact:
    print("<th>Contact</th>")

print("""<th>Pet Name</th><th>Breed</th><th>Status</th><th>Submitted On</th><th>Actions</th></tr>
</thead><tbody>""")

status_colors = {"Pending": "#ffc107", "Approved": "#28a745", "Rejected": "#dc3545"}

for req in requests:
    if has_contact:
        adoption_id, user_name, email, contact, pet, breed, status, date = req
    else:
        adoption_id, user_name, email, pet, breed, status, date = req
        contact = "-"
    color = status_colors.get(status, "#6c757d")
    print(f"""
<tr>
<td>{adoption_id}</td>
<td>{user_name}</td>
<td>{email}</td>""")
    if has_contact:
        print(f"<td>{contact}</td>")
    print(f"""
<td>{pet}</td>
<td>{breed}</td>
<td><span class='badge-status' style='background:{color};'>{status}</span></td>
<td>{date}</td>
<td>
<form method="post" style="display:inline">
<input type="hidden" name="action" value="update_status">
<input type="hidden" name="adoption_id" value="{adoption_id}">
<select name="status" class="form-select form-select-sm d-inline w-auto">
<option value="Pending" {"selected" if status=="Pending" else ""}>Pending</option>
<option value="Approved" {"selected" if status=="Approved" else ""}>Approved</option>
<option value="Rejected" {"selected" if status=="Rejected" else ""}>Rejected</option>
</select>
<button type="submit" class="btn btn-sm btn-primary">Update</button>
</form>
</td>
</tr>
""")

print("</tbody></table></div></div></div>")

# ---- Sidebar toggle JS ----
print("""
<script>
const hamburger = document.getElementById('hamburger');
const sidebar = document.getElementById('sidebar');
const overlay = document.getElementById('overlay');
const mainContent = document.getElementById('mainContent');

hamburger.addEventListener('click', () => {
  const isOpen = sidebar.style.left === '0px';
  sidebar.style.left = isOpen ? '-250px' : '0px';
  if (window.innerWidth > 768) { mainContent.classList.toggle('content-shift'); }
  else { overlay.style.display = isOpen ? 'none' : 'block'; }
});
overlay.addEventListener('click', () => { sidebar.style.left = '-250px'; overlay.style.display = 'none'; });

const searchInput = document.getElementById('searchInput');
searchInput.addEventListener('keyup', () => {
  const filter = searchInput.value.toLowerCase();
  document.querySelectorAll('#requestsTable tbody tr').forEach(tr => {
    tr.style.display = tr.textContent.toLowerCase().includes(filter) ? '' : 'none';
  });
});
</script>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.7/dist/js/bootstrap.bundle.min.js"></script>
</body></html>
""")

cur.close()
con.close()
