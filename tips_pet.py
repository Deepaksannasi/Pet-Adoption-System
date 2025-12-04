#!C:/Users/Deepak/AppData/Local/Programs/Python/Python311/python.exe
print("Content-Type: text/html\r\n\r\n")

import cgi
import cgitb
import pymysql

cgitb.enable()

form = cgi.FieldStorage()

# --- Database Connection ---
con = pymysql.connect(host="localhost", user="root", password="", database="pet")
cur = con.cursor()

# --- Handle Form Submission for New Tip ---
if "add_tip" in form:
    title = form.getvalue("title", "")
    short_text = form.getvalue("short_text", "")
    full_text = form.getvalue("full_text", "")
    image_url = form.getvalue("image_url", "")

    cur.execute("INSERT INTO admin_tips (title, short_text, full_text, image_url) VALUES (%s,%s,%s,%s)",
                (title, short_text, full_text, image_url))
    con.commit()

# --- Fetch All Tips ---
cur.execute("SELECT * FROM admin_tips ORDER BY created_at DESC")
tips = cur.fetchall()

# --- HTML Output ---
print("""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Local Vet Tips </title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.7/dist/css/bootstrap.min.css" rel="stylesheet">
<link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css" rel="stylesheet">
<style>
body { font-family: 'Segoe UI', sans-serif; background-color: #f8f9fa; transition: margin-left 0.3s; }
.card { border-radius: 15px; }

.overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); display: none; z-index: 1050; }
#mainContent { transition: margin-left 0.3s; }
@media (max-width: 768px) { .sidebar { width: 200px; } .content-shift { margin-left: 0 !important; } }
@media (min-width: 769px) { .content-shift { margin-left: 250px !important; } }

/* Navbar Styling */
body {
  font-family: 'Segoe UI', sans-serif;
  background-color: #f8f9fa;
}

.navbar {
  background-color: #343a40;       /* Dark background */
  padding: 0.8rem 1rem;
}

.navbar-brand {
  font-weight: 600;
  color: #ffffff !important;
  letter-spacing: 0.5px;
}

.navbar-nav .nav-link {
  color: #ffffff !important;
  font-size: 16px;
  margin-right: 15px;
  transition: color 0.3s, background-color 0.3s;
}

.navbar-nav .nav-link:hover {
  color: #05b1ef !important;      /* Highlight color on hover */
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 8px 12px;
}

.navbar-toggler {
  border-color: rgba(255, 255, 255, 0.3);
}

.navbar-toggler-icon {
  filter: invert(1);               /* Make toggler white */
}

/* Adjustments for responsiveness */
@media (max-width: 992px) {
  .navbar-nav {
    text-align: center;
    background-color: #343a40;
    padding: 10px 0;
  }
  .navbar-nav .nav-link {
    margin-right: 0;
    padding: 10px;
    display: block;
  }
}

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
      </ul>
    </div>
  </div>
</nav>

<div class="overlay" id="overlay"></div>


<!-- Main Content -->
<div class="content" id="mainContent">
  <div class="container mt-5 pt-4">
    <h2 class="mb-4">Local Vet Tips</h2>
    <div class="row">
""")

# --- Loop through tips ---
for tip in tips:
    tip_id, title, short_text, full_text, image_url, created_at = tip
    print(f"""
    <div class="col-md-4 mb-4">
      <div class="card shadow-sm h-100">
        <img src="{image_url}" class="card-img-top" alt="Tip Image">
        <div class="card-body">
          <h5 class="card-title">{title}</h5>
          <p class="card-text short-text">{short_text}</p>
          <p class="card-text full-text d-none">{full_text}</p>
        </div>
      </div>
    </div>
    """)

# --- Add Tip Button ---
print("""
    </div> <!-- End row -->
    <div class="text-center my-4">
      <button class="btn btn-success btn-lg" data-bs-toggle="modal" data-bs-target="#addTipModal">
        + Add New Tip
      </button>
    </div>
  </div>
</div>

<!-- Modal -->
<div class="modal fade" id="addTipModal" tabindex="-1" aria-labelledby="addTipModalLabel" aria-hidden="true">
  <div class="modal-dialog">
    <div class="modal-content">
      <form method="post">
        <div class="modal-header">
          <h5 class="modal-title" id="addTipModalLabel">Add New Tip</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <div class="mb-3">
            <label class="form-label">Title</label>
            <input type="text" class="form-control" name="title" required>
          </div>
          <div class="mb-3">
            <label class="form-label">Short Text</label>
            <input type="text" class="form-control" name="short_text" required>
          </div>
          <div class="mb-3">
            <label class="form-label">Full Text</label>
            <textarea class="form-control" name="full_text" rows="4" required></textarea>
          </div>
          <div class="mb-3">
            <label class="form-label">Image URL</label>
            <input type="text" class="form-control" name="image_url">
          </div>
        </div>
        <div class="modal-footer">
          <button type="submit" name="add_tip" class="btn btn-primary">Add Tip</button>
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
        </div>
      </form>
    </div>
  </div>
</div>



<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.7/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
""")
