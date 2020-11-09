from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction
from api.serializers import CustomAuthTokenSerializer, WalletEnableSerializer, \
    WalletDisableSerializer, TransactionSerializer
from api.models import Wallet, Transaction

import datetime


class HasWallet(IsAuthenticated):
    def has_permission(self, request, view):
        resp = super(HasWallet, self).has_permission(request, view)
        perm = False
        try:
            wallet = Wallet.objects.get(user=request.user)
            if not wallet.is_enabled:
                perm = False
            else:
                perm = True
        except Wallet.DoesNotExist:
            perm = False
        return perm and resp


class CustomAuthToken(ObtainAuthToken):
    serializer_class = CustomAuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'data': {
                'token': token.key,
            },
            'status': "success"

        })

class WalletEnableDisable(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user_wallet, created = self.get_or_create_wallet(request.user)
        if user_wallet.is_enabled and not created:
            return Response({"status": "failed", "message": "Wallet is already enabled"})
        elif not user_wallet.is_enabled:
            user_wallet.is_enabled = True
            user_wallet.enabled_at = datetime.datetime.now()
            user_wallet.save()
        serializer = WalletEnableSerializer(user_wallet)
        return Response({
            "status": "success",
            "data": serializer.data
        })

    def get(self, request):
        user_wallet, created = self.get_or_create_wallet(request.user)
        if user_wallet.is_enabled:
            serializer = WalletEnableSerializer(user_wallet)
            return Response({
                "status": "success",
                "data": serializer.data
            })
        else:
            return Response({"status": "failed", "message": "Wallet is not enabled"})

    def patch(self, request):
        user_wallet, created = self.get_or_create_wallet(request.user)
        print(user_wallet.is_enabled)
        if not user_wallet.is_enabled:
            return Response({"status": "failed", "message": "Wallet is not enabled"})
        user_wallet.is_enabled = False
        user_wallet.disabled_at = datetime.datetime.now()
        user_wallet.save()
        serializer = WalletDisableSerializer(user_wallet)
        return Response({
            "status": "success",
            "data": serializer.data
        })

    def get_or_create_wallet(self,user):
        created = False
        try:
            user_wallet = Wallet.objects.get(user=user)
        except Wallet.DoesNotExist:
            user_wallet = Wallet.objects.create(user=user,
                                                is_enabled=True, enabled_at=datetime.datetime.now())
            created = True
        return user_wallet, created


class WalletDeposit(APIView):
    permission_classes = (IsAuthenticated, HasWallet,)
    serializer_class = TransactionSerializer

    @transaction.atomic
    def post(self, request):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        if serializer.is_valid():
            transaction_object = Transaction.objects.create(
                user=request.user,
                amount=serializer.validated_data['amount'],
                reference_id=serializer.validated_data['reference_id'],
                transaction_type=Transaction.DEPOSIT
            )
            serializer = TransactionSerializer(transaction_object)
            return Response({
                "status": "success",
                "data": {
                    'deposit': serializer.data
                }
            })
        return Response({
                "status": "failed",
                "errors": serializer.errors
            })


class WalletWithdraw(APIView):
    permission_classes = (IsAuthenticated,HasWallet, )
    serializer_class = TransactionSerializer

    @transaction.atomic
    def post(self, request):

        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        if serializer.is_valid():
            user_wallet = Wallet.objects.get(user=request.user)
            if user_wallet.balance < serializer.validated_data['amount']:
                return Response({
                    "status": "failed",
                    "errors": "Amount should be less than wallet balance"
                })
            transaction_object = Transaction.objects.create(
                user=request.user,
                amount=serializer.validated_data['amount'],
                reference_id=serializer.validated_data['reference_id'],
                transaction_type=Transaction.WITHDRAW
            )
            serializer = TransactionSerializer(transaction_object)
            return Response({
                "status": "success",
                "data": {
                    'withdrawal': serializer.data
                }
            })
        return Response({
                "status": "failed",
                "errors": serializer.errors
            })