from django.urls import path
from .views import profile, dashboard, become_a_seller, earnings

app_name = 'users'

urlpatterns = [
    path('profile/', profile, name='profile'),
    path('dashboard/', dashboard, name='dashboard'),
    path('dashboard/my-earnings/', earnings, name='earnings'),
    path('become-a-seller/', become_a_seller, name='become_a_seller')
]