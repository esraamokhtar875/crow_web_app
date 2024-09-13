from django.urls import path
from . import views

urlpatterns = [
    path('', views.projects_list, name='projects_list'),
    path('create/', views.create_project, name='create_project'),
    path('<slug:slug>/', views.project_details, name='project_details'),
    path('<slug:slug>/rate', views.rate_project, name='rate_project'),
    path('<slug:slug>/donate/', views.add_donation, name='add_donation'),
    path('<slug:slug>/cancel/', views.cancel_project, name='cancel_project'),
    path('<slug:slug>/rate/', views.rate_project, name='rate_project'),
    path('<slug:slug>/donate/', views.add_donation, name='add_donation'),
    path('<slug:slug>/comment/', views.add_comment, name='add_comment'),
    path('<slug:slug>/report/', views.report_project, name='report_project'),
    path('comments/<int:comment_id>/report/', views.report_comment, name='report_comment'),
    path('tags/<slug:slug>/', views.tagged, name="tagged"),
]