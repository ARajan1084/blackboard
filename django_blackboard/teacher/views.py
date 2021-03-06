import mimetypes
import os
import uuid
from datetime import datetime

import pandas as pd
from django.http import HttpResponse

from django_blackboard.settings import MEDIA_ROOT

from student.utils import calculate_grade
from teacher.analysis import get_score_dist, get_score_hist, get_score_box, get_general_stats

from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.utils import timezone

from .forms import UserLoginForm, CreateAssignmentForm, Scores, CreateCategoryForm, EditCategoriesForm, ThreadReplyForm, \
    NewThreadForm, ResourceUploadForm
from .models import Teacher
from board.models import Class, ClassAssignments, Course, Assignment, Category, ClassCategories, Notification, Discussion, ClassDiscussions
from student.models import ClassEnrollment, Student, Submission, GradeHistory
from .decorators import authentication_required
from .utils import fetch_assignments_with_categories, fetch_gradesheet_data, fetch_raw_grades, fetch_category_breakdown, \
    fetch_full_thread, fetch_class_discussions, fetch_all_discussions, get_submissions, get_student_scores, \
    get_assignments


@authentication_required
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


@authentication_required
def klass(request, element, class_id):
    if element == 'gradesheet':
        return gradesheet(request, class_id, active=element)
    elif element == 'dashboard':
        return dashboard(request, class_id, active=element)
    elif element == 'resources':
        return resources(request, class_id, active=element)
    elif element == 'discussions':
        return discussions(request, class_id, active=element)


@authentication_required
def gradesheet(request, class_id, active):
    klass = Class.objects.all().get(id=uuid.UUID(class_id).hex)
    course_name = get_course(class_id).course_name
    period = klass.period
    enrollments = ClassEnrollment.objects.all().filter(class_id=class_id)
    assignments = fetch_assignments_with_categories(class_id)

    gradesheet_data = fetch_gradesheet_data(klass, enrollments, assignments)
    data = gradesheet_data.get('data')
    grades = gradesheet_data.get('grades')
    raw_grades = fetch_raw_grades(grades)
    grade_dist = get_score_dist(raw_grades)
    grade_box = get_score_box(raw_grades)
    grade_stats = get_general_stats(raw_grades, 100)

    category_breakdown = fetch_category_breakdown(klass, enrollments)
    category_data = [[]]
    if category_breakdown:
        r = 0
        c = 1
        for category, category_scores in category_breakdown.items():
            if category_scores:
                category_dist = get_score_dist(category_scores)
                category_box = get_score_box(category_scores)
                category_stats = get_general_stats(category_scores, 100)
                category_data[r].append((category, (category_dist, category_box, category_stats)))
                if c == 3:
                    r += 1
                    category_data.append([])
                    c = 1
                c += 1
    context = {
        'active': active,
        'class_id': class_id,
        'course_name': course_name,
        'period': period,
        'assignments': assignments,
        'data': data,
        'grades': grades,
        'grade_dist': grade_dist,
        'grade_box': grade_box,
        'grade_stats': grade_stats,
        'category_data': category_data
    }
    return render(request, 'teacher/gradesheet.html', context)


@authentication_required
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


@authentication_required
def resources(request, class_id, active):
    resources_path = os.path.join(MEDIA_ROOT + '/resources/', class_id)
    if request.method == 'POST':
        form = ResourceUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['media']
            file_path = resources_path + '/' + file.name
            with open(file_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
    klass = Class.objects.all().get(id=uuid.UUID(class_id).hex)
    course_name = Course.objects.all().get(course_id=klass.course_id).course_name
    period = klass.period

    form = ResourceUploadForm()
    files = []
    for path in os.listdir(resources_path):
        full_path = os.path.join(resources_path, path)
        files.append((full_path, path))

    context = {
        'active': active,
        'class_id': class_id,
        'period': period,
        'course_name': course_name,
        'form': form,
        'files': files
    }
    return render(request, 'teacher/resources.html', context)


@authentication_required
def discussions(request, class_id, active):
    klass = Class.objects.all().get(id=uuid.UUID(class_id).hex)
    discussions = fetch_class_discussions(str(klass.id.hex))
    course_name = Course.objects.all().get(course_id=klass.course_id).course_name
    period = klass.period

    context = {
        'active': active,
        'class_id': class_id,
        'period': period,
        'course_name': course_name,
        'discussions': discussions
    }
    return render(request, 'teacher/discussions.html', context)


@authentication_required
def thread(request, class_id, discussion_id):
    root = Discussion.objects.all().get(id=uuid.UUID(discussion_id))
    if request.method == 'POST':
        all_discussions = fetch_all_discussions(root, all_discussions=None)
        form = ThreadReplyForm(discussions=all_discussions, data=request.POST)
        if form.is_valid():
            discussions = {}
            for key, value in form.cleaned_data.items():
                if value:
                    key_split = key.split('_')
                    reply = discussions.get(key_split[0])
                    if not reply:
                        reply = Discussion(user=request.user, reply_to=key_split[0], is_root=False)
                    if key_split[1] == 'message':
                        reply.message = value
                    elif key_split[1] == 'media':
                        reply.attached_media = value
                    discussions.update({key_split[0]: reply})
            for disc_id, discussion in discussions.items():
                discussion.save()
            return redirect('teacher-discussion', class_id, discussion_id)

    klass = Class.objects.all().get(id=uuid.UUID(class_id).hex)
    course_name = Course.objects.all().get(course_id=klass.course_id).course_name

    full_thread_w_form = fetch_full_thread(0, root, None, None)
    full_thread = full_thread_w_form[0]
    form = full_thread_w_form[1]

    context = {
        'active': 'discussions',
        'class_id': class_id,
        'course_name': course_name,
        'period': klass.period,
        'root': root,
        'full_thread': full_thread,
        'form': form
    }
    return render(request, 'teacher/thread.html', context)


@authentication_required
def new_thread(request, class_id):
    klass = Class.objects.all().get(id=uuid.UUID(class_id).hex)

    if request.method == 'POST':
        form = NewThreadForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data.get('title')
            message = form.cleaned_data.get('message')
            media = form.cleaned_data.get('media')
            discussion = Discussion(is_root=True, title=title, message=message, user=request.user, attached_media=media)
            discussion.save()
            class_discussion = ClassDiscussions(class_id=str(klass.id.hex), discussion_id=str(discussion.id.hex))
            class_discussion.save()
        return redirect('teacher-class', class_id=class_id, element='discussions')

    course = Course.objects.all().get(course_id=klass.course_id)
    form = NewThreadForm()

    context = {
        'active': 'discussions',
        'class_id': class_id,
        'course_name': course.course_name,
        'period': klass.period,
        'form': form
    }
    return render(request, 'teacher/new_thread.html', context)


@authentication_required
def new_assignment(request, class_id):
    teacher = Teacher.objects.all().get(user=request.user)
    klass = Class.objects.all().get(id=uuid.UUID(class_id))
    category_ids = ClassCategories.objects.all().filter(class_id=class_id)
    categories = []
    for category_id in category_ids:
        category_name = Category.objects.all().get(id=uuid.UUID(category_id.category_id).hex).category_name
        categories.append((category_id.category_id, category_name))

    if request.method == 'POST':
        form = CreateAssignmentForm(request.POST, request.FILES, categories=categories)
        if form.is_valid():
            name = form.cleaned_data.get('name')
            description = form.cleaned_data.get('description')
            category_id = form.cleaned_data.get('category')
            points = form.cleaned_data.get('points')
            due_date = form.cleaned_data.get('due_date')
            due_time = form.cleaned_data.get('due_time')
            est_completion_time_min = form.cleaned_data.get('est_completion_time_min')
            create_discussion_thread = form.cleaned_data.get('create_discussion_thread')
            due = datetime.combine(due_date, due_time)
            attached_media = request.FILES.get('attached_media')
            assignment = Assignment(assignment_name=name,
                                    assignment_description=description,
                                    category_id=category_id,
                                    points=points,
                                    due_date=due,
                                    assigned=timezone.now(),
                                    est_completion_time_min=est_completion_time_min,
                                    attached_media=attached_media)
            enrollments = ClassEnrollment.objects.all().filter(class_id=class_id)
            if 'assign' in request.POST:
                for enrollment in enrollments:
                    submission = Submission(assignment_id=str(assignment.id.hex),
                                            enrollment_id=str(enrollment.id.hex))
                    # creates notifications for students in the class
                    student = Student.objects.all().get(student_id=enrollment.student_id)
                    message = teacher.pref_title + ' ' + teacher.last_name + ' posted a new assignment: ' + \
                              assignment.assignment_name + ' due ' + str(assignment.due_date)
                    url = reverse('student-class', kwargs={'element': 'dashboard', 'enrollment_id': str(enrollment.id.hex)})
                    notification = Notification(recipient=student.user, message=message, link=url)
                    notification.save()
                    if due:
                        reminder = {'method': 'popup', 'minutes': 10}
                        submission.cal_event_id = student.add_reminder(summary=name, start_date_time=due,
                                                                       useDefault=False, override=reminder)
                    submission.save()
                class_assignment = ClassAssignments(class_id=class_id, assignment_id=str(assignment.id.hex))
                class_assignment.save()
                if create_discussion_thread:
                    title = assignment.assignment_name + ': Discussion Thread'
                    message = 'This is the official discussion thread for ' + assignment.assignment_name + '!'
                    discussion = Discussion(is_root=True, title=title, message=message, reply_to=None, user=teacher.user)
                    discussion.save()
                    class_discussion = ClassDiscussions(class_id=class_id, discussion_id=str(discussion.id.hex))
                    class_discussion.save()
            assignment.save()
            return redirect('teacher-class', class_id=class_id, element='gradesheet')
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


@authentication_required
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


@authentication_required
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
                    student = Student.objects.all().get(student_id=student_id)
                    if submission.score != score:
                        assignments = get_assignments(class_id)
                        gradeUpdate = GradeHistory(enrollment_id=str(enrollment.id.hex),
                                                   grade=calculate_grade(assignments=assignments,
                                                                         enrollment_id=str(enrollment.id.hex),
                                                                         weighted=klass.weighted)[1])
                        gradeUpdate.save()
                        message = 'Scores for ' + assignment.assignment_name + ' have been updated.'
                        url = reverse('student-class',
                                      kwargs={'element': 'grades', 'enrollment_id': str(enrollment.id.hex)})
                        notification = Notification(recipient=student.user, message=message, link=url)
                        notification.save()
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
    stats = get_general_stats(scores=scores, points=assignment.points)
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
        'box': box,
        'stats': stats
    }
    return render(request, 'teacher/assignment.html', context)


def assignment_export(request, class_id, assignment_id):
    assignment = Assignment.objects.all().get(id=uuid.UUID(assignment_id))
    data = {
        'student': [],
        'score': [],
        'comments': [],
    }

    enrollment_refs = ClassEnrollment.objects.all().filter(class_id=class_id)
    for enrollment_ref in enrollment_refs:
        student = Student.objects.all().get(student_id=enrollment_ref.student_id)
        submission = Submission.objects.all().get(enrollment_id=str(enrollment_ref.id.hex), assignment_id=assignment_id)
        data['student'].append(student.first_name + ' ' + student.last_name)
        data['score'].append(submission.score)
        data['comments'].append(submission.comments)

    path = os.path.join(MEDIA_ROOT + '/assignment_media/' + class_id, assignment_id + '/scores.xlsx')
    writer = pd.ExcelWriter(path)
    df = pd.DataFrame(data)
    df.to_excel(writer, header=True, index=False)
    writer.save()

    file = open(path, 'rb')
    response = HttpResponse(file, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(assignment.assignment_name + ' Scores.xlsx')
    return response


def get_course(class_id):
    course_id = Class.objects.all().get(id=uuid.UUID(class_id)).course_id
    return Course.objects.all().get(course_id=course_id)


@authentication_required
def download_content(request, file_path):
    file_path = file_path.replace('-', '/')
    file_path_breakdown = file_path.split('/')
    file = open(file_path, 'rb')
    mime_type = mimetypes.guess_type(file_path)
    response = HttpResponse(file, content_type=mime_type)
    response['Content-Disposition'] = "attachment; filename=%s" % file_path_breakdown[-1]
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
