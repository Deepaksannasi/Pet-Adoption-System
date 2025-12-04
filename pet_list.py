#!C:/Users/Deepak/AppData/Local/Programs/Python/Python311/python.exe
print("Content-Type: text/html\r\n\r\n")

import cgi, cgitb, pymysql, os
cgitb.enable()
form = cgi.FieldStorage()

# ------------------ Get shelter_id from URL ------------------
query_string = os.environ.get("QUERY_STRING", "")
shelter_id = ""
if "shelter_id=" in query_string:
    shelter_id = query_string.split("shelter_id=")[1].split("&")[0]

if not shelter_id:
    print("<h3>Error: Shelter ID not provided in URL.</h3>")
    exit()

action = form.getvalue("action", "")  # add, edit, delete, adopt

# --- DB connection ---
con = pymysql.connect(host="localhost", user="root", password="", database="pet")
cur = con.cursor()

# ------------------ Fetch Shelter Name ------------------
cur.execute("SELECT organization_name FROM shelters WHERE shelter_id=%s", (shelter_id,))
shelter_data = cur.fetchone()
shelter_name = shelter_data[0] if shelter_data else "Shelter"

# ------------------ Handle form submissions ------------------
if action == "add":
    name = form.getvalue("name")
    breed = form.getvalue("breed")
    age = form.getvalue("age")
    location = form.getvalue("location")
    desc = form.getvalue("description")
    img = form.getvalue("image_url")
    cur.execute(
        "INSERT INTO pets (name, breed, age, location, description, image_url, shelter_id) VALUES (%s,%s,%s,%s,%s,%s,%s)",
        (name, breed, age, location, desc, img, shelter_id)
    )
    con.commit()

elif action == "edit":
    pet_id = form.getvalue("pet_id")
    name = form.getvalue("name")
    breed = form.getvalue("breed")
    age = form.getvalue("age")
    location = form.getvalue("location")
    desc = form.getvalue("description")
    img = form.getvalue("image_url")
    cur.execute(
        "UPDATE pets SET name=%s, breed=%s, age=%s, location=%s, description=%s, image_url=%s WHERE pet_id=%s AND shelter_id=%s",
        (name, breed, age, location, desc, img, pet_id, shelter_id)
    )
    con.commit()

elif action == "delete":
    pet_id = form.getvalue("pet_id")
    cur.execute("DELETE FROM pets WHERE pet_id=%s AND shelter_id=%s", (pet_id, shelter_id))
    con.commit()

elif action == "adopt":
    pet_id = form.getvalue("pet_id")
    user_id = 0
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
            print(f'<script>alert("Adoption application submitted successfully!");window.location.href="pet_list.py?shelter_id={shelter_id}";</script>')
        except Exception as e:
            print(f'<script>alert("Database Error: {str(e)}");window.history.back();</script>')

# ------------------ Fetch Data ------------------
cur.execute("SELECT pet_id, name, breed, age, location, description, image_url FROM pets WHERE shelter_id=%s", (shelter_id,))
pets = cur.fetchall()

cur.execute("""
SELECT a.adoption_id, p.name, a.full_name, a.contact, a.email, a.address,
       a.previous_experience, a.reason, a.submission_date
FROM adoptions a
JOIN pets p ON a.pet_id = p.pet_id
WHERE p.shelter_id=%s
ORDER BY a.submission_date DESC
""", (shelter_id,))
applications = cur.fetchall()

current_page = os.path.basename(__file__)

# ------------------ HTML Output ------------------
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
body {{font-family: 'Segoe UI', sans-serif; background-color: #f8f9fa; transition: margin-left 0.3s;}}
.navbar {{background: #343a40;}}
.navbar-brand {{color:white !important; font-weight:bold;}}
.navbar-nav .nav-link {{color:white !important;}}
.navbar-nav .nav-link:hover {{color:#05b1ef !important;}}
.summary-card {{border-radius:12px; text-align:center; padding:20px; color:white;}}
.bg-total {{background-color:#007bff;}}
.bg-approved {{background-color:#28a745;}}
.bg-pending {{background-color:#ffc107; color:#000;}}
.bg-rejected {{background-color:#dc3545;}}
.table thead th {{background-color:#007bff; color:white;}}
.status-pending {{color:orange; font-weight:500;}}
.status-approved {{color:green; font-weight:500;}}
.status-rejected {{color:red; font-weight:500;}}

/* Sidebar */
.sidebar {{height:100%; width:250px; position:fixed; top:0; left:-250px; background-color:#05b1ef; overflow-x:hidden; transition:0.3s; padding-top:60px; z-index:1100;}}
.sidebar a {{padding:12px 20px; text-decoration:none; font-size:18px; display:block; color:#01080f;}}
.sidebar a:hover {{background-color:#5a94ce; color:white;}}
.sidebar .active {{background-color:#343a40; color:white;}}
.hamburger {{font-size:1.5rem; cursor:pointer; position:fixed; top:15px; left:15px; z-index:1200; color:white;}}
.overlay {{position:fixed; top:0; left:0; width:100%; height:100%; background: rgba(0,0,0,0.5); display:none; z-index:1050;}}
#mainContent {{transition: margin-left 0.3s;}}
@media (min-width:769px) {{ .content-shift {{margin-left:250px !important;}} }}
</style>
</head>
<body>

<!-- Navbar -->
<nav class="navbar navbar-expand-lg navbar-dark">
<div class="container">
<span class="hamburger" id="hamburger">&#9776;</span>
<a class="navbar-brand fw-bold ms-3" href="#">{shelter_name}</a>
<ul class="navbar-nav ms-auto">
<li class="nav-item"><a class="nav-link" href="home.py">Home</a></li>
<li class="nav-item"><a class="nav-link" href="pet_list.py?shelter_id={shelter_id}">Add Pet</a></li>
<li class="nav-item"><a class="nav-link" href="shelter_dash.py?shelter_id={shelter_id}">Dashboard</a></li>
<li class="nav-item"><a class="nav-link" href="logout.py">Logout</a></li>
</ul>
</div>
</nav>

<div class="overlay" id="overlay"></div>

<!-- Sidebar -->
<nav id="sidebar" class="sidebar p-0">
<div class="pt-4">
<h4 class="text-center mb-4">{shelter_name}</h4>
<ul class="nav flex-column">
<li><a href="shelter_dash.py?shelter_id={shelter_id}" class="nav-link "><i class="bi bi-house"></i> Dashboard</a></li>
<li><a href="pet_list.py?shelter_id={shelter_id}" class="nav-link "><i class="bi bi-card-list"></i> Pet Listings</a></li>
<li><a href="adopt_track.py?shelter_id={shelter_id}" class="nav-link"><i class="bi bi-clipboard-check"></i> Adoption Tracking</a></li>
<li><a href="chat_shelter.py?shelter_id={shelter_id}" class="nav-link"><i class="bi bi-chat-dots"></i> Communicate</a></li>
 <li><a href="profile_manage_shelter.py?shelter_id={shelter_id}" class="nav-link>"><i class="bi bi-clipboard-check"></i> Profile Management</a></li>
</ul>
</div>
</nav>

<div id="mainContent" class="container my-4">
<h2>Pet Listings</h2>
<button class="btn btn-primary mb-3" data-bs-toggle="modal" data-bs-target="#addModal">Add Pet</button>
<div class="row g-4">
""")

# ---- Pets Display ----
for pet in pets:
    pet_id, name, breed, age, location, desc, img = pet
    print(f"""
    <div class="col-md-4">
      <div class="card">
        <img src="{img}" class="card-img-top" alt="Pet">
        <div class="card-body">
          <h5 class="card-title">{name}</h5>
          <p>Breed: {breed} | Age: {age} | Location: {location}</p>
          <button class="btn btn-success" data-bs-toggle="modal" data-bs-target="#adoptModal" 
            data-id="{pet_id}">Adopt</button>
          <button class="btn btn-warning" data-bs-toggle="modal" data-bs-target="#editModal"
            data-id="{pet_id}" data-name="{name}" data-breed="{breed}" data-age="{age}" data-location="{location}" data-desc="{desc}" data-img="{img}">Edit</button>
          <button type="button" class="btn btn-danger" data-bs-toggle="modal" data-bs-target="#deleteModal"
            data-id="{pet_id}">Delete</button>
        </div>
      </div>
    </div>
    """)

print("</div>")  # close row

# ---- Adoption Applications Table ----
print("""
<h2 class="mt-5">Adoption Applications</h2>
<div class="table-responsive">
<table class="table table-bordered">
<thead class="table-dark">
<tr>
<th>#</th><th>Pet Name</th><th>Applicant</th><th>Contact</th><th>Email</th><th>Address</th><th>Prev Experience</th><th>Reason</th><th>Date</th>
</tr>
</thead>
<tbody>
""")

if applications:
    for app in applications:
        adoption_id, pet_name, full_name, contact, email, address, prev_exp, reason, date = app
        print(f"<tr><td>{adoption_id}</td><td>{pet_name}</td><td>{full_name}</td><td>{contact}</td><td>{email}</td><td>{address}</td><td>{prev_exp}</td><td>{reason}</td><td>{date}</td></tr>")
else:
    print("<tr><td colspan='9'>No applications yet.</td></tr>")

print("</tbody></table></div></div>")

# ---- Add/Edit/Delete/Adopt Modals ----
print(f"""
<!-- Add Pet Modal -->
<div class="modal fade" id="addModal" tabindex="-1">
  <div class="modal-dialog">
    <div class="modal-content">
      <form method="post">
        <div class="modal-header">
          <h5 class="modal-title">Add New Pet</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <input type="hidden" name="action" value="add">
          <div class="mb-3"><label>Name</label><input type="text" name="name" class="form-control" required></div>
          <div class="mb-3"><label>Breed</label><input type="text" name="breed" class="form-control" required></div>
          <div class="mb-3"><label>Age</label><input type="text" name="age" class="form-control" required></div>
          <div class="mb-3"><label>Location</label><input type="text" name="location" class="form-control" required></div>
          <div class="mb-3"><label>Description</label><textarea name="description" class="form-control" required></textarea></div>
          <div class="mb-3"><label>Image URL</label><input type="text" name="image_url" class="form-control" required></div>
        </div>
        <div class="modal-footer">
          <button type="submit" class="btn btn-primary">Add Pet</button>
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
        </div>
      </form>
    </div>
  </div>
</div>

<!-- Edit Pet Modal -->
<div class="modal fade" id="editModal" tabindex="-1">
  <div class="modal-dialog">
    <div class="modal-content">
      <form method="post">
        <div class="modal-header">
          <h5 class="modal-title">Edit Pet</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <input type="hidden" name="action" value="edit">
          <input type="hidden" name="pet_id" id="editPetId">
          <div class="mb-3"><label>Name</label><input type="text" name="name" id="editPetName" class="form-control" required></div>
          <div class="mb-3"><label>Breed</label><input type="text" name="breed" id="editPetBreed" class="form-control" required></div>
          <div class="mb-3"><label>Age</label><input type="text" name="age" id="editPetAge" class="form-control" required></div>
          <div class="mb-3"><label>Location</label><input type="text" name="location" id="editPetLocation" class="form-control" required></div>
          <div class="mb-3"><label>Description</label><textarea name="description" id="editPetDesc" class="form-control" required></textarea></div>
          <div class="mb-3"><label>Image URL</label><input type="text" name="image_url" id="editPetImg" class="form-control" required></div>
        </div>
        <div class="modal-footer">
          <button type="submit" class="btn btn-warning">Update Pet</button>
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
        </div>
      </form>
    </div>
  </div>
</div>

<!-- Delete Pet Modal -->
<div class="modal fade" id="deleteModal" tabindex="-1">
  <div class="modal-dialog">
    <div class="modal-content">
      <form method="post">
        <div class="modal-header">
          <h5 class="modal-title">Delete Pet</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <input type="hidden" name="action" value="delete">
          <input type="hidden" name="pet_id" id="deletePetId">
          <p>Are you sure you want to delete this pet?</p>
        </div>
        <div class="modal-footer">
          <button type="submit" class="btn btn-danger">Delete</button>
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
        </div>
      </form>
    </div>
  </div>
</div>

<!-- Adopt Pet Modal -->
<div class="modal fade" id="adoptModal" tabindex="-1">
  <div class="modal-dialog">
    <div class="modal-content">
      <form method="post">
        <div class="modal-header">
          <h5 class="modal-title">Adopt Pet</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <input type="hidden" name="action" value="adopt">
          <input type="hidden" name="pet_id" id="adoptPetId">
          <div class="mb-3"><label>Full Name</label><input type="text" name="full_name" class="form-control" required></div>
          <div class="mb-3"><label>Contact</label><input type="text" name="contact" class="form-control" required></div>
          <div class="mb-3"><label>Email</label><input type="email" name="email" class="form-control" required></div>
          <div class="mb-3"><label>Address</label><textarea name="address" class="form-control" required></textarea></div>
          <div class="mb-3"><label>Previous Experience</label><input type="text" name="previous_experience" class="form-control"></div>
          <div class="mb-3"><label>Reason for Adoption</label><textarea name="reason" class="form-control"></textarea></div>
        </div>
        <div class="modal-footer">
          <button type="submit" class="btn btn-success">Submit Application</button>
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
        </div>
      </form>
    </div>
  </div>
</div>

<!-- JS to populate Edit, Delete, Adopt modals -->
<script>
var editModal = document.getElementById('editModal');
editModal.addEventListener('show.bs.modal', function (event) {{
  var button = event.relatedTarget;
  document.getElementById('editPetId').value = button.getAttribute('data-id');
  document.getElementById('editPetName').value = button.getAttribute('data-name');
  document.getElementById('editPetBreed').value = button.getAttribute('data-breed');
  document.getElementById('editPetAge').value = button.getAttribute('data-age');
  document.getElementById('editPetLocation').value = button.getAttribute('data-location');
  document.getElementById('editPetDesc').value = button.getAttribute('data-desc');
  document.getElementById('editPetImg').value = button.getAttribute('data-img');
}});

var deleteModal = document.getElementById('deleteModal');
deleteModal.addEventListener('show.bs.modal', function (event) {{
  var button = event.relatedTarget;
  document.getElementById('deletePetId').value = button.getAttribute('data-id');
}});

var adoptModal = document.getElementById('adoptModal');
adoptModal.addEventListener('show.bs.modal', function (event) {{
  var button = event.relatedTarget;
  document.getElementById('adoptPetId').value = button.getAttribute('data-id');
}});
</script>

<script>
const hamburger = document.getElementById('hamburger');
const sidebar = document.getElementById('sidebar');
const mainContent = document.getElementById('mainContent');
const overlay = document.getElementById('overlay');

hamburger.addEventListener('click', () => {{
  const isOpen = sidebar.style.left === '0px';
  sidebar.style.left = isOpen ? '-250px' : '0px';
  if (window.innerWidth > 768) {{ mainContent.classList.toggle('content-shift'); }}
  else {{ overlay.style.display = isOpen ? 'none' : 'block'; }}
}});
overlay.addEventListener('click', () => {{ sidebar.style.left = '-250px'; overlay.style.display = 'none'; }});
</script>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.7/dist/js/bootstrap.bundle.min.js"></script>
</body></html>
""")
con.close()
