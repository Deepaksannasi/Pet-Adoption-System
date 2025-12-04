#!C:/Users/Deepak/AppData/Local/Programs/Python/Python311/python.exe
print("Content-Type: text/html\r\n\r\n")

import sys, io, cgi, cgitb, pymysql, smtplib, ssl
from email.message import EmailMessage

# Force UTF-8 output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
cgitb.enable()
form = cgi.FieldStorage()

# --- DB Connection ---
con = pymysql.connect(host="localhost", user="root", password="", database="pet")
cur = con.cursor()

# Ensure the status column exists
cur.execute("ALTER TABLE adoptions ADD COLUMN IF NOT EXISTS status ENUM('Pending','Approved','Rejected') DEFAULT 'Pending'")

# --- Helper: send email ---
def send_email(to_email, subject, body):
    sender_email = "deepaknavin321@gmail.com"
    sender_password = "uwoz tzql phkx hjho"  # Gmail App Password

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = to_email
    msg.set_content(body)

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"<script>alert('Email sending failed: {str(e)}');</script>")
        return False

# Handle updates
if "update_adoption" in form:
    adoption_id = form.getvalue("adoption_id")
    status = form.getvalue("status")

    # Fetch user email before update
    cur.execute("SELECT Email FROM adoptions WHERE Adoption_ID=%s", (adoption_id,))
    user_email = cur.fetchone()[0]

    cur.execute("UPDATE adoptions SET status=%s WHERE Adoption_ID=%s", (status, adoption_id))
    con.commit()

    # Send email if approved
    if status == "Approved" and user_email:
        subject = "Your Pet Adoption Request is Approved!"
        body = f"Hello,\n\nCongratulations! Your adoption request (ID: {adoption_id}) has been approved.\n\nThank you for choosing PetAdopt."
        send_email(user_email, subject, body)

# Fetch pending adoption applications with pet info
try:
    cur.execute("""
        SELECT a.Adoption_ID, a.Full_Name, a.Contact, a.Email, a.Address, a.Pet_ID, a.status, 
               p.breed, p.image_url
        FROM adoptions a
        LEFT JOIN pets p ON a.Pet_ID = p.pet_id
        WHERE a.status='Pending'
    """)
    pending_adoptions = cur.fetchall()
except Exception as e:
    print(f"<h3>Error fetching pending adoptions: {e}</h3>")
    pending_adoptions = []

# Fetch all adoption applications with pet info
cur.execute("""
    SELECT a.Adoption_ID, a.Full_Name, a.Contact, a.Email, a.Address, a.Pet_ID, a.status, 
           p.breed, p.image_url
    FROM adoptions a
    LEFT JOIN pets p ON a.Pet_ID = p.pet_id
""")
all_adoptions = cur.fetchall()

# --- HTML Output ---
print("""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Adoption Applications</title>
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
#mainContent { transition: margin-left 0.3s; }
.table-title { background-color: #05b1ef; color:white; padding:10px; border-radius:5px 5px 0 0; margin-bottom:0; }
.table-container { margin-bottom:50px; box-shadow:0 0 5px rgba(0,0,0,0.1); border-radius:5px; background:white; overflow-x:auto; }
img.pet-img { max-width:80px; max-height:60px; border-radius:5px; object-fit:cover; }
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
    <li><a class="nav-link" href="care_dash_admin.py"><i class="bi bi-gear me-2"></i>Care Resource</a></li>
    <li><a class="nav-link" href="#"><i class="bi bi-gear me-2"></i> Settings</a></li>
  </ul>
</nav>

<div id="mainContent" class="container my-5">
""")

# --- Pending Adoptions Table ---
print("""
<h2 class="table-title">Pending Adoption Applications</h2>
<div class="table-container p-3">
<table class="table table-bordered table-striped text-center align-middle">
<tr class="table-dark">
<th>ID</th><th>Applicant</th><th>Contact</th><th>Email</th><th>Address</th><th>Pet Breed</th><th>Pet Image</th><th>Status</th><th>Action</th>
</tr>
""")

for a in pending_adoptions:
    pet_img = f'<img src="{a[8]}" class="pet-img">' if a[8] else "No Image"
    print(f"""
<tr>
<form method="post">
<input type="hidden" name="update_adoption" value="1">
<input type="hidden" name="adoption_id" value="{a[0]}">
<td>{a[0]}</td>
<td>{a[1]}</td>
<td>{a[2]}</td>
<td>{a[3]}</td>
<td>{a[4]}</td>
<td>{a[7]}</td>
<td>{pet_img}</td>
<td>
<select class="form-select" name="status">
<option value="Pending" {"selected" if a[6]=="Pending" else ""}>Pending</option>
<option value="Approved">Approved</option>
<option value="Rejected">Rejected</option>
</select>
</td>
<td><button class="btn btn-success btn-sm">Update</button></td>
</form>
</tr>
""")

print("</table></div>")

# --- All Adoptions Table ---
print("""
<h2 class="table-title">All Adoption Applications</h2>
<div class="table-container p-3">
<table class="table table-bordered table-striped text-center align-middle">
<tr class="table-dark">
<th>ID</th><th>Applicant</th><th>Contact</th><th>Email</th><th>Address</th><th>Pet Breed</th><th>Pet Image</th><th>Status</th><th>Action</th>
</tr>
""")

for a in all_adoptions:
    pet_img = f'<img src="{a[8]}" class="pet-img">' if a[8] else "No Image"
    print(f"""
<tr>
<form method="post">
<input type="hidden" name="update_adoption" value="1">
<input type="hidden" name="adoption_id" value="{a[0]}">
<td>{a[0]}</td>
<td>{a[1]}</td>
<td>{a[2]}</td>
<td>{a[3]}</td>
<td>{a[4]}</td>
<td>{a[7]}</td>
<td>{pet_img}</td>
<td>
<select class="form-select" name="status">
<option value="Pending" {"selected" if a[6]=="Pending" else ""}>Pending</option>
<option value="Approved" {"selected" if a[6]=="Approved" else ""}>Approved</option>
<option value="Rejected" {"selected" if a[6]=="Rejected" else ""}>Rejected</option>
</select>
</td>
<td><button class="btn btn-success btn-sm">Update</button></td>
</form>
</tr>
""")

print("""
</table></div>

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

cur.close()
con.close()
