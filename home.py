#!C:/Users/Deepak/AppData/Local/Programs/Python/Python311/python.exe
print("Content-Type: text/html\r\n\r\n")

import cgi
import cgitb
import pymysql
cgitb.enable()

# --- Database Connection ---
con = pymysql.connect(host="localhost", user="root", password="", database="pet")
cur = con.cursor()

# ✅ Fetch only approved pets that are not adopted
query = """
SELECT pet_id, name, breed, age, location, image_url, status
FROM pets
WHERE status = 'approved'
AND pet_id NOT IN (
    SELECT pet_id FROM adoptions
    WHERE status IN ('Approved')
)
ORDER BY created_at DESC
LIMIT 4;
"""
cur.execute(query)
pets = cur.fetchall()


# ✅ Start HTML
print("""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>PetAdopt - Home</title>

  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css" rel="stylesheet">
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap" rel="stylesheet">

  <style>
    body { font-family: 'Poppins', sans-serif; background-color: #f0f2f5; color: #333; }
    .navbar { background: linear-gradient(90deg, #6a11cb, #2575fc); }
    .navbar .nav-link { color: #fff !important; font-weight: 500; }
    .navbar .nav-link:hover { color: #ffdd57 !important; }

    .hero {
      background: url('https://placedog.net/1200/500?id=20') center/cover no-repeat;
      height: 480px;
      display: flex;
      align-items: center;
      justify-content: center;
      position: relative;
      text-align: center;
      color: white;
    }
    .hero::after {
      content: "";
      position: absolute;
      top:0; left:0; right:0; bottom:0;
      background: linear-gradient(to bottom, rgba(0,0,0,0.4), rgba(0,0,0,0.6));
      animation: gradientShift 8s infinite alternate;
    }
    @keyframes gradientShift {
      0% { background: linear-gradient(to bottom, rgba(0,0,0,0.4), rgba(0,0,0,0.6)); }
      100% { background: linear-gradient(to bottom, rgba(0,0,0,0.6), rgba(0,0,0,0.4)); }
    }
    .hero-content { position: relative; z-index: 1; text-shadow: 2px 2px 15px rgba(0,0,0,0.7); }
    .hero-content h1 { font-size: 3rem; font-weight: 700; }
    .hero-content p { font-size: 1.25rem; margin-top: 10px; }
    .hero-content .btn-primary { background: linear-gradient(90deg, #6a11cb, #2575fc); border: none; transition: 0.3s; }
    .hero-content .btn-primary:hover { background: linear-gradient(90deg, #2575fc, #6a11cb); }

    .card {
      border-radius: 20px;
      transition: all 0.4s ease;
      overflow: hidden;
      box-shadow: 0 4px 20px rgba(0,0,0,0.1);
      position: relative;
      backdrop-filter: blur(4px);
      background: rgba(255,255,255,0.8);
    }
    .card:hover { transform: translateY(-10px); box-shadow: 0 12px 30px rgba(0,0,0,0.2); }
    .card img { height: 220px; object-fit: cover; border-top-left-radius: 20px; border-top-right-radius: 20px; }
    .card-body { text-align: center; }
    .card-title { font-weight: 600; color: #2575fc; }
    .card-text { font-size: 0.9rem; color: #555; }
    .badge-available {
      position: absolute;
      top: 12px; right: 12px;
      background: #28a745;
      color: white;
      font-size: 0.75rem;
      padding: 5px 10px;
      border-radius: 12px;
      font-weight: 500;
    }

    .section-title { font-weight: 700; font-size: 32px; margin: 50px 0 30px; text-align: center; color: #2575fc; }

    footer {
      background: linear-gradient(90deg, #6a11cb, #2575fc);
      color: #fff;
      padding: 50px 0;
    }
    footer a { color: #fff; margin: 0 10px; transition: 0.3s; }
    footer a:hover { color: #ffdd57; transform: scale(1.2); }
  </style>
</head>
<body>

<!-- Navbar -->
<nav class="navbar navbar-expand-lg navbar-dark bg-dark">
  <div class="container">
    <a class="navbar-brand fw-bold" href="#">PetAdopt</a>
    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav"
      aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
      <span class="navbar-toggler-icon"></span>
    </button>

    <div class="collapse navbar-collapse" id="navbarNav">
      <ul class="navbar-nav ms-auto">
        <li class="nav-item"><a class="nav-link" href="home.py">Home</a></li>

        <li class="nav-item dropdown">
          <a class="nav-link dropdown-toggle" href="#" data-bs-toggle="dropdown">User</a>
          <ul class="dropdown-menu">
            <li><a class="dropdown-item" href="user_login.py"><i class="bi bi-person me-2"></i>Login</a></li>
            <li><a class="dropdown-item" href="user_reg.py"><i class="bi bi-person-plus me-2"></i>Register</a></li>
          </ul>
        </li>

        <li class="nav-item dropdown">
          <a class="nav-link dropdown-toggle" href="#" data-bs-toggle="dropdown">Shelter</a>
          <ul class="dropdown-menu">
            <li><a class="dropdown-item" href="shelter_login.py"><i class="bi bi-house-door me-2"></i>Login</a></li>
            <li><a class="dropdown-item" href="shelter_reg.py"><i class="bi bi-house-add me-2"></i>Register</a></li>
          </ul>
        </li>
      </ul>
    </div>
  </div>
</nav>

<!-- Hero Section -->
<section class="hero">
  <div class="hero-content">
    <h1 class="display-4 fw-bold">Find Your Perfect Pet</h1>
    <p class="lead">Adopt, Care, and Love - Because Every Pet Deserves a Home</p>
    <a href="#pets" class="btn btn-primary btn-lg mt-3">View Pets</a>
  </div>
</section>

<!-- Pets Section -->
<div class="container my-5" id="pets">
  <h2 class="section-title">Meet Our Lovely Pets</h2>
  <div class="row g-4">
""")

# ✅ Display Pets (up to 4)
if pets:
    for pet in pets:
        pet_id, name, breed, age, location, image, status = pet
        if not image:
            image = "https://placekitten.com/400/300"
        badge = "Available" if status == "approved" else "Pending"

        print(f"""
        <div class="col-md-3">
          <div class="card h-100">
            <span class="badge-available">{badge}</span>
            <img src="{image}" class="card-img-top" alt="{name}">
            <div class="card-body text-center">
              <h5 class="card-title">{breed}</h5>
              <p class="card-text">Age: {age}</p>
              <p class="text-muted small"><i class="bi bi-geo-alt"></i> {location}</p>
              <a href="user_login.py" class="btn btn-outline-primary btn-sm">Adopt Me</a>
            </div>
          </div>
        </div>
        """)
else:
    print("""
      <div class='col-12 text-center text-muted'>
        <h5>No approved or available pets at the moment.</h5>
      </div>
    """)

print("""
  </div>
""")

# ✅ Correct logic for showing Explore More button
if len(pets) >= 4:
    print("""
      <div class="text-center mt-4">
        <a href="pet_list_user.py" class="btn btn-primary btn-lg px-4">
          Explore More <i class="bi bi-arrow-right-circle ms-2"></i>
        </a>
      </div>
    """)

# ✅ Footer
print("""
</div>
<footer class="text-center">
  <div class="container">
    <p class="mb-2">&copy; 2025 PetAdopt | All Rights Reserved</p>
    <p><i class="bi bi-envelope"></i> contact@petadopt.com | <i class="bi bi-telephone"></i> +123-456-7890</p>
  </div>
</footer>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
""")

cur.close()
con.close()
