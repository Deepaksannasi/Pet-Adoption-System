#!C:/Users/Deepak/AppData/Local/Programs/Python/Python311/python.exe
print("Content-Type: text/html\r\n\r\n")
import cgi, cgitb, sys,pymysql
cgitb.enable()
form = cgi.FieldStorage()
conn = pymysql.connect(host="localhost", user="root", password="", database="pet")
cur = conn.cursor()

# --- HTML Output ---
print(f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Care Resources Dashboard</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.7/dist/css/bootstrap.min.css" rel="stylesheet">
<link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css" rel="stylesheet">
<style>
body {{ font-family: 'Segoe UI', sans-serif; background-color: #f8f9fa; transition: margin-left 0.3s; }}
.navbar {{ background: #343a40; }}
.card {{ border-radius: 15px; }}
.card i {{ font-size: 40px; margin-bottom: 10px; }}
.sidebar {{ height: 100%; width: 250px; position: fixed; top: 0; left: -250px; background-color: #05b1ef; overflow-x: hidden; transition: 0.3s; padding-top: 60px; z-index: 1100; }}
.sidebar a {{ padding: 12px 20px; text-decoration: none; font-size: 18px; display: block; color: #01080f; }}
.sidebar a:hover {{ background-color: #5a94ce; color: white; }}
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

    <li><a class="nav-link" href="adoption_manage.py.py"><i class="bi bi-house me-2"></i> Manage Adoptions</a></li>
    <li><a class="nav-link" href="content_moderate.py"><i class="bi bi-journal-text me-2"></i> Content Moderate</a></li>
    <li><a class="nav-link" href="adoption_report.py"><i class="bi bi-bar-chart-line me-2"></i> Adoption Report</a></li>
    <li><a class="nav-link" href="care_dash_admin.py"><i class="bi bi-gear me-2"></i>Care Resource</a></li>
    <li><a class="nav-link" href="care_dash_shelter.py"><i class="bi bi-gear me-2"></i> Settings</a></li>
  </ul>
</nav>

<!-- Main Content -->
<div id="mainContent" class="container my-5">
  <h2 class="text-center text-primary mb-4">Care Resources </h2>
  <div class="row g-4">

    <!-- Articles Card -->
    <div class="col-md-4">
      <div class="card shadow-sm h-100 text-center p-3">
        <i class="bi bi-file-earmark-text text-primary"></i>
        <h5>Articles on Pet Care</h5>
        <p>Guides on nutrition, grooming, training, and more.</p>
        <a href="article_petcare.py" class="btn btn-primary">Open</a>
      </div>
    </div>

    <!-- Tips Card -->
    <div class="col-md-4">
      <div class="card shadow-sm h-100 text-center p-3">
        <i class="bi bi-lightbulb text-warning"></i>
        <h5>Tips for New Owners</h5>
        <p>Quick advice for first-time pet parents.</p>
        <a href="tips_pet.py" class="btn btn-warning">Open</a>
      </div>
    </div>

    <!-- Vets & Services Card -->
    <div class="col-md-4">
      <div class="card shadow-sm h-100 text-center p-3">
        <i class="bi bi-hospital text-success"></i>
        <h5>Local Vets & Services</h5>
        <p>Nearby clinics, grooming, and pet supply stores.</p>
        <a href="localvet_petservice.py" class="btn btn-success">Open</a>
      </div>
    </div>

  </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.7/dist/js/bootstrap.bundle.min.js"></script>
<script>
  const hamburger = document.getElementById('hamburger');
  const sidebar = document.getElementById('sidebar');
  const mainContent = document.getElementById('mainContent');
  const overlay = document.getElementById('overlay');

  // Toggle sidebar
  hamburger.addEventListener('click', () => {{
    const isOpen = sidebar.style.left === '0px';
    sidebar.style.left = isOpen ? '-250px' : '0px';
    if (window.innerWidth > 768) {{
      mainContent.classList.toggle('content-shift');
    }} else {{
      overlay.style.display = isOpen ? 'none' : 'block';
    }}
  }});

  // Close sidebar when clicking overlay
  overlay.addEventListener('click', () => {{
    sidebar.style.left = '-250px';
    overlay.style.display = 'none';
  }});
</script>

</body>
</html>
""")
