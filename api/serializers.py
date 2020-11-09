from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from api.models import CustomUser,Wallet, Transaction


class CustomAuthTokenSerializer(serializers.Serializer):
    customer_xid = serializers.CharField(
        label=_("Userid"),
        write_only=True
    )
    token = serializers.CharField(
        label=_("Token"),
        read_only=True
    )

    def validate(self, attrs):
        customer_xid = attrs.get('customer_xid')
        if customer_xid:
            try:
                user = CustomUser.objects.get(pk=customer_xid, is_active=True)
            except CustomUser.DoesNotExist:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "customer_xid".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs


class WalletDisableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['id', 'user', 'is_enabled', 'balance', 'disabled_at']


class WalletEnableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['id', 'user', 'is_enabled', 'balance', 'enabled_at']


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'user', 'amount', 'reference_id',
                  'transaction_date', 'transaction_type', 'transaction_status']
