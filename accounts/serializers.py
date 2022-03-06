import random, string

from rest_framework import serializers
from accounts.models import Client, Branch, Account, Card

class ClientSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Client
        exclude = ['last_login']

    def create(self, validated_data):
        email = validated_data.pop("email", "")
        password = validated_data.pop("password", "")
        num = ''.join(random.choices(string.digits, k=10))
        while Client.objects.filter(number=num).exists():
            num = ''.join(random.choices(string.digits, k=10))
        validated_data["number"] = num
        client = Client.objects.create_user(email, password, **validated_data)
        return client


class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        exclude = []


class CardSerializer(serializers.ModelSerializer):
    account = serializers.PrimaryKeyRelatedField(read_only=True)
    account_id = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all(), write_only=True, source="account")

    class Meta:
        model = Card
        exclude = []
        read_only_fields = ['cvv', 'number']

    def create(self, validated_data):
        num = ''.join(random.choices(string.digits, k=16))
        while Card.objects.filter(number=num).exists():
            num = ''.join(random.choices(string.digits, k=16))
        validated_data["number"] = num
        validated_data["cvv"] = ''.join(random.choices(string.digits, k=3))
        validated_data["exp_date"] = "2024-12-15"
        card = Card.objects.create(**validated_data)
        return card

class CardDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Card
        exclude = ['account']


class AccountSerializer(serializers.ModelSerializer):
    branch = BranchSerializer(read_only=True)
    client = ClientSerializer(read_only=True)
    client_id = serializers.PrimaryKeyRelatedField(queryset=Client.objects.all(), write_only=True, source="client")
    branch_id = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all(), write_only=True, source="branch")

    class Meta:
        model = Account
        exclude = []
        read_only_fields = ['money', 'cutoff_date', 'number']

    def create(self, validated_data):
        num = ''.join(random.choices(string.digits, k=10))
        while Account.objects.filter(number=num).exists():
            num = ''.join(random.choices(string.digits, k=10))
        validated_data["number"] = num
        account = Account.objects.create(**validated_data)
        return account

class AccountSimpleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Account
        fields = ["id", "number"]

class AccountDetailSerializer(serializers.ModelSerializer):
    branch = BranchSerializer(read_only=True)
    card = CardDetailSerializer(read_only=True)

    class Meta:
        model = Account
        exclude = ['client']


class ClientDetailSerializer(serializers.ModelSerializer):
    accounts = AccountDetailSerializer(many=True, read_only=True)
    
    class Meta:
        model = Client
        exclude = ['last_login', 'password']