from flask import Flask, render_template, jsonify, request
from flask import Flask, render_template, request, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

import flask_login

import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL configuration
mysql_config = {
    'user': 'admin',
    'password': 'rootroot',
    'host': 'myappdb.c5eagbhyes8m.us-east-1.rds.amazonaws.com',
    'database': 'myapp',
    'raise_on_warnings': True
}

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://admin:rootroot@myappdb.c5eagbhyes8m.us-east-1.rds.amazonaws.com/myapp'

db = SQLAlchemy(app)

bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)

math_courses = []
summer_courses = []
user_info = {8: ["English ", "Social Studies", "Visual and Performing Arts", "Open Humanities", "World Language", "Math",
                 "Science", "Open Steam", "Additional Credits"],
             9: [], 10: [], 11: [], 12: [], 13: []}

categories = ['english', 'socialstudies', 'art', 'humanities', 'language', 'math', 'science', 'steam', 'additional']

required_9_attempt = {'english': [1, 'core'], 'socialstudies': [1, 'core'], 'art': [0, None], 'humanities': [0, None],
                      'language': [0, None], 'math': [0, None], 'science': [0, None], 'steam': [0, None], 'additional': [0, None]}

required_9_credit = {1.0: "core", 1: "core", 0: "none", 0: "none", 0: "none", 0: "none", 0: "none", 0: "none", 0: "none"}
required_10_credit = {2.0, 1.0, 0, 0, 0, 0, 0, 0, 0}
required_11_credit = {2.0, 0, 0, 0, 0, 0, 0, 0, 0}
required_12_credit = {4.0, 3, 1, 1, 2, 3, 3, 3, 2.5}

course_id_to_groupId = {}
course_id_to_course = {}
course_groupid_to_name = {}


class UserCourses(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, nullable=False)
    grade = db.Column(db.Integer, nullable=False)
    courseid = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(50), nullable=True)

    def get_course_id(self):
        return self.courseid

    def get_grade(self):
        return self.grade

    def get_user_id(self):
        return self.userid

    def get_category(self):
        return self.category

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def is_authenticated(self):
        # Your custom authentication logic here
        return False  # Example condition

    def get_id(self):
        return self.id

@login_manager.user_loader
def load_user(user_id):
    print(user_id)
    return User.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            get_data()
            session['user_id'] = user.id  # Maintain session
            return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if request.method == 'POST':

        info12 = [(request.form.get(category), category) for category in categories]

        add_course_to_info(info12, 12)
        userid = session['user_id']
        grade = 12
        add_courses_to_user(userid, grade, info12)

        return render_template('formcompleted.html', user_info=user_info)
    return render_template('dashboard.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('user_id', None)  # Clear session
    return redirect(url_for('login'))


@app.route('/contactus', methods=['GET', 'POST'])
def contact():
    return render_template('contact.html')

@app.route('/signup', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user:
            return render_template('register.html', error="User Already Exists. Please select a different UserId")

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('register.html', error="")

def get_data():
    try:

        # Connect to the MySQL database
        conn = mysql.connector.connect(**mysql_config)
        cursor = conn.cursor()

        # Execute a query to retrieve data from the first table
        query1 = "SELECT * FROM courses"
        cursor.execute(query1)
        data1 = cursor.fetchall()

        # Process and print the data from the first table
        global data
        data = [{'course_id': row[0],
                 'school_id': row[1],
                 'course_group': row[2],
                 'name': row[3],
                 'description': row[4],
                 'teacher_rec': row[5],
                 'credit': row[6],
                 'prereqs': row[7],
                 'grade_level': row[8],
                 'term': row[9],
                 'guidelines': row[10],
                 'grad_requirement': row[11],
                 'courseType': row[12]} for row in data1]

        # Execute a query to retrieve data from the second table
        query2 = "SELECT * FROM school_requirements"
        cursor.execute(query2)
        data2 = cursor.fetchall()

        # Process and print the data from the second table
        global school_reqs
        # Convert the data to a JSON response
        school_reqs = [{'school_id': row[0],
                        'course_group': row[1],
                        'grade_level': row[2],
                        'credits': row[3],
                        'course_type': row[4]} for row in data2]

        # Execute a query to retrieve data from the second table
        query3 = "SELECT * FROM course_group"
        cursor.execute(query3)
        data3 = cursor.fetchall()

        # Process and print the data from the second table
        global course_groups
        course_groups = {}

        for row in data3:
            course_groups[row[2]] = int(row[0])
            course_groupid_to_name[int(row[0])] = row[2]

        # Close the cursor and connection
        cursor.close()
        conn.close()

        # Close the cursor and connection
        cursor.close()
        conn.close()

        for course in data:
            course_id_to_groupId[course["course_id"]] = course["course_group"]
            course_id_to_course[course["course_id"]] = course

        sort_data()

    except mysql.connector.Error as error:
        return jsonify({'error': str(error)})



def sort_data():
    math_courses.clear()
    summer_courses.clear()
    math_courses.append(("Math 8", -1))
    summer_courses.append(("No", -2))
    for course in data:
        if course["course_group"] == 1 and "9" in course["grade_level"]:
            course_name = ""
            for word in course["name"].split():
                course_name += " " + word[0].upper() + word[1:].lower()
            math_courses.append((course_name, course["course_id"]))
        if "Summer" in course["term"]:
            course_name = ""
            for word in course["name"].split():
                course_name += " " + word[0].upper() + word[1:].lower()
            summer_courses.append((course_name, course["course_id"]))


@app.route('/')
def sum():
    return render_template('new.html')


@app.route('/math_courses', methods=['GET'])
def get_math():
    userid = session['user_id']
    default_options = get_default_option(userid, 8, ['math_course'])

    default_math_opt = ()
    if default_options['math_course'] != 0:
        course_id = default_options['math_course']
        default_math_opt = (course_id_to_course[course_id]['name'], course_id)

    return jsonify(options=math_courses, defaultOption=default_math_opt)


@app.route('/summer_courses', methods=['GET'])
def get_summer():
    userid = session['user_id']
    default_options = get_default_option(userid, 8, ['summer_course'])

    default_summer_opt = ()
    if default_options['summer_course'] != 0:
        course_id = default_options['summer_course']
        default_summer_opt = (course_id_to_course[course_id]['name'], course_id)

    return jsonify(options=summer_courses, defaultOption=default_summer_opt)


grade = "9"
school = 1

@app.route('/9th_form', methods=['GET', 'POST'])
@login_required
def ninth_survey():
    userid = session['user_id']
    categories_survey = ['math_course', 'summer_course']

    if request.method == 'POST':
        info8 = [(request.form.get(category), category) for category in categories_survey]
        add_courses_to_user(userid, 8, info8)
        return ninth_form_submit()

    return render_template('9th_form.html')

@app.route('/9th_form_submit', methods=['GET'])
@login_required
def ninth_form_submit():

    userid = session['user_id']
    english, social_studies, arts, humanities, languages, math, science, steam, other = get_course_options(school, 9)

    default_options = get_default_option(userid, 9, categories)

    return render_template('9th_submit.html',
                               english=english, english_default_option=default_options['english'],
                               socialstudies=social_studies, socialstudies_default_option=default_options['socialstudies'],
                               art=arts, art_default_option=default_options['art'],
                               humanities=humanities, humanities_default_option=default_options['humanities'],
                               language=languages, language_default_option=default_options['language'],
                               math=math, math_default_option=default_options['math'],
                               science=science, science_default_option=default_options['science'],
                               steam=steam, steam_default_option=default_options['steam'],
                               additional=other, additional_default_option=default_options['additional'])


def get_default_option(userid, current_grade, categories):
    default_options = {category: 0 for category in categories}

    for category in categories:
        user_courses = UserCourses.query.filter_by(userid=userid, grade=current_grade, category=category).all()
        for user_course in user_courses:
            default_options[category] = user_course.get_course_id()
    return default_options


@app.route('/10th_form', methods=['POST', 'GET'])
def tenth_form():
    userid = session['user_id']
    if request.method == 'POST':

        info9 = [(request.form.get(category), category) for category in categories]
        credits = [0 for category in categories]
        user_info[13] = credits
        grade = 9
        add_course_to_info(info9, 9)

        add_courses_to_user(userid, grade, info9)

    english, social_studies, arts, humanities, languages, math, science, steam, other = get_course_options(school, 10)

    default_options = get_default_option(userid, 10, categories)
    print(f"THIS IS THE:   {default_options}")

    credits = credits_earned(userid, 9)
    color_coding = color_coded_reqs(user_info, required_9_attempt, 10)

    return render_template('/10th_form.html',
                               reqmet=credits[0],
                               credits=user_info[13],
                               color_coding=color_coding,
                               english_choice=user_info[9][0], english=english,
                               english_default_option=default_options['english'],
                               socialstudies_choice=user_info[9][1], socialstudies=social_studies,
                               socialstudies_default_option=default_options['socialstudies'],
                               art_choice=user_info[9][2], art=arts, art_default_option=default_options['art'],
                               humanities_choice=user_info[9][3], humanities=humanities,
                               humanities_default_option=default_options['humanities'],
                               language_choice=user_info[9][4], language=languages,
                               language_default_option=default_options['language'],
                               math_choice=user_info[9][5], math=math, math_default_option=default_options['math'],
                               science_choice=user_info[9][6], science=science,
                               science_default_option=default_options['science'],
                               steam_choice=user_info[9][7], steam=steam, steam_default_option=default_options['steam'],
                               additional_choice=user_info[9][8], additional=other,
                               additional_default_option=default_options['additional'])

@app.route('/11th_form', methods=['POST', 'GET'])
def submit2():
    userid = session['user_id']

    if request.method == 'POST':
        info10 = [(request.form.get(category), category) for category in categories]
        grade = 10
        add_course_to_info(info10, grade)
        add_courses_to_user(userid, grade, info10)

    english, social_studies, arts, humanities, languages, math, science, steam, other = get_course_options(school, 11)

    default_options = get_default_option(userid, 11, categories)

    credits9 = credits_earned(userid, 9)
    credits = credits_earned(userid, 10)

    return render_template('/11th_form.html',
                           reqmet9=credits9[0],
                           reqmet=credits[0],
                           credits=user_info[13],
                           english9=user_info[9][0], english_choice=user_info[10][0], english=english, english_default_option=default_options['english'],
                           ss9=user_info[9][1], socialstudies_choice=user_info[10][1], socialstudies=social_studies, socialstudies_default_option=default_options['socialstudies'],
                           art9=user_info[9][2], art_choice=user_info[10][2], art=arts, art_default_option=default_options['art'],
                           humanities9=user_info[9][3], humanities_choice=user_info[10][3], humanities=humanities, humanities_default_option=default_options['humanities'],
                           language9=user_info[9][4], language_choice=user_info[10][4], language=languages, language_default_option=default_options['language'],
                           math9=user_info[9][5], math_choice=user_info[10][5], math=math, math_default_option=default_options['math'],
                           sci9=user_info[9][6], science_choice=user_info[10][6], science=science, science_default_option=default_options['science'],
                           steam9=user_info[9][7], steam_choice=user_info[10][7],steam=steam, steam_default_option=default_options['steam'],
                           other9=user_info[9][8], additional_choice=user_info[10][8], additional=other, additional_default_option=default_options['additional'])


@app.route('/12th_form', methods=['POST'])
def submit3():
    userid = session['user_id']

    if request.method == 'POST':
        info11 = [(request.form.get(category), category) for category in categories]
        grade = 11
        add_course_to_info(info11, grade)
        add_courses_to_user(userid, grade, info11)

    english, social_studies, arts, humanities, languages, math, science, steam, other = get_course_options(school, 12)
    default_options = get_default_option(userid, 12, categories)

    credits9 = credits_earned(userid, 9)
    credits10 = credits_earned(userid, 10)
    credits = credits_earned(userid, 11)

    return render_template('/12th_form.html',
                           reqmet9=credits9[0],
                           reqmet10=credits10[0],
                           reqmet=credits[0],
                           credits=user_info[13],
                           english9=user_info[9][0], english_choice=user_info[10][0], english11=user_info[11][0], english=english, english_default_option=default_options['english'],
                           ss9=user_info[9][1], socialstudies_choice=user_info[10][1], ss11=user_info[11][1], socialstudies=social_studies, socialstudies_default_option=default_options['socialstudies'],
                           art9=user_info[9][2], art_choice=user_info[10][2], art11=user_info[11][2], art=arts, art_default_option=default_options['art'],
                           humanities9=user_info[9][3], humanities_choice=user_info[10][3], humanities11=user_info[11][3], humanities=humanities, humanities_default_option=default_options['humanities'],
                           language9=user_info[9][4], language_choice=user_info[10][4], language11=user_info[11][4], language=languages, language_default_option=default_options['language'],
                           math9=user_info[9][5], math_choice=user_info[10][5], math11=user_info[11][5], math=math, math_default_option=default_options['math'],
                           sci9=user_info[9][6], science_choice=user_info[10][6], sci11=user_info[11][6], science=science, science_default_option=default_options['science'],
                           steam9=user_info[9][7], steam_choice=user_info[10][7], steam11=user_info[11][7], steam=steam, steam_default_option=default_options['steam'],
                           other9=user_info[9][8], additional_choice=user_info[10][8], other11=user_info[11][8], additional=other,  additional_default_option=default_options['additional'])

def add_courses_to_user(userid, grade, info):
    # delete existing plan first
    user_courses_to_delete = UserCourses.query.filter_by(userid=userid, grade=grade).all()
    for to_delete in user_courses_to_delete:
        db.session.delete(to_delete)
        db.session.commit()

    # add new
    for i in info:
        opt = i[0]
        if opt is not None and len(opt) > 8:
            print(opt)
            print(len(opt))
            opt = opt.replace(')', '')
            courseid = int(opt.split(",")[1])

            new_user_course = UserCourses(userid=userid, grade=grade, courseid=courseid, category=i[1])
            db.session.add(new_user_course)
            db.session.commit()


def get_course_type(school, grade, course_group):
    for reqs in school_reqs:
        if reqs["school_id"] == school and reqs["grade_level"] == int(grade) and str(course_group) in reqs["course_group"]:
            return reqs["course_type"]
    return None


def done_a_higher_course(course_group, course, completed_course, grade):

    if grade <= 9 and course_group != "Math":
        return False

    highest_course_done_in_this_group = -1
    course_grp_id = course_id_to_groupId[course["course_id"]]

    for done in completed_course:
        if course_grp_id == done[1]:
            highest_course_done_in_this_group = max(highest_course_done_in_this_group, done[0])

    return course["course_id"] < highest_course_done_in_this_group
def is_prereq_done(course, completed_course):
    prereqs_str = course["prereqs"]
    prereqs = set()
    req_done = False
    if prereqs_str is not None:
        prereqs_split = prereqs_str.split(",")
        for c in prereqs_split:
            if c.isdigit():
                prereqs.add(int(c))
    else:
        req_done = True

    for req in prereqs:
        for done in completed_course:
            if req == done[0]:
                req_done = True
                break

    return req_done

def credits_earned(userid, grade):

    credits = {}
    retCredits = {}

    print(user_info)

    for i in range(9, grade+1):
        print(user_info[i])


    """
    courses_done_so_far = UserCourses.query.filter_by(userid=userid).all()
    for done_so_far in courses_done_so_far:
        if done_so_far.get_grade() <= grade:
            course = course_id_to_course[done_so_far.get_course_id()]
            course_grp_id = course['course_group']
            credit = course['credit']

            credits[course_grp_id] = credits.get(course_grp_id, 0) + credit

    retCredits = { course_groupid_to_name[i]: credits[i] for i in credits}

    for school_req in school_reqs:
        if school_req['grade_level'] == grade:
            course_grps = school_req['course_group']
            for grp in course_grps.split(","):
                grpid = int(grp)
                if credits.get(grpid,0) < int(school_req['credits']):
                    return ("No", retCredits)
    """

    return ("Yes", retCredits)

def get_individual_course_option(school, userid, grade, coursegroups, elective):

    options = [('', '')]

    completed_courses = set()
    completed_course_ids = set()

    courses_done_so_far = UserCourses.query.filter_by(userid=userid).all()
    for done_so_far in courses_done_so_far:
        if done_so_far.get_grade() < grade:
            completed_courses.add((done_so_far.get_course_id(), course_id_to_groupId[done_so_far.get_course_id()]))
            completed_course_ids.add(done_so_far.get_course_id())

    for course_group in coursegroups:
        course_group_id = course_groups[course_group]
        course_type = get_course_type(school, grade, course_group_id)

        if course_group_id == 1 and grade == 12:
            print("hello")

        for course in data:
            course_name = get_course_name(course)
            if course["course_group"] != course_group_id:
                continue

            if course["course_id"] in completed_course_ids:
                continue

            if elective is False and done_a_higher_course(course_group, course, completed_courses, grade):
                continue

            prereqs_met = is_prereq_done(course, completed_courses)

            if str(grade) not in course["grade_level"] and prereqs_met is False:
                continue

            add = False

            if course_type is not None:
                if course["courseType"] == course_type and elective is False:
                    add = True
                elif course["courseType"] != course_type and elective is True:
                    add = True
            else:
               add = True

            if add is True:
                options.append((course_name, course["course_id"]))

    return options
def get_course_options(school, grade):
    userid = session['user_id']

    print("grade = " + str(grade))
    english = get_individual_course_option(school, userid, grade, ['English'], grade > 10)

    social_studies = get_individual_course_option(school, userid, grade, ['Social Studies'], grade > 10)

    arts = get_individual_course_option(school, userid, grade, ['ART'], True)

    math = get_individual_course_option(school, userid, grade, ['Math'], grade > 11)

    science = get_individual_course_option(school, userid, grade, ['Science'], True)

    humanities = get_individual_course_option(school, userid, grade, ['English',
                                                              'Social Studies',
                                                              'Language',
                                                              'ART'], True)

    languages = get_individual_course_option(school, userid, grade, ['Language'], True)

    steam = get_individual_course_option(school, userid, grade, ['Math',
                                                         'Science',
                                                         'Media',
                                                         'Technology Education'], True)

    other = get_individual_course_option(school, userid, grade, ['Academic Support',
                                                         'Culinary Arts',
                                                         'ESOL',
                                                         'Health & Physical Education',
                                                         'Math',
                                                         'Science',
                                                         'Media',
                                                         'Technology Education',
                                                         'English',
                                                         'Social Studies',
                                                         'Language',
                                                         'ART'], True)


    """
    CHANGE:
    if no limits, proceed..
    if there are reqs, then dont!
    also remove extra data...
    
    if theres school req, get rid of it.
    if studenet has not completed prereq, get rid of it
    if there are extra copies of the same data, remove it
    """
    return [english, social_studies, arts, humanities, languages, math, science, steam, other]


def check_if_reqs_filled(courses, school, grade):
    """
    if grade != 12, check requirements, confirm coursetype

    else, check all requirements fulfilled
    """
    to_return = [False, [0 for course in courses]]
    # get credits for courses completed
    all_courses = user_info.copy()
    course_modified = []
    for course in courses:
        try:
            course_modified.append(course[0].split("\'")[1])
        except:
            print(course)
    all_courses[grade] = course_modified
    for grades in all_courses:
        for index in range(len(all_courses[grades])):
            if all_courses[grades][index] != '':
                for options in data:
                    if options["school_id"] == school and options["grade_level"] == grade and options["name"] == all_courses[grade][index]:
                        course_credit = float(options["term"])
                        to_return[1][index] += course_credit
    # go through requirements
    for requirement in school_reqs:
        # if relevant
        if school == requirement["school_id"] and grade == requirement["grade_level"]:
            # courseType != none
            courses = [['English'], ['Social Studies'], ['Arts', 'Music', 'Theater'], ['English', 'Social Studies','Arts', 'Music', 'Theater'],
                       ['Math'], ['Science'], ['Math', 'Science', 'Technology Education', 'Media'], 'Language', ]
            if requirement["course_type"] is not None:
                for grade_levels in range(len(9, grade + 1)):
                    for course_completed in all_courses[grade_levels]:
                        for options in data:
                            if options["school_id"] == school and options["name"].upper() in course_completed.upper() and options["course_group"] == requirement["course_group"]:
                                # if the course type fits, then check credits good. else, not met, so return false.
                                if requirement["course_type"] == course_completed["courseType"]:
                                    if int(options["term"]) != int(requirement["credits"]):
                                        to_return[0] = False
            # courseType = None
            else:
                print("hi")


def get_course_name(course):
    course_name = ""
    for word in course["name"].split():
        if word == "AP":
            course_name += "AP"
        elif "." in word:
            course_name += " " + word[0].upper()
            for letter in range(1, len(word)):
                if word[letter - 1] == ".":
                    course_name += word[letter].upper()
                else:
                    course_name += word[letter].lower()
        else:
            course_name += " " + word[0].upper() + word[1:].lower()
    return course_name

def add_course_to_info(info, grade):
    info_modified = []
    index = 0

    for course in info:
        try:
            info_modified.append(course[0].split("\'")[1])
            course_id_str = course[0].replace(')', '')
            courseid = int(course_id_str.split(",")[1])

            lookedup_course = course_id_to_course[courseid]
            user_info[13][index] += lookedup_course['credit']
        except:
            print(course)
        index += 1
    user_info[grade] = info_modified


def color_coded_reqs(user_info, required_credits_list, grade):
    color_coding = ["red"] * 9
    # get all courses completed so far
    user_courses = []
    for grade_levels in range(9, grade):
        for course in user_info[grade_levels]:
            if course != "":
                user_courses.append(course)

    # check if reqs met
    for i in required_credits_list:
        if required_credits_list[i][0] == 0:  # if there is no req
            color_coding[list(required_credits_list).index(i)] = "green"
        else:  # if there is a req
            credits_completed = 0
            for course in user_courses:
                new_dict = get_course_info(course)
                if new_dict is None:
                    print("bug")
                elif required_credits_list[i][1] in new_dict['courseType'].lower():
                    credits_completed += int(get_course_info(course)['credit'])
            if credits_completed >= required_credits_list[i][0]:
                color_coding[list(required_credits_list).index(i)] = "green"
    return color_coding


def get_course_info(course):
    for course_info in data:
        if course_info["name"].lower() in course.lower():
            print(f" LOOK AT THIS: {course_info}")
            print(type(course_info))
            return course_info


if __name__ == '__main__':
    app.run(port=5001)
