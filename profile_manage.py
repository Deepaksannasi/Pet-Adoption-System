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
user_id = form.getvalue("user_id")
if isinstance(user_id, list):
    user_id = user_id[0]

if not user_id:
    print("""
        <script>
        alert('User ID not provided! Please login first.');
        window.location.href='user_login.py';
        </script>
    """)
    sys.exit()

# --- Fetch current profile ---
cur.execute("""
    SELECT full_name, email, password, phone, dob, profile_pic, id_proof,
           door_no, city, state, postal_code, status
    FROM user_reg
    WHERE user_id=%s
""", (user_id,))
user = cur.fetchone()

if not user:
    print("<h3>User not found!</h3>")
    sys.exit()

(full_name, email, password, phone, dob, old_profile_pic, old_id_proof,
 door_no, city, state, postal_code, status) = user

msg = ""

# --- Handle Profile Update ---
if form.getvalue("update_profile") == "1":
    try:
        # Helper function to safely get string value
        def safe_get(key, old_value):
            val = form.getfirst(key, old_value)  # form.getfirst ensures a single value string
            if val is None:
                return old_value
            return val

        # Read form data safely
        full_name = safe_get("full_name", full_name)
        email = safe_get("email", email)
        password = safe_get("password", password)
        phone = safe_get("phone", phone)
        dob = safe_get("dob", dob)
        door_no = safe_get("door_no", door_no)
        city = safe_get("city", city)
        state = safe_get("state", state)
        postal_code = safe_get("postal_code", postal_code)

        # Handle profile picture upload
        profile_pic = old_profile_pic
        if 'profile_pic' in form:
            profile_pic_item = form['profile_pic']
            if getattr(profile_pic_item, 'filename', None):
                profile_pic = os.path.basename(profile_pic_item.filename)
                with open(os.path.join(uploads_dir, profile_pic), "wb") as f:
                    f.write(profile_pic_item.file.read())

        # Handle ID proof upload
        id_proof = old_id_proof
        if 'id_proof' in form:
            id_proof_item = form['id_proof']
            if getattr(id_proof_item, 'filename', None):
                id_proof = os.path.basename(id_proof_item.filename)
                with open(os.path.join(uploads_dir, id_proof), "wb") as f:
                    f.write(id_proof_item.file.read())

        # Update database
        cur.execute("""
            UPDATE user_reg SET
                full_name=%s, email=%s, password=%s, phone=%s, dob=%s,
                profile_pic=%s, id_proof=%s, door_no=%s, city=%s, state=%s, postal_code=%s
            WHERE user_id=%s
        """, (full_name, email, password, phone, dob,
              profile_pic, id_proof, door_no, city, state, postal_code, user_id))
        con.commit()
        msg = "<div class='alert alert-success text-center'>Profile updated successfully!</div>"

    except Exception as e:
        msg = f"<div class='alert alert-danger text-center'>Error updating profile: {e}</div>"


# --- HTML output ---
print(f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>User Profile Management</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
<link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css" rel="stylesheet">
<style>
body {{ font-family: 'Segoe UI', sans-serif; background-color: #f8f9fa; transition: margin-left 0.3s; }}
.navbar {{ background-color: #343a40; padding: 0.8rem 1rem; }}
.navbar-brand {{ font-weight: 600; color: #ffffff !important; letter-spacing: 0.5px; }}
.navbar-nav .nav-link {{ color: #ffffff !important; font-size: 16px; margin-right: 15px; transition: color 0.3s, background-color 0.3s; }}
.navbar-nav .nav-link:hover {{ color: #05b1ef !important; background-color: rgba(255,255,255,0.1); border-radius: 8px; padding: 8px 12px; }}
.card {{ padding: 25px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); max-width: 700px; margin: 30px auto; background-color: white; }}
.status-badge {{ font-weight: bold; color: white; padding: 5px 10px; border-radius: 5px; }}
.status-pending {{ background: orange; }}
.status-approved {{ background: green; }}
.status-rejected {{ background: red; }}
.sidebar {{ height: 100%; width: 250px; position: fixed; top: 0; left: -250px; background-color: #05b1ef; overflow-x: hidden; transition: 0.3s; padding-top: 60px; color: white; z-index: 1100; }}
.sidebar a {{ padding: 12px 20px; text-decoration: none; font-size: 18px; display: block; color: #01080f; }}
.sidebar a:hover {{ background-color: #5a94ce; color: white; }}
.hamburger {{ font-size: 1.5rem; cursor: pointer; position: fixed; top: 15px; left: 15px; z-index: 1200; color: white; }}
.overlay {{ position: fixed; top:0; left:0; width:100%; height:100%; background: rgba(0,0,0,0.5); display:none; z-index:1050; }}
#mainContent {{ transition: margin-left 0.3s; }}
img.preview {{ max-width: 120px; max-height: 120px; display: block; margin-top: 5px; border-radius: 8px; }}
@media (max-width:768px) {{ .sidebar {{ width:200px; }} .content-shift {{ margin-left:0 !important; }} }}
@media (min-width:769px) {{ .content-shift {{ margin-left:250px !important; }} }}
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
       <li class="nav-item"><a class="nav-link" href="home.py?user_id={user_id}">Home</a></li>
       <li class="nav-item"><a class="nav-link" href="pet_list_user.py?user_id={user_id}">Adoption</a></li>
       <li class="nav-item"><a class="nav-link" href="care_dash_user.py?user_id={user_id}">Care Resources</a></li>
      </ul>
    </div>
  </div>
</nav>

<div class="overlay" id="overlay"></div>

<!-- Sidebar -->
<nav id="sidebar" class="sidebar p-0">
  <div class="pt-4 text-center">
    <h4 class="mb-4">PetAdopt</h4>
  </div>
  <ul class="nav flex-column">
    <li><a class="nav-link" href="dashboard.py?user_id={user_id}"><i class="bi bi-house me-2"></i> Dashboard</a></li>
    <li><a class="nav-link" href="profile_manage.py?user_id={user_id}"><i class="bi bi-person-circle me-2"></i> Profile Management</a></li>
    <li><a class="nav-link" href="pet_list_user.py?user_id={user_id}"><i class="bi bi-heart me-2"></i> Pet Adoption</a></li>
    <li><a class="nav-link" href="care_dash_user.py?user_id={user_id}"><i class="bi bi-journal-medical me-2"></i> Care Resources</a></li>
    <li> <a class="nav-link" href="chat.py?user_id={user_id}"><i class="bi bi-gear me-2"></i> Communicate Adopt</a></li>
    <li><a class="nav-link" href="#"><i class="bi bi-gear me-2"></i> Settings</a></li>
  </ul>
</nav>

<!-- Main Content -->
<div id="mainContent">
<div class="card">
  <h2 class="text-center text-primary mb-4">My Profile</h2>
  {msg}

  <form method="post" enctype="multipart/form-data">
    <input type="hidden" name="update_profile" value="1">
    <input type="hidden" name="user_id" value="{user_id}">

    <label>Full Name:</label>
    <input type="text" class="form-control" name="full_name" value="{full_name or ''}" required>

    <label>Email:</label>
    <input type="email" class="form-control" name="email" value="{email or ''}" required>

    <label>Password:</label>
    <input type="password" class="form-control" name="password" value="{password or ''}" required>

    <label>Phone:</label>
    <input type="text" class="form-control" name="phone" value="{phone or ''}" required>

    <label>Date of Birth:</label>
    <input type="date" class="form-control" name="dob" value="{dob or ''}">

    <label>Door No:</label>
    <input type="text" class="form-control" name="door_no" value="{door_no or ''}">

    <label>City:</label>
    <input type="text" class="form-control" name="city" value="{city or ''}">

    <label>State:</label>
    <input type="text" class="form-control" name="state" value="{state or ''}">

    <label>Postal Code:</label>
    <input type="text" class="form-control" name="postal_code" value="{postal_code or ''}">

    <div class="mb-3">
      <label>Profile Picture (current):</label>
      <input type="file" class="form-control" name="profile_pic">
      {"<img src='uploads/"+old_profile_pic+"' class='preview'>" if old_profile_pic else ""}
    </div>

    <div class="mb-3">
      <label>ID Proof (current):</label>
      <input type="file" class="form-control" name="id_proof">
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
