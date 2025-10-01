from django.urls import path
from . import views

app_name = "core"
urlpatterns = [
    path('company/', views.company_view, name='company_view'),
    path('company/update', views.company_update_view, name='company_update'),

    path('exchange-rate-modal', views.exchange_rate_modal_view, name='exchange_rate_modal'),
    path('exchange-rates/', views.exchange_rate_list_view, name='exchange_rate_list'),
    path('api/latest-exchange-rate/', views.get_latest_exchange_rate_api, name='get_latest_exchange_rate_api'),
    path('api/payment-methods/', views.payment_method_list_api, name='payment_method_list_api'),
]
