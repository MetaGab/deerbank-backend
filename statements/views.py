from datetime import datetime, timezone as tz, timedelta as td
from decimal import Decimal

from rest_framework.response import Response
from rest_framework.status import HTTP_401_UNAUTHORIZED, HTTP_200_OK
from rest_framework.views import APIView
from django.utils import timezone

from bank.utilities import DocumentUtility
from bank.permissions import IsExecutive, IsTeller, IsBusiness, IsPerson, IsClientReadOnly
from accounts.models import Account
from transactions.models import Transaction
from transactions.serializers import TransactionSerializer


class GetStatement(APIView):
    permission_classes = [IsTeller | IsBusiness | IsPerson]

    def get(self, request, *args, **kwargs):
        filters = {'card__number': request.GET.get("number", "")}
        if request.user.client_type != "Cajero":
            filters['client'] = self.request.user

        account = Account.objects.filter(**filters).first()
        if not account:
            return Response({'msg': 'Datos de cuenta incorrectos'}, status=HTTP_401_UNAUTHORIZED)

        end_date = timezone.now().replace(day=account.cutoff_date.day)
        if end_date < timezone.now():
            try:
                end_date = end_date.replace(month=end_date.month+1)
            except ValueError:
                if end_date.month == 12:
                    end_date = end_date.replace(year=end_date.year+1, month=1)
                elif end_date.month == 1:
                    end_date = end_date.replace(month=end_date.month+1, day=28)
                else:
                    end_date = end_date.replace(month=end_date.month+1, day=30)
        try:
            start_date = end_date.replace(month=end_date.month-1, day=end_date.day+1)
        except ValueError:
            replaces = {"day":end_date.day+1, "month": end_date.month+1}
            if end_date.month == 1 and end_date.day != 31:
                replaces["year"] = end_date.year-1
                replaces["month"] = 12
            elif end_date.month == 1:
                replaces["year"] = end_date.year
                replaces["month"] = 1
                replaces["day"] = 1
            else:
                replaces["month"] = end_date.month
                replaces["day"] = 1
            start_date = end_date.replace(**replaces)

        zone = tz(td(hours=-7), name="America/Hermosillo")
        if "start_date" in request.GET and request.GET.get("start_date"):
            try:
                start_date = datetime.strptime(request.GET.get("start_date"), "%Y-%m-%d").replace(tzinfo=zone)
            except:
                return Response({'msg': 'Formato de fecha de inicio incorrecto'}, status=HTTP_401_UNAUTHORIZED)

        if "end_date" in request.GET and request.GET.get("end_date"):
            try:
                end_date = datetime.strptime(request.GET.get("end_date"), "%Y-%m-%d").replace(tzinfo=zone)
            except:
                return Response({'msg': 'Formato de fecha de fin incorrecto'}, status=HTTP_401_UNAUTHORIZED)

        end_date = end_date.replace(hour=23, minute=59, second=59)
        
        transactions = account.transactions.filter(timestamp__gte=start_date, timestamp__lt=end_date, status="Completada").order_by('timestamp')
        deposits, withdrawals = 0, 0
        balance = account.get_cutoff_ammount(start_date)
        movements = []
        last_date = start_date.date()
        last_balance = balance
        avg_balance = 0

        for t in transactions:
            deposit = None
            withdrawal = None
            if t.ammount > 0:
                deposits += t.ammount
                deposit = t.ammount
            else:
                withdrawals += (t.ammount*-1)
                withdrawal = t.ammount * -1
            balance += t.ammount

            if last_date == (t.timestamp- td(hours=7)).date():
                last_balance = balance 
            else:
                avg_balance += last_balance*(((t.timestamp - td(hours=7)).date()- last_date).days+1)
                last_balance = balance
                last_date = (t.timestamp - td(hours=7)).date()

            movements.append({
                "date": datetime.strftime(t.timestamp - td(hours=7), "%d/%m/%Y"),
                "concept": t.concept,
                "auth_num": t.auth_number,
                "deposit": deposit,
                "withdrawal": withdrawal,
                "balance": balance
            })

        avg_balance += last_balance*((end_date.date()-last_date).days+1)
        avg_balance = (avg_balance/((end_date-start_date).days+1)).quantize(Decimal('.01'))

        
        data = {
            'client': {
                'name': account.client.name,
                'address':account.client.address,
                'place':account.client.place,
                'zip_code':account.client.zip_code,
                'number':account.client.number,
                'rfc':account.client.rfc,
                'account_number': account.number
            },
            'branch': {
                'name':account.branch.name,
                'number': account.branch.number,
                'address':account.branch.address,
                'place':account.branch.place,
                'zip_code':account.branch.zip_code,
            },
            'cutoff_date': datetime.strftime(end_date, "%d/%m/%Y"),
            'start_date': datetime.strftime(start_date, "%d/%m/%Y"),
            'end_date': datetime.strftime(end_date, "%d/%m/%Y"),
            'prev_balance': account.get_cutoff_ammount(start_date),
            'deposits': deposits,
            'withdrawals': withdrawals,
            'final_balance': balance,
            'avg_balance': avg_balance,
            'movements': movements
        }

        DocumentUtility.generate_statement(data)

        data["file"] = "https://deerbank.herokuapp.com/media/statement/{}.pdf".format(account.client.number)
        
        return Response(data, status=HTTP_200_OK)


class GetCurrentAmmount(APIView):
    permission_classes = [IsTeller | IsBusiness | IsPerson]

    def get(self, request, *args, **kwargs):
        filters = {'card__number': request.GET.get("number", "")}
        if request.user.client_type != "Cajero":
            filters['client'] = self.request.user

        account = Account.objects.filter(**filters).first()
        if not account:
            return Response({'msg': 'Datos de cuenta incorrectos'}, status=HTTP_401_UNAUTHORIZED)

        return Response({'ammount': account.money}, status=HTTP_200_OK)
