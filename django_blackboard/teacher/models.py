from django.db import models
from django.contrib.auth.models import User


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    teacher_id = models.CharField(max_length=4)
    id_picture = models.ImageField(upload_to='id_pictures', blank=True, default='id_pictures/default_pfp.png')
    email_address = models.CharField(max_length=320)

    def __str__(self):
        return self.first_name+'_'+self.last_name+'_'+self.teacher_id

    class Meta:
        db_table = 'teachers'
        order_with_respect_to = 'teacher_id'
