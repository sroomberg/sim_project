from Student import *
from Faculty import *
from Course import *

import operator
import random
import scipy.stats as st
import sys

global student_id_inc
global passfail
global dropouts
global graduates
global minors 
global core_classes

#electives globals
global elective_bag
global electives_inc


#distribution will be a dictionary of class num to a modifying value:
#e.g. [401: 4.15, 441:3.2, 1501:3, 445: 5.38 , ...]
def calculate_class_sizes(num_sections):
    global core_classes

    total = 0
    for each_class in core_classes:
        total += len(each_class.students) + len(each_class.waitlist)
    for each_class in core_classes:
        level_of_interest = len(each_class.students) + len(each_class.waitlist)
        ratio_of_interest = level_of_interest/total
        ratio_of_interest = num_sections if ratio_of_interest == 0 else ratio_of_interest
        each_class.class_size = int(round(num_sections/ratio_of_interest)) * 40

#9 classes with 34 total sections of core classes
def generate_core_courses(num_core):

    courses = []

    cs401 = Course(401, difficulty = .1, class_size = 7*40)
    cs441 = Course(441, difficulty = .05, class_size = 6*40)
    cs445 = Course(445, requirements=[401], difficulty = .15, class_size = 5*40)
    cs447 = Course(447, requirements=[445], difficulty = .15, class_size = 5*40)
    cs449 = Course(449, requirements=[447], difficulty = .1, class_size = 4*40)
    cs1501 = Course(1501, requirements=[401, 445], difficulty = .2, class_size = 4*40)
    cs1502 = Course(1502, requirements=[441, 445], difficulty = .1, class_size = 3*40)
    cs1550 = Course(1550, requirements=[447, 449], difficulty = .25, class_size = 2*40)

    courses.append(cs401)
    courses.append(cs441)
    courses.append(cs445)
    courses.append(cs447)
    courses.append(cs449)
    courses.append(cs1501)
    courses.append(cs1502)
    courses.append(cs1550)


    return courses

#14 electives
def generate_electives(number_of_electives):
    global electives_bag
    global electives_inc

    courses = []
    if len(electives_bag) < number_of_electives:
        #add new electives
        for i in range(number_of_electives - len(electives_bag)):
            requirement = [445] if random.random() < .2 else [1501]
            electives_bag.append(Course(i, requirements = requirement, is_core = False, difficulty = .15, class_size = 40))
            electives_inc += 1

    #pick from a deep copy of the bag
    bag_copy = electives_bag[:]
    random.shuffle(bag_copy)

    for i in range(number_of_electives):
        courses.append(bag_copy.pop())
    return courses

def generate_students(num_to_generate):
    global student_id_inc
    
    students = []

    for i in range(num_to_generate):
        students.append(Student(skill_level = random.random(), student_id = student_id_inc, is_minor = random.random() > .35))
        student_id_inc +=1

    return students



def find_leaving_students(students):
    global graduates
    global dropouts
    global minors
    global core_classes

    global num_dropped_out_for_failed_classes
    global num_dropped_out_for_dropout_rate
    global num_dropped_out_for_too_many_semesters

    new_grads_or_dropouts_or_minors = []

    core_class_ids = [x.course_id for x in core_classes]

    for student in students:
        dropout_chance = random.random() < .01

        if completed_core_classes(student):
            graduates.append(student)
            new_grads_or_dropouts_or_minors.append(student)

        elif student.is_minor and len([x for x in classes_passed(student) if x in core_class_ids]) >= 5:
            minors.append(student)
            new_grads_or_dropouts_or_minors.append(student)

        elif len(student.classes_failed) > 10 or dropout_chance or student.semesters_completed > 12:#or completed exactly half the core courses and 50%
            #print("someone is leaving.  They failed {} classes, the dropout chance was {}, and the semesters completed was {}".format(
            #    student.classes_failed, dropout_chance, student.semesters_completed))
            if len(student.classes_failed) > 10:
                num_dropped_out_for_failed_classes +=1
            if dropout_chance:
                num_dropped_out_for_dropout_rate +=1
            if student.semesters_completed > 12:
                num_dropped_out_for_too_many_semesters +=1
            dropouts.append(student)
            new_grads_or_dropouts_or_minors.append(student)


    for student in new_grads_or_dropouts_or_minors:
        students.remove(student)


# a term is a list of courses
def update_students_with_new_grades(term):
    global passfail
    for course in term:
        if verbose:
            print("at the end of the semester, course {} had {} students out of {}".format(
                course.course_id, len(course.students), course.class_size))
        for student in course.students:
            grade = assign_grade_to_student(course.difficulty, passfail)
            student.add_course_grade(course.course_id,grade)


def assign_grade_to_student(difficulty, passfail = True):
    if passfail:
        return 1.0 if random.random() >= (difficulty) else 0.0
    else:
        grade = random.random()
        return grade if grade >= 1 - difficulty else 0.0


# term is a list of courses for the semester
def find_plans_to_retake(term):
    for course in term:
        for student in course.students:
            # this key should exist by the time this is called
            if student.course_transcript[course.course_id] == 0 and course.course_id not in student.plan_to_retake:
                student.plan_to_retake.append(course.course_id)


def classes_passed(student):
    return [x for x, grade in student.course_transcript.items() if grade >= .7]

def completed_core_classes(student):
    global core_classes

    passed_classes = classes_passed(student)

    required = [x.course_id for x in core_classes]

    completed_core = all(x in passed_classes for x in required)

    completed_electives = [x for x in passed_classes if x not in required]

    return completed_core and len(completed_electives) > 4



def sort_students(student1, student2):
    credits1 = len(student1.course_transcript)
    credits2 = len(student2.course_transcript)
    if credits1 > credits2:
        return -1
    elif credits1 == credits2:
        return 0
    else:
        return 1

def remove_students_from_courses(term):
    for course in term:
        course.students = []

def populate_courses_with_students(term,students):
    required = []
    electives = []
    for course in term:
        if course.course_id <= 400:
            electives.append(course)
        else:
            required.append(course)

    students.sort(key = lambda x: len(x.course_transcript), reverse=True)
    for student in students:
        courses_taken=[]
        max_courses = 2 + (1 if random.random() < student.skill_level else 0)
        #try to retake courses the student plans to retake first
        for course_id in student.plan_to_retake:
            if course_id <= 400:
                # elective
                for i in range(len(electives)):
                    if course_id == electives[i].course_id and len(courses_taken) < max_courses:
                        if electives[i].class_size > len(electives[i].students):
                            courses_taken.append(course_id)
                            electives[i].students.append(student)
            else:
                # required
                for i in range(len(required)):
                    if course_id == required[i].course_id and len(courses_taken) < max_courses:
                        if required[i].class_size > len(required[i].students):
                            courses_taken.append(course_id)
                            required[i].students.append(student)
                            if len(courses_taken) == max_courses:
                                continue

        # remove the courses we just added from plan_to_retake  
        for course_id in courses_taken:
            student.plan_to_retake.remove(course_id)

        required.sort(key = lambda x: x.course_id)
        random.shuffle(electives)
        for course in required:
            if len(courses_taken) >= max_courses:
                break

            if course.course_id not in courses_taken and course.course_id not in student.course_transcript \
                    and course.class_size > len(course.students):
                courses_taken.append(course.course_id)
                course.students.append(student)

        for course in electives:
            if len(courses_taken) >= max_courses:
                break

            if course.course_id not in courses_taken and course.course_id not in student.course_transcript \
                    and course.class_size > len(course.students):
                courses_taken.append(course.course_id)
                course.students.append(student)


def runloop(students, term, num_incoming):
    global verbose

    new_students = generate_students(num_incoming)

    #this causes a deep change in the object instead of changing list pointer
    number_new = len(new_students)
    for i in range(number_new):
        students.append(new_students.pop())

    populate_courses_with_students(term, students)
    if verbose:
        print ("{}, size: {}, students: {}, term: {}, waitlist: {}".format(term[2].course_id, term[2].class_size, len(term[2].students), term[2].term, term[2].waitlist))
    
    update_students_with_new_grades(term)


    find_leaving_students(students)
    find_plans_to_retake(term)
    calculate_class_sizes(40)

    courses.sort(key=lambda x: x.course_id)
    remove_students_from_courses(term)
    for student in students:
        student.semesters_completed +=1


    return students


if __name__ == "__main__":

    global passfail
    global dropouts
    global graduates
    global minors
    global student_id_inc
    global core_classes

    global num_dropped_out_for_failed_classes
    global num_dropped_out_for_dropout_rate
    global num_dropped_out_for_too_many_semesters

    global electives_bag
    global electives_inc


    if len(sys.argv) <3 or len(sys.argv) > 4:
        print("run with number of terms and number of iterations to run that many terms as an argument")
    else:

        if len(sys.argv) == 4:
            verbose = True
        else:
            verbose = False

        num_terms = int(sys.argv[1])
        num_iterations = int(sys.argv[2])


        for i in range(num_iterations):
            print("\niteration {}".format(i+1))
            #set term variables

            electives_bag = []
            electives_inc = 0

            passfail = True
            dropouts = []
            graduates = []
            student_id_inc = 0
            minors = []

            num_dropped_out_for_failed_classes = 0
            num_dropped_out_for_dropout_rate = 0
            num_dropped_out_for_too_many_semesters = 0


            students = []
            core_classes = generate_core_courses(30)
            courses = generate_electives(14) + core_classes

            for z in range(num_terms):
                if verbose:
                    print("\n\nsemester {}".format(z))
                students = runloop(students, courses, 275)

            student_ids = []
            for student in students:
                student_ids.append(student.student_id)

            grad_ids = []
            for graduate in graduates:
                grad_ids.append(graduate.student_id)

            dropout_ids = []
            for dropout in dropouts:
                dropout_ids.append(dropout.student_id)

            minor_ids = []
            for minor in minors:
                minor_ids.append(minor.student_id)

            student_ids.sort()
            grad_ids.sort()
            dropout_ids.sort()
            minor_ids.sort()

            print("students at end of sim: {}".format(len(student_ids)))
            print("graduates at end of sim: {}".format(len(grad_ids)))
            print("dropouts at end of sim: {}".format(len(dropout_ids)))
            print("minors at the end of sim: {}".format(len(minor_ids)))

            print("number dropped out for failing classes: {}".format(num_dropped_out_for_failed_classes))
            print("number naturally droppout out: {}".format(num_dropped_out_for_dropout_rate))
            print("number dropped out for being in system too long: {}".format(num_dropped_out_for_too_many_semesters))


