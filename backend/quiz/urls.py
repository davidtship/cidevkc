from django.urls import path, include
from . import views



urlpatterns = [
    path("terminal", views.TerminalView.as_view()),
    path("question", views.QuestionView.as_view()),
    path("categorie", views.CategorieView.as_view()),
    path("custcategorie", views.CustomCategorieView.as_view()),
    path("custcreatecategorie", views.CustomCreateCategorieView.as_view()),
    path("changestatus/<pk>", views.changestatus.as_view()),
    path("getFormbyid/<pk>", views.getFormbyid.as_view()),
    path("form", views.FormView.as_view()),
    path("choices", views.ChoicesView.as_view()),
    path("getMac_adress", views.getMac_adress.as_view()),
    path("get_count", views.Dashboard.as_view()),
    path("save_response", views.SaveRespone.as_view()),
    path("save_form", views.SaveForm.as_view()),
     path("returndataformuser", views.Return_reponses_form.as_view()),
     path("returndataformuser/<f>", views.Return_reponses_formbyid.as_view()),
     path("listeusers", views.ListeUsers.as_view()),

]