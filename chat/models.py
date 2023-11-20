from django.db import models
from django.contrib.auth.models import AbstractUser,User

# Create your models here.

class CustomUser(AbstractUser):
    USER = (
        ('1','Admin'),
        ('2','User'),
    )
    user_type = models.CharField(choices=USER, default=1, max_length=50)

class Timetable(models.Model):
    semester = models.CharField(max_length=100)
    day = models.CharField(max_length=20)
    course_name = models.CharField(max_length=100)
    time = models.TimeField()
    location = models.CharField(max_length=100)
    def __str__(self):
        return self.course_name


class Datesheet(models.Model):
    semester = models.CharField(max_length=100)
    exam_date = models.DateField()
    time = models.TimeField()
    exam_subject = models.CharField(max_length=100)
    def __str__(self):
        return self.semester

class Staff(models.Model):
    name = models.CharField(max_length=100)
    faculty = models.CharField(max_length=200)
    department = models.CharField(max_length=200)
    designation = models.CharField(max_length=100)
    def __str__(self):
        return self.designation

class ChatHistory(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    questions = models.TextField()
    responses = models.TextField()
    reply = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Chat History for {self.user.username}"