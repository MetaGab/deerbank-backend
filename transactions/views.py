from datetime import datetime
from decimal import Decimal
import random, string

from rest_framework.response import Response
from rest_framework.status import HTTP_401_UNAUTHORIZED, HTTP_200_OK
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from bank.permissions import IsExecutive, IsTeller, IsBusiness, IsPerson, IsClientReadOnly
from bank.utilities import DocumentUtility
from accounts.models import Account
from transactions.models import Transaction
from transactions.serializers import TransactionSerializer

# Create your views here.
class TransactionViewSet(ModelViewSet):
    queryset = Transaction.objects.none()
    serializer_class = TransactionSerializer
    permission_classes = [IsTeller | IsClientReadOnly]

    def get_queryset(self):
        if self.request.user.client_type == "Cajero":
            return Transaction.objects.all().order_by("-timestamp")
        return Transaction.objects.filter(account__client_id=self.request.user.id).order_by("-timestamp")
        
class PerformTransfer(APIView):
    permission_classes = [IsTeller | IsBusiness | IsPerson]

    def post(self, request, *args, **kwargs):
        destiny_account = request.data.get("destiny_account", "")
        origin_account = request.data.get("origin_account", "")
        try:
            exp_date = datetime.strptime("15/"+request.data.get("exp_date", ""), "%d/%m/%y")
        except:
            return Response({'msg': 'Error en formato de fecha de vencimiento'}, status=HTTP_401_UNAUTHORIZED)

        cvv = request.data.get("cvv", "")

        try:
            ammount = Decimal(request.data.get("ammount", ""))
        except:
            return Response({'msg': 'Error en monto'}, status=HTTP_401_UNAUTHORIZED)

        concept = request.data.get("concept", "")

        destiny = Account.objects.filter(card__number=destiny_account, status="Activa")
        if not destiny.exists():
            return Response({'msg': 'Datos de cuenta destino incorrectos'}, status=HTTP_401_UNAUTHORIZED)
        destiny = destiny.first()

        origin = Account.objects.filter(card__number=origin_account, card__cvv=cvv, card__exp_date__year=exp_date.year, card__exp_date__month=exp_date.month, status="Activa")
        if not origin.exists():
            return Response({'msg': 'Datos de cuenta origen incorrectos'}, status=HTTP_401_UNAUTHORIZED)
        origin = origin.first()

        if ammount <= 0:
            return Response({'msg': 'Monto no válido'}, status=HTTP_401_UNAUTHORIZED)

        if "timestamp" in request.data:
            response = {"msg": "Transacción programada"}
            auth_num = ''.join(random.choices(string.digits, k=16))
            while Transaction.objects.filter(auth_number=auth_num).exists():
                auth_num = ''.join(random.choices(string.digits, k=16))

            transaction = Transaction.objects.create(transaction_type="Retiro", status="Programada", concept=concept,
            ammount=-ammount, auth_number=auth_num, account=origin)
            transaction.timestamp = request.data.get("timestamp")
            transaction.save()

            transaction = Transaction.objects.create(transaction_type="Depósito", status="Programada", concept=concept,
            ammount=ammount, auth_number=auth_num, account=destiny)
            transaction.timestamp = request.data.get("timestamp")
            transaction.save()
        elif origin.money < ammount: 
            return Response({'msg': 'Monto insuficiente en cuenta origen'}, status=HTTP_401_UNAUTHORIZED)
        else:
            transaction = origin.transfer(ammount, destiny, concept)

        DocumentUtility.generate_receipt(transaction, request.user, origin, destiny)

        response = {
            "transaction_num": transaction.auth_number,
            "status": transaction.status,
            "date": transaction.timestamp,
            "ammount": transaction.ammount,
            "origin": origin.card.number[-4:],
            "destiny": destiny.card.number[-4:],
            "receipt": "https://deerbank.herokuapp.com/media/receipt/{}.pdf".format(transaction.auth_number)
        }

        return Response(response, status=HTTP_200_OK)

class PerformDeposit(APIView):
    permission_classes = [IsTeller]
    def post(self, request, *args, **kwargs):
        account = request.data.get("account", "")
        ammount = request.data.get("ammount", "")

        account = Account.objects.filter(card__number=account).first()

        if account and account.status == "Inactiva" and not account.transactions.exists():
            account.status = "Activa"
        elif account and account.status == "Inactiva":
            return Response({'msg': 'Cuenta inactiva'}, status=HTTP_401_UNAUTHORIZED)

        if not account:
            return Response({'msg': 'Datos de cuenta incorrectos'}, status=HTTP_401_UNAUTHORIZED)

        transaction = account.deposit(ammount)

        DocumentUtility.generate_ticket(transaction, account)

        response = {
            "transaction_num": transaction.auth_number,
            "status": transaction.status,
            "date": transaction.timestamp,
            "ammount": transaction.ammount,
            "account": account.card.number[-4:],
            "receipt": "https://deerbank.herokuapp.com/media/receipt/{}.pdf".format(transaction.auth_number)
        }

        return Response(response, status=HTTP_200_OK)

class PerformWithdrawal(APIView):
    permission_classes = [IsTeller]
    def post(self, request, *args, **kwargs):
        account = request.data.get("account", "")
        pin = request.data.get("pin", "")
        ammount = request.data.get("ammount", "")
        
        account = Account.objects.get(card__number=account, card__pin=pin, status="Activa")
        if account.money < ammount: 
            return Response({'msg': 'Monto insuficiente en cuenta origen'}, status=HTTP_401_UNAUTHORIZED)

        transaction = account.withdrawal(ammount)
        
        DocumentUtility.generate_ticket(transaction, account)

        response = {
            "transaction_num": transaction.auth_number,
            "status": transaction.status,
            "date": transaction.timestamp,
            "ammount": transaction.ammount,
            "account": account.card.number[-4:],
            "receipt": "https://deerbank.herokuapp.com/media/receipt/{}.pdf".format(transaction.auth_number)
        }

        return Response(response, status=HTTP_200_OK)