from django.db import models

# Create your models here.
class Product(models.Model):
    sale_id = models.CharField(max_length=200)
    category = models.CharField(max_length=50)
    price = models.IntegerField()
    name = models.CharField(max_length=200)
    quantity = models.IntegerField()

    def __str__(self):
        return self.sale_id + ":" + self.name


class Payment(models.Model):
    sale_id = models.CharField(max_length=200)
    amount = models.IntegerField()
    type = models.CharField(max_length=50)

    def __str__(self):
        return self.sale_id + ":" + str(self.amount)


class Sale(models.Model):
    closed = models.DateTimeField()
    zone = models.CharField(max_length=50)
    waiter = models.CharField(max_length=200)
    cashier = models.CharField(max_length=200)
    diners = models.IntegerField()
    opened = models.DateTimeField()
    table = models.IntegerField()
    total = models.IntegerField()
    sale_id = models.CharField(max_length=200, primary_key=True)

    def __str__(self):
        return self.sale_id

