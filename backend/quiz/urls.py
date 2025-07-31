from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

urlpatterns = [
    path("terminal", views.TerminalView.as_view()),
    path("get_count", views.Dashboard.as_view()),
    path("listeusers", views.ListeUsers.as_view()),
    path('save-device/', views.RegisterTerminalView.as_view(), name='save-device'),
    path('check_device/', views.check_device, name='check_device'),
    path('formulaires/', views.FormulaireCreateAPIView.as_view(), name='create-formulaire'),
    path('list-formulaires/', views.FormulaireListAPIView.as_view(), name='list-formulaires'),
    path('formulaires/<int:pk>/', views.FormulaireDetailAPIView.as_view(), name='formulaire-detail'),
    path('reponses/', views.ReponseFormulaireCreateAPIView.as_view(), name='envoyer-reponses'),
    path('formulaires-reponses/<int:pk>/', views.ReponseDetailAPIView.as_view(), name='reponse-detail'),
    path('formulaires-reponses-liste/', views.ReponseListeAPIView.as_view(), name='reponse-liste'),
   
]
