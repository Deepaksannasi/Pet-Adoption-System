#!C:/Users/Deepak/AppData/Local/Programs/Python/Python311/python.exe
print("Content-Type: text/html\r\n\r\n")

import cgi, cgitb, pymysql, os
cgitb.enable()
form = cgi.FieldStorage()

# --- Get user_id from URL (login check) ---
query_string = os.environ.get("QUERY_STRING", "")
user_id = ""
if "user_id=" in query_string:
    user_id = query_string.split("user_id=")[1].split("&")[0]

if not user_id:
    print('<script>alert("Please login first!");window.location.href="user_login.py";</script>')
    exit()

# --- DB connection ---
con = pymysql.connect(host="localhost", user="root", password="", database="pet")
cur = con.cursor()

# --- Handle adoption submission ---
action = form.getvalue("action", "")
if action == "adopt":
    pet_id = form.getvalue("pet_id")
    full_name = form.getvalue("full_name")
    contact = form.getvalue("contact")
    email = form.getvalue("email")
    address = form.getvalue("address")
    previous_experience = form.getvalue("previous_experience")
    reason = form.getvalue("reason")

    if not all([pet_id, full_name, contact, email, address]):
        print("<script>alert('Please fill all required fields!');window.history.back();</script>")
    else:
        try:
            cur.execute(
                """INSERT INTO adoptions 
                   (User_ID, Pet_ID, Full_Name, Contact, Email, Address, Previous_Experience, Reason, status)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,'Pending')""",
                (user_id, pet_id, full_name, contact, email, address, previous_experience, reason)
            )
            con.commit()
            print(f'<script>alert("Adoption application submitted successfully!");window.location.href="pet_list_user.py?user_id={user_id}";</script>')
        except Exception as e:
            print(f'<script>alert("Database Error: {str(e)}");window.history.back();</script>')

# --------------------------
# Handle search filters
search = form.getvalue("search") or ""
breed = form.getvalue("breed") or ""
age = form.getvalue("age") or ""
location = form.getvalue("location") or ""

# Build dynamic query to exclude pets with approved adoption
query = """
SELECT p.pet_id, p.name, p.breed, p.age, p.location, p.description, p.image_url
FROM pets p
LEFT JOIN adoptions a ON p.pet_id = a.Pet_ID AND a.status='Approved'
WHERE a.Pet_ID IS NULL
"""
params = []

if search:
    query += " AND p.name LIKE %s"
    params.append(f"%{search}%")
if breed:
    query += " AND p.breed LIKE %s"
    params.append(f"%{breed}%")
if age:
    query += " AND p.age=%s"
    params.append(age)
if location:
    query += " AND p.location LIKE %s"
    params.append(f"%{location}%")

cur.execute(query, tuple(params))
pets = cur.fetchall()

# Fetch user info
cur.execute("SELECT full_name, profile_pic FROM user_reg WHERE user_id=%s", (user_id,))
user = cur.fetchone()
full_name, profile_pic = user if user else ("User", "default.png")

# --- HTML Output ---
print(f""" 
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Pet Listings</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.7/dist/css/bootstrap.min.css" rel="stylesheet">
<link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css" rel="stylesheet">
<style>
/* -- Your existing CSS -- */
body {{
  font-family: 'Segoe UI', sans-serif;
  background-color: #f8f9fa;
  transition: margin-left 0.3s;
}}
.navbar {{ background-color: #1e1e2d; }}
.navbar-brand {{ font-weight: 600; color: #fff !important; }}
.navbar-nav .nav-link {{ color: #fff !important; margin-right: 15px; }}
.navbar-nav .nav-link:hover {{ color:#05b1ef !important; background-color: rgba(255,255,255,0.1); border-radius:8px; }}
.card {{ border-radius: 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); transition: transform 0.2s ease-in-out; }}
.card:hover {{ transform: scale(1.02); }}
.pet-card img {{ object-fit: cover; height: 220px; border-radius: 15px 15px 0 0; }}
.sidebar {{ height:100%; width:250px; position:fixed; top:0; left:-250px; background-color:#05b1ef; padding-top:60px; color:white; overflow-x:hidden; transition:0.3s; z-index:1100; }}
.sidebar a {{ padding:12px 20px; display:block; text-decoration:none; color:#01080f; font-size:18px; }}
.sidebar a:hover {{ background-color:#5a94ce; color:white; }}
.hamburger {{ font-size:1.5rem; cursor:pointer; position:fixed; top:15px; left:15px; z-index:1200; color:white; }}
.overlay {{ position:fixed; top:0; left:0; width:100%; height:100%; background: rgba(0,0,0,0.5); display:none; z-index:1050; }}
#mainContent {{ transition: margin-left 0.3s; }}
@media(max-width:768px){{ .sidebar {{ width:200px; }} .content-shift {{ margin-left:0 !important; }} }}
@media(min-width:769px){{ .content-shift {{ margin-left:250px !important; }} }}
</style>
</head>
<body>

<!-- Navbar -->
<nav class="navbar navbar-expand-lg navbar-dark shadow-sm">
  <div class="container">
    <span class="hamburger" id="hamburger">&#9776;</span>
    <a class="navbar-brand fw-bold ms-3" href="#"> PetAdopt</a>
    <div class="collapse navbar-collapse">
      <ul class="navbar-nav ms-auto">
        <li class="nav-item"><a class="nav-link" href="home.py?user_id={user_id}">Home</a></li>
        <li class="nav-item"><a class="nav-link" href="pet_list_user.py?user_id={user_id}">Adoption</a></li>
        <li class="nav-item"><a class="nav-link" href="care_dash_user.py?user_id={user_id}">Care Resource</a></li>
      </ul>
    </div>
  </div>
</nav>

<div class="overlay" id="overlay"></div>

<!-- Sidebar -->
<nav id="sidebar" class="sidebar p-0">
  <div class="pt-4 text-center"><h4 class="mb-4">PetAdopt</h4></div>
  <ul class="nav flex-column">
    <li><a class="nav-link" href="dashboard.py?user_id={user_id}"><i class="bi bi-house me-2"></i> Dashboard</a></li>
    <li><a class="nav-link" href="profile_manage.py?user_id={user_id}"><i class="bi bi-person-circle me-2"></i> Profile Management</a></li>
    <li><a class="nav-link" href="pet_list_user.py?user_id={user_id}"><i class="bi bi-heart me-2"></i> Pet Adoption</a></li>
    <li><a class="nav-link" href="care_dash_user.py?user_id={user_id}"><i class="bi bi-journal-medical me-2"></i> Care Resources</a></li>
    <li><a class="nav-link" href="chat.py?user_id={user_id}"><i class="bi bi-gear me-2"></i> Communicate Adopt</a></li>
    <li><a class="nav-link" href="#"><i class="bi bi-gear me-2"></i> Settings</a></li>
  </ul>
</nav>

<!-- Main Content -->
<div id="mainContent" class="container my-5">
  <h2 class="text-primary fw-bold mb-4 text-center"> Available Pets for Adoption </h2>

  <!-- Search Content -->
  <div class="card shadow-sm p-4 mb-5 border-0">
    <form class="row g-3 align-items-end" method="get">
      <input type="hidden" name="user_id" value="{user_id}">
      <div class="col-md-3">
        <label class="form-label">Breed</label>
        <input type="text" class="form-control" name="breed" placeholder="e.g. Labrador" value="{breed}">
      </div>
      <div class="col-md-3">
        <label class="form-label">Age</label>
        <select class="form-select" name="age">
          <option value="">Any</option>
          {''.join([f'<option value="{i} Years" {"selected" if age==f"{i} Years" else ""}>{i} Years</option>' for i in range(1,11)])}
        </select>
      </div>
      <div class="col-md-3">
        <label class="form-label">Location</label>
        <input type="text" class="form-control" name="location" placeholder="e.g. Chennai" value="{location}">
      </div>
      <div class="col-md-3 text-md-start text-center">
        <button type="submit" class="btn btn-primary w-100 fw-semibold"><i class="bi bi-search me-2"></i>Search</button>
      </div>
    </form>
  </div>

  <div class="row g-4">
""")

# --- Display pets ---
for pet in pets:
    pet_id, name, breed, age, loc, desc, img = pet
    print(f"""
      <div class="col-md-4">
        <div class="card pet-card h-100 border-0 shadow-sm">
          <img src="{img}" class="card-img-top" alt="Pet">
          <div class="card-body">
            <h5 class="card-title text-primary">{breed}</h5>
            <p class="mb-1"><b>Age:</b> {age}</p>
            <p class="mb-3"><b>Location:</b> {loc}</p>
            <div class="d-flex justify-content-between">
              <button class="btn btn-outline-primary btn-sm" data-bs-toggle="modal" data-bs-target="#viewModal"
                data-id="{pet_id}" data-name="{name}" data-breed="{breed}" data-age="{age}" data-location="{loc}" data-desc="{desc}" data-img="{img}">
                <i class="bi bi-eye"></i> View
              </button>
              <button class="btn btn-success btn-sm" data-bs-toggle="modal" data-bs-target="#adoptModal"
                data-id="{pet_id}" data-name="{breed}">
                <i class="bi bi-heart-fill"></i> Adopt
              </button>
            </div>
          </div>
        </div>
      </div>
    """)

# --- Close search container ---
print("""</div></div>""")

# --- View Modal ---
print("""
<div class="modal fade" id="viewModal" tabindex="-1">
  <div class="modal-dialog"><div class="modal-content">
    <div class="modal-header bg-primary text-white">
      <h5 id="viewModalTitle"></h5>
      <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
    </div>
    <div class="modal-body">
      <img id="view_img" class="img-fluid mb-3 rounded" alt="Pet">
      <p><b>Breed:</b> <span id="view_breed"></span></p>
      <p><b>Age:</b> <span id="view_age"></span></p>
      <p><b>Location:</b> <span id="view_location"></span></p>
      <p id="view_desc" class="mt-2 text-secondary"></p>
    </div>
  </div></div>
</div>
""")

# --- Adopt Modal ---
print(f"""
<div class="modal fade" id="adoptModal" tabindex="-1">
  <div class="modal-dialog"><div class="modal-content">
    <form method="post">
      <input type="hidden" name="action" value="adopt">
      <input type="hidden" name="pet_id" id="adopt_pet_id">
      <div class="modal-header bg-success text-white">
        <h5 id="adoptModalTitle"></h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
      </div>
      <div class="modal-body">
        <label>Full Name</label><input type="text" name="full_name" class="form-control mb-2" required>
        <label>Contact</label><input type="text" name="contact" class="form-control mb-2" required>
        <label>Email</label><input type="email" name="email" class="form-control mb-2" required>
        <label>Address</label><textarea name="address" class="form-control mb-2" required></textarea>
        <label>Previous Experience</label>
        <select name="previous_experience" class="form-select mb-2">
          <option value="">Choose...</option>
          <option>Yes</option>
          <option>No</option>
        </select>
        <label>Reason</label><textarea name="reason" class="form-control mb-2"></textarea>
      </div>
      <div class="modal-footer">
        <input type="submit" class="btn btn-success" value="Submit Application">
        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
      </div>
    </form>
  </div></div>
</div>
""")

# --- JavaScript ---
print("""
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.7/dist/js/bootstrap.bundle.min.js"></script>
<script>
var adoptModal=document.getElementById('adoptModal');
adoptModal.addEventListener('show.bs.modal',function(event){
    var button=event.relatedTarget;
    document.getElementById('adopt_pet_id').value=button.dataset.id;
    document.getElementById('adoptModalTitle').innerText="Adopt "+button.dataset.name;
});
var viewModal=document.getElementById('viewModal');
viewModal.addEventListener('show.bs.modal',function(event){
    var button=event.relatedTarget;
    document.getElementById('viewModalTitle').innerText=button.dataset.name;
    document.getElementById('view_breed').innerText=button.dataset.breed;
    document.getElementById('view_age').innerText=button.dataset.age;
    document.getElementById('view_location').innerText=button.dataset.location;
    document.getElementById('view_desc').innerText=button.dataset.desc;
    document.getElementById('view_img').src=button.dataset.img;
});
// Sidebar toggle
const hamburger=document.getElementById('hamburger');
const sidebar=document.getElementById('sidebar');
const mainContent=document.getElementById('mainContent');
const overlay=document.getElementById('overlay');
hamburger.addEventListener('click',()=>{
  const isOpen=sidebar.style.left==='0px';
  sidebar.style.left=isOpen?'-250px':'0px';
  if(window.innerWidth>768) mainContent.classList.toggle('content-shift');
  else overlay.style.display=isOpen?'none':'block';
});
overlay.addEventListener('click',()=>{
  sidebar.style.left='-250px';
  overlay.style.display='none';
});
</script>
</body></html>
""")

con.close()
