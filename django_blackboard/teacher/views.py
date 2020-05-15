import uuid
from collections import OrderedDict
from datetime import datetime
from teacher.analysis import get_score_dist, get_score_hist, get_score_box

from student.views import calculate_grade
from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from .forms import UserLoginForm, CreateAssignmentForm, Scores, CreateCategoryForm, EditCategoriesForm
from .models import Teacher
from board.models import Class, ClassAssignments, Course, Assignment, Category, ClassCategories
from student.models import ClassEnrollment, Student, Submission


@login_required(login_url='teacher-login')
def home(request):
    teacher = Teacher.objects.all().get(user=request.user)
    classes = Class.objects.all().filter(teacher_id=str(teacher.id.hex))
    class_data = []
    for klass in classes:
        course = get_course(str(klass.id.hex))
        num_students = ClassEnrollment.objects.all().filter(class_id=str(klass.id.hex)).count()
        class_data.append(
            [klass.period,
             course.course_name,
             num_students,
             str(klass.id.hex)]
        )
    context = {
        'class_data': class_data
    }
    return render(request, 'teacher/home.html', context)


@login_required(login_url='teacher-login')
def klass(request, element, class_id):
    if element == 'gradesheet':
        return gradesheet(request, class_id, active=element)
    elif element == 'dashboard':
        return dashboard(request, class_id, active=element)
    elif element == 'resources':
        return resources(request, class_id, active=element)
    elif element == 'discussions':
        return discussions(request, class_id, active=element)


@login_required(login_url='teacher-login')
def gradesheet(request, class_id, active):
    klass = Class.objects.all().get(id=uuid.UUID(class_id).hex)
    course_name = get_course(class_id).course_name
    period = klass.period
    enrollments = ClassEnrollment.objects.all().filter(class_id=class_id)
    assignment_ids = ClassAssignments.objects.all().filter(class_id=class_id)
    assignments = []
    for assignment_id in assignment_ids:
        assignment = Assignment.objects.all().get(id=uuid.UUID(assignment_id.assignment_id).hex)
        category = Category.objects.all().get(id=uuid.UUID(assignment.category_id))
        assignments.append((assignment, category))
    data = OrderedDict({})
    grades = {}
    for enrollment in enrollments:
        student = Student.objects.all().get(student_id=enrollment.student_id)
        grades.update({student: calculate_grade(assignments=[assignment[0] for assignment in assignments],
                                 enrollment_id=str(enrollment.id.hex),
                                 weighted=klass.weighted)})
        for assignment, category in assignments:
            submission = Submission.objects.get(enrollment_id=str(enrollment.id.hex),
                                                assignment_id=str(assignment.id.hex))
            try:
                current = data[student]
                score = (assignment, submission)
                data[student] = current + (score,)
            except:
                data.update({student: ((assignment, submission),)})
    context = {
        'active': active,
        'class_id': class_id,
        'course_name': course_name,
        'period': period,
        'assignments': assignments,
        'data': data,
        'grades': grades
    }
    return render(request, 'teacher/gradesheet.html', context)


def get_student_name(enrollment):
    student = Student.objects.all().get(student_id=enrollment.student_id)
    student_name = student.first_name + ' ' + student.last_name
    return student_name


@login_required(login_url='teacher-login')
def dashboard(request, class_id, active):
    klass = Class.objects.all().get(id=uuid.UUID(class_id).hex)
    course_name = Course.objects.all().get(course_id=klass.course_id).course_name
    period = klass.period
    context = {
        'active': active,
        'class_id': class_id,
        'period': period,
        'course_name': course_name
    }
    return render(request, 'teacher/dashboard.html', context)



@login_required(login_url='teacher-login')
def resources(request, class_id, active):
    klass = Class.objects.all().get(id=uuid.UUID(class_id).hex)
    course_name = Course.objects.all().get(course_id=klass.course_id).course_name
    period = klass.period;
    context = {
        'active': active,
        'class_id': class_id,
        'period': period,
        'course_name': course_name
    }
    return render(request, 'teacher/resources.html', context)


@login_required(login_url='teacher-login')
def discussions(request, class_id, active):
    klass = Class.objects.all().get(id=uuid.UUID(class_id).hex)
    course_name = Course.objects.all().get(course_id=klass.course_id).course_name
    period = klass.period
    context = {
        'active': active,
        'class_id': class_id,
        'period': period,
        'course_name': course_name
    }
    return render(request, 'teacher/discussions.html', context)


@login_required(login_url='teacher-login')
def new_assignment(request, class_id):
    klass = Class.objects.all().get(id=uuid.UUID(class_id))
    category_ids = ClassCategories.objects.all().filter(class_id=class_id)
    categories = []
    for category_id in category_ids:
        category_name = Category.objects.all().get(id=uuid.UUID(category_id.category_id).hex).category_name
        categories.append((category_id.category_id, category_name))

    if request.method == 'POST':
        form = CreateAssignmentForm(request.POST, categories=categories)
        if form.is_valid():
            name = form.cleaned_data.get('name')
            description = form.cleaned_data.get('description')
            category_id = form.cleaned_data.get('category')
            points = form.cleaned_data.get('points')
            due_date = form.cleaned_data.get('due_date')
            due_time = form.cleaned_data.get('due_time')
            due = datetime.combine(due_date, due_time)
            assignment = Assignment(assignment_name=name,
                                    assignment_description=description,
                                    category_id=category_id,
                                    points=points,
                                    due_date=due,
                                    assigned=timezone.now())
            enrollments = ClassEnrollment.objects.all().filter(class_id=class_id)
            for enrollment in enrollments:
                submission = Submission(assignment_id=str(assignment.id.hex),
                                        enrollment_id=str(enrollment.id.hex))
                student = Student.objects.all().get(student_id=enrollment.student_id)
                if due:
                    reminder = {'method': 'popup', 'minutes': 10}
                    submission.cal_event_id = student.add_reminder(summary=name, start_date_time=due,
                                                                   useDefault=False, override=reminder)
                submission.save()
            assignment.save()
            class_assignment = ClassAssignments(class_id=class_id, assignment_id=str(assignment.id.hex))
            class_assignment.save()
            return gradesheet(request, class_id, active='gradesheet')
        else:
            print(form.errors)
            print(form.non_field_errors())
    else:
        form = CreateAssignmentForm(categories=categories)
        context = {
            'active': 'gradesheet',
            'period': klass.period,
            'course_name': get_course(class_id).course_name,
            'class_id': class_id,
            'categories': categories,
            'form': form
        }
        return render(request, 'teacher/new_assignment.html', context)


@login_required(login_url='teacher-login')
def new_category(request, class_id, edit):
    klass = Class.objects.all().get(id=uuid.UUID(class_id).hex)
    period = klass.period

    current_category_refs = ClassCategories.objects.all().filter(class_id=str(klass.id.hex))
    current_categories = []
    for current_category_ref in current_category_refs:
        current_category = Category.objects.all().get(id=uuid.UUID(current_category_ref.category_id).hex)
        current_categories.append(current_category)

    if request.method == 'POST':
        if 'create_save' in request.POST:
            create_form = CreateCategoryForm(request.POST)
            if create_form.is_valid():
                category_name = create_form.cleaned_data.get('name')
                category_description = create_form.cleaned_data.get('description')
                weight = create_form.cleaned_data.get('weight')
                category = Category.objects.create(category_name=category_name,
                                                   category_description=category_description,
                                                   category_weight=weight)
                category.save()
                if weight:
                    klass.weighted = True
                    klass.save()
                class_category = ClassCategories.objects.create(class_id=class_id, category_id=str(category.id.hex))
                class_category.save()
                return redirect('teacher-new-category', class_id=class_id, edit='edit=false')
        elif 'save_edits' in request.POST:
            edit_form = EditCategoriesForm(request.POST, categories=current_categories)
            weighted = False
            if edit_form.is_valid():
                for category_id, weight in edit_form.cleaned_data.items():
                    category = Category.objects.all().get(id=uuid.UUID(category_id).hex)
                    category.category_weight = weight
                    category.save()
                    if weight:
                        weighted = True
                        klass.weighted = True
                        klass.save()
                if weighted:
                    klass.weighted = False
                    klass.save()
                return redirect('teacher-new-category', class_id=class_id, edit='edit=false')

    create_form = CreateCategoryForm()
    edit_form = EditCategoriesForm(categories=current_categories)
    context = {
        'active': 'gradesheet',
        'class_id': class_id,
        'course_name': get_course(class_id).course_name,
        'edit': edit,
        'period': period,
        'current_categories': current_categories,
        'create_form': create_form,
        'edit_form': edit_form
    }
    return render(request, 'teacher/new_category.html', context)


@login_required(login_url='teacher-login')
def assignment(request, class_id, assignment_id, edit):
    klass = Class.objects.all().get(id=uuid.UUID(class_id))
    assignment = Assignment.objects.all().get(id=uuid.UUID(assignment_id).hex)
    class_assignment = ClassAssignments.objects.all().get(class_id=class_id, assignment_id=assignment_id)
    student_scores = get_student_scores(assignment_id)
    if request.method == 'POST':
        form = Scores(request.POST, student_scores=student_scores)
        if form.is_valid():
            for student_id, score in form.cleaned_data.items():
                enrollment = ClassEnrollment.objects.all().get(student_id=student_id, class_id=class_id)
                submission = Submission.objects.all().get(enrollment_id=str(enrollment.id).replace('-', ''),
                                                          assignment_id=assignment_id)
                if 'save' in request.POST:
                    submission.score = score
                    submission.save()
                elif 'delete' in request.POST:
                    submission.delete()

            if 'delete' in request.POST:
                assignment.delete()
                class_assignment.delete()
                return redirect('teacher-class', element='gradesheet', class_id=class_id)
            edit = 'edit=false'
            return redirect('teacher-assignment', class_id=class_id, assignment_id=assignment_id, edit=edit)
    form = Scores(student_scores=student_scores)
    submissions = get_submissions(class_id, assignment_id)
    student_submissions = {}
    for submission in submissions:
        class_enrollment = ClassEnrollment.objects.all().get(id=uuid.UUID(submission.enrollment_id).hex)
        student = Student.objects.all().get(student_id=class_enrollment.student_id)
        student_submissions.update({student: submission})

    scores = []
    for student_score in student_scores:
        if student_score[1]:
            scores.append(student_score[1])
    curve = get_score_dist(scores)
    box = get_score_box(scores)
    context = {
        'class_id': class_id,
        'active': 'gradesheet',
        'course_name': get_course(class_id).course_name,
        'period': klass.period,
        'edit': edit,
        'form': form,
        'assignment': assignment,
        'student_scores': student_submissions,
        'curve': curve,
        'box': box
    }
    return render(request, 'teacher/assignment.html', context)


def get_course(class_id):
    course_id = Class.objects.all().get(id=uuid.UUID(class_id)).course_id
    return Course.objects.all().get(course_id=course_id)


def get_submissions(class_id, assignment_id):
    class_enrollments = ClassEnrollment.objects.all().filter(class_id=class_id)
    submissions = []
    for enrollment in class_enrollments:
        submission = Submission.objects.all().get(enrollment_id=str(enrollment.id).replace('-', ''),
                                                  assignment_id=assignment_id)
        submissions.append(submission)
    return submissions


def get_student_scores(assignment_id):
    class_assignment = ClassAssignments.objects.all().get(assignment_id=assignment_id)
    klass = Class.objects.all().get(id=uuid.UUID(class_assignment.class_id).hex)
    class_enrollments = ClassEnrollment.objects.all().filter(class_id=str(klass.id).replace('-', ''))
    student_scores = []
    for enrollment in class_enrollments:
        student = Student.objects.all().get(student_id=enrollment.student_id)
        submission_score = Submission.objects.all().get(enrollment_id=str(enrollment.id).replace('-', ''),
                                                        assignment_id=assignment_id).score
        student_scores.append((student, submission_score))
    return student_scores


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
                    teacher = Teacher.objects.all().get(user=user)
                    auth_login(request, user)
                    if next:
                        return redirect(next)
                    return redirect('teacher-board')
                except:
                    messages.error(request, 'teacher not found. wrong portal?')
            else:
                messages.error(request, 'invalid username or password')
    else:
        form = UserLoginForm()
    return render(request, 'teacher/login.html', {'form': form})


def logout(request):
    auth_logout(request)
    return login(request)
