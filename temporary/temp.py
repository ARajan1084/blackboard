with open('/Users/achintya/blackboard/teacher_data.csv') as f:
    reader = csv.reader(f)
    for row in reader:
        _, created = Teacher.objects.get_or_create(
            User.objects.all().get(username=row[0], password=row[1]),
            first_name=row[3],
            last_name=row[4],
            teacher_id=row[2],
            email_address=row[5]
        )
        print(created)

with open('/Users/achintya/blackboard/course_data.csv') as f:
    reader = csv.reader(f)
    for row in reader:
        _, created = Course.objects.get_or_create(
            course_id=row[0],
            course_name=row[1]
        )