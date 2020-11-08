import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.dispatch import receiver
from django.db.models.signals import post_save


class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)


class Wallet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_enabled = models.BooleanField(verbose_name='status', default=False)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    balance = models.FloatField(default=0)
    enabled_at = models.DateTimeField(null=True, blank=True)
    disabled_at = models.DateTimeField(null=True, blank=True)


class Transaction(models.Model):
    SUCCESS = 'success'
    FAILED = 'failed'
    PENDING = 'pending'

    TRANSACTION_STATUS = (
        (PENDING, 'Pending'),
        (SUCCESS, 'Success'),
        (FAILED, 'Failed')
    )

    DEPOSIT = 'deposit'
    WITHDRAW = 'withdraw'

    TRANSACTION_TYPE = (
        (DEPOSIT, 'Deposit'),
        (WITHDRAW, 'Withdraw')
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser,related_name='transactions',on_delete=models.SET_NULL,null=True)
    amount = models.FloatField(default=0)
    reference_id = models.UUIDField(unique=True)
    transaction_date = models.DateTimeField(auto_now_add=True)
    transaction_type = models.CharField(max_length=100, choices=TRANSACTION_TYPE, default=DEPOSIT)
    transaction_status = models.CharField(max_length=100, choices=TRANSACTION_STATUS, default=PENDING)



@receiver(post_save,sender=Transaction)
def tansactionCreated(sender,instance,created,**kwargs):
    if created:
        if instance.transaction_type == Transaction.DEPOSIT:
            ob = Wallet.objects.get(user=instance.user)
            ob.balance = ob.balance + instance.amount
            ob.save()
        elif instance.transaction_type == Transaction.WITHDRAW:
            ob = Wallet.objects.get(user=instance.user)
            ob.balance = ob.balance - instance.amount
            ob.save()
        else:
            pass