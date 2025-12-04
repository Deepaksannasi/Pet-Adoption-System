#!C:/Users/Deepak/AppData/Local/Programs/Python/Python311/python.exe
print("Content-Type: text/html\r\n\r\n")
import cgi, cgitb, sys
cgitb.enable()
form = cgi.FieldStorage()

# --- Get user_id or shelter_id safely ---
user_id = form.getvalue("user_id")
shelter_id = form.getvalue("shelter_id")

if isinstance(user_id, list): user_id = user_id[0]
if isinstance(shelter_id, list): shelter_id = shelter_id[0]

# If neither provided, redirect
if not user_id and not shelter_id:
    print("""
        <script>
        alert('You must login first!');
        window.location.href='user_login.py';
        </script>
    """)
    sys.exit()

# Use whichever ID is provided
current_id = user_id if user_id else shelter_id
id_type = "user_id" if user_id else "shelter_id"

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
    <a class="navbar-brand fw-bold ms-3" href="#">PetAdopt</a>
    <div class="collapse navbar-collapse">
      <ul class="navbar-nav ms-auto">
        <li class="nav-item"><a class="nav-link" href="home.py?{id_type}={current_id}">Home</a></li>
        <li class="nav-item"><a class="nav-link" href="pet_list_user.py?{id_type}={current_id}">Adoption</a></li>
        <li class="nav-item"><a class="nav-link" href="care_dash_user.py?{id_type}={current_id}">Care Resources</a></li>
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
    <li><a class="nav-link" href="dashboard.py?{id_type}={current_id}"><i class="bi bi-house me-2"></i> Dashboard</a></li>
    <li><a class="nav-link" href="profile_manage.py?{id_type}={current_id}"><i class="bi bi-person-circle me-2"></i> Profile Management</a></li>
    <li><a class="nav-link" href="pet_list_user.py?{id_type}={current_id}"><i class="bi bi-heart me-2"></i> Pet Adoption</a></li>
    <li><a class="nav-link" href="care_dash_user.py?{id_type}={current_id}"><i class="bi bi-journal-medical me-2"></i> Care Resources</a></li>
    <li> <a class="nav-link" href="chat.py?{id_type}={current_id}"><i class="bi bi-gear me-2"></i> Communicate Adopt</a></li>
    <li><a class="nav-link" href="#"><i class="bi bi-gear me-2"></i> Settings</a></li>
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
        <a href="article_petcare.py?{id_type}={current_id}" class="btn btn-primary">Open</a>
      </div>
    </div>

    <!-- Tips Card -->
    <div class="col-md-4">
      <div class="card shadow-sm h-100 text-center p-3">
        <i class="bi bi-lightbulb text-warning"></i>
        <h5>Tips for New Owners</h5>
        <p>Quick advice for first-time pet parents.</p>
        <a href="tips_pet.py?{id_type}={current_id}" class="btn btn-warning">Open</a>
      </div>
    </div>

    <!-- Vets & Services Card -->
    <div class="col-md-4">
      <div class="card shadow-sm h-100 text-center p-3">
        <i class="bi bi-hospital text-success"></i>
        <h5>Local Vets & Services</h5>
        <p>Nearby clinics, grooming, and pet supply stores.</p>
        <a href="localvet_petservice.py?{id_type}={current_id}" class="btn btn-success">Open</a>
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
