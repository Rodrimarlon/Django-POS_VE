from django.urls import path

from . import views

app_name = "products"
urlpatterns = [
    # List products
    path('', views.products_list_view, name='products_list'),
    # Get products AJAX
    path("api/list", views.product_list_api, name="product_list_api"),
    path('api/categories/', views.category_list_api, name='category_list_api'),
    # Inventory Report
    path("inventory/report", views.inventory_report_view, name="inventory_report"),
]
