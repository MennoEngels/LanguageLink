from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from flask_mysqldb import MySQL
from flask import jsonify
import MySQLdb.cursors, os
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



@app.route('/courses')
def courses():
    # Redirect to login page if not logged in
    if session.get('loggedin') != True:
        return redirect(url_for('login'))

    userid = session.get('id')

    # Get all the courses that the user is not enrolled in
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM courses WHERE id NOT IN (SELECT courseid FROM users_courses WHERE userid = %s)', (userid,))
    courses = cursor.fetchall()

    # Render the courses template with the list of available courses
    return render_template('courses.html', courses=courses)



# This route handles requests to enroll a user into a course
@app.route('/enroll/<int:id>', methods=['GET', 'POST'])
@app.route('/enroll', methods=['GET', 'POST'], defaults={'id': None})
def enroll_user(courseid):
    userid = session.get('id')

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    try:
        # Check if the user is already enrolled in the course
        enrolled = is_enrolled(userid=userid, courseid=courseid)

        if not enrolled:
            # If the user is not enrolled, enroll the user
            cursor.execute('INSERT INTO users_courses (userid, courseid) VALUES (%s, %s)', (userid, courseid,))

            # Retrieve all slides for this course
            cursor.execute('SELECT slides.id FROM slides INNER JOIN lessons ON slides.lessonid = lessons.lesson_id INNER JOIN courses ON lessons.courseid = courses.id WHERE courses.id = %s', (courseid,))
            slide_ids = cursor.fetchall()

            # Create a list of tuples that maps each slide ID from the course with the current userid
            values = [(slide_id['id'], userid) for slide_id in slide_ids]

            # Creating a new instance for each slide specific to the current user
            cursor.executemany('INSERT INTO users_slides (slideid, userid) VALUES (%s, %s)', values)

            mysql.connection.commit()

            # Get the course and its lessons
            cursor.execute('SELECT * FROM courses WHERE id =  %s', (courseid,))
            course = cursor.fetchone()
            cursor.execute('SELECT * FROM lessons WHERE courseid =  %s', (courseid,))
            lessons = cursor.fetchall()
    except Exception as e:
        mysql.connection.rollback()
        raise e
    finally:
        cursor.close()

    # Render the course page with the retrieved course and lessons
    return render_template('course.html', course=course, lessons=lessons)



# This route handles requests to remove a course from the user's enrolled courses list
@app.route('/removecourse/<int:id>', methods=['GET', 'POST'])
@app.route('/removecourse', methods=['GET', 'POST'], defaults={'id': None})
def removecourse(id):
    userid = session.get('id')

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        # Remove all the user's slides for this course
        cursor.execute('DELETE users_slides FROM users_slides INNER JOIN users_courses ON users_slides.userid = users_courses.userid WHERE users_courses.courseid = %s', (id,))
        mysql.connection.commit()

        # Remove the course from the user's enrolled courses
        cursor.execute('DELETE FROM users_courses WHERE userid = %s AND courseid = %s', (userid, id,))
        mysql.connection.commit()

        # Get the remaining courses the user is enrolled in
        cursor.execute('SELECT courses.id, courses.name, courses.category, courses.photo FROM courses INNER JOIN users_courses ON courses.id = users_courses.courseid WHERE users_courses.userid =  %s', (userid,))
        courses = cursor.fetchall()
    except Exception as e:
        mysql.connection.rollback()
        raise e
    finally:
        cursor.close()

    return render_template('index.html', courses=courses)



# This route handles requests to the '/course' endpoint.
@app.route('/course/<int:courseid>', methods=['GET', 'POST'])
@app.route('/course', methods=['GET', 'POST'], defaults={'courseid': None})
def course(courseid):
    userid = session.get('id')

    # Get the course and its lessons
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM courses WHERE id =  %s', (courseid,))
    course = cursor.fetchone()
    cursor.execute('SELECT * FROM lessons WHERE courseid =  %s', (courseid,))
    lessons = cursor.fetchall()

    # Check if user enrolled in a course 
    enrolled = is_enrolled(userid=userid, courseid=courseid)

    if enrolled: 
        # Check if the user has learned all slides of the course
        learned_all_slides = did_learn_all_slides(userid=userid, courseid=courseid)

        # If the users hasn't learned all slides, Get the lessonid of the first unlearned slide
        if not learned_all_slides:
            lessonid = get_first_unlearned_slide_lessonid(userid=userid, courseid=courseid)

    return render_template('course.html', course=course, lessons=lessons, enrolled=enrolled, learned_all_slides=learned_all_slides, lessonid=lessonid)



# This route handles requests to the '/lesson' endpoint.
@app.route('/lesson/<int:lesson_id>', methods=['GET', 'POST'])
@app.route('/lesson', methods=['GET', 'POST'], defaults={'lesson_id': None})
def lesson(lesson_id):
    lesson, slides = get_lessons_slides(lesson_id)


    # Renders view lesson template
    return render_template('lesson.html', lesson=lesson, slides=slides)



# This route handles requests to the '/startlesson' endpoint.
@app.route('/startlesson/<int:lesson_id>', methods=['GET', 'POST'])
@app.route('/startlesson', methods=['GET', 'POST'], defaults={'lesson_id': None})
def startlesson(lesson_id):
    lesson, slides = get_lessons_slides(lesson_id)

    # Renders playlesson template and returns the data needed to play the lesson
    return render_template('playlesson.html', lesson=lesson, slides=slides)



# This route handles requests to the '/multiple_choice_lesson' endpoint.
@app.route('/multiple_choice_lesson/<int:lesson_id>', methods=['GET', 'POST'])
@app.route('/multiple_choice_lesson', methods=['GET', 'POST'], defaults={'lesson_id': None})
def start_mp_lesson(lesson_id):
    lesson, slides = get_lessons_slides(lesson_id)

    # Renders multiple choice template and returns the data needed to play the lesson
    return render_template('multiple_choice_lesson.html', lesson=lesson, slides=slides)



# This route handles requests to the '/slides' endpoint.
# If a lesson ID parameter is provided, it returns the slides for that lesson.
# Otherwise, it returns a list of all available slides.
@app.route('/slides', methods=['GET', 'POST'], defaults={'lesson_id': None})
@app.route('/slides/<int:lesson_id>', methods=['GET', 'POST'])
def get_slides(lesson_id):
    userid = session.get('id')
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    if lesson_id is None:
        # If no lesson ID is provided, retrieve all slides 
        cursor.execute('SELECT * FROM slides WHERE lessonid')
        slides = cursor.fetchall()

        cursor.close()

        return jsonify(slides)
    else:
        # If a lesson ID is provided, retrieve the slides for that lesson.
        cursor.execute('SELECT * FROM slides INNER JOIN users_slides ON slides.id = users_slides.slideid WHERE userid = %s AND slides.lessonid = %s', (userid, lesson_id,))
        slides = cursor.fetchall()

        cursor.close()

        return jsonify(slides)


        
# This route handles requests for a specific audio file.
# The 'path:filename' parameter in the URL allows for filenames with slashes in them.
@app.route('/audio/<path:filename>', methods=['GET', 'POST'])
def download_audio(filename):
    # Set the directory where uploaded audio files are stored.
    uploads = os.path.join(app.root_path, 'static/audio/')

    # Return the audio file
    return send_from_directory(directory=uploads, path=filename + '.mp3')



# Check if user enrolled in a course 
def is_enrolled(userid, courseid):
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM users_courses WHERE userid = %s AND courseid = %s', (userid, courseid,))
    enrolled_in_course = cursor.fetchone()
    cursor.close()
    if enrolled_in_course:
        return True
    return False



# Check if user has learned all slides in a course 
def did_learn_all_slides(userid, courseid):
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT users_slides.id FROM users_slides INNER JOIN slides ON users_slides.slideid = slides.id INNER JOIN lessons ON slides.lessonid = lessons.lesson_id WHERE state = %s AND userid = %s AND courseid = %s', ('unlearned', userid, courseid,))
    slides = cursor.fetchone()
    cursor.close()
    if not slides:
        return True
    return False



def get_first_unlearned_slide_lessonid(userid, courseid):
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT lessonid FROM slides WHERE id = (SELECT slideid FROM users_slides INNER JOIN slides ON users_slides.slideid = slides.id INNER JOIN lessons ON slides.lessonid = lessons.lesson_id WHERE userid = %s AND courseid = %s AND state = %s LIMIT 1);', (userid, courseid, 'unlearned',))
    lessonid = cursor.fetchone()
    cursor.close()
    return lessonid



# Returns a lesson and its slides
def get_lessons_slides(lesson_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM lessons WHERE lesson_id =  %s', (lesson_id,))
    lesson = cursor.fetchone()

    cursor.execute('SELECT * FROM slides WHERE lessonid =  %s', (lesson_id,))
    slides = cursor.fetchall()

    return (lesson, slides)