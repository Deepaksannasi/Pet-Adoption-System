#!C:/Users/Deepak/AppData/Local/Programs/Python/Python311/python.exe
print("Content-Type: text/html\r\n\r\n")
import cgi
import cgitb
import pymysql
import os

cgitb.enable()
form = cgi.FieldStorage()
con = pymysql.connect(host="localhost", user="root", password="", database="pet")
cur = con.cursor()

# Optional: Capture user_id if passed (after redirect)
user_id = form.getvalue("user_id") or ""
if form.getvalue("register"):
    Full_Name = form.getvalue("Full_Name")
    Email = form.getvalue("Email")
    Password = form.getvalue("Password")
    Phone = form.getvalue("Phone_Number")
    DOB = form.getvalue("DOB")
    Door_No = form.getvalue("Door_No")
    City = form.getvalue("City")
    State = form.getvalue("State")
    Postal_Code = form.getvalue("Postal_Code")

    # Check if email already exists
    cur.execute("SELECT user_id FROM user_reg WHERE email=%s", (Email,))
    if cur.fetchone():
        print(f"""
        <script>
            alert("Email '{Email}' already registered. Try logging in or use another email.");
            window.location.href="user_reg.py";
        </script>
        """)
    else:
        photo = form["Profile_Pic"]
        id_proof = form["Id_Proof"]

        if photo.filename and id_proof.filename:
            pho = os.path.basename(photo.filename)
            open("pets/" + pho, "wb").write(photo.file.read())

            idproof = os.path.basename(id_proof.filename)
            open("pets/" + idproof, "wb").write(id_proof.file.read())

            q = """INSERT INTO user_reg
            (full_name,email,password,phone,dob,profile_pic,id_proof,door_no,city,state,postal_code)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
            cur.execute(q, (Full_Name, Email, Password, Phone, DOB, pho, idproof, Door_No, City, State, Postal_Code))
            con.commit()

            new_user_id = cur.lastrowid
            print(f"""
            <script>
              alert("Registration Successful! Your User ID is {new_user_id}");
              window.location.href="profile_manage.py?user_id={new_user_id}";
            </script>
            """)


# --- HTML Rendering ---
print(f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>User Registration</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.7/dist/css/bootstrap.min.css" rel="stylesheet">
<link href="https://cdn.jsdelivr.net/npm/bootstrap-icons/font/bootstrap-icons.css" rel="stylesheet">
<style>
body {{ font-family: 'Segoe UI', sans-serif; background-color: #f8f9fa; transition: margin-left 0.3s; }}
.card {{ border-radius: 15px; }}
.overlay {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); display: none; z-index: 1050; }}
#mainContent {{ transition: margin-left 0.3s; }}
.register-card {{ max-width: 1200px; margin: 2% auto; }}
.form-label {{ font-weight: 500; }}
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
       <li class="nav-item"><a class="nav-link" href="pet_list_user.py">Adoption</a></li>
       <li class="nav-item"><a class="nav-link" href="care_dash.py">Care Resources</a></li>
       <li class="nav-item"><a class="nav-link" href="user_login.py">Login</a></li>
      </ul>
    </div>
  </div>
</nav>



<!-- Main Registration Form -->
<div id="mainContent" class="container my-5">
  <div class="card shadow-lg register-card p-4">
    <h2 class="text-center text-primary mb-4">User Registration</h2>
    <form method="post" enctype="multipart/form-data">
      <div class="row mb-3">
        <div class="col-md-4">
          <label class="form-label">Full Name</label>
          <input type="text" class="form-control" name="Full_Name" placeholder="Enter your name" required>
        </div>
        <div class="col-md-4">
          <label class="form-label">Email</label>
          <input type="email" class="form-control" name="Email" placeholder="Enter email" required>
        </div>
        <div class="col-md-4">
          <label class="form-label">Password</label>
          <input type="password" class="form-control" name="Password" placeholder="Enter Password" required>
        </div>
      </div>

      <div class="row mb-3">
        <div class="col-md-4">
          <label class="form-label">Phone Number</label>
          <input type="tel" class="form-control" name="Phone_Number" placeholder="Enter your number" required>
        </div>
        <div class="col-md-4">
          <label class="form-label">Date of Birth</label>
          <input type="date" class="form-control" name="DOB" required>
        </div>
        <div class="col-md-4">
          <label class="form-label">Profile Picture</label>
          <input type="file" class="form-control" name="Profile_Pic" required>
        </div>
      </div>

      <div class="row mb-3">
        <div class="col-md-4">
          <label class="form-label">ID Proof</label>
          <input type="file" class="form-control" name="Id_Proof" required>
        </div>
      </div>

      <h5 class="text-primary mt-4">Address</h5>
      <div class="row mb-3">
        <div class="col-md-3">
          <label class="form-label">Door No</label>
          <input type="text" class="form-control" name="Door_No" required>
        </div>
        <div class="col-md-3">
          <label class="form-label">City</label>
          <input type="text" class="form-control" name="City" required>
        </div>
        <div class="col-md-3">
          <label class="form-label">State</label>
          <input type="text" class="form-control" name="State" required>
        </div>
        <div class="col-md-3">
          <label class="form-label">Postal Code</label>
          <input type="text" class="form-control" name="Postal_Code" required>
        </div>
      </div>

      <div class="d-grid mt-4">
        <input type="submit" name="register" href="user_login.py" class="btn btn-primary btn-lg" value="Register">
      </div>
    </form>
  </div>
</div>



<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.7/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
""")
