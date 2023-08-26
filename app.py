import os
from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func


current_dir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(current_dir, "week7_database.sqlite3")
db = SQLAlchemy(app)

class Student(db.Model):
	__tablename__ = 'student'
	student_id = db.Column(db.Integer, autoincrement = True, primary_key = True)
	roll_number = db.Column(db.String, unique = True, nullable = False)
	first_name = db.Column(db.String, nullable = False)
	last_name = db.Column(db.String)
	
class Course(db.Model):
	__tablename__ = 'course'
	course_id = db.Column(db.Integer, autoincrement = True, primary_key = True)
	course_code = db.Column(db.String, unique = True, nullable = False)
	course_name = db.Column(db.String, nullable = False)
	course_description = db.Column(db.String)

class Enrollments(db.Model):
	__tablename__ = 'enrollments'
	enrollment_id = db.Column(db.Integer, autoincrement = True, primary_key = True)
	estudent_id = db.Column(db.Integer, db.ForeignKey("student.student_id"), primary_key = True, nullable = False)
	ecourse_id = db.Column(db.Integer, db.ForeignKey("course.course_id"), primary_key = True, nullable = False)

# Part 1 The home page
@app.route('/', methods=["GET"])	
def index():
	_student_data = Student.query.all()
	return render_template("index.html", data=_student_data) #Tested Ok

# Part 2 when we click on Add Student
@app.route("/student/create", methods=["GET","POST"])
def create_form():
	if request.method =='GET':
		return render_template("create_student_form.html")
	else:
		while True:
			try:
	# Adding the student data into student database
				_student = Student(student_id = None, roll_number=int(request.form["roll"]), first_name = request.form["f_name"], last_name=request.form["l_name"])
				db.session.add(_student)
				db.session.commit()
				break
			except: # Exception was handled with some mumbo jumbo
				return render_template("student_id_exists.html")
		return redirect("/") #Tested Ok


# Part 3 when we click on Update button
@app.route("/student/<int:student_id>/update", methods=["GET","POST"])
def update_details(student_id):
	_student_query = Student.query.filter_by(student_id=student_id).first()
	_course_query = Course.query.all()
	if request.method == 'GET':
		return render_template("update_student_form.html", Data1=_student_query,Data2=_course_query)
	else:
		_student_query.first_name = request.form["f_name"]
		_student_query.last_name = request.form["l_name"]
		db.session.add(_student_query)
		db.session.commit()
		_course_id = request.form["course"]
		# return _course_id
		_enrollments_query = Enrollments.query.filter_by(estudent_id=student_id).all()
		A = []
		for D in _enrollments_query:
			if D.ecourse_id==int(_course_id):
				return redirect("/")
		_enrollments = Enrollments(enrollment_id=None, estudent_id = student_id, ecourse_id = _course_id)
		db.session.add(_enrollments)
		db.session.commit()
		return redirect("/")


# Part 4 When we click on delete button from the homepage
@app.route("/student/<int:student_id>/delete", methods=["GET"])
def delete_details(student_id):
	_student = Student.query.get(student_id)
	db.session.delete(_student)
	db.session.commit()
	
	_clear = Enrollments.query.filter_by(estudent_id=student_id).all()
	for i in _clear:
		db.session.delete(i)
		db.session.commit()
	return redirect("/"),200 #Tested Ok
	
# Part 5 When we click on roll number to open the details of students
@app.route("/student/<int:student_id>/delete", methods=["GET"])
def display_details(student_id):
	_student = Student.query.get(student_id)
	_enrollments = Enrollments.query.filter_by(estudent_id=student_id).all()
	data2 = []
	for i in range(len(_enrollments)):
		data = Course.query.get(_enrollments[i].ecourse_id)
		data2.append(data)
	return render_template("student_details.html", data1=_student, data2=data2)

# Part 6 When we click on the withdraw button
@app.route("/student/<int:student_id>/withdraw/<int:course_id>", methods=["GET"])
def withdraw(student_id,course_id):
	_enrollments_query = Enrollments.query.filter_by(estudent_id=student_id,ecourse_id=course_id).first()
	db.session.delete(_enrollments_query)
	db.session.commit()
	return redirect("/")

# Part 7 When we click on Go to course
@app.route("/courses",methods=["GET"])
def courses():
	_course_query = Course.query.all()
	return render_template("courses.html", data=_course_query)

# Part 8 When we click on Add Course Button
@app.route("/course/create", methods=["GET","POST"])
def create_course():
	if request.method == "GET":
		return render_template("create_course_form.html")
	else:
		_course_query = Course.query.filter_by(course_code=request.form['code'])
		if _course_query:
			return render_template("course_id_exists.html")
		else:
			_course = Course(course_id=None,course_code=request.form["code"],course_name=request.form["c_name"],course_description=request.form["desc"])
			db.session.add(_course)
			db.session.commit()
			return redirect("/courses") 

# Part 9 When we click on Update on Courses Page
@app.route("/course/<int:course_id>/update", methods=["GET", "POST"])
def update_course(course_id):
	_course_query = Course.query.filter_by(course_id=course_id).first()
	if request.method == "GET":
		return render_template("update_course_form.html", Data=_course_query), 200 #Tested Ok
	else:
		_course_query.course_name = request.form['c_name']
		_course_query.course_description = request.form['desc']
		db.session.add(_course_query)
		db.session.commit()
		return redirect("/courses"),200 # Tested Ok

# Part 10 When we click on the delete button
@app.route("/course/<int:course_id>/delete", methods=["GET"])
def delete_course(course_id):
	_course_query = Course.query.get(course_id)
	db.session.delete(_course_query)
	db.session.commit()

	_clear = Enrollments.query.filter_by(ecourse_id=course_id).all()
	for i in _clear:
		db.session.delete(i)
		db.session.commit()
	return redirect("/") # Tested Ok

# Part 11 When we click on the 
@app.route("/course/<int:course_id>", methods=["GET"])
def course_details(course_id):
	_course_query = Course.query.get(course_id)
	_enrollments_query = Enrollments.query.filter_by(ecourse_id=course_id).all()
	_students_data = []
	for _enrollment in _enrollments_query:
		_student_query = Student.query.get(_enrollment.estudent_id)
		_students_data.append(_student_query)
	return render_template("course_details.html",data1=_course_query,data2=_students_data) #Tested Ok
















	
if __name__=='__main__':
	app.run()