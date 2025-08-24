from django.urls import path
from . import views

app_name = "core"
urlpatterns = [
    path('payment-methods/', views.payment_method_list_view, name='payment_method_list'),
    path('payment-methods/add', views.payment_method_add_view, name='payment_method_add'),
    path('payment-methods/update/<str:payment_method_id>', views.payment_method_update_view, name='payment_method_update'),
    path('payment-methods/delete/<str:payment_method_id>', views.payment_method_delete_view, name='payment_method_delete'),

    path('company/', views.company_view, name='company_view'),
    path('company/update', views.company_update_view, name='company_update'),

    path('exchange-rate-modal', views.exchange_rate_modal_view, name='exchange_rate_modal'),
    path('exchange-rates/', views.exchange_rate_list_view, name='exchange_rate_list'),
]