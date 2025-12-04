#!C:/Users/Deepak/AppData/Local/Programs/Python/Python311/python.exe
print("Content-Type: text/html\r\n\r\n")

import cgi, cgitb, pymysql, sys, io, os
cgitb.enable(display=1)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# --- Directory to save uploaded files ---
uploads_dir = "uploads"
if not os.path.exists(uploads_dir):
    os.makedirs(uploads_dir)

# --- DB Connection ---
con = pymysql.connect(host="localhost", user="root", password="", database="pet")
cur = con.cursor()

form = cgi.FieldStorage()
shelter_id = form.getvalue("shelter_id")
if isinstance(shelter_id, list):
    shelter_id = shelter_id[0]

if not shelter_id:
    print("""
        <script>
        alert('Shelter ID not provided! Please login first.');
        window.location.href='shelter_login.py';
        </script>
    """)
    sys.exit()

# --- Fetch shelter profile ---
cur.execute("""
    SELECT organization_name, License_no, person_Name, email, password, phone, door_no, street,
           city, state, postal_code, year_publish, no_of_animals_sheltered, status, id_proof
    FROM shelters
    WHERE shelter_id=%s
""", (shelter_id,))
shelter = cur.fetchone()

if not shelter:
    print("<h3>Shelter not found!</h3>")
    sys.exit()

(org_name, license_no, person_name, email, password, phone, door_no, street,
 city, state, postal_code, year_publish, animals_sheltered, status, old_id_proof) = shelter

msg = ""

# --- Handle Profile Update ---
if form.getvalue("update_profile") == "1":
    try:
        def safe_get(key, old_value):
            val = form.getfirst(key, old_value)
            return old_value if val is None else val

        # Read form data safely
        org_name = safe_get("Organization_Name", org_name)
        license_no = safe_get("License_Number", license_no)
        person_name = safe_get("Person_Name", person_name)
        email = safe_get("email", email)
        password = safe_get("password", password)
        phone = safe_get("Phone_Number", phone)
        door_no = safe_get("Door_No", door_no)
        street = safe_get("Street", street)
        city = safe_get("City", city)
        state = safe_get("State", state)
        postal_code = safe_get("Postal_Code", postal_code)
        year_publish = safe_get("Year_Published", year_publish)
        animals_sheltered = safe_get("No_of_Animals_Sheltered", animals_sheltered)

        # Handle ID Proof upload
        id_proof = old_id_proof
        if 'ID_Proof' in form:
            id_file = form['ID_Proof']
            if getattr(id_file, 'filename', None):
                id_proof = os.path.basename(id_file.filename)
                with open(os.path.join(uploads_dir, id_proof), "wb") as f:
                    f.write(id_file.file.read())

        # Update database
        cur.execute("""
            UPDATE shelters SET
                organization_name=%s, License_no=%s, person_Name=%s, email=%s,
                password=%s, phone=%s, door_no=%s, street=%s, city=%s, state=%s,
                postal_code=%s, year_publish=%s, no_of_animals_sheltered=%s, id_proof=%s
            WHERE shelter_id=%s
        """, (org_name, license_no, person_name, email, password, phone, door_no,
              street, city, state, postal_code, year_publish, animals_sheltered,
              id_proof, shelter_id))
        con.commit()
        msg = "<div class='alert alert-success text-center'>Profile updated successfully!</div>"

    except Exception as e:
        msg = f"<div class='alert alert-danger text-center'>Error updating profile: {e}</div>"

# --- HTML Output ---
print(f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Shelter Profile Management</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.7/dist/css/bootstrap.min.css" rel="stylesheet">
<link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css" rel="stylesheet">
<style>
body {{ font-family: 'Segoe UI', sans-serif; background-color: #f8f9fa; transition: margin-left 0.3s; }}
.navbar {{ background-color: #343a40; padding: 0.8rem 1rem; }}
.navbar-brand {{ font-weight: 600; color: #ffffff !important; letter-spacing: 0.5px; }}
.navbar-nav .nav-link {{ color: #ffffff !important; font-size: 16px; margin-right: 15px; }}
.navbar-nav .nav-link:hover {{ color: #05b1ef !important; }}
.card {{ padding: 25px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); max-width: 800px; margin: 30px auto; background-color: white; }}
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
img.preview {{ max-width: 120px; max-height: 120px; display: block; margin-top: 5px; border-radius: 8px; }}
.status-badge {{ font-weight: bold; color: white; padding: 5px 10px; border-radius: 5px; }}
.status-pending {{ background: orange; }}
.status-approved {{ background: green; }}
.status-rejected {{ background: red; }}
</style>
</head>
<body>

<!-- Navbar -->
<nav class="navbar navbar-expand-lg navbar-dark">
  <div class="container">
    <span class="hamburger" id="hamburger">&#9776;</span>
    <a class="navbar-brand fw-bold ms-3" href="#">{org_name}</a>
    <ul class="navbar-nav ms-auto">
      <li class="nav-item"><a class="nav-link" href="home.py?shelter_id={shelter_id}">Home</a></li>
      <li class="nav-item"><a class="nav-link" href="pet_list.py?shelter_id={shelter_id}">Add Pet</a></li>
      <li class="nav-item"><a class="nav-link" href="shelter_dash.py?shelter_id={shelter_id}">Dashboard</a></li>
      <li class="nav-item"><a class="nav-link" href="logout.py">Logout</a></li>
    </ul>
  </div>
</nav>

<div class="overlay" id="overlay"></div>

<!-- Sidebar -->
<nav id="sidebar" class="sidebar p-0">
  <div class="pt-4 text-center">
    <h4 class="mb-4">{org_name}</h4>
    <ul class="nav flex-column">
      <li>
        <a href="shelter_dash.py?shelter_id={shelter_id}" class="nav-link ">
          <i class="bi bi-house me-2"></i> Dashboard
        </a>
      </li>
      <li>
        <a href="pet_list.py?shelter_id={shelter_id}" class="nav-link">
          <i class="bi bi-card-list me-2"></i> Pet Listings
        </a>
      </li>
      <li>
        <a href="adopt_track.py?shelter_id={shelter_id}" class="nav-link">
          <i class="bi bi-clipboard-check me-2"></i> Adoption Tracking
        </a>
      </li>
      <li>
        <a href="chat_shelter.py?shelter_id={shelter_id}" class="nav-link">
          <i class="bi bi-chat-dots me-2"></i> Communicate
        </a>
      </li>
      <li>
        <a href="profile_manage_shelter.py?shelter_id={shelter_id}" class="nav-link">
          <i class="bi bi-clipboard-check me-2"></i> Profile Management
        </a>
      </li>
    </ul>
  </div>
</nav>



<!-- Main Content -->
<div id="mainContent">
<div class="card">
  <h2 class="text-center text-primary mb-4">My Shelter Profile</h2>
  {msg}

  <form method="post" enctype="multipart/form-data">
    <input type="hidden" name="update_profile" value="1">
    <input type="hidden" name="shelter_id" value="{shelter_id}">

    <label>Organization Name:</label>
    <input type="text" class="form-control" name="Organization_Name" value="{org_name or ''}" required>

    <label>License Number:</label>
    <input type="text" class="form-control" name="License_Number" value="{license_no or ''}" required>

    <label>Person Name:</label>
    <input type="text" class="form-control" name="Person_Name" value="{person_name or ''}" required>

    <label>Email:</label>
    <input type="email" class="form-control" name="email" value="{email or ''}" required>

    <label>Password:</label>
    <input type="password" class="form-control" name="password" value="{password or ''}" required>

    <label>Phone:</label>
    <input type="text" class="form-control" name="Phone_Number" value="{phone or ''}" required>

    <label>Door No:</label>
    <input type="text" class="form-control" name="Door_No" value="{door_no or ''}">

    <label>Street:</label>
    <input type="text" class="form-control" name="Street" value="{street or ''}">

    <label>City:</label>
    <input type="text" class="form-control" name="City" value="{city or ''}">

    <label>State:</label>
    <input type="text" class="form-control" name="State" value="{state or ''}">

    <label>Postal Code:</label>
    <input type="text" class="form-control" name="Postal_Code" value="{postal_code or ''}">

    <label>Year Published:</label>
    <input type="number" class="form-control" name="Year_Published" value="{year_publish or ''}">

    <label>No. of Animals Sheltered:</label>
    <input type="number" class="form-control" name="No_of_Animals_Sheltered" value="{animals_sheltered or ''}">

    <div class="mb-3">
      <label>ID Proof (current):</label>
      <input type="file" class="form-control" name="ID_Proof">
      {"<img src='uploads/"+old_id_proof+"' class='preview'>" if old_id_proof else ""}
    </div>

    <label>Status (Admin Only):</label><br>
    <span class="status-badge status-{status}">{status}</span><br><br>

    <button class="btn btn-primary mt-2" type="submit">Update Profile</button>
  </form>
</div>
</div>

<script>
const hamburger = document.getElementById('hamburger');
const sidebar = document.getElementById('sidebar');
const mainContent = document.getElementById('mainContent');
const overlay = document.getElementById('overlay');

function toggleSidebar() {{
    const isOpen = sidebar.style.left === '0px';
    sidebar.style.left = isOpen ? '-250px' : '0px';
    if(window.innerWidth >= 769) {{
        mainContent.classList.toggle('content-shift');
    }} else {{
        overlay.style.display = isOpen ? 'none' : 'block';
    }}
}}

hamburger.addEventListener('click', toggleSidebar);
overlay.addEventListener('click', () => {{
    sidebar.style.left = '-250px';
    overlay.style.display = 'none';
}});
</script>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.7/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
""")

cur.close()
con.close()
