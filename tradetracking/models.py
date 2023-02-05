from django.db import models

# Create your models here.

class Filing(models.Model):
    Prefix = models.CharField(max_length=255, null=True)
    First = models.CharField(max_length=255)
    Last = models.CharField(max_length=255)
    Suffix = models.CharField(max_length=255, null=True)
    FilingType = models.CharField(max_length=1)
    StateDst = models.CharField(max_length=255)
    Year = models.IntegerField()
    FilingDate = models.DateField()
    DocID = models.IntegerField(unique=True)