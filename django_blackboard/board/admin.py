from django.contrib import admin
from .models import Course, Class, ClassAssignments, Assignment, ClassCategories, Category


admin.site.register(Course)
admin.site.register(Class)
admin.site.register(ClassAssignments)
admin.site.register(ClassCategories)
admin.site.register(Assignment)
admin.site.register(Category)
