from Student import Student
from Faculty import Faculty
from Course import Course

import operator
import random
import scipy.stats as st
import sys

global student_id_inc
global passfail
global dropouts
global graduates 
global verbose
global core_classes

#9 classes with 34 total sections of core classes
def generate_core_courses(num_core):
	global core_classes

	courses = []

	for i in range(num_core):
		courses.append(Course(i, students = []))

	return courses

#15 electives
def generate_electives(num_core):

	courses = []

	for i in range(num_core):
		courses.append(Course(i, students = []))

	return courses

def generate_students(num_to_generate):
	global student_id_inc
	
	students = []

	for i in range(num_to_generate):
		students.append(Student(skill_level = random.random(), student_id = student_id_inc))
		student_id_inc +=1

	return students



def assignGradeToStudent(difficulty, passfail = True):
	if passfail:
		return 1.0 if random.random() >= (difficulty) else 0.0
	else:
		grade = random.random()
		return grade if grade >= () (difficulty) else 0.0

# a term is a list of courses
def update_students_with_new_grades(term):
	global passfail
	for course in term:
		if verbose:
			print("at the end of the semester, course {} had {} students out of {}".format(
				course.course_id, len(course.students), course.class_size))
		for student in course.students:
			grade = assignGradeToStudent(course.difficulty, passfail)
			student.add_course_grade(course.course_id,grade)


def sort_students(student1, student2):
	credits1 = len(student1.course_transcript)
	credits2 = len(student2.course_transcript)
	if credits1 > credits2:
		return -1
	elif credits1 == credits2:
		return 0
	else:
		return 1

def populate_courses_with_students(term,students):
	students.sort(key = lambda x: len(x.course_transcript), reverse=True)
	for student in students:
		courses_taken=[]
		max_courses = 2 + (1 if random.random() < student.skill_level else 0)
		#try to retake courses the student plans to retake first
		for course_id in student.plan_to_retake:
			for i in range(len(term)):
				if course_id == term[i].course_id and len(courses_taken <= max_courses):
					#if there is space left in the class, take it
					if term[i].class_size>len(term[i].students):
						courses_taken.append(course_id)
						term[i].students.append(student)


		#remove the courses we just added from plan_to_retake	
		for course_id in courses_taken:
			student.plan_to_retake.remove(course_id)

		random.shuffle(term)
		for course in term:
			if len(courses_taken) >= max_courses:
				break

			if verbose:
				print("looking to add student {} to course {}".format(student.student_id, course.course_id))
			
			if course.course_id not in courses_taken and course.course_id not in student.course_transcript \
					and course.class_size>=len(course.students):

				if verbose:
					print("course {} has {} students in it before adding a student".format(course.course_id, len(course.students)))
					print("adding student {} to course {}".format(student.student_id, course.course_id))

				courses_taken.append(course.course_id)
				course.students.append(student)
				if verbose:
					print("course {} has {} students in it after adding a student".format(course.course_id, len(course.students)))
		if verbose:
			print("a student registered for classes {}".format(courses_taken))

def completed_core_classes(student):
	return len(student.course_transcript) >= 20

def find_leaving_students(students):
	global graduates
	global dropouts

	new_grads_or_dropouts = []
	for student in students:
		#print("the length of this student's transcript is {}.".format(len(student.course_transcript)))
			
		if completed_core_classes(student):
			graduates.append(student)
			new_grads_or_dropouts.append(student)
		elif len(student.classes_failed) > 10 or random.random() < .02:
			dropouts.append(student)
			new_grads_or_dropouts.append(student)

	for student in new_grads_or_dropouts:
		students.remove(student)


# term is a list of courses for the semester
def find_plans_to_retake(term):
	for course in term:
		for student in course.students:
			# this key should exist by the time this is called
			if student.course_transcript[course.course_id] == 0:
				student.plan_to_retake.append(course.course_id)



def runloop(students, term, num_incoming):
	global verbose

	if verbose:
		print ("{}, size: {}, students: {}, term: {}".format(term[2].course_id, term[2].class_size, term[2].students, term[2].term))
	new_students = generate_students(num_incoming)

	#this causes a deep change in the object instead of changing list pointer
	number_new = len(new_students)
	for i in range(number_new):
		students.append(new_students.pop())

	populate_courses_with_students(term, students)
	if verbose:
		print ("{}, size: {}, students: {}, term: {}".format(term[2].course_id, term[2].class_size, term[2].students, term[2].term))
	
	update_students_with_new_grades(term)

	find_leaving_students(students)
	find_plans_to_retake(term)

	return students


if __name__ == "__main__":

	global passfail
	global dropouts
	global graduates
	global student_id_inc
	global verbose
	global core_classes

	core_classes = {0:1, 1:1, 2:1, 3:1, 4:1, 5:1, 6:1, 7:1, 8:1}


	passfail = True
	dropouts = []
	graduates = []
	student_id_inc = 0

	if len(sys.argv) <2 or len(sys.argv) > 3:
		print("run with number of iterations as an argument")
	else:

		if len(sys.argv) == 3:
			verbose = True
		else:
			verbose = False

		num_iterations = int(sys.argv[1])

		students = []

		for i in range(num_iterations):
			courses = generate_core_courses(30)
			courses += generate_electives(15)
			students = runloop(students, courses, 5)

		print("at the end of the simulation, there were {} dropouts and {} graduates".format(len(dropouts), len(graduates)))
		print("{} students were still in the system.".format(len(students)))
		print("some sample GPAs were: ")
		for i in range(10):
			if len(graduates)>=i:
				break
			print(graduates[i].calculate_GPA())

		student_ids = []
		for student in students:
			student_ids.append(student.student_id)

		grad_ids = []
		for graduate in graduates:
			grad_ids.append(graduate.student_id)

		dropout_ids = []
		for dropout in dropouts:
			dropout_ids.append(dropout.student_id)

		student_ids.sort()
		grad_ids.sort()
		dropout_ids.sort()

		print("students at end of sim: {}".format(student_ids))
		print("graduates at end of sim: {}".format(grad_ids))
		print("dropouts at end of sim: {}".format(dropout_ids))
