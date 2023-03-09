from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from flask import jsonify
import MySQLdb.cursors
from config import app

# Intialize MySQL
mysql = MySQL(app)

@app.route('/')
def index():
    # Check if the user is logged in
    if session.get('loggedin') == True:
        userid = session['id']

        # Get all the courses that the user is enrolled in
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT courses.id, courses.name, courses.category, courses.photo FROM courses INNER JOIN users_courses ON courses.id = users_courses.courseid WHERE users_courses.userid =  %s', (userid,))
        courses = cursor.fetchall()

        return render_template('index.html', courses=courses, loggedin=True)
    else:
        return render_template('index.html', loggedin=False)



# This route handles user login request
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    # Check if "username" and "password", POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']

        # Check if user exists
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password,))
        user = cursor.fetchone()

        # If user exists
        if user:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = user['id']
            session['username'] = user['username']

            msg = 'Logged in!'
            # Show courses page
            return redirect(url_for('index'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'

    return render_template('login.html', msg=msg)



# This route handels user signup request
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    msg = ''
    # Check if "username", "password", "cpassword" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'cpassword' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        cpassword = request.form['cpassword']
        email = request.form['email']

        # Check if account exists
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = cursor.fetchone()

        # Validation
        if user:
            msg = 'Account already exists!'
        elif password != cpassword:
            msg = 'Passwords do not match!'
        elif len(password) < 6:
            msg = 'Password should be at least 6 characters!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO users (username, password, email) VALUES (%s, %s, %s)', (username, password, email,))
            mysql.connection.commit()
  
			# Output message
            msg = 'You have registered! You can now login!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'

    return render_template('signup.html', msg=msg)



@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    session.pop('role', None)

    return render_template('index.html', loggedin=False)

