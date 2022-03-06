from django.db import models
# Create your models here.

class Transaction(models.Model):
    transaction_type = models.CharField(max_length=20)
    status = models.CharField(max_length=20)
    concept = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    ammount = models.DecimalField(max_digits=10, decimal_places=2)
    auth_number = models.CharField(max_length=16)
    account = models.ForeignKey('accounts.Account', on_delete=models.CASCADE, related_name="transactions")