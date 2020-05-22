import pickle
import traceback

from django.db.models import ObjectDoesNotExist
from django.db.utils import IntegrityError
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from .forms import UserLoginForm, CreateStudentForm, UploadCSVForm, CreateTeacherForm, CreateCourseForm, CreateClassForm, EnrollStudentForm
from .models import Administrator
from student.models import Student, ClassEnrollment, Submission
from teacher.models import Teacher
from board.models import Course, Schedule, Class, ClassAssignments
from django.contrib.auth.models import User
from django.contrib.staticfiles import finders
import mimetypes
import pandas as pd
import uuid


INTERNAL_ERROR_MESSAGE = 'Something went horribly wrong. Please try again later.'


@login_required(login_url='administration-login')
def home(request):
    return render(request, 'administration/home.html')


def enroll_student(request):
    classes = []
    for klass in Class.objects.all():
        course_name = Course.objects.all().get(course_id=klass.course_id).course_name
        teacher = Teacher.objects.all().get(id=uuid.UUID(klass.teacher_id))
        teacher_name = teacher.first_name + ' ' + teacher.last_name
        period = klass.period
        class_description = teacher_name + ' (P' + str(period) + '): ' + course_name
        classes.append((str(klass.id.hex), class_description))
    all_students = Student.objects.all()

    if request.method == 'POST':
        create_form = EnrollStudentForm(request.POST, classes=classes, students=all_students)
        if create_form.is_valid():
            class_id = create_form.cleaned_data.get('klass')
            enrolled_students = create_form.cleaned_data.get('students')
            num_students_enrolled = 0
            for student in enrolled_students:
                try:
                    enrollment = ClassEnrollment.objects.get(class_id=class_id, student_id=student.student_id)
                except ObjectDoesNotExist:
                    enrollment = ClassEnrollment(class_id=class_id, student_id=student.student_id)
                    enrollment.save(init_events=False)
                    # creates submissions for the student in case student is being enrolled mid term
                    assignment_refs = ClassAssignments.objects.all().filter(class_id=class_id)
                    for assignment_ref in assignment_refs:
                        submission = Submission(assignment_id=assignment_ref.assignment_id,
                                                enrollment_id=str(enrollment.id.hex))
                        submission.save()
                    num_students_enrolled += 1
                except:
                    traceback.print_exc()
                    messages.error(request, INTERNAL_ERROR_MESSAGE)
            messages.success(request, str(num_students_enrolled) + ' students enrolled successfully.')
        else:
            print(create_form.errors)

    create_form = EnrollStudentForm(classes=classes, students=all_students)
    context = {
        'create_form': create_form
    }
    return render(request, 'administration/enroll_student.html', context)


def add_class(request):
    courses = []
    for course in Course.objects.all().order_by('course_name'):
        courses.append((course.course_id, course.course_name))
    teachers = []
    for teacher in Teacher.objects.all().order_by('first_name'):
        name = teacher.first_name + ' ' + teacher.last_name
        teachers.append((str(teacher.id.hex), name))
    periods = []
    for period in Schedule.objects.order_by().values_list('period').distinct():
        periods.append((period[0], period[0]))

    if request.method == 'POST':
        create_form = CreateClassForm(request.POST, courses=courses, teachers=teachers, periods=periods)
        if create_form.is_valid():
            course_id = create_form.cleaned_data.get('course')
            teacher_id = create_form.cleaned_data.get('teacher')
            period = create_form.cleaned_data.get('period')
            klass = Class(course_id=course_id, teacher_id=teacher_id, period=period)
            try:
                klass.save()
                messages.success(request, 'Class successfully added.')
            except IntegrityError:
                messages.error(request, 'The class you are trying to add already exists.')
            except:
                traceback.print_exc()
                messages.error(request, INTERNAL_ERROR_MESSAGE)
        else:
            print(create_form.errors)

    create_form = CreateClassForm(courses=courses, teachers=teachers, periods=periods)
    context = {
        'create_form': create_form
    }
    return render(request, 'administration/add_class.html', context)


def add_course(request):
    if request.method == 'POST':
        if 'confirm_upload' in request.POST:
            courses = serializers.deserialize('json', request.session.get('courses'))
            num_courses_added = 0
            for course in courses:
                try:
                    course.save()
                    num_courses_added += 1
                except IntegrityError:
                    pass
                except:
                    traceback.print_exc()
                    messages.error(request, INTERNAL_ERROR_MESSAGE)
                    break
            messages.success(request, message=(str(num_courses_added) + ' courses added successfully!'))
        elif 'upload' in request.POST:
            upload_form = UploadCSVForm(request.POST, request.FILES)
            if upload_form.is_valid():
                csv = upload_form.cleaned_data.get('csv')
                df = pd.read_csv(csv, header=0, dtype=str)
                try:
                    courses = []
                    for index, row in df.iterrows():
                        course = Course(course_id=row['course_id'],
                                        course_name=row['course_name'])
                        courses.append(course)
                    request.session['courses'] = serializers.serialize('json', courses)
                    return confirm_course_uploads(request, courses)
                except:
                    traceback.print_exc()
                    messages.error(request, 'Errors exist in the formatting of the uploaded CSV.')
        elif 'save' in request.POST:
            create_form = CreateCourseForm(request.POST)
            if create_form.is_valid():
                course_id = create_form.cleaned_data.get('course_id')
                course_name = create_form.cleaned_data.get('course_name')
                course = Course(course_id=course_id, course_name=course_name)
                try:
                    course.save()
                    messages.success(request, 'Course added successfully.')
                except IntegrityError:
                    messages.error(request, 'The course you are trying to add already exists.')
                except:
                    traceback.print_exc()
                    messages.error(request, INTERNAL_ERROR_MESSAGE)
    create_form = CreateCourseForm()
    course_id_description = 'Note that every course must have a unique alphanumeric ID'
    upload_form = UploadCSVForm()
    context = {
        'create_form': create_form,
        'course_id_description': course_id_description,
        'upload_form': upload_form
    }
    return render(request, 'administration/add_course.html', context)


def confirm_course_uploads(request, courses):
    context = {
        'courses': courses
    }
    return render(request, 'administration/confirm_course_uploads.html', context)


def add_teacher(request):
    if request.method == 'POST':
        if 'confirm_upload' in request.POST:
            users = request.session.get('users')
            teachers = serializers.deserialize('json', request.session.get('teachers'))
            num_teachers_added = 0
            for user_info, teacher in zip(users, list(teacher.object for teacher in teachers)):
                user_get_or_create = User.objects.get_or_create(username=user_info[0])
                user = user_get_or_create[0]
                if user_get_or_create[1]:
                    user.set_password(user_info[1])
                user.save()
                teacher.user = user
                try:
                    teacher_get_or_create = Teacher.objects.get_or_create(user=user, email_address=teacher.email_address)
                    num_teachers_added += int(teacher_get_or_create[1])
                except IntegrityError:
                    pass
                except:
                    traceback.print_exc()
                    messages.error(request, INTERNAL_ERROR_MESSAGE)
                    break
            messages.success(request, message=(str(num_teachers_added) + ' teachers added successfully!'))
        elif 'upload' in request.POST:
            upload_form = UploadCSVForm(request.POST, request.FILES)
            if upload_form.is_valid():
                csv = upload_form.cleaned_data.get('csv')
                df = pd.read_csv(csv, header=0, dtype=str)
                print(df.head())
                try:
                    users = []
                    teachers = []
                    for index, row in df.iterrows():
                        user_info = (row['username'], row['password'])
                        teacher = Teacher(user=None,
                                          first_name=row['first_name'],
                                          last_name=row['last_name'],
                                          email_address=row['email_address'],
                                          pref_title=row['pref_title'])
                        users.append(user_info)
                        teachers.append(teacher)
                    request.session['users'] = users
                    request.session['teachers'] = serializers.serialize('json', teachers)
                    return confirm_teacher_uploads(request, users, teachers)
                except:
                    traceback.print_exc()
                    messages.error(request, 'Errors exist in the formatting of the uploaded CSV.')
        elif 'save' in request.POST:
            create_form = CreateTeacherForm(request.POST)
            if create_form.is_valid():
                username = create_form.cleaned_data.get('username')
                password = create_form.cleaned_data.get('password')
                first_name = create_form.cleaned_data.get('first_name')
                last_name = create_form.cleaned_data.get('last_name')
                email_address = create_form.cleaned_data.get('email_address')
                pref_title = create_form.cleaned_data.get('pref_title')

                user_get_or_create = User.objects.get_or_create(username=username)
                user = user_get_or_create[0]
                if user_get_or_create[1]:
                    user.set_password(password)
                user.save()
                teacher = Teacher(user=user,
                                  first_name=first_name,
                                  last_name=last_name,
                                  email_address=email_address,
                                  pref_title=pref_title)
                try:
                    teacher_get_or_create = Teacher.objects.get_or_create(user=user, email_address=teacher.email_address)
                    if not teacher_get_or_create[1]:
                        raise IntegrityError
                    messages.success(request, 'Teacher successfully added!')
                except IntegrityError:
                    messages.error(request, 'The teacher you are trying to add already exists.')
                except:
                    traceback.print_exc()
                    messages.error(request, INTERNAL_ERROR_MESSAGE)
            else:
                print(create_form.errors)
    create_form = CreateTeacherForm()
    upload_form = UploadCSVForm()
    context = {
        'create_form': create_form,
        'upload_form': upload_form
    }
    return render(request, 'administration/add_teacher.html', context)


def confirm_teacher_uploads(request, users, teachers):
    context = {
        'students': list(zip(users, teachers))
    }
    return render(request, 'administration/confirm_teacher_upload.html', context)


def add_student(request):
    if request.method == 'POST':
        if 'confirm_upload' in request.POST:
            users = request.session.get('users')
            students = serializers.deserialize('json', request.session.get('students'))
            num_students_added = 0
            for user_info, student in zip(users, list(student.object for student in students)):
                user_get_or_create = User.objects.get_or_create(username=user_info[0])
                user = user_get_or_create[0]
                if user_get_or_create[1]:
                    user.set_password(user_info[1])
                user.save()
                student.user = user
                try:
                    student.save(student_id=student.student_id, auth_calendar=False)
                    num_students_added += 1
                except IntegrityError:
                    pass
                except:
                    traceback.print_exc()
                    messages.error(request, INTERNAL_ERROR_MESSAGE)
                    break
            messages.success(request, message=(str(num_students_added) + ' students added successfully!'))
        elif 'upload' in request.POST:
            upload_form = UploadCSVForm(request.POST, request.FILES)
            if upload_form.is_valid():
                csv = upload_form.cleaned_data.get('csv')
                df = pd.read_csv(csv, header=0, dtype=str)
                try:
                    users = []
                    students = []
                    for index, row in df.iterrows():
                        user_info = (row['username'], row['password'])
                        student = Student(user=None,
                                          first_name=row['first_name'],
                                          last_name=row['last_name'],
                                          email_address=row['email_address'],
                                          student_id=row['student_id'],
                                          grade=int(row['grade']))
                        users.append(user_info)
                        students.append(student)
                    request.session['users'] = users
                    request.session['students'] = serializers.serialize('json', students)
                    return confirm_student_uploads(request, users, students)
                except:
                    traceback.print_exc()
                    messages.error(request, 'Errors exist in the formatting of the uploaded CSV.')
        elif 'save' in request.POST:
            create_form = CreateStudentForm(request.POST)
            if create_form.is_valid():
                username = create_form.cleaned_data.get('username')
                password = create_form.cleaned_data.get('password')
                first_name = create_form.cleaned_data.get('first_name')
                last_name = create_form.cleaned_data.get('last_name')
                email_address = create_form.cleaned_data.get('email_address')
                student_id = create_form.cleaned_data.get('student_id')
                grade = create_form.cleaned_data.get('grade')
                user_get_or_create = User.objects.all().get_or_create(username=username)
                user = user_get_or_create[0]
                if user_get_or_create[1]:
                    user.set_password(password)
                user.save()
                student = Student(user=user,
                                  first_name=first_name,
                                  last_name=last_name,
                                  email_address=email_address,
                                  student_id=student_id,
                                  grade=grade)
                try:
                    student.save(student_id=student_id, auth_calendar=False)
                    messages.success(request, 'Student successfully added!')
                except IntegrityError:
                    messages.error(request, 'The students you are trying to add already exists.')
                except:
                    traceback.print_exc()
                    messages.error(request, INTERNAL_ERROR_MESSAGE)
            else:
                print(create_form.errors)

    create_form = CreateStudentForm()
    upload_form = UploadCSVForm()
    context = {
        'create_form': create_form,
        'upload_form': upload_form
    }
    return render(request, 'administration/add_student.html', context)


def confirm_student_uploads(request, users, students):
    context = {
        'students': list(zip(users, students))
    }
    return render(request, 'administration/confirm_student_upload.html', context)


def download_file(request, file_path):
    file_name = file_path
    file_path = file_path.replace('-', '/')
    file_path = finders.find(file_path)

    file = open(file_path, 'r')
    mime_type = mimetypes.guess_type(file_path)
    response = HttpResponse(file, content_type=mime_type)
    response['Content-Disposition'] = "attachment; filename=%s" % file_name
    return response


def login(request):
    next = request.GET.get('next')
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)

            if user is not None:
                try:
                    admin = Administrator.objects.all().get(user=user)
                    auth_login(request, user)
                    if next:
                        return redirect(next)
                    return redirect('administration-home')
                except:
                    messages.error(request, 'Administrator not found. Wrong portal?')
            else:
                messages.error(request, 'Invalid username or password')

    form = UserLoginForm()
    return render(request, 'administration/login.html', {'form': form})
