#!C:/Users/Deepak/AppData/Local/Programs/Python/Python311/python.exe
print("Content-Type: text/html\r\n\r\n")

import sys, io, cgi, cgitb, pymysql, os

# Force UTF-8 output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
cgitb.enable()
form = cgi.FieldStorage()

# --- DB Connection ---
con = pymysql.connect(host="localhost", user="root", password="", database="pet")
cur = con.cursor()

# Ensure status and id_proof columns exist
cur.execute("ALTER TABLE shelters ADD COLUMN IF NOT EXISTS status ENUM('pending','approved','rejected') DEFAULT 'pending'")
cur.execute("ALTER TABLE shelters ADD COLUMN IF NOT EXISTS id_proof VARCHAR(255)")

# --- Initialize pending_shelters to avoid NameError ---
pending_shelters = []

# Handle updates
if "update_shelter" in form:
    shelter_id = form.getvalue("shelter_id")
    status = form.getvalue("status")
    no_of_animals_sheltered = form.getvalue("no_of_animals_sheltered")
    cur.execute("UPDATE shelters SET status=%s, no_of_animals_sheltered=%s WHERE shelter_id=%s",
                (status, no_of_animals_sheltered, shelter_id))
    con.commit()

# Fetch pending shelters
try:
    cur.execute(
        "SELECT shelter_id, organization_name, person_Name, email, phone, city, state, no_of_animals_sheltered, status, id_proof FROM shelters WHERE status='pending'")
    pending_shelters = cur.fetchall()
except Exception as e:
    print(f"<h3>Error fetching pending shelters: {e}</h3>")
    pending_shelters = []

# Fetch all shelters
cur.execute("SELECT shelter_id, organization_name, person_Name, email, phone, city, state, no_of_animals_sheltered, status, id_proof FROM shelters")
shelters = cur.fetchall()

# --- HTML Output ---
print("""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Shelter Management</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.7/dist/css/bootstrap.min.css" rel="stylesheet">
<link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css" rel="stylesheet">
<style>
body { font-family:'Segoe UI'; background:#f8f9fa; transition: margin-left 0.3s; }
.navbar { background-color: #343a40; }
.navbar-brand { font-weight:600; color:#fff !important; letter-spacing:0.5px; }
.navbar-nav .nav-link { color:#fff !important; font-size:16px; margin-right:15px; transition:0.3s; }
.navbar-nav .nav-link:hover { color:#05b1ef !important; background: rgba(255,255,255,0.1); border-radius:8px; padding:8px 12px; }
.hamburger { font-size:1.5rem; cursor:pointer; position:fixed; top:15px; left:15px; z-index:1200; color:white; }
.sidebar { height:100%; width:250px; position:fixed; top:0; left:-250px; background-color:#05b1ef; overflow-x:hidden; transition:0.3s; padding-top:60px; color:white; z-index:1100; }
.sidebar a { padding:12px 20px; text-decoration:none; font-size:18px; display:block; color:#01080f; }
.sidebar a:hover { background-color:#5a94ce; color:white; }
.overlay { position:fixed; top:0; left:0; width:100%; height:100%; background: rgba(0,0,0,0.5); display:none; z-index:1050; }
#mainContent { transition: margin-left 0.3s; }
.ms-3 { margin-left:1rem !important; }
.table-title { background-color: #05b1ef; color:white; padding:10px; border-radius:5px 5px 0 0; margin-bottom:0; }
.table-container { margin-bottom:50px; box-shadow:0 0 5px rgba(0,0,0,0.1); border-radius:5px; background:white; overflow-x:auto; }
img.id-proof { max-width:100px; max-height:100px; object-fit:contain; border:1px solid #ccc; border-radius:5px; }
</style>
</head>
<body>

<!-- Navbar -->
<nav class="navbar navbar-expand-lg navbar-dark">
  <div class="container">
    <span class="hamburger" id="hamburger">&#9776;</span>
    <a class="navbar-brand fw-bold ms-3" href="#">PetAdopt Admin</a>
    <div class="collapse navbar-collapse">
      <ul class="navbar-nav ms-auto">
       <li class="nav-item"><a class="nav-link" href="home.py">Home</a></li>
       <li class="nav-item"><a class="nav-link" href="#">Logout</a></li>
      </ul>
    </div>
  </div>
</nav>

<!-- Sidebar -->
<div class="overlay" id="overlay"></div>
<nav id="sidebar" class="sidebar p-0">
  <div class="pt-4 text-center">
    <h4 class="mb-4" style="color:white;">Admin Panel</h4>
  </div>
  <ul class="nav flex-column">
    <li><a class="nav-link" href="admin_dash.py"><i class="bi bi-speedometer2 me-2"></i> Dashboard</a></li>
    <li class="nav-item">
        <a class="nav-link" data-bs-toggle="collapse" href="#managementLinks" role="button" aria-expanded="false" aria-controls="managementLinks">
            <i class="bi bi-gear me-2"></i> Management
        </a>
        <div class="collapse ms-3" id="managementLinks">
            <ul class="nav flex-column">
                <li class="nav-item"><a class="nav-link" href="user_manage.py"><i class="bi bi-people me-2"></i> Manage Users</a></li>
                <li class="nav-item"><a class="nav-link" href="shelter_manage.py"><i class="bi bi-building me-2"></i> Manage Shelters</a></li>
                <li class="nav-item"><a class="nav-link" href="pet_manage.py"><i class="bi bi-bag-heart me-2"></i> Manage Pets</a></li>
            </ul>
        </div>
    </li>
    <li><a class="nav-link" href="adoption_manage.py"><i class="bi bi-house me-2"></i> Manage Adoptions</a></li>
    <li><a class="nav-link" href="content_moderate.py"><i class="bi bi-journal-text me-2"></i> Content Moderate</a></li>
    <li><a class="nav-link" href="adoption_report.py"><i class="bi bi-bar-chart-line me-2"></i> Adoption Report</a></li>
    <li><a class="nav-link" href="care_dash_admin.py"><i class="bi bi-gear me-2"></i>Care Resource</a></li>
     <li>
        <a href="profile_manage_shelter.py?shelter_id={shelter_id}" class="nav-link {'active' if 'adopt_track.py' in current_page else ''}">
          <i class="bi bi-clipboard-check"></i> Profile Management
        </a>
      </li>
    <li><a class="nav-link" href="#"><i class="bi bi-gear me-2"></i> Settings</a></li>
  </ul>
</nav>

<!-- Main Content -->
<div id="mainContent" class="container my-5">

<h2 class="table-title">Pending Shelters</h2>
<div class="table-container p-3">
<table class="table table-bordered table-striped text-center">
<tr class="table-dark"><th>ID</th><th>Organization</th><th>Person</th><th>Email</th><th>Phone</th><th>City</th><th>State</th><th>Animals</th><th>ID Proof</th><th>Status</th><th>Action</th></tr>
""")

# Pending shelters with ID Proof
for s in pending_shelters:
    id_proof = s[9] if s[9] else None
    if id_proof and id_proof.lower().endswith(('.png','.jpg','.jpeg','.gif')):
        id_display = f'<img src="uploads/{id_proof}" class="id-proof">'
    else:
        id_display = id_proof if id_proof else "Not Uploaded"

    print(f"""
<tr>
<form method="post">
<input type="hidden" name="update_shelter" value="1">
<input type="hidden" name="shelter_id" value="{s[0]}">
<td>{s[0]}</td><td>{s[1]}</td><td>{s[2]}</td><td>{s[3]}</td><td>{s[4]}</td><td>{s[5]}</td><td>{s[6]}</td>
<td>{s[7]}</td>
<td>{id_display}</td>
<td>
<select class="form-select" name="status">
<option value="pending" {"selected" if s[8]=="pending" else ""}>Pending</option>
<option value="approved">Approved</option>
<option value="rejected">Rejected</option>
</select>
</td>
<td><button class="btn btn-success btn-sm">Update</button></td>
</form>
</tr>
""")

print("""
</table>
</div>

<h2 class="table-title">All Shelters</h2>
<div class="table-container p-3">
<table class="table table-bordered table-striped text-center">
<tr class="table-dark"><th>ID</th><th>Organization</th><th>Person</th><th>Email</th><th>Phone</th><th>City</th><th>State</th><th>Animals</th><th>ID Proof</th><th>Status</th><th>Action</th></tr>
""")

# All shelters table with ID Proof
for s in shelters:
    id_proof = s[9] if s[9] else None
    if id_proof and id_proof.lower().endswith(('.png','.jpg','.jpeg','.gif')):
        id_display = f'<img src="uploads/{id_proof}" class="id-proof">'
    else:
        id_display = id_proof if id_proof else "Not Uploaded"

    print(f"""
<tr>
<form method="post">
<input type="hidden" name="update_shelter" value="1">
<input type="hidden" name="shelter_id" value="{s[0]}">
<td>{s[0]}</td><td>{s[1]}</td><td>{s[2]}</td><td>{s[3]}</td><td>{s[4]}</td><td>{s[5]}</td><td>{s[6]}</td>
<td><input class="form-control form-control-sm" name="no_of_animals_sheltered" value="{s[7]}"></td>
<td>{id_display}</td>
<td>
<select class="form-select" name="status">
<option value="pending" {"selected" if s[8]=="pending" else ""}>Pending</option>
<option value="approved" {"selected" if s[8]=="approved" else ""}>Approved</option>
<option value="rejected" {"selected" if s[8]=="rejected" else ""}>Rejected</option>
</select>
</td>
<td><button class="btn btn-success btn-sm">Update</button></td>
</form>
</tr>
""")

print("""
</table>
</div>

<!-- Bootstrap & Sidebar Toggle Script -->
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.7/dist/js/bootstrap.bundle.min.js"></script>
<script>
const hamburger = document.getElementById('hamburger');
const sidebar = document.getElementById('sidebar');
const overlay = document.getElementById('overlay');

hamburger.addEventListener('click', () => {
  const isOpen = sidebar.style.left === '0px';
  sidebar.style.left = isOpen ? '-250px' : '0px';
  overlay.style.display = isOpen ? 'none' : 'block';
});
overlay.addEventListener('click', () => {
  sidebar.style.left = '-250px';
  overlay.style.display = 'none';
});
</script>

</body>
</html>
""")

cur.close()
con.close()
