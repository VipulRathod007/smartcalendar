from django.db import models


class Meeting(models.Model):
    date = models.CharField(max_length=50, default="")
    time = models.CharField(max_length=50, default="")
    urlAddr = models.CharField(max_length=500, default="")
    meetAddr = models.CharField(max_length=500, default="")
    title = models.CharField(max_length=50, default="")
    meetType = models.CharField(max_length=25, default="")
    description = models.CharField(max_length=1000, default="")
    userid = models.IntegerField()

    def __str__(self):
        return self.title
