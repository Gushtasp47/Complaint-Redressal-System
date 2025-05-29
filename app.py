from flask import Flask, render_template, request, redirect, session, flash, url_for
from db_config import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "letsnottalkaboutit"

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/get_complaints_ajax')
def get_complaints_ajax():
    if 'user_id' not in session:
        return {"complaints": []}

    conn = get_db_connection()
    cursor = conn.cursor()

    if session['role'] == 'Admin':
        cursor.execute("""
            SELECT c.ComplaintID, c.Title, c.Priority, s.StatusName, d.DepartmentName, u.Name AS UserName
            FROM Complaint c
            JOIN Status s ON c.StatusID = s.StatusID
            JOIN Department d ON c.DepartmentID = d.DepartmentID
            JOIN [User] u ON c.UserID = u.UserID
        """)
    else:
        cursor.execute("""
            SELECT c.ComplaintID, c.Title, c.Priority, s.StatusName
            FROM Complaint c
            JOIN Status s ON c.StatusID = s.StatusID
            WHERE c.UserID = ?
        """, (session['user_id'],))

    rows = cursor.fetchall()
    return {"complaints": [dict(zip([col[0] for col in cursor.description], row)) for row in rows]}

@app.route('/get_titles/<int:dept_id>')
def get_titles(dept_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT Title FROM IssueTitle WHERE DepartmentID = ?", (dept_id,))
    titles = [row[0] for row in cursor.fetchall()]
    return {"titles": titles}

@app.route('/get_users_ajax')
def get_users_ajax():
    if session.get('role') != 'Admin':
        return {"users": []}

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT UserID, Name, Email, Role FROM [User]")
    rows = cursor.fetchall()

    return {"users": [dict(zip([col[0] for col in cursor.description], row)) for row in rows]}

@app.route('/register', methods=['POST'])
def register():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    role = request.form['role']

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if email already exists
    cursor.execute("SELECT * FROM [User] WHERE Email = ?", (email,))
    if cursor.fetchone():
        flash("Email already registered", "danger")
        return redirect('/signup')

    import re

    if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$', password):
        flash("Password must be at least 8 characters and include letters and numbers.", "danger")
        return redirect('/signup')

    # Use plaintext now; for hashing later:
    # password = generate_password_hash(password)

    cursor.execute("INSERT INTO [User] (Name, Email, Password, Role) VALUES (?, ?, ?, ?)",
                   (name, email, password, role))
    conn.commit()

    # Log them in right after registration
    session['user_id'] = cursor.execute("SELECT SCOPE_IDENTITY()").fetchval()
    session['role'] = role
    flash("Registration successful. You are now logged in!", "success")
    return redirect('/dashboard')

@app.route('/auth', methods=['POST'])
def auth():
    email = request.form['email']
    password = request.form['password']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT UserID, Role, Password FROM [User] WHERE Email=?", (email,))
    user = cursor.fetchone()

    if user and user.Password == password:
    # if user and check_password_hash(user.password, password):
        session['user_id'] = user.UserID
        session['role'] = user.Role
        flash('Login successful!', 'success')
        return redirect('/dashboard')
    else:
        flash('Invalid email or password', 'danger')
        return redirect('/')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash("Login required", 'warning')
        return redirect('/')

    conn = get_db_connection()
    cursor = conn.cursor()

    if session['role'] == 'Admin':
        cursor.execute("""
            SELECT c.ComplaintID, u.Name AS UserName, c.Title, d.DepartmentName, c.Priority, s.StatusName
            FROM Complaint c
            JOIN [User] u ON c.UserID = u.UserID
            JOIN Department d ON c.DepartmentID = d.DepartmentID
            JOIN Status s ON c.StatusID = s.StatusID
        """)
        complaints = cursor.fetchall()
        return render_template('dashboard_admin.html', complaints=complaints)

    else:
        cursor.execute("""
            SELECT c.ComplaintID, c.Title, c.Priority, s.StatusName
            FROM Complaint c
            JOIN Status s ON c.StatusID = s.StatusID
            WHERE c.UserID = ?
        """, (session['user_id'],))
        complaints = cursor.fetchall()
        cursor.execute("""
            SELECT DepartmentID, DepartmentName
            FROM Department
        """)
        departments = cursor.fetchall()

        return render_template('dashboard_student.html', complaints=complaints, departments = departments)


@app.route('/submit_complaint', methods=['GET', 'POST'])
def submit_complaint():
    if session['role'] != 'Student':
        return "Access Denied"
    if request.method == 'POST':
        title = request.form['title']
        desc = request.form['desc']
        dept = request.form['department']
        priority = request.form['priority']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Complaint (UserID, DepartmentID, StatusID, Title, Description, Priority)
            VALUES (?, ?, 1, ?, ?, ?)
        """, (session['user_id'], dept, title, desc, priority))
        conn.commit()
        return redirect('/dashboard')
    return render_template('submit_complaint.html')


@app.route('/submit_complaint_ajax', methods=['POST'])
def submit_complaint_ajax():
    if session.get('role') != 'Student':
        return {"status": "danger", "message": "Access denied"}

    user_id = session['user_id']
    dept = request.form['department']
    title = request.form['title']
    desc = request.form['desc']
    priority = request.form['priority']
    if title == "Other":
        title = request.form.get('custom_title', 'Other')

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO Complaint (UserID, DepartmentID, StatusID, Title, Description, Priority)
            VALUES (?, ?, 1, ?, ?, ?)
        """, (user_id, dept, title, desc, priority))
        conn.commit()

        return {"status": "success", "message": "Complaint submitted successfully!"}
    except Exception as e:
        print("Error:", e)
        return {"status": "danger", "message": "Failed to submit complaint."}

@app.route('/delete_complaint/<int:id>')
def delete_complaint(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if session['role'] == 'Admin':
        cursor.execute("DELETE FROM Complaint WHERE ComplaintID=?", (id,))
    else:
        cursor.execute("DELETE FROM Complaint WHERE ComplaintID=? AND UserID=?", (id, session['user_id']))
    
    conn.commit()
    return redirect('/dashboard')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect('/')


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect('/')

    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        # Optional: Hash the password later
        cursor.execute("UPDATE [User] SET Name=?, Email=?, Password=? WHERE UserID=?",
                       (name, email, password, session['user_id']))
        conn.commit()
        flash("Profile updated", "success")
        return redirect('/dashboard')

    cursor.execute("SELECT Name, Email FROM [User] WHERE UserID=?", (session['user_id'],))
    user = cursor.fetchone()
    return render_template('profile.html', user=user)

@app.route('/manage_users')
def manage_users():
    if session.get('role') != 'Admin':
        return "Access Denied"
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT UserID, Name, Email, Role FROM [User]")
    users = cursor.fetchall()
    return render_template('manage_users.html', users=users)

@app.route('/delete_user/<int:id>')
def delete_user(id):
    if session.get('role') != 'Admin':
        return "Access Denied"
    if 'user_id' not in session:
        return redirect('/')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM [User] WHERE UserID=?", (id,))
    conn.commit()
    session.clear()
    flash("User deleted", "warning")
    return redirect('/manage_users')

@app.route('/change_role/<int:id>')
def change_role(id):
    if session.get('role') != 'Admin':
        return "Access Denied"
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT Role FROM [User] WHERE UserID=?", (id,))
    role = cursor.fetchone().Role
    new_role = 'Admin' if role == 'Student' else 'Student'
    cursor.execute("UPDATE [User] SET Role=? WHERE UserID=?", (new_role, id))
    conn.commit()
    flash(f"Role changed to {new_role}", "success")
    return redirect('/manage_users')

@app.route('/change_role_ajax/<int:id>', methods=['POST'])
def change_role_ajax(id):
    if session.get('role') != 'Admin':
        return {"status": "danger", "message": "Access denied"}

    if id == session['user_id']:
        return {"status": "danger", "message": "You cannot change your own role."}

    new_role = request.json.get('role')
    if new_role not in ('Admin', 'Student'):
        return {"status": "danger", "message": "Invalid role"}

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE [User] SET Role=? WHERE UserID=?", (new_role, id))
    conn.commit()

    return {"status": "success", "message": f"Role updated to {new_role}"}

@app.route('/delete_account')
def delete_account():
    if 'user_id' not in session:
        return redirect('/')

    user_id = session['user_id']
    
    # Step 1: Log out first
    session.clear()
    
    # Step 2: Delete account after logout
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM [User] WHERE UserID=?", (user_id,))
    conn.commit()

    flash("Your account has been deleted.", "warning")
    return redirect('/')

@app.route('/view_complaint/<int:id>')
def view_complaint(id):
    if 'user_id' not in session:
        return redirect('/')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.*, s.StatusName, d.DepartmentName
        FROM Complaint c
        JOIN Status s ON c.StatusID = s.StatusID
        JOIN Department d ON c.DepartmentID = d.DepartmentID
        WHERE c.ComplaintID = ?
    """, (id,))
    row = cursor.fetchone()

    if not row:
        flash("Complaint not found.", "danger")
        return redirect('/dashboard')

    complaint = dict(zip([col[0] for col in cursor.description], row))
    return render_template("view_complaint.html", complaint=complaint)

if __name__ == "__main__":
    app.run(debug=True)
