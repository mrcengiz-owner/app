from django.urls import path
from django.contrib.auth import views as auth_views  # auth_views doğru şekilde içe aktarılıyor
from .views import *

urlpatterns = [
    path('', home, name='home'),
    path('order/', order_page, name='order_page'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),  # LoginView kullanılıyor
    # path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),  # LogoutView kullanılıyor
    path('logout/', logout_view, name='logout'),
    path('orderlist/', orderlist, name='orderlist'),
    path('create_order/', create_order, name='create_order'),
    path('firma/', firma, name='firma'),
    path('download_all_orders_pdf/', download_all_orders_pdf, name='download_all_orders_pdf'),
    path('download_company_orders_pdf/<int:company_id>/', download_company_orders_pdf, name='download_company_orders_pdf'),





]
