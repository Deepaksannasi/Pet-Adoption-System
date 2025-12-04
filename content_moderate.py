#!C:/Users/Deepak/AppData/Local/Programs/Python/Python311/python.exe
print("Content-Type: text/html\r\n\r\n")

import sys, io, cgi, cgitb, pymysql

# --- UTF-8 Output and Error Debug ---
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
cgitb.enable(display=1, logdir=".")

form = cgi.FieldStorage()

# --- Database Connection ---
try:
    con = pymysql.connect(host="localhost", user="root", password="", database="pet")
    cur = con.cursor()
except Exception as e:
    print(f"<h2>Database Connection Error: {e}</h2>")
    exit()

# --- Fetch Pending Users ---
try:
    cur.execute("""
        SELECT user_id, full_name, email, phone, city, state, id_proof, status 
        FROM user_reg 
        WHERE status='pending'
    """)
    pending_users = cur.fetchall()
except Exception as e:
    print(f"<h3>Error fetching pending users: {e}</h3>")
    pending_users = []

# --- Fetch Pending Shelters ---
try:
    cur.execute("""
        SELECT shelter_id, organization_name, person_Name, email, phone, id_proof, city, state, status 
        FROM shelters 
        WHERE status='pending'
    """)
    pending_shelters = cur.fetchall()
except Exception as e:
    print(f"<h3>Error fetching pending shelters: {e}</h3>")
    pending_shelters = []

# --- Fetch Pending Pets ---
try:
    cur.execute("""
        SELECT pet_id, name, breed, image_url, age, location, created_at, status 
        FROM pets 
        WHERE status='pending'
    """)
    pending_pets = cur.fetchall()
except Exception as e:
    print(f"<h3>Error fetching pending pets: {e}</h3>")
    pending_pets = []

# --- Start HTML ---
print("""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Pending Approvals | PetAdopt Admin</title>
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
.table-title { background-color: #05b1ef; color:white; padding:10px; border-radius:5px 5px 0 0; margin-bottom:0; }
.table-container { margin-bottom:50px; box-shadow:0 0 5px rgba(0,0,0,0.1); border-radius:5px; background:white; overflow-x:auto; }
img.pet-img, img.id-proof { max-width:80px; max-height:60px; border-radius:5px; object-fit:cover; }
.table thead th {
  background-color: #212529;
  color: #ffffff;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
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
                <li class="nav-item"><a class="nav-link" href="pet_manage.py"><i class="bi bi-paw me-2"></i> Manage Pets</a></li>
            </ul>
        </div>
    </li>
    <li><a class="nav-link" href="adoption_manage.py"><i class="bi bi-house me-2"></i> Manage Adoptions</a></li>
    <li><a class="nav-link" href="content_moderate.py"><i class="bi bi-journal-text me-2"></i> Content Moderate</a></li>
    <li><a class="nav-link" href="adoption_report.py"><i class="bi bi-bar-chart-line me-2"></i> Adoption Report</a></li>
    <li><a class="nav-link" href="care_dash_admin.py"><i class="bi bi-gear me-2"></i> Care Resource</a></li>
  </ul>
</nav>

<!-- Main Content -->
<div id="mainContent" class="container my-5">
""")

def display_table(title, headers, rows, img_index=None, img_prefix=""):
    print(f'<h2 class="table-title">{title}</h2>')
    print('<div class="table-container p-3">')

    if not rows:
        print("<p class='text-muted'>No records found.</p>")
    else:
        print("<table class='table table-bordered table-striped text-center align-middle'>")
        print("<thead class='table-dark'><tr>")
        for header in headers:
            print(f"<th>{header}</th>")
        print("</tr></thead><tbody>")

        for row in rows:
            print("<tr>")
            for i, col in enumerate(row):
                if img_index is not None and i == img_index:
                    img_src = f"{img_prefix}{col}" if not col.startswith("http") else col
                    print(f"<td><img src='{img_src}' alt='Image' width='80' height='80' class='rounded shadow-sm'></td>")
                else:
                    print(f"<td>{col}</td>")
            print("</tr>")
        print("</tbody></table>")
    print("</div>")


# --- Display Tables with Images ---
display_table("Pending Users",
              ["ID", "Full Name", "Email", "Phone", "City", "State", "ID Proof", "Status"],
              pending_users, img_index=6, img_prefix="uploads/")

display_table("Pending Shelters",
              ["ID", "Organization Name", "Person Name", "Email", "Phone", "ID Proof", "City", "State", "Status"],
              pending_shelters, img_index=5, img_prefix="uploads/")

display_table("Pending Pets",
              ["ID", "Name", "Breed", "Image", "Age", "Location", "Created At", "Status"],
              pending_pets, img_index=3)

# --- Close DB ---
cur.close()
con.close()

print("""
</div>

<!-- JS for Sidebar -->
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
