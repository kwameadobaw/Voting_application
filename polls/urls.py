from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('positions/', views.position_selection, name='position_selection'),
    path('vote/<int:position_id>/', views.voting, name='voting'),
    path('complete/', views.complete_voting, name='complete_voting'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('get-results/', views.get_results, name='get_results'),
    path('results/login/', views.voting_results_login, name='voting_results_login'),
    path('results/', views.voting_results, name='voting_results'),
    path('results/logout/', views.logout_results, name='logout_results'),
    path('results/reset/', views.reset_votes, name='reset_votes'),
    path('results/pdf/', views.download_results_pdf, name='download_results_pdf'),
    path('logout/', views.logout_view, name='logout'),
]