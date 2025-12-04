#!C:/Users/Deepak/AppData/Local/Programs/Python/Python311/python.exe
print("Content-Type: text/html\r\n\r\n")

import cgi
import cgitb
import pymysql

cgitb.enable(display=True)

form = cgi.FieldStorage()
user_id = form.getvalue("user_id")

# Fix: if user_id is a list, pick the first element
if isinstance(user_id, list):
    user_id = user_id[0]

# Convert to int if not None, else default to None for admin posts
try:
    user_id = int(user_id) if user_id else None
except:
    user_id = None

# Database connection
try:
    con = pymysql.connect(host="localhost", user="root", password="", database="pet")
    cur = con.cursor()
except pymysql.Error as e:
    print(f"<h3 style='color:red;'>Database connection error: {e}</h3>")
    exit()

# Fetch logged-in user name
if user_id:
    cur.execute("SELECT full_name FROM user_reg WHERE user_id=%s", (user_id,))
    user = cur.fetchone()
    full_name = user[0] if user else "Guest"
else:
    full_name = "Guest"

# Handle Add Article
action = form.getvalue("action")
if action == "add":
    title = form.getvalue("title")
    description = form.getvalue("description")
    image_url = form.getvalue("image_url") or None

    if title and description:
        uid = user_id if user_id else 0  # Admin posts have user_id = 0
        cur.execute(
            "INSERT INTO articles (user_id, title, description, image_url) VALUES (%s, %s, %s, %s)",
            (uid, title, description, image_url)
        )
        con.commit()

# Fetch all articles
cur.execute("""
    SELECT a.id, a.user_id, a.title, a.description, a.image_url, u.full_name
    FROM articles a
    LEFT JOIN user_reg u ON a.user_id = u.user_id
    ORDER BY a.created_at DESC
""")
articles = cur.fetchall()

# ---- HTML Page ----
print(f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Articles on Pet Care</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.7/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
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
  <h2 class="text-center text-primary mb-4">Articles on Pet Care</h2>
  <h5 class="text-center mb-4">Welcome, {full_name}!</h5>

  <!-- Add Article Button -->
  <div class="text-center mb-4">
    <button class="btn btn-success" data-bs-toggle="modal" data-bs-target="#addArticleModal">Add New Article</button>
  </div>

  <!-- Articles Row -->
  <div class="row g-4">
""")

for article in articles:
    article_id, owner_id, title, description, image_url, owner_name = article
    owner_name_display = "Admin" if owner_id == 0 else owner_name
    print(f"""
    <div class="col-md-4">
      <div class="card shadow-lg h-100">
        <img src="{image_url or 'https://via.placeholder.com/300'}" class="card-img-top" alt="{title}">
        <div class="card-body">
          <h5 class="card-title">{title}</h5>
          <p class="card-text">{description}</p>
          <p class="text-muted"><small>By: {owner_name_display}</small></p>
        </div>
      </div>
    </div>
    """)

# Modal HTML
print(f"""
  </div> <!-- row -->

  <!-- Add Article Modal -->
  <div class="modal fade" id="addArticleModal" tabindex="-1" aria-labelledby="addArticleModalLabel" aria-hidden="true">
    <div class="modal-dialog">
      <div class="modal-content">
        <form method="post">
          <input type="hidden" name="action" value="add">
          <input type="hidden" name="user_id" value="{user_id}">
          <div class="modal-header">
            <h5 class="modal-title" id="addArticleModalLabel">Add New Article</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label">Title</label>
              <input type="text" name="title" class="form-control" required>
            </div>
            <div class="mb-3">
              <label class="form-label">Description</label>
              <textarea name="description" class="form-control" rows="4" required></textarea>
            </div>
            <div class="mb-3">
              <label class="form-label">Image URL</label>
              <input type="text" name="image_url" class="form-control">
            </div>
          </div>
          <div class="modal-footer">
            <button type="submit" class="btn btn-success">Add Article</button>
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
          </div>
        </form>
      </div>
    </div>
  </div>

</div> <!-- container -->

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.7/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
""")

# Close connection
con.close()
