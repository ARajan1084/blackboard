from django.db import models
from django.contrib.auth.models import User


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    id_number = models.IntegerField()
    id_picture = models.ImageField(upload_to='id_pictures')

    def __str__(self):
        return self.first_name+'_'+self.last_name+'_'+self.id_number
