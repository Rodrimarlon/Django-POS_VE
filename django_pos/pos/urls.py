from django.urls import path

from . import views

app_name = "pos"
urlpatterns = [
    path('', views.index, name='index'),
    # Add sale (new or load draft)
    path('add/<int:sale_id>/', views.pos_view, name='pos_add_with_id'),
    path('add/', views.pos_view, name='pos'),
]
