from django.urls import path
from . import views

app_name = "suppliers"
urlpatterns = [
    path('', views.supplier_list_view, name='supplier_list'),
    path('add', views.supplier_add_view, name='supplier_add'),
    path('update/<str:supplier_id>', views.supplier_update_view, name='supplier_update'),
    path('delete/<str:supplier_id>', views.supplier_delete_view, name='supplier_delete'),
]