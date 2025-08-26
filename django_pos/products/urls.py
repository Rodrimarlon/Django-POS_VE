from django.urls import path

from . import views

app_name = "products"
urlpatterns = [
    # List products
    path('', views.products_list_view, name='products_list'),
    # Get products AJAX
    path("get", views.get_products_ajax_view, name="get_products"),
    # Inventory Report
    path("inventory/report", views.inventory_report_view, name="inventory_report"),
]
