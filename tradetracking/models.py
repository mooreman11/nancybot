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

class Trade(models.Model):
    DocID = models.ForeignKey(to=Filing, on_delete=models.CASCADE)
    Ticker = models.CharField(max_length=255)
    Transaction = models.CharField(max_length=2)
    Quantity = models.IntegerField()
    StrikePrice = models.IntegerField(null=True)
    PurchaseDate: models.DateField(null=True)
    ExpirationData = models.DateField(null=True)

