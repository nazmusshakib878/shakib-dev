from flask import Flask, render_template, request, redirect, jsonify
import sqlite3
import os

app = Flask(__name__)

# Database setup
def init_db():
    conn = sqlite3.connect('portfolio.db')
    c = conn.cursor()
    
    # About table
    c.execute('''CREATE TABLE IF NOT EXISTS about
                 (id INTEGER PRIMARY KEY, name TEXT, title TEXT, bio TEXT, 
                  email TEXT, phone TEXT, location TEXT)''')
    
    # Skills table
    c.execute('''CREATE TABLE IF NOT EXISTS skills
                 (id INTEGER PRIMARY KEY, name TEXT, level INTEGER, category TEXT)''')
    
    # Projects table
    c.execute('''CREATE TABLE IF NOT EXISTS projects
                 (id INTEGER PRIMARY KEY, title TEXT, description TEXT,
                  technologies TEXT, github_link TEXT, live_link TEXT)''')
    
    # Admin table
    c.execute('''CREATE TABLE IF NOT EXISTS admin
                 (id INTEGER PRIMARY KEY, username TEXT, password TEXT)''')
    
    # Add default admin if not exists
    c.execute("SELECT * FROM admin WHERE username='admin'")
    if not c.fetchone():
        c.execute("INSERT INTO admin (username, password) VALUES ('admin', 'admin123')")
    
    conn.commit()
    conn.close()

init_db()

# ==================== FRONTEND ====================
@app.route('/')
def home():
    conn = sqlite3.connect('portfolio.db')
    c = conn.cursor()
    
    c.execute("SELECT * FROM about LIMIT 1")
    about = c.fetchone()
    
    c.execute("SELECT * FROM skills")
    skills = c.fetchall()
    
    c.execute("SELECT * FROM projects")
    projects = c.fetchall()
    
    conn.close()
    
    # Convert to dict for template
    about_data = None
    if about:
        about_data = {
            'name': about[1] or 'Your Name',
            'title': about[2] or 'Web Developer',
            'bio': about[3] or 'Add your bio from admin panel',
            'email': about[4] or 'example@email.com',
            'phone': about[5] or '+880 XXX XXXXXX',
            'location': about[6] or 'City, Country'
        }
    
    return render_template('index.html', 
                         about=about_data, 
                         skills=skills, 
                         projects=projects)

# ==================== ADMIN ====================
@app.route('/admin')
def admin():
    # Check if logged in (simple session)
    if not request.args.get('logged_in'):
        return redirect('/admin/login')
    
    conn = sqlite3.connect('portfolio.db')
    c = conn.cursor()
    
    c.execute("SELECT * FROM about LIMIT 1")
    about = c.fetchone()
    
    c.execute("SELECT * FROM skills")
    skills = c.fetchall()
    
    c.execute("SELECT * FROM projects")
    projects = c.fetchall()
    
    conn.close()
    
    return render_template('admin.html', about=about, skills=skills, projects=projects)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == 'admin' and password == 'admin123':
            return redirect('/admin?logged_in=true')
        else:
            return "Login failed! Try again."
    
    return '''
    <html>
    <body style="font-family: Arial; background: #f0f0f0; display: flex; justify-content: center; align-items: center; height: 100vh;">
        <div style="background: white; padding: 40px; border-radius: 10px; box-shadow: 0 0 20px rgba(0,0,0,0.1);">
            <h2>Admin Login</h2>
            <form method="POST">
                <div style="margin-bottom: 15px;">
                    <label>Username:</label><br>
                    <input type="text" name="username" style="padding: 8px; width: 200px;" required>
                </div>
                <div style="margin-bottom: 15px;">
                    <label>Password:</label><br>
                    <input type="password" name="password" style="padding: 8px; width: 200px;" required>
                </div>
                <button type="submit" style="background: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer;">
                    Login
                </button>
            </form>
            <p style="margin-top: 20px; font-size: 12px; color: #666;">
                Default: username="admin", password="admin123"
            </p>
        </div>
    </body>
    </html>
    '''

# ==================== CRUD OPERATIONS ====================
@app.route('/update_about', methods=['POST'])
def update_about():
    data = request.form
    
    conn = sqlite3.connect('portfolio.db')
    c = conn.cursor()
    
    # Check if about exists
    c.execute("SELECT * FROM about")
    if c.fetchone():
        c.execute('''UPDATE about SET 
                    name=?, title=?, bio=?, email=?, phone=?, location=?
                    WHERE id=1''',
                  (data['name'], data['title'], data['bio'], 
                   data['email'], data['phone'], data['location']))
    else:
        c.execute('''INSERT INTO about (name, title, bio, email, phone, location)
                     VALUES (?, ?, ?, ?, ?, ?)''',
                  (data['name'], data['title'], data['bio'], 
                   data['email'], data['phone'], data['location']))
    
    conn.commit()
    conn.close()
    return redirect('/admin?logged_in=true')

@app.route('/add_skill', methods=['POST'])
def add_skill():
    conn = sqlite3.connect('portfolio.db')
    c = conn.cursor()
    
    c.execute('''INSERT INTO skills (name, level, category)
                 VALUES (?, ?, ?)''',
              (request.form['name'], request.form['level'], request.form['category']))
    
    conn.commit()
    conn.close()
    return redirect('/admin?logged_in=true')

@app.route('/delete_skill/<int:id>')
def delete_skill(id):
    conn = sqlite3.connect('portfolio.db')
    c = conn.cursor()
    
    c.execute("DELETE FROM skills WHERE id=?", (id,))
    
    conn.commit()
    conn.close()
    return redirect('/admin?logged_in=true')

@app.route('/add_project', methods=['POST'])
def add_project():
    conn = sqlite3.connect('portfolio.db')
    c = conn.cursor()
    
    c.execute('''INSERT INTO projects (title, description, technologies, github_link, live_link)
                 VALUES (?, ?, ?, ?, ?)''',
              (request.form['title'], request.form['description'],
               request.form['technologies'], request.form['github_link'],
               request.form['live_link']))
    
    conn.commit()
    conn.close()
    return redirect('/admin?logged_in=true')

@app.route('/delete_project/<int:id>')
def delete_project(id):
    conn = sqlite3.connect('portfolio.db')
    c = conn.cursor()
    
    c.execute("DELETE FROM projects WHERE id=?", (id,))
    
    conn.commit()
    conn.close()
    return redirect('/admin?logged_in=true')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
