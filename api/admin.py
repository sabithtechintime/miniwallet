from django.contrib import admin
from api.models import Wallet, Transaction, CustomUser

# Register your models here.

admin.site.register(Wallet)
admin.site.register(Transaction)
admin.site.register(CustomUser)