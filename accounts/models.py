import random, string

from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.base_user import BaseUserManager
from django.utils.timezone import now
from transactions.models import Transaction

class ClientManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.pop('is_superuser', False)
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

class Client(AbstractBaseUser):
    number = models.CharField(max_length=10, blank=True, null=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    rfc = models.CharField(max_length=13, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    place = models.CharField(max_length=255, blank=True, null=True)
    zip_code = models.CharField(max_length=5, blank=True, null=True)
    client_type = models.CharField(max_length=15)

    objects = ClientManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'client_type']

    def __str__(self):
        return self.name


class Branch(models.Model):
    number = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=255)
    place = models.CharField(max_length=255)
    zip_code = models.CharField(max_length=5, blank=True, null=True)

    def __str__(self):
        return self.name


class Account(models.Model):
    number = models.CharField(max_length=10, unique=True)
    cutoff_date = models.DateField(auto_now_add=True)
    money = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=50, default="Inactiva")
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="accounts")
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)

    def __str__(self):
        return self.number

    def hidden_name(self):
        names = self.client.name.split()
        hidden = ""
        for n in names:
            hidden += n[0] + "*** "
        return hidden

    def activate(self):
        self.status = "Activa"
        self.save()

    def get_current_ammount(self):
        return self.money

    def get_cutoff_ammount(self, date):
        ammount = self.money
        for transaction in self.transactions.filter(status="Completada", timestamp__gte=date):
            ammount -= transaction.ammount
        return ammount

    def deposit(self, ammount):
        self.money += ammount

        auth_num = ''.join(random.choices(string.digits, k=16))
        while Transaction.objects.filter(auth_number=auth_num).exists():
            auth_num = ''.join(random.choices(string.digits, k=16))

        deposit = Transaction(transaction_type="Depósito", status="Completada", concept="Depósito en Caja",
            ammount=ammount, auth_number=auth_num, account=self)
        deposit.save()
        self.save()
        
        return deposit

    
    def withdrawal(self, ammount):
        self.money -= ammount

        auth_num = ''.join(random.choices(string.digits, k=16))
        while Transaction.objects.filter(auth_number=auth_num).exists():
            auth_num = ''.join(random.choices(string.digits, k=16))

        withdrawal = Transaction(transaction_type="Retiro", status="Completada", concept="Retiro en Caja",
            ammount=-ammount, auth_number=auth_num, account=self)
        withdrawal.save()
        self.save()

        return withdrawal

    def transfer(self, ammount, destiny, concept):
        self.money -= ammount
        destiny.money += ammount

        auth_num = ''.join(random.choices(string.digits, k=16))
        while Transaction.objects.filter(auth_number=auth_num).exists():
            auth_num = ''.join(random.choices(string.digits, k=16))

        withdrawal = Transaction(transaction_type="Retiro", status="Completada", concept=concept,
            ammount=-ammount, auth_number=auth_num, account=self)

        deposit = Transaction(transaction_type="Depósito", status="Completada", concept=concept,
            ammount=ammount, auth_number=auth_num, account=destiny)

        withdrawal.save()
        deposit.save()
        self.save()
        destiny.save()
        
        return deposit

class Card(models.Model):
    number = models.CharField(max_length=16, unique=True)
    exp_date = models.DateField(default=now)
    pin = models.CharField(max_length=4)
    cvv = models.CharField(max_length=3)
    account = models.OneToOneField(Account, on_delete=models.CASCADE)

    def __str__(self):
        return self.number