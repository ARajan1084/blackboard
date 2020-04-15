import csv
from django.contrib.auth.models import User


with open('/Users/achintya/blackboard/teacher_data.csv') as f:
    reader = csv.reader(f)
    for row in reader:
        _, created = User.objects.get_or_create(
            username=row[0],
            password=row[1]
        )
        print(created)