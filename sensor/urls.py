from django.urls import path
from . import views


app_name = 'sensor'
urlpatterns = [
path('temperature/', views.user_temperature_data, name='user_temperature_data'),
path('offer-service/', views.offer_service, name='offer_service'),
path('services/', views.service_list, name='service_list'),
path('my-subscriptions/', views.my_subscriptions, name='my_subscriptions'),
path('subscribe/<int:service_id>/', views.subscribe, name='subscribe'),

]
