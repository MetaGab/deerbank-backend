from rest_framework import serializers
from accounts.serializers import AccountSimpleSerializer
from transactions.models import Transaction

class TransactionSerializer(serializers.ModelSerializer):
    account = AccountSimpleSerializer(read_only=True)
    
    class Meta:
        model = Transaction
        exclude = []