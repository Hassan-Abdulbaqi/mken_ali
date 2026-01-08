from django.urls import path
from . import views

app_name = 'storage'

urlpatterns = [
    path('', views.storage_list_view, name='list'),
    path('add/', views.storage_add_view, name='add'),
    path('edit/<int:item_id>/', views.storage_edit_view, name='edit'),
    path('delete/<int:item_id>/', views.storage_delete_view, name='delete'),
    path('api/departments/', views.get_departments_by_branch, name='get_departments'),
]

