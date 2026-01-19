from django.urls import path

from . import views
from . import admin
from . import api_views

app_name = 'finance'

urlpatterns = [
    # Web Views
    path('initiate_payment/', views.initiate_payment, name='initiate_payment'),
    path('get_payment_update/<id>/', views.get_payment_update, name='get_payment_update'),
    path('decline_payment/<id>/', admin.declinePayment, name='decline_payment'),
    path('user_wallet/<id>/<username>', views.user_wallet, name='user_wallet'),
    
    # API Endpoints
    path('api/wallet/balance/', api_views.wallet_balance, name='wallet_balance'),
    path('api/wallet/topup/', api_views.wallet_topup, name='wallet_topup'),
    path('api/wallet/deduct/', api_views.deduct_ride_payment, name='deduct_payment'),
    path('api/wallet/transactions/', api_views.transaction_history, name='transaction_history'),
]