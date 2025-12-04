#!C:/Users/Deepak/AppData/Local/Programs/Python/Python311/python.exe
print("Content-Type: text/html\r\n\r\n")

import cgi
import cgitb
import pymysql
import os

cgitb.enable()

form = cgi.FieldStorage()

# --- Get user_id from URL/query ---
query_string = os.environ.get("QUERY_STRING", "")
user_id = ""
if "user_id=" in query_string:
    user_id = query_string.split("user_id=")[1].split("&")[0]

if not user_id:
    print("<h3>User ID not provided. Please login first.</h3>")
    exit()

# --- Database connection ---
con = pymysql.connect(host="localhost", user="root", password="", database="pet")
cur = con.cursor()

# --- Total pets (global) ---
cur.execute("SELECT COUNT(*) FROM pets")
total_pets = cur.fetchone()[0]

# --- User-specific adoption counts ---
cur.execute("SELECT COUNT(*) FROM adoptions WHERE User_ID=%s AND status='Approved'", (user_id,))
adopted_pets = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM adoptions WHERE User_ID=%s AND status='Pending'", (user_id,))
pending_pets = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM adoptions WHERE User_ID=%s AND status='Rejected'", (user_id,))
rejected_pets = cur.fetchone()[0]

# --- Fetch adoption applications for this user ---
cur.execute("""
    SELECT a.Adoption_ID, p.image_url, p.name, p.breed, p.age, a.status
    FROM adoptions a
    JOIN pets p ON a.Pet_ID = p.pet_id
    WHERE a.User_ID=%s
""", (user_id,))
applications = cur.fetchall()

# --- Print HTML ---
print(f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Pet Adoption Dashboard</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.7/dist/css/bootstrap.min.css" rel="stylesheet">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css" rel="stylesheet">
  <style>
    body {{ font-family: 'Segoe UI', sans-serif; background-color: #f8f9fa; transition: margin-left 0.3s; }}
    .navbar {{ background: #343a40; }}
    .summary-card {{ border-radius: 12px; text-align: center; padding: 20px; color: white; }}
    .bg-total {{ background-color: #007bff; }}
    .bg-adopted {{ background-color: #28a745; }}
    .bg-pending {{ background-color: #ffc107; color: #000; }}
    .bg-rejected {{ background-color: #dc3545; }}
    .table thead th {{ background-color: #007bff; color: white; }}
    .status-pending {{ color: orange; font-weight: 500; }}
    .status-approved {{ color: green; font-weight: 500; }}
    .status-rejected {{ color: red; font-weight: 500; }}
    .card {{ border-radius: 15px; }}
    .sidebar {{ height: 100%; width: 250px; position: fixed; top: 0; left: -250px; background-color: #05b1ef; overflow-x: hidden; transition: 0.3s; padding-top: 60px; color: white; z-index: 1100; }}
    .sidebar a {{ padding: 12px 20px; text-decoration: none; font-size: 18px; display: block; color: #01080f; }}
    .sidebar a:hover {{ background-color: #5a94ce; color: white; }}
    .sidebar .submenu {{ padding-left: 30px; }}
    .sidebar-heading {{ font-size: 14px; text-transform: uppercase; padding: 15px 20px 5px; color: #acc6e0; }}
    .hamburger {{ font-size: 1.5rem; cursor: pointer; position: fixed; top: 15px; left: 15px; z-index: 1200; color: white; }}
    .overlay {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); display: none; z-index: 1050; }}
    #mainContent {{ transition: margin-left 0.3s; }}
    @media (max-width: 768px) {{ .sidebar {{ width: 200px; }} .content-shift {{ margin-left: 0 !important; }} }}
    @media (min-width: 769px) {{ .content-shift {{ margin-left: 250px !important; }} }}
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
       <li class="nav-item">
          <a class="nav-link" href="#" data-bs-toggle="modal" data-bs-target="#logoutModal">Logout</a>
        </li>
      </ul>
    </div>
  </div>
</nav>

<div class="overlay" id="overlay"></div>

<!-- Sidebar -->
<nav id="sidebar" class="sidebar p-0">
  <div class="pt-4 text-center">
    <h4 class="mb-4" style="color:white;">PetAdopt</h4>
  </div>
  <ul class="nav flex-column">
    <li>
      <a class="nav-link" href="dashboard.py?user_id={user_id}">
        <i class="bi bi-house me-2"></i> Dashboard
      </a>
    </li>
    <li>
      <a class="nav-link" href="profile_manage.py?user_id={user_id}">
        <i class="bi bi-person-circle me-2"></i> Profile Management
      </a>
    </li>
    <li>
      <a class="nav-link" href="pet_list_user.py?user_id={user_id}">
        <i class="bi bi-heart me-2"></i> Pet Adoption
      </a>
    </li>
    <li>
      <a class="nav-link" href="care_dash_user.py?user_id={user_id}">
        <i class="bi bi-journal-medical me-2"></i> Care Resources
      </a>
    </li>
    <li>
      <a class="nav-link" href="chat.py?user_id={user_id}">
        <i class="bi bi-gear me-2"></i> Communicate Adopt
      </a>
    </li>
    <li>
      <a class="nav-link" href="#">
        <i class="bi bi-gear me-2"></i> Settings
      </a>
    </li>
  </ul>
</nav>

<!-- Main Content -->
<div id="mainContent" class="container my-5">

  <h2 class="text-center text-primary mb-4">Pet Adoption Summary</h2>

  <!-- Summary Cards -->
  <div class="row mb-5 g-4">
    <div class="col-md-3">
      <div class="summary-card bg-total">
        <h4>Total Pets</h4>
        <p class="fs-3">{total_pets}</p>
      </div>
    </div>
    <div class="col-md-3">
      <div class="summary-card bg-adopted">
        <h4>Adopted Pets</h4>
        <p class="fs-3">{adopted_pets}</p>
      </div>
    </div>
    <div class="col-md-3">
      <div class="summary-card bg-pending">
        <h4>Pending Pets</h4>
        <p class="fs-3">{pending_pets}</p>
      </div>
    </div>
    <div class="col-md-3">
      <div class="summary-card bg-rejected">
        <h4>Rejected Pets</h4>
        <p class="fs-3">{rejected_pets}</p>
      </div>
    </div>
  </div>
  

  <!-- Adoption Table -->
  <div class="card shadow-sm p-4">
    <h2 class="text-center text-primary mb-4">My Adoption Applications</h2>
    <div class="table-responsive">
      <table class="table table-bordered align-middle">
        <thead>
          <tr>
            <th>Pet Image</th>
            <th>Pet Name</th>
            <th>Breed</th>
            <th>Age</th>
            <th>Status</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
""")


for app in applications:
    adoption_id, img, name, breed, age, status = app
    status_class = "status-pending" if status=="Pending" else "status-approved" if status=="Approved" else "status-rejected"
    action_btn = f'<button class="btn btn-danger btn-sm">Cancel</button>' if status=="Pending" else "-"
    print(f"""
          <tr>
            <td><img src="{img}" alt="Pet" style="width: 100px; height: 100px; object-fit: cover; border-radius: 5px;"></td>
            <td>{name}</td>
            <td>{breed}</td>
            <td>{age}</td>
            <td class="{status_class}">{status}</td>
            <td>{action_btn}</td>
          </tr>
""")

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
        <a href="user_login.py" class="btn btn-danger">Logout</a>
      </div>
    </div>
  </div>
</div>
""")


print(""" 

        </tbody>
      </table>
    </div>
  </div>

</div>





<script>
  const hamburger = document.getElementById('hamburger');
  const sidebar = document.getElementById('sidebar');
  const mainContent = document.getElementById('mainContent');
  const overlay = document.getElementById('overlay');

  hamburger.addEventListener('click', () => {
    const isOpen = sidebar.style.left === '0px';
    sidebar.style.left = isOpen ? '-250px' : '0px';
    if (window.innerWidth > 768) { mainContent.classList.toggle('content-shift'); }
    else { overlay.style.display = isOpen ? 'none' : 'block'; }
  });

  overlay.addEventListener('click', () => { sidebar.style.left = '-250px'; overlay.style.display = 'none'; });
</script>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.7/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
""")

con.close()
