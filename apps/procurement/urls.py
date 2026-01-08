from django.urls import path
from . import views

app_name = 'procurement'

urlpatterns = [
    # Procurement Committee URLs
    path('pending/', views.pending_orders_view, name='pending_orders'),
    path('price/<int:order_id>/', views.price_order_view, name='price_order'),
    path('decisions/', views.decisions_view, name='decisions'),
    path('acknowledge/<int:order_id>/', views.acknowledge_order_view, name='acknowledge'),
    path('export/<int:order_id>/pdf/', views.export_order_pdf, name='export_pdf'),
    
    # Administrator URLs
    path('admin/pending/', views.admin_pending_view, name='admin_pending'),
    path('admin/review/<int:order_id>/', views.admin_review_view, name='admin_review'),
    path('admin/history/', views.admin_history_view, name='admin_history'),
]


