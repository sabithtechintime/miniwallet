from django.contrib import admin
from api.models import Wallet, Transaction, CustomUser

# Register your models here.
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username')


admin.site.register(Wallet)
admin.site.register(Transaction)