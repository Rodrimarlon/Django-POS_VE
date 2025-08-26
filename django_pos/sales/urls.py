from django.urls import path

from . import views

app_name = "sales"
urlpatterns = [
    # List sales
    path('', views.sales_list_view, name='sales_list'),
    # Details sale
    path('details/<str:sale_id>',
         views.sales_details_view, name='sales_details'),
    # Sale receipt PDF
    path("pdf/<str:sale_id>",
         views.receipt_pdf_view, name="sales_receipt_pdf"),
    # Pending sales
    path('pending/', views.pending_sales_list_view, name='pending_sales_list'),
    # Pay credit sale
    path('pay_credit/<str:sale_id>/', views.pay_credit_sale_view, name='pay_credit_sale'),
    # Daily cash close report
    path('daily_cash_close_report/', views.daily_cash_close_report_view, name='daily_cash_close_report'),
]
