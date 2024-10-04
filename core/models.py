from django.db import models

# Create your models here.
class Interpreter(models.Model):
    interpreter_name = models.CharField(max_length=255)
    district = models.CharField(max_length=100)
    employer = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    contact = models.CharField(max_length=15)
    years_experience = models.PositiveIntegerField()
    unique_code = models.CharField(max_length=10, unique=True)
    
    
    def __str__(self):
        return self.interpreter_name


class Course(models.Model):
    course_name = models.CharField(max_length=255)
    description = models.TextField()
    instructor = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    mode = models.CharField(max_length=50, choices=[('online', 'Online'), ('physical', 'Physical')])
    recurring_link = models.URLField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.course_name
    

class Videos(models.Model):
    video_name = models.CharField(max_length=255)
    video_link = models.URLField(max_length=500)
    description = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.video_name
    

class Event(models.Model):
    event_name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    description = models.TextField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    date = models.DateField()
    image = models.ImageField(upload_to='', null=True, blank=True) 

    def __str__(self):
        return self.event_name

    

class PDFUpload(models.Model):
    pdf_name = models.CharField(max_length=255)
    pdf_file = models.FileField(upload_to='pdfs/')

    def __str__(self):
        return self.pdf_name

