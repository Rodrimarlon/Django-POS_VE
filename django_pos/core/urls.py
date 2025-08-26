from django.urls import path
from . import views

app_name = "core"
urlpatterns = [
    path('company/', views.company_view, name='company_view'),
    path('company/update', views.company_update_view, name='company_update'),

    path('exchange-rate-modal', views.exchange_rate_modal_view, name='exchange_rate_modal'),
    path('exchange-rates/', views.exchange_rate_list_view, name='exchange_rate_list'),
]
