from django.urls import path

from . import views

app_name = "customers"
urlpatterns = [
    # List customers
    path('', views.customers_list_view, name='customers_list'),
    # Add customer
    path('add', views.customers_add_view, name='customers_add'),
    # Update customer
    path('update/<str:customer_id>',
         views.customers_update_view, name='customers_update'),
    # Delete customer
    path('delete/<str:customer_id>',
         views.customers_delete_view, name='customers_delete'),
    # Get customers AJAX
    path("api/list", views.get_customers_ajax_view, name="get_customers_api"),
    # Create customer API
    path("api/create", views.customer_create_api, name="create_customer_api"),
    # Customer Purchase History Report
    path("history/<int:customer_id>/", views.customer_purchase_history_view, name="customer_purchase_history"),
]