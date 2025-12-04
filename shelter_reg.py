#!C:/Users/Deepak/AppData/Local/Programs/Python/Python311/python.exe
print("Content-Type: text/html\r\n\r\n")

import cgi
import cgitb
import pymysql
import os
cgitb.enable()

# --- Connect to Database ---
con = pymysql.connect(host="localhost", user="root", password="", database="pet")
cur = con.cursor()

form = cgi.FieldStorage()
upload_dir = "uploads"
if not os.path.exists(upload_dir):
    os.makedirs(upload_dir)

# --- If updating an existing shelter ---
shelter_data = {}
shelter_id = form.getvalue("shelter_id")
if shelter_id:
    cur.execute("SELECT * FROM shelters WHERE shelter_id=%s", (shelter_id,))
    shelter_data = cur.fetchone()
    if shelter_data:
        fields_db = ["shelter_id", "organization_name", "License_no", "person_Name", "email",
                     "password", "phone", "door_no", "street", "city", "state", "postal_code",
                     "year_publish", "no_of_animals_sheltered", "status", "id_proof"]
        shelter_data = dict(zip(fields_db, shelter_data))

# --- Handle Registration / Update ---
if form.getvalue("register") or form.getvalue("update"):
    org = form.getvalue("Organization_Name")
    lic = form.getvalue("License_Number")
    person = form.getvalue("Person_Name")
    email = form.getvalue("email")
    phone = form.getvalue("Phone_Number")
    year = form.getvalue("Year_Published")
    animals = form.getvalue("No_of_Animals_Sheltered")
    door = form.getvalue("Door_No")
    street = form.getvalue("Street")
    city = form.getvalue("City")
    state = form.getvalue("State")
    postal = form.getvalue("Postal_Code")
    password = form.getvalue("password")
    status = form.getvalue("status") or "pending"

    # Handle ID Proof upload
    id_file = form['ID_Proof'] if 'ID_Proof' in form else None
    id_filename = shelter_data.get("id_proof") if shelter_data else ""
    if id_file and id_file.filename:
        id_filename = os.path.basename(id_file.filename)
        with open(os.path.join(upload_dir, id_filename), 'wb') as f:
            f.write(id_file.file.read())

    try:
        if shelter_data:  # Update
            cur.execute("""
                UPDATE shelters SET
                organization_name=%s, License_no=%s, person_Name=%s, email=%s, password=%s,
                phone=%s, door_no=%s, street=%s, city=%s, state=%s, postal_code=%s,
                year_publish=%s, no_of_animals_sheltered=%s, status=%s, id_proof=%s
                WHERE shelter_id=%s
            """, (org, lic, person, email, password, phone, door, street, city, state,
                  postal, year, animals, status, id_filename, shelter_id))
            con.commit()
            print(f"<script>alert('Shelter updated successfully!');window.location.href='shelter_login.py';</script>")
        else:  # New registration
            cur.execute("""
                INSERT INTO shelters
                (organization_name, License_no, person_Name, email, password, phone, door_no, street,
                 city, state, postal_code, year_publish, no_of_animals_sheltered, status, id_proof)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (org, lic, person, email, password, phone, door, street, city, state, postal,
                  year, animals, status, id_filename))
            con.commit()
            print("<script>alert('Shelter registered successfully!');window.location.href='shelter_login.py';</script>")
    except Exception as e:
        print(f"<script>alert('Database Error: {str(e)}');window.history.back();</script>")

# --- HTML Form ---
print("""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Shelter Registration</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.7/dist/css/bootstrap.min.css" rel="stylesheet">
<style>
body { font-family: 'Segoe UI', sans-serif; background-color: #f8f9fa; }
.card { border-radius: 15px; max-width: 1200px; margin: 30px auto; padding: 30px; }
.form-label { font-weight: 500; }
h2 { font-weight: 600; }
</style>
</head>
<body>
<div class="container my-5">
<div class="card shadow-lg">
<h2 class="text-center text-primary mb-4">Shelter Registration</h2>

<form method="post" enctype="multipart/form-data">
""")

# Include hidden field for editing
if shelter_data:
    print(f'<input type="hidden" name="shelter_id" value="{shelter_data["shelter_id"]}">')

# Grid layout for desktop
form_fields = [
    ("Organization Name", "Organization_Name", "text"),
    ("License Number", "License_Number", "text"),
    ("Person Name", "Person_Name", "text"),
    ("Email", "email", "email"),
    ("Password", "password", "password"),
    ("Phone Number", "Phone_Number", "tel"),
    ("Door No", "Door_No", "text"),
    ("Street", "Street", "text"),
    ("City", "City", "text"),
    ("State", "State", "text"),
    ("Postal Code", "Postal_Code", "text"),
    ("Year Published", "Year_Published", "number"),
    ("No. of Animals Sheltered", "No_of_Animals_Sheltered", "number")
]

# Display fields in two-column desktop format
print('<div class="row">')
for i, (label, name, type_) in enumerate(form_fields):
    value = shelter_data.get(name.lower()) if shelter_data else ""
    print(f'<div class="col-md-6 mb-3"><label class="form-label">{label}</label><input type="{type_}" class="form-control" name="{name}" value="{value}" required></div>')
print('</div>')

# ID Proof
id_value = shelter_data.get("id_proof") if shelter_data else ""
id_display = f"Current file: {id_value}" if id_value else "No file uploaded yet"
print(f"""
<div class="mb-3">
<label class="form-label">Upload ID Proof (Aadhaar)</label>
<input type="file" class="form-control" name="ID_Proof" accept=".jpg,.jpeg,.png,.pdf">
<small>{id_display}</small>
</div>
""")

# Submit
btn_name = "update" if shelter_data else "register"
btn_text = "Update Shelter" if shelter_data else "Register Shelter"
print(f'<div class="d-grid"><button type="submit" name="{btn_name}" class="btn btn-primary btn-lg">{btn_text}</button></div>')

print("""
</form>
</div>
</div>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.7/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
""")

con.close()
