from django.urls import path
from .views import index
from django.contrib.auth import views as auth_views

app_name = 'Inicio'

urlpatterns = [
    path('', index, name='index'),
    # path(
    #     'password_reset/', 
    #     CustomPasswordResetView.as_view(), 
    #     name='password_reset'
    # ),
    # path(
    #     'reset/<uidb64>/<token>/', 
    #     custom_password_reset_confirm, 
    #     name='password_reset_confirm'
    # ),
    # path(
    #     'reset/done/', 
    #     auth_views.PasswordResetCompleteView.as_view(template_name='auth/password_reset_complete.html'), 
    #     name='password_reset_complete'
    # ),
    # path(
    #     'logout/', 
    #     auth_views.LogoutView.as_view(next_page='Inicio:index'),
    #     name='logout'
    # ),
]
