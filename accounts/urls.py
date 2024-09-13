from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.create_user, name='accounts_register'),
    path('login_/', views.login_user, name='login_'),
    path('logout/', views.logout_user, name='logout'),
    path('activate/<uidb64>/<token>', views.activate, name='accounts_activate'),
    path('delete_account/', views.delete_account, name='delete_account'),
    path("profile/<int:id>", views.edit_profile, name="profile"),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path("change_password/", views.change_password, name="change_password"),
    path("reset_password", views.password_reset_request, name="reset_password"),
    path('reset/<uidb64>/<token>', views.password_reset_confirm, name='password_reset_confirm'),
]




































# from django.urls import path
# from .views import register, activate, user_login, user_logout
# from django.contrib.auth import views as auth_views
#
#
# urlpatterns = [
#    path('register/', register, name='register'),
#    path('activate/<uidb64>/<token>/', activate, name='activate'),
#    path('login/', user_login, name='login'),
#    path('logout/', user_logout, name='logout'),
#     path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
# ]
