from django.db import models


class Meeting(models.Model):
    date = models.CharField(max_length=50, default="")
    time = models.CharField(max_length=50, default="")
    urlAddr = models.CharField(max_length=500, default="")
    meetAddr = models.CharField(max_length=500, default="")
    title = models.CharField(max_length=50, default="")
    meetType = models.CharField(max_length=25, default="")
    description = models.CharField(max_length=1000, default="")
    meetingNotes = models.CharField(max_length=2000, default="")
    refMeet = models.IntegerField(default=0)
    userid = models.IntegerField()

    def __str__(self):
        return self.title


class Task(models.Model):
    date = models.CharField(max_length=50, default="")
    time = models.CharField(max_length=50, default="")
    title = models.CharField(max_length=50, default="")
    taskGroup = models.CharField(max_length=25, default="")
    description = models.CharField(max_length=1000, default="")
    taskNotes = models.CharField(max_length=2000, default="")
    refTask = models.IntegerField(default=0)
    userid = models.IntegerField()

    def __str__(self):
        return self.title
