from django.db import models

# Create your models here.


class UploadedFile(models.Model):
    uploadfile = models.BinaryField()
    filename = models.CharField(max_length=30)
    rowscount = models.IntegerField()
    colscount = models.IntegerField()
    uploadtime = models.DateTimeField(auto_now_add=True)
