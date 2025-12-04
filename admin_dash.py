#!C:/Users/Deepak/AppData/Local/Programs/Python/Python311/python.exe
print("Content-Type: text/html\r\n\r\n")

import sys, io, cgi, cgitb, pymysql

# Force UTF-8 output to avoid Unicode errors
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
cgitb.enable()
form = cgi.FieldStorage()

# --- DataBase Connection ---
con = pymysql.connect(host="localhost", user="root", password="", database="pet")
cur = con.cursor()

# --- Handle Updates ---
if "update_user" in form:
    cur.execute("UPDATE user_reg SET status=%s WHERE user_id=%s", (form.getvalue("status"), form.getvalue("user_id")))
    con.commit()
if "update_shelter" in form:
    cur.execute("UPDATE shelters SET status=%s, no_of_animals_sheltered=%s WHERE shelter_id=%s",
                (form.getvalue("status"), form.getvalue("no_of_animals_sheltered"), form.getvalue("shelter_id")))
    con.commit()
if "update_adoption" in form:
    cur.execute("UPDATE adoptions SET status=%s WHERE Adoption_ID=%s", (form.getvalue("status"), form.getvalue("adoption_id")))
    con.commit()

# --- Fetch Summary Counts ---
cur.execute("SELECT COUNT(*) FROM user_reg")
total_users = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM shelters")
total_shelters = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM adoptions")
total_adoptions = cur.fetchone()[0]

# --- Fetch Tables ---
cur.execute("SELECT user_id, full_name, email, phone, city, state, status FROM user_reg")
users = cur.fetchall()

cur.execute("SELECT shelter_id, organization_name, person_Name, email, phone, city, state, no_of_animals_sheltered, status FROM shelters")
shelters = cur.fetchall()

cur.execute("""
SELECT a.Adoption_ID, u.full_name, p.name, p.breed, s.organization_name, a.Submission_Date, a.status
FROM adoptions a
LEFT JOIN user_reg u ON a.User_ID=u.user_id
LEFT JOIN pets p ON a.Pet_ID=p.pet_id
LEFT JOIN shelters s ON a.Shelter_ID=s.shelter_id
ORDER BY a.Submission_Date DESC
""")
adoptions = cur.fetchall()

# --- HTML Output ---
print(f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Admin Dashboard</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.7/dist/css/bootstrap.min.css" rel="stylesheet">
<link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css" rel="stylesheet">
<style>
body {{ font-family:'Segoe UI'; background:#f8f9fa; transition: margin-left 0.3s; }}
.summary-card {{ border-radius:12px; text-align:center; padding:20px; color:white; }}
.bg-users {{ background:#007bff; }}
.bg-shelters {{ background:#28a745; }}
.bg-adoptions {{ background:#ffc107; color:#000; }}
.status-pending {{ color:orange; font-weight:500; }}
.status-approved {{ color:green; font-weight:500; }}
.status-rejected {{ color:red; font-weight:500; }}
.table thead th {{ background:#007bff; color:white; }}

.navbar {{ background-color: #343a40; }}
.navbar-brand {{ font-weight:600; color:#fff !important; letter-spacing:0.5px; }}
.navbar-nav .nav-link {{ color:#fff !important; font-size:16px; margin-right:15px; transition:0.3s; }}
.navbar-nav .nav-link:hover {{ color:#05b1ef !important; background: rgba(255,255,255,0.1); border-radius:8px; padding:8px 12px; }}
.hamburger {{ font-size:1.5rem; cursor:pointer; position:fixed; top:15px; left:15px; z-index:1200; color:white; }}

.sidebar {{ height:100%; width:250px; position:fixed; top:0; left:-250px; background-color:#05b1ef; overflow-x:hidden; transition:0.3s; padding-top:60px; color:white; z-index:1100; }}
.sidebar a {{ padding:12px 20px; text-decoration:none; font-size:18px; display:block; color:#01080f; }}
.sidebar a:hover {{ background-color:#5a94ce; color:white; }}
.overlay {{ position:fixed; top:0; left:0; width:100%; height:100%; background: rgba(0,0,0,0.5); display:none; z-index:1050; }}
#mainContent {{ transition: margin-left 0.3s;  }}

@media (min-width: 769px) {{ .content-shift {{ margin-left:250px !important; }} }}
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
        <li class="nav-item">
          <a class="nav-link" href="#" data-bs-toggle="modal" data-bs-target="#logoutModal">Logout</a>
        </li>
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
    <li><a class="nav-link" href="care_dash_shelter.py"><i class="bi bi-gear me-2"></i> Settings</a></li>
  </ul>
</nav>

<div id="mainContent" class="container my-5">

<h2 class="text-center mb-4">Admin Dashboard</h2>

<!-- Summary Cards -->
<div class="row g-4 mb-5">
<div class="col-md-4"><div class="summary-card bg-users"><h5>Total Users</h5><p class="fs-3">{total_users}</p></div></div>
<div class="col-md-4"><div class="summary-card bg-shelters"><h5>Total Shelters</h5><p class="fs-3">{total_shelters}</p></div></div>
<div class="col-md-4"><div class="summary-card bg-adoptions"><h5>Total Adoptions</h5><p class="fs-3">{total_adoptions}</p></div></div>
</div>
""")

# --- Users Table ---
print("<h3>Users Management</h3><table class='table table-bordered table-striped'>")
print("<tr><th>ID</th><th>Name</th><th>Email</th><th>Phone</th><th>City</th><th>State</th><th>Status</th><th>Action</th></tr>")
for u in users:
    print(f"""
<tr>
<form method="post">
<input type="hidden" name="update_user" value="1">
<input type="hidden" name="user_id" value="{u[0]}">
<td>{u[0]}</td><td>{u[1]}</td><td>{u[2]}</td><td>{u[3]}</td>
<td>{u[4]}</td><td>{u[5]}</td><td>{u[6]}</td>
<td>
<select class="form-select" name="status">
<option value="Pending" {"selected" if u[6]=="Pending" else ""}>Pending</option>
<option value="Approved" {"selected" if u[6]=="Approved" else ""}>Approved</option>
<option value="Rejected" {"selected" if u[6]=="Rejected" else ""}>Rejected</option>
</select>
<button class="btn btn-success btn-sm mt-1" type="submit">Update</button>
</td>
</form>
</tr>
""")
print("</table>")

# --- Shelters Table ---
print("<h3>Shelters Management</h3><table class='table table-bordered table-striped'>")
print("<tr><th>ID</th><th>Organization</th><th>Person</th><th>Email</th><th>Phone</th><th>City</th><th>State</th><th>No of Animals</th><th>Status</th><th>Action</th></tr>")
for s in shelters:
    print(f"""
<tr>
<form method="post">
<input type="hidden" name="update_shelter" value="1">
<input type="hidden" name="shelter_id" value="{s[0]}">
<td>{s[0]}</td><td>{s[1]}</td><td>{s[2]}</td><td>{s[3]}</td><td>{s[4]}</td><td>{s[5]}</td><td>{s[6]}</td>
<td><input class="form-control" name="no_of_animals_sheltered" value="{s[7]}"></td><td>{s[8]}</td>
<td>
<select class="form-select" name="status">
<option value="Pending" {"selected" if s[8]=="Pending" else ""}>Pending</option>
<option value="Approved" {"selected" if s[8]=="Approved" else ""}>Approved</option>
<option value="Rejected" {"selected" if s[8]=="Rejected" else ""}>Rejected</option>
</select>
<button class="btn btn-success btn-sm mt-1" type="submit">Update</button>
</td>
</form>
</tr>
""")
print("</table>")

# --- Adoption Table ---
print("<h3>Adoption Applications</h3><table class='table table-bordered table-striped'>")
print("<tr><th>ID</th><th>User</th><th>Pet</th><th>Breed</th><th>Shelter</th><th>Submission Date</th><th>Status</th><th>Action</th></tr>")
for a in adoptions:
    aid, uname, pname, breed, sname, date, status = a
    print(f"""
<tr>
<form method="post">
<input type="hidden" name="update_adoption" value="1">
<input type="hidden" name="adoption_id" value="{aid}">
<td>{aid}</td><td>{uname}</td><td>{pname}</td><td>{breed}</td><td>{sname}</td><td>{date}</td><td>{status}</td>
<td>
<select class="form-select" name="status">
<option value="Pending" {"selected" if status=="Pending" else ""}>Pending</option>
<option value="Approved" {"selected" if status=="Approved" else ""}>Approved</option>
<option value="Rejected" {"selected" if status=="Rejected" else ""}>Rejected</option>
</select>
<button class="btn btn-success btn-sm mt-1" type="submit">Update</button>
</td>
</form>
</tr>
""")
print("</table></div>")

# --- Logout Modal ---
print("""
<div class="modal fade" id="logoutModal" tabindex="-1" aria-labelledby="logoutModalLabel" aria-hidden="true">
  <div class="modal-dialog modal-dialog-centered">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title" id="logoutModalLabel">Confirm Logout</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
      </div>
      <div class="modal-body">Are you sure you want to logout?</div>
      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
        <a href="admin_login.py" class="btn btn-danger">Logout</a>
      </div>
    </div>
  </div>
</div>
""")

# --- Sidebar toggle script ---
print("""
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
