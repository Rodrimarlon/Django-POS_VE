from django.urls import path

from . import views

app_name = "pos"
urlpatterns = [
    path('', views.index, name='index'),
    # Add sale (new or load draft)
    path('add/<int:sale_id>/', views.pos_view, name='pos_add_with_id'),
    path('add/', views.pos_view, name='pos'),
    path('orders/save/', views.save_order_view, name='save_order'),
    path('orders/list/', views.order_list_view, name='order_list'),
    path('orders/<int:order_id>/delete/', views.delete_order_view, name='delete_order'),
    path('orders/<int:order_id>/detail/', views.order_detail_view, name='order_detail'),
]
