from django.urls import path
from api import views

urlpatterns = [
    path('init', views.CustomAuthToken.as_view(), name='api_token_auth'),
    path('wallet', views.WalletEnableDisable.as_view(), name='api_token_auth'),
    path('wallet/deposits', views.WalletDeposit.as_view(), name='api_token_auth'),
    path('wallet/withdrawals', views.WalletWithdraw.as_view(), name='api_token_auth'),
]