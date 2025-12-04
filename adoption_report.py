#!C:/Users/Deepak/AppData/Local/Programs/Python/Python311/python.exe
print("Content-Type: text/html\r\n\r\n")

import cgi
import cgitb
import pymysql
import random

cgitb.enable()

# --- Database connection ---
try:
    con = pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="pet"
    )
    cur = con.cursor()
except Exception as e:
    print(f"<h2>Database Connection Error: {e}</h2>")
    exit()

# --- Fetch total adoptions ---
cur.execute("SELECT COUNT(*) FROM adoptions WHERE status='Approved'")
total_adoptions = cur.fetchone()[0]

# --- Top shelters by adoptions ---
cur.execute("""
    SELECT s.organization_name, COUNT(a.Adoption_ID) AS total
    FROM adoptions a
    LEFT JOIN shelters s ON a.Shelter_ID = s.shelter_id
    WHERE a.status='Approved'
    GROUP BY s.shelter_id
    ORDER BY total DESC
    LIMIT 5
""")
top_shelters = cur.fetchall()

# --- Top pet breeds adopted ---
cur.execute("""
    SELECT p.breed, COUNT(a.Adoption_ID) AS total
    FROM adoptions a
    LEFT JOIN pets p ON a.Pet_ID = p.pet_id
    WHERE a.status='Approved'
    GROUP BY p.breed
    ORDER BY total DESC
    LIMIT 5
""")
top_breeds = cur.fetchall()

# --- Recent approved adoptions ---
cur.execute("""
    SELECT a.Adoption_ID, u.full_name, p.name, p.breed, s.organization_name, a.Submission_Date
    FROM adoptions a
    LEFT JOIN user_reg u ON a.User_ID = u.user_id
    LEFT JOIN pets p ON a.Pet_ID = p.pet_id
    LEFT JOIN shelters s ON a.Shelter_ID = s.shelter_id
    WHERE a.status='Approved'
    ORDER BY a.Submission_Date DESC
    LIMIT 50
""")
recent_adoptions = cur.fetchall()

# --- Function to generate random pastel color ---
def random_color():
    colors = ['#ffadad','#ffd6a5','#fdffb6','#caffbf','#9bf6ff','#a0c4ff','#bdb2ff','#ffc6ff']
    return random.choice(colors)

# --- HTML Output ---
print(f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Adoption Reports</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.7/dist/css/bootstrap.min.css" rel="stylesheet">
<link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css" rel="stylesheet">
<style>
body {{
    font-family:'Segoe UI', sans-serif;
    background: linear-gradient(120deg,#f0f4f8,#d9e2ec);
    color:#102a43;
    transition: margin-left 0.3s;
}}

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
.card {{
    border-radius:15px;
    padding:20px;
    margin:20px 0;
    box-shadow:0 10px 20px rgba(0,0,0,0.1);
    background: linear-gradient(135deg,#ffffff,#e0f7fa);
    transition: transform 0.3s;
}}
.card:hover {{ transform: translateY(-5px); }}
.badge-custom {{
    font-size:0.9rem;
    color:white;
    padding:5px 10px;
    border-radius:12px;
}}
#searchInput {{ margin-bottom:15px; max-width:400px; }}
table th, table td {{ text-align:center; vertical-align:middle; }}
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

    <!-- Management toggle (no down arrow) -->
    <li class="nav-item">
        <a class="nav-link" data-bs-toggle="collapse" href="#managementLinks" role="button" aria-expanded="false" aria-controls="managementLinks">
            <i class="bi bi-gear me-2"></i> Management
        </a>
        <div class="collapse ms-3" id="managementLinks">
            <ul class="nav flex-column">
                <li class="nav-item">
                    <a class="nav-link" href="user_manage.py"><i class="bi bi-people me-2"></i> Manage Users</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="shelter_manage.py"><i class="bi bi-building me-2"></i> Manage Shelters</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="pet_manage.py"><i class="bi bi-bag-heart me-2"></i> Manage Pets</a>
                </li>
            </ul>
        </div>
    </li>

    <li><a class="nav-link" href="adoption_manage.py"><i class="bi bi-house me-2"></i> Manage Adoptions</a></li>
    <li><a class="nav-link" href="content_moderate.py"><i class="bi bi-journal-text me-2"></i> Content Moderate</a></li>
    <li><a class="nav-link" href="adoption_report.py"><i class="bi bi-bar-chart-line me-2"></i> Adoption Report</a></li>
    <li><a class="nav-link" href="care_dash_admin.py"><i class="bi bi-gear me-2"></i>Care Resource</a></li>
    <li><a class="nav-link" href="#"><i class="bi bi-gear me-2"></i> Settings</a></li>
  </ul>
</nav>

<!-- Main Content -->
<div id="mainContent" class="container my-5">
    <h1 class="mb-4 text-center">Adoption Reports</h1>

    <!-- Total Approved Adoptions -->
    <div class="card text-center">
        <h2>Total Approved Adoptions</h2>
        <h3><span class="badge" style="background:#05b1ef;">{total_adoptions}</span></h3>
    </div>

    <!-- Top Shelters -->
    <div class="card">
        <h3>Top 5 Shelters by Adoptions</h3>
        <div class="row">
""")
for shelter in top_shelters:
    color = random_color()
    print(f"""
        <div class="col-md-6 mb-3">
            <div class="card text-center" style="background:{color};">
                <h5>{shelter[0]}</h5>
                <span class="badge badge-custom" style="background:#102a43;">{shelter[1]}</span>
            </div>
        </div>
    """)

print("""
        </div>
    </div>

    <!-- Top Breeds -->
    <div class="card">
        <h3>Top 5 Adopted Breeds</h3>
        <div class="row">
""")
for breed in top_breeds:
    color = random_color()
    print(f"""
        <div class="col-md-6 mb-3">
            <div class="card text-center" style="background:{color};">
                <h5>{breed[0]}</h5>
                <span class="badge badge-custom" style="background:#102a43;">{breed[1]}</span>
            </div>
        </div>
    """)

print("""
        </div>
    </div>

    <!-- Recent Adoptions -->
    <div class="card">
        <h3>Recent Approved Adoptions</h3>
        <input type="text" id="searchInput" class="form-control" placeholder="Search by User, Pet, Breed, Shelter...">
        <table class="table table-striped table-bordered" id="adoptionTable">
            <thead class="table-dark">
                <tr>
                    <th>ID</th>
                    <th>User</th>
                    <th>Pet</th>
                    <th>Breed</th>
                    <th>Shelter</th>
                    <th>Submission Date</th>
                </tr>
            </thead>
            <tbody>
""")
for row in recent_adoptions:
    shelter_color = random_color()
    breed_color = random_color()
    print(f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td><span class='badge badge-custom' style='background:{breed_color};'>{row[3]}</span></td><td><span class='badge badge-custom' style='background:{shelter_color};'>{row[4]}</span></td><td>{row[5]}</td></tr>")

print("""
            </tbody>
        </table>
    </div>
</div>

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

// Table Search Filter
const searchInput = document.getElementById('searchInput');
searchInput.addEventListener('keyup', () => {
    const filter = searchInput.value.toLowerCase();
    const table = document.getElementById('adoptionTable');
    const trs = table.tBodies[0].getElementsByTagName('tr');
    for (let i=0; i<trs.length; i++) {
        const rowText = trs[i].textContent.toLowerCase();
        trs[i].style.display = rowText.indexOf(filter) > -1 ? '' : 'none';
    }
});
</script>

</body>
</html>
""")

cur.close()
con.close()
