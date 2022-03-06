from django.core.management.base import BaseCommand
from django.utils.timezone import now
from transactions.models import Transaction

class Command(BaseCommand):
    help = 'Executes programmed transactions'

    def handle(self, *args, **options):
        time_now = now()
        transactions = Transaction.objects.filter(status="Programada", timestamp__lte=time_now, transaction_type="Retiro")
        for t in transactions:
            if t.account.money < (t.ammount*-1):
                t.status = "Cancelada"
                print(t.auth_number, "Cancelada")
                t.save()
                counter = Transaction.objects.filter(status="Programada", auth_number=t.auth_number, transaction_type="Depósito").first()
                if counter:
                    counter.status = "Cancelada"
                    print(t.auth_number, "Cancelada")
                    counter.save()
                continue
            t.status = "Completada"
            print(t.auth_number, "Completada")
            t.save()
            t.account.money += t.ammount
            t.account.save()

        transactions = Transaction.objects.filter(status="Programada", timestamp__lte=now(), transaction_type="Depósito")
        for t in transactions:
            t.status = "Completada"
            print(t.auth_number, "Completada")
            t.save()
            t.account.money += t.ammount
            t.account.save()


