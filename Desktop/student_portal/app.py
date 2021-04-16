from flask import Flask, render_template, url_for, request, flash, current_app, session, jsonify, redirect
from flaskext.mysql import MySQL
import pymysql.cursors
import json
import os

 
app = Flask(__name__)

# connection to database configuration
app.secret_key = 'secret'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_DB'] = 'student_portal'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '1000naira'

mysql = MySQL(app, cursorclass=pymysql.cursors.DictCursor)



#funtion variables

# define a function to query the database
def db_connection(sql_query, var=None):
    conn = mysql.get_db()
    cur = conn.cursor()
    cur.execute(sql_query, var)
    fetched_output = cur.fetchall()

    return fetched_output
    
# Getting the list of all states in Nigeria from the database
def get_all_states():
    sql_query = 'select * from nigeria_states'
    all_states = db_connection(sql_query)

    return all_states


# Query the database to get all student information
def get_all_student_info():
    sql_query = 'select * from Student_Information'
    all_students_info = db_connection(sql_query)

    return all_students_info


# Getting the state id from the selected state and using it to query the database
@app.route('/local-govts', methods=['POST'])
def get_all_local_govts():
    # Getting the state id with ajax
    req = request.get_json()
    state_id = req['state_id']

    if state_id == 0:
        return None
    else: 
        # Querying the database with the state id to get the list of its local government
        sql_query = 'select * from nigeria_local_govts where state_id=%s' 
        # Calling the function above to query database and storing in a variable
        all_local_govt = db_connection(sql_query, var=state_id)

        # Stored list of local govt gotten in a session so that it can be used in other function
        session['local_govts_qs'] = all_local_govt
        
        # Caling the json.dumps method to perform the action on successful in the ajax call
        return json.dumps('success')


# Creating the api endpoint for the local government
@app.route('/api/local-govt')
def api_local_govt():
    # Get list of local government in the state selected from the session where it was stored
    local_govts_from_selected_state = session.get('local_govts_qs')
    html_string_selected = ''

    # Looping through the list of local government of selected sated and storing in a variable
    for local_govt in local_govts_from_selected_state:
            html_string_selected += '<option value="{}">{}</option>'.format(local_govt['LGA'], local_govt['LGA'])

    # Returning a json object and sending to the route on this view
    return jsonify(html_string_selected=html_string_selected)



# Landing pages view and route
@app.route('/')
def landing():
    return render_template('landing.html')


# Sudent portal views and route
@app.route('/portal', methods=['GET', 'POST'])
def portal():
    # Getting all Nigeria States from the database
    state_qs = get_all_states()

    # Getting form inputs
    if request.method == 'POST':
        image = request.files['photo']
        first_name = request.form.get('firstName')
        middle_name = request.form.get('middleName')
        last_name = request.form.get('lastName')
        email = request.form.get('email')
        gender = request.form.get('gender')
        date_of_birth = request.form.get('d-o-b')
        phone_number = request.form.get('phone')
        address = request.form.get('address')
        state = request.form.get('state')
        local_govt = request.form.get('local-govt-area')
        next_of_kin = request.form.get('next-of-kin')
        jamb_score = request.form.get('jamb-score')


        # Check if all form input are filled
        if (image == '' or first_name == '' or last_name == '' or middle_name == '' or email == '' or
            gender == None or date_of_birth == '' or phone_number == '' or address == '' or state == 'Select State' or
            local_govt == 'Select Local Goverment' or next_of_kin == '' or jamb_score == ''):
            flash('Fill in all the required field')

        else:
            # Phone validation
            phone_num_length = len(phone_number)
            if phone_num_length < 11 or phone_num_length > 11:
                flash("Invalid Phone Number")
            else:
                #Jamb score validation
                jamb_score = int(jamb_score)
                if jamb_score < 1:
                    flash("Jamb score cannot be less than 1")
                else:
                    #Check for existing student data in the database
                    if email or phone_number:
                        conn = mysql.get_db()
                        cur = conn.cursor()
                        cur.execute("select Email, PhoneNumber from Student_Information where Email=%s or PhoneNumber=%s", (email, phone_number))
                        check_existing_data = cur.fetchall()

                        # Notify user if student data already exist
                        if check_existing_data:
                            flash('Student already exist')
                        # Connect to the database and submit form if a validation is correct
                        else:
                            # Getting image name 
                            image_name = image.filename
                            # Adding phone number to image name to make it unique
                            changed_image_name = phone_number + image_name
                            # Creating image path in the project folder
                            filepath =  'static/images/{}'.format(changed_image_name)
                            # connecting and saving to the database
                            conn = mysql.get_db()
                            cur = conn.cursor()
                            cur.execute('insert into Student_Information(FirstName, MiddleName, LastName, Email, DateOfBirth, Sex, PhoneNumber, Address, StateOfOrigin, LocalGovernment, NextOfKin, JambScore, profile_img_url) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s)', (first_name, middle_name, last_name, email, date_of_birth, gender, phone_number, address, state, local_govt, next_of_kin, jamb_score, changed_image_name))
                            conn.commit()
                            cur.close()
                            # Save image path the project folder
                            image.save(filepath)
                            flash('Form has been submitted succefully')
                            # Redirecting user to next page 
                            return redirect(url_for('index'))   
                
    return render_template('portal.html', state_qs=state_qs)


# Index page view and route
@app.route('/index', methods=['GET', 'POST'])
def index():
    # Getting all student information by call the one of the funtion variable aboive
    students_info = get_all_student_info()
    return render_template('index.html', students_info=students_info)


# Detail page and route
@app.route('/detail/<id>')
def detail(id):
    # Passing student id from the template and saving it in a variable so as to query the database
    student_id = id
    sql_query = 'select * from Student_Information where StudentID=%s' 
    student_details = db_connection(sql_query, var=student_id)
  
    return render_template('detail.html', student_details=student_details)


# Search page and route
@app.route('/search', methods=['GET', 'POST'])
def search():
    # Get all inut from the search
    student_name  = request.form.get('student-name')
    student_status = request.form.get('student-status')
    student_gender = request.form.get('student-gender')
    student_score = request.form.get('student-jamb-score')

    search_by_student_name = ""
    
    # Adding % to student so as to query the database with a wildcard
    if student_name:
        student_name_wildcard = str(student_name) + "%"
    # If no value of student_name is gotten from the student name input, return empty string
    else:
        student_name_wildcard = student_name
        # Connect to the database and searching with the input received by the search
        conn = mysql.get_db()
        cur = conn.cursor()
        cur.execute("select * from Student_Information where FirstName LIKE %s OR MiddleName LIKE %s OR LastName LIKE %s OR JambScore=%s OR Sex=%s", (student_name_wildcard, student_name_wildcard, student_name_wildcard, student_score, student_gender))
        search_by_student_name = cur.fetchall()
    
    return render_template('search.html', search_by_student_name=search_by_student_name)



if __name__ == "__main__":
    app.run(debug=True)