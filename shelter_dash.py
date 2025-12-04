#!C:/Users/Deepak/AppData/Local/Programs/Python/Python311/python.exe
print("Content-Type: text/html\r\n\r\n")

import cgi
import cgitb
import pymysql
import os
cgitb.enable()
import os

# Get the current page filename
current_page = os.path.basename(__file__)
# --- Get shelter_id from URL/query ---
form = cgi.FieldStorage()
shelter_id = form.getvalue("shelter_id")

if not shelter_id:
    print("<h3>Shelter ID not provided. Please login first.</h3>")
    exit()

# --- Database connection ---
conn = pymysql.connect(host="localhost", user="root", password="", database="pet")
cur = conn.cursor()

# --- Fetch Shelter Name ---
cur.execute(f"SELECT organization_name FROM shelters WHERE shelter_id={shelter_id}")
shelter_data = cur.fetchone()
shelter_name = shelter_data[0] if shelter_data else "Shelter"

# --- Total Pets Listed by this Shelter ---
cur.execute(f"SELECT COUNT(*) FROM pets WHERE shelter_id={shelter_id}")
total_pets = cur.fetchone()[0]

# --- Adoption Stats for this Shelter ---
cur.execute(f"SELECT COUNT(*) FROM adoptions WHERE Shelter_ID={shelter_id} AND status='Approved'")
approved_adoptions = cur.fetchone()[0]

cur.execute(f"SELECT COUNT(*) FROM adoptions WHERE Shelter_ID={shelter_id} AND status='Pending'")
pending_adoptions = cur.fetchone()[0]

cur.execute(f"SELECT COUNT(*) FROM adoptions WHERE Shelter_ID={shelter_id} AND status='Rejected'")
rejected_adoptions = cur.fetchone()[0]

# --- Fetch Adoption Applications for this Shelter ---
cur.execute(f"""
    SELECT a.Adoption_ID, p.image_url, p.name, p.breed, p.age, a.Full_Name, a.Contact, a.status
    FROM adoptions a
    JOIN pets p ON a.Pet_ID = p.pet_id
    WHERE a.Shelter_ID={shelter_id}
""")
applications = cur.fetchall()

# --- Determine current page for active sidebar link ---
current_page = os.path.basename(__file__)

# --- Print HTML ---
print(f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{shelter_name} Dashboard</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.7/dist/css/bootstrap.min.css" rel="stylesheet">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css" rel="stylesheet">
  <style>
    body {{ font-family: 'Segoe UI', sans-serif; background-color: #f8f9fa; transition: margin-left 0.3s; }}
    .navbar {{ background: #007bff; }}
    .summary-card {{ border-radius: 12px; text-align: center; padding: 20px; color: white; }}
    .navbar-brand {{color:white !important; font-weight:bold;}}
    .navbar-nav .nav-link {{color:white !important;}}
    .navbar-nav .nav-link:hover {{color:#05b1ef !important;}}
    .bg-total {{ background-color: #007bff; }}
    .bg-approved {{ background-color: #28a745; }}
    .bg-pending {{ background-color: #ffc107; color: #000; }}
    .bg-rejected {{ background-color: #dc3545; }}
    .table thead th {{ background-color: #007bff; color: white; }}
    .status-pending {{ color: orange; font-weight: 500; }}
    .status-approved {{ color: green; font-weight: 500; }}
    .status-rejected {{ color: red; font-weight: 500; }}
    .card {{ border-radius: 15px; }}
    /* Sidebar styling */
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
    <a class="navbar-brand fw-bold ms-3" href="#">{shelter_name}</a>
    <ul class="navbar-nav ms-auto">
      <li class="nav-item"><a class="nav-link" href="home.py?shelter_id={shelter_id}">Home</a></li>
      <li class="nav-item"><a class="nav-link" href="pet_list.py?shelter_id={shelter_id}">Add Pet</a></li>
      <li class="nav-item"><a class="nav-link" href="shelter_dash.py?shelter_id={shelter_id}">Dashboard</a></li>
      <li class="nav-item">
          <a class="nav-link" href="#" data-bs-toggle="modal" data-bs-target="#logoutModal">Logout</a>
        </li>
    </ul>
  </div>
</nav>

<div class="overlay" id="overlay"></div>

<!-- Sidebar -->
<nav id="sidebar" class="sidebar p-0">
  <div class="pt-4">
    <h4 class="text-center mb-4">{shelter_name}</h4>
    <ul class="nav flex-column">
      <li>
        <a href="shelter_dash.py?shelter_id={shelter_id}" class="nav-link {'active' if 'shelter_dash.py' in current_page else ''}">
          <i class="bi bi-house me-2"></i> Dashboard
        </a>
      </li>
      <li>
        <a href="pet_list.py?shelter_id={shelter_id}" class="nav-link {'active' if 'pet_list.py' in current_page else ''}">
          <i class="bi bi-card-list me-2"></i> Pet Listings
        </a>
      </li>
      <li>
        <a href="adopt_track.py?shelter_id={shelter_id}" class="nav-link {'active' if 'adopt_track.py' in current_page else ''}">
          <i class="bi bi-clipboard-check me-2"></i> Adoption Tracking
        </a>
      </li>
      <li>
        <a href="chat_shelter.py?shelter_id={shelter_id}" class="nav-link {'active' if 'chat_shelter.py' in current_page else ''}">
          <i class="bi bi-chat-dots me-2"></i> Communicate
        </a>
        
 <li><a href="profile_manage_shelter.py?shelter_id={shelter_id}" class="nav-link>"><i class="bi bi-clipboard-check"></i> Profile Management</a></li>


    </ul>
  </div>
</nav>

<!-- Main Content -->
<div id="mainContent" class="container my-5">

  <h2 class="text-center text-primary mb-4">Shelter Dashboard</h2>

  <!-- Summary Cards -->
  <div class="row mb-5 g-4">
    <div class="col-md-3">
      <div class="summary-card bg-total">
        <h4>Total Pets</h4>
        <p class="fs-3">{total_pets}</p>
      </div>
    </div>
    <div class="col-md-3">
      <div class="summary-card bg-approved">
        <h4>Approved Adoptions</h4>
        <p class="fs-3">{approved_adoptions}</p>
      </div>
    </div>
    <div class="col-md-3">
      <div class="summary-card bg-pending">
        <h4>Pending Requests</h4>
        <p class="fs-3">{pending_adoptions}</p>
      </div>
    </div>
    <div class="col-md-3">
      <div class="summary-card bg-rejected">
        <h4>Rejected Requests</h4>
        <p class="fs-3">{rejected_adoptions}</p>
      </div>
    </div>
  </div>

  <!-- Adoption Table -->
  <div class="card shadow-sm p-4">
    <h2 class="text-center text-primary mb-4">Adoption Applications</h2>
    <div class="table-responsive">
      <table class="table table-bordered align-middle">
        <thead>
          <tr>
            <th>Pet Image</th>
            <th>Pet Name</th>
            <th>Breed</th>
            <th>Age</th>
            <th>Applicant Name</th>
            <th>Contact</th>
            <th>Status</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
""")

for app in applications:
    adoption_id, img, pet_name, breed, age, full_name, contact, status = app
    status_class = "status-pending" if status=="Pending" else "status-approved" if status=="Approved" else "status-rejected"
    action_btn = f'<a href="update_status.py?adoption_id={adoption_id}&action=approve" class="btn btn-success btn-sm me-1">Approve</a>' \
                 f'<a href="update_status.py?adoption_id={adoption_id}&action=reject" class="btn btn-danger btn-sm">Reject</a>' if status=="Pending" else "-"
    print(f"""
          <tr>
            <td><img src="{img}" class="img-fluid rounded" alt="Pet" style="max-width:80px;"></td>
            <td>{pet_name}</td>
            <td>{breed}</td>
            <td>{age}</td>
            <td>{full_name}</td>
            <td>{contact}</td>
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
            <a href="shelter_login.py" class="btn btn-danger">Logout</a>
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
