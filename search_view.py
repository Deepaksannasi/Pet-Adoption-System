#!C:/Users/Deepak/AppData/Local/Programs/Python/Python311/python.exe
print("Content-Type: text/html\r\n\r\n")
import cgi
import cgitb
import pymysql
cgitb.enable()

form = cgi.FieldStorage()
con = pymysql.connect(host="localhost", user="root", password="", database="pet")
cur = con.cursor()

# --------------------------
# Get user_id
user_id = form.getvalue("user_id")
if not user_id:
    # Redirect to login page if user_id is missing
    print("""
    <script>
        alert("Please login first!");
        window.location.href = "user_login.py";
    </script>
    """)
    exit()

# Fetch user info
cur.execute("SELECT full_name, profile_pic FROM user_reg WHERE user_id=%s", (user_id,))
user = cur.fetchone()
full_name, profile_pic = user if user else ("User", "default.png")

# --------------------------
# Handle search filters
search = form.getvalue("search") or ""
breed = form.getvalue("breed") or ""
age = form.getvalue("age") or ""
location = form.getvalue("location") or ""

# Build dynamic query
query = "SELECT pet_id, name, breed, age, location, description, image_url FROM pets WHERE 1=1"
params = []

if search:
    query += " AND name LIKE %s"
    params.append(f"%{search}%")
if breed:
    query += " AND breed LIKE %s"
    params.append(f"%{breed}%")
if age:
    query += " AND age=%s"
    params.append(age)
if location:
    query += " AND location LIKE %s"
    params.append(f"%{location}%")

cur.execute(query, tuple(params))
pets = cur.fetchall()

# --------------------------
print(f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Search & View Pets</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.7/dist/css/bootstrap.min.css" rel="stylesheet">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css" rel="stylesheet">
  <style>
    body {{ font-family: 'Segoe UI', sans-serif; background-color: #f8f9fa; transition: margin-left 0.3s; }}
    .navbar {{ background: #343a40; }}
    .card {{ border-radius: 15px; }}
    .sidebar {{
      height: 100%; width: 250px; position: fixed; top: 0; left: -250px;
      background-color: #05b1ef; overflow-x: hidden; transition: 0.3s;
      padding-top: 60px; color: white; z-index: 1100;
    }}
    .sidebar a {{ padding: 12px 20px; text-decoration: none; font-size: 18px; display: block; color: #01080f; }}
    .sidebar a:hover {{ background-color: #5a94ce; color: white; }}
    .sidebar .submenu {{ padding-left: 30px; }}
    .hamburger {{ font-size: 1.5rem; cursor: pointer; position: fixed; top: 15px; left: 15px; z-index: 1200; color: white; }}
    .overlay {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); display: none; z-index: 1050; }}
    #mainContent {{ transition: margin-left 0.3s; }}
    .pet-card img {{ object-fit: cover; height: 200px; border-radius: 15px; }}
    @media (max-width: 768px) {{ .sidebar {{ width: 200px; }} .content-shift {{ margin-left: 0 !important; }} }}
    @media (min-width: 769px) {{ .content-shift {{ margin-left: 250px !important; }} }}
    
    /* Navbar Styling */
body {{
  font-family: 'Segoe UI', sans-serif;
  background-color: #f8f9fa;
}}

.navbar {{
  background-color: #343a40;
  padding: 0.8rem 1rem;
}}

.navbar-brand {{
  font-weight: 600;
  color: #ffffff !important;
  letter-spacing: 0.5px;
}}

.navbar-nav .nav-link {{
  color: #ffffff !important;
  font-size: 16px;
  margin-right: 15px;
  transition: color 0.3s, background-color 0.3s;
}}

.navbar-nav .nav-link:hover {{
  color: #05b1ef !important;
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 8px 12px;
}}

.navbar-toggler {{
  border-color: rgba(255, 255, 255, 0.3);
}}

.navbar-toggler-icon {{
  filter: invert(1);
}}

/* Responsive Adjustments */
@media (max-width: 992px) {{
  .navbar-nav {{
    text-align: center;
    background-color: #343a40;
    padding: 10px 0;
  }}
  .navbar-nav .nav-link {{
    margin-right: 0;
    padding: 10px;
    display: block;
  }}
}}
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
       <li class="nav-item"><a class="nav-link" href="user_login.py">Login</a></li>
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
      <a class="nav-link" href="search_view.py?user_id={user_id}">
        <i class="bi bi-search me-2"></i> Search & View Pets
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
<div id="mainContent" class="container-fluid my-5">
  <div class="card shadow-sm p-4">
    <h2 class="text-center text-primary mb-4">Find Your Pet</h2>

    <form class="row g-3 mb-4" method="get">
      <input type="hidden" name="user_id" value="{user_id}">
      <div class="col-md-3">
        <label class="form-label">Search</label>
        <input type="text" class="form-control" name="search" placeholder="Search by name" value="{search}">
      </div>
      <div class="col-md-2">
        <label class="form-label">Breed</label>
        <input type="text" class="form-control" name="breed" placeholder="e.g. Labrador" value="{breed}">
      </div>
      <div class="col-md-2">
        <label class="form-label">Age</label>
        <select class="form-select" name="age">
          <option value="">Any</option>
          <option value="Puppy/Kitten" {"selected" if age=="Puppy/Kitten" else ""}>Puppy/Kitten</option>
          <option value="Adult" {"selected" if age=="Adult" else ""}>Adult</option>
        </select>
      </div>
      <div class="col-md-3">
        <label class="form-label">Location</label>
        <input type="text" class="form-control" name="location" placeholder="e.g. Chennai" value="{location}">
      </div>
      <div class="col-md-12 text-center mt-3">
        <button type="submit" class="btn btn-primary w-25">Search</button>
      </div>
    </form>

    <div class="row g-4">
""")

# Display pets dynamically
for pet in pets:
    pet_id, name, breed, pet_age, pet_location, description, image_url = pet
    image_url = image_url or "https://via.placeholder.com/300x200"
    print(f"""
      <div class="col-md-4">
        <div class="card pet-card shadow-sm">
          <img src="{image_url}" class="card-img-top" alt="Pet Image">
          <div class="card-body">
            <h5 class="card-title">{name}</h5>
            <p class="card-text">Age: {pet_age}<br>Breed: {breed}<br>Location: {pet_location}</p>
            <a href="pet_profile.py?pet_id={pet_id}&user_id={user_id}" class="btn btn-outline-primary">View Details</a>
          </div>
        </div>
      </div>
    """)

print("""
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
