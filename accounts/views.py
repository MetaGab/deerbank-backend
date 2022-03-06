from django.shortcuts import render
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.status import HTTP_401_UNAUTHORIZED, HTTP_200_OK
from rest_framework.permissions import IsAuthenticated
from bank.permissions import IsExecutive, IsTeller, IsBusiness, IsPerson, IsClientReadOnly
from accounts.serializers import ClientSerializer, ClientDetailSerializer, AccountSerializer, CardSerializer, BranchSerializer
from accounts.models import Client, Account, Card, Branch

# Create your views here.

class AuthTokenView(ObtainAuthToken):
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        request.data["username"] = request.data["email"]
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'email': user.email,
            'name': str(user),
            'type': user.client_type
        })
    
class VerifyAuthTokenView(APIView):
    authentication_classes = []
    
    def post(self, request, *args, **kwargs):

        if "token" in request.data and Token.objects.filter(key=request.data["token"]).exists():
            user = Token.objects.get(key=request.data["token"]).user
            return Response({"email":user.email, "name":str(user)}, status=HTTP_200_OK)

        return Response({}, status=HTTP_401_UNAUTHORIZED)
       

class LogoutUserAPIView(APIView):

    def get(self, request, format=None):
        request.user.auth_token.delete()
        return Response(status=HTTP_200_OK)


class ClientViewSet(ModelViewSet):
    queryset = Client.objects.none()
    permission_classes = [IsExecutive | IsClientReadOnly]

    def get_queryset(self):
        if self.request.user.client_type != "Ejecutivo":
            return Client.objects.filter(id=self.request.user.id)   
        return Client.objects.filter(client_type__in=["Persona Física", "Persona Moral"])

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ClientDetailSerializer
        return ClientSerializer


class AccountViewSet(ModelViewSet):
    queryset = Account.objects.none()
    serializer_class = AccountSerializer
    permission_classes = [IsExecutive | IsClientReadOnly]

    def get_queryset(self):
        if self.request.user.client_type != "Ejecutivo":
            return Account.objects.filter(client_id=self.request.user.id)
        return Account.objects.all()


class CardViewSet(ModelViewSet):
    queryset = Card.objects.none()
    serializer_class = CardSerializer
    permission_classes = [IsExecutive | IsClientReadOnly]

    def get_queryset(self):
        if self.request.user.client_type != "Ejecutivo":
            return Card.objects.filter(account__client_id=self.request.user.id)
        return Card.objects.all()

class BranchViewSet(ModelViewSet):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    permission_classes = [IsExecutive | IsTeller | IsClientReadOnly]