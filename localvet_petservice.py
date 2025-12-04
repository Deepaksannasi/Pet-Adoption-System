#!C:/Users/Deepak/AppData/Local/Programs/Python/Python311/python.exe
print("Content-Type: text/html\r\n\r\n")

import cgi, cgitb, pymysql
cgitb.enable()

form = cgi.FieldStorage()

# --- Database connection ---
try:
    con = pymysql.connect(host="localhost", user="root", password="", database="pet")
    cur = con.cursor()
except pymysql.Error as e:
    print(f"<h3 style='color:red;text-align:center;'>Database connection error: {e}</h3>")
    exit()

# --- Hardcoded Admin Info ---
admin_id = 1
admin_name = "Admin"

# --- Handle Admin Actions ---
action = form.getvalue("action")
service_id = form.getvalue("service_id")

if action == "add":
    name = form.getvalue("name")
    description = form.getvalue("description")
    phone = form.getvalue("phone")
    address = form.getvalue("address")
    image_url = form.getvalue("image_url")
    if name and description:
        cur.execute(
            "INSERT INTO local_services (name, description, phone, address, image_url, added_by) VALUES (%s,%s,%s,%s,%s,%s)",
            (name, description, phone, address, image_url, admin_id)
        )
        con.commit()

elif action == "edit" and service_id:
    name = form.getvalue("name")
    description = form.getvalue("description")
    phone = form.getvalue("phone")
    address = form.getvalue("address")
    image_url = form.getvalue("image_url")
    cur.execute(
        "UPDATE local_services SET name=%s, description=%s, phone=%s, address=%s, image_url=%s WHERE service_id=%s",
        (name, description, phone, address, image_url, service_id)
    )
    con.commit()

elif action == "delete" and service_id:
    cur.execute("DELETE FROM local_services WHERE service_id=%s", (service_id,))
    con.commit()

# --- Fetch Local Services ---
cur.execute("SELECT service_id, name, description, phone, address, image_url FROM local_services ORDER BY created_at DESC")
services = cur.fetchall()

# --- HTML Output ---
print(f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Local Vets & Services</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.7/dist/css/bootstrap.min.css" rel="stylesheet">
<link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css" rel="stylesheet">
<style>
body {{ font-family: 'Segoe UI', sans-serif; background-color: #f8f9fa; }}
.card {{ border-radius: 15px; }}
.service-card {{ border-radius: 20px; transition: transform 0.2s ease, box-shadow 0.2s ease; position:relative; }}
.service-card:hover {{ transform: translateY(-5px); box-shadow: 0 6px 20px rgba(0,0,0,0.15); }}
.service-card img {{ height: 200px; object-fit: cover; }}
.admin-btns {{ position:absolute; top:10px; right:10px; display:flex; gap:5px; }}

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
      </ul>
    </div>
  </div>
</nav>

<div class="container my-5">
<h2 class="text-center text-primary mb-4">Local Vets & Services</h2>

<!-- Admin Add Modal -->
<div class="container mb-4">
  <button class="btn btn-success mb-3" type="button" data-bs-toggle="collapse" data-bs-target="#addServiceForm">
    + Add New Service
  </button>
  <div class="collapse" id="addServiceForm">
    <div class="card p-4 shadow-sm">
      <h2 class="text-primary mb-4">Add New Local Service</h2>
      <form method="post">
        <input type="hidden" name="action" value="add">
        <div class="mb-3">
          <label class="form-label">Service Name</label>
          <input type="text" name="name" class="form-control" required>
        </div>
        <div class="mb-3">
          <label class="form-label">Description</label>
          <textarea name="description" class="form-control" rows="3" required></textarea>
        </div>
        <div class="mb-3">
          <label class="form-label">Phone</label>
          <input type="text" name="phone" class="form-control">
        </div>
        <div class="mb-3">
          <label class="form-label">Address</label>
          <input type="text" name="address" class="form-control">
        </div>
        <div class="mb-3">
          <label class="form-label">Image URL</label>
          <input type="text" name="image_url" class="form-control">
        </div>
        <button type="submit" class="btn btn-success">Add Service</button>
      </form>
    </div>
  </div>
</div>

<!-- Show Services -->
<div class="row g-4">
""")

if services:
    for s in services:
        sid, name, desc, phone, addr, img = s
        img_url = img if img else "https://via.placeholder.com/400x200.png?text=Pet+Service"
        admin_buttons = f"""
        <div class="admin-btns">
          <form method="post" style="display:inline;">
            <input type="hidden" name="action" value="delete">
            <input type="hidden" name="service_id" value="{sid}">
            <button type="submit" class="btn btn-danger btn-sm">Delete</button>
          </form>
          <button type="button" class="btn btn-warning btn-sm" onclick="editService({sid}, `{name}`, `{desc}`, `{phone}`, `{addr}`, `{img_url}`)">Edit</button>
        </div>
        """
        print(f"""
        <div class="col-md-4">
          <div class="card service-card shadow-sm">
            {admin_buttons}
            <img src="{img_url}" class="card-img-top" alt="{name}">
            <div class="card-body">
              <h5 class="card-title">{name}</h5>
              <p class="card-text">{desc}</p>
              <p><i class="bi bi-telephone"></i> {phone if phone else "N/A"}</p>
              <p><i class="bi bi-geo-alt"></i> {addr if addr else "Address not available"}</p>
            </div>
          </div>
        </div>
        """)

else:
    print("<p class='text-center text-muted'>No services available at the moment.</p>")

print("""
</div>
</div>

<script>
// Edit Service function
function editService(id, name, desc, phone, addr, img_url){
  const form = document.createElement('form');
  form.method = 'post';
  form.innerHTML = `
    <input type="hidden" name="action" value="edit">
    <input type="hidden" name="service_id" value="${id}">
    <div class="mb-3"><label>Service Name</label><input type="text" name="name" class="form-control" value="${name}" required></div>
    <div class="mb-3"><label>Description</label><textarea name="description" class="form-control" rows="3" required>${desc}</textarea></div>
    <div class="mb-3"><label>Phone</label><input type="text" name="phone" class="form-control" value="${phone}"></div>
    <div class="mb-3"><label>Address</label><input type="text" name="address" class="form-control" value="${addr}"></div>
    <div class="mb-3"><label>Image URL</label><input type="text" name="image_url" class="form-control" value="${img_url}"></div>
    <button type="submit" class="btn btn-primary">Update Service</button>
  `;
  document.body.prepend(form);
}
</script>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.7/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
""")

# --- Close Connection ---
con.close()
