from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('create/', views.create_order_view, name='create'),
    path('submit/<int:order_id>/', views.submit_order_view, name='submit'),
    path('my-orders/', views.my_orders_view, name='my_orders'),
    path('<int:order_id>/', views.order_detail_view, name='detail'),
    path('remove-item/<int:item_id>/', views.remove_order_item_view, name='remove_item'),
    path('search-items/', views.search_items_view, name='search_items'),
    path('quick-add/<int:item_id>/', views.quick_add_item_view, name='quick_add'),
]


