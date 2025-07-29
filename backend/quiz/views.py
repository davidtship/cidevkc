from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from getmac import get_mac_address as gma
import uuid
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import (CustomTokenObtainPairSerializer,
TerminalSerializer,
QuestionSerializer,
CategorieSerializer,
CustomFormSerializer,
CustomCategorieSerializer,
CustomCategorieSerializer,
ReponseUserSerializer,
ReponseSerializer,
UserSerializer,
FormSerializer,
ChoisesSerializer)
from django.contrib.auth import get_user_model
from rest_framework.generics import  ListAPIView, ListCreateAPIView,RetrieveUpdateDestroyAPIView

from .models import (Terminal,
                     Question,
                     Categorie,
                     Form,
                     Choices,
                     Reponse,
                     ReponseUser)
import uuid
User = get_user_model()

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        mac = gma()
        term = Terminal.objects.filter(adresse = str(mac))
        if term.exists():
            pass
            try:
                user = User.objects.get(email=request.data.get('email'))
            except User.DoesNotExist:
                return Response({'error': '18'}, status=status.HTTP_200_OK)
        else:
            try:
                user = User.objects.get(email=request.data.get('email'))
            except User.DoesNotExist:
                return Response({'error': '18'}, status=status.HTTP_200_OK)
        return super().post(request, *args, **kwargs)

class TerminalView(ListCreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = TerminalSerializer
    queryset = Terminal.objects.all() 

class QuestionView(ListCreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = QuestionSerializer
    queryset = Question.objects.all() 

class CategorieView(ListCreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = CategorieSerializer
    queryset = Categorie.objects.all() 

class FormView(ListCreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = CustomFormSerializer
    queryset = Form.objects.all() 

class ChoicesView(ListCreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = ChoisesSerializer
    queryset = Choices.objects.all() 

class CustomCategorieView(ListCreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = CustomCategorieSerializer
    queryset = Categorie.objects.all() 


class getMac_adress(APIView):
    permission_classes = (AllowAny,)
    def get(self, request):
        return Response({"mac":gma()})
    def post(self, request):
        mac=request.data["mac"]
        ad = Terminal.objects.filter(adresse = mac)
        if ad.exists():
            message="Ce terminal existe"
        else:
            message="Ce terminal n'existe pas"
        return Response({"message":message})
    
class CustomCreateCategorieView(APIView):
    permission_classes = (AllowAny,)
    def get(self, request):
            categories = Categorie.objects.all()
            serializer = CustomCategorieSerializer(categories , many=True)
            data = serializer.data
            return Response(data)
    def post(self, request):
        
        form = request.data["form"]
        sections = request.data["sections"]
        cat_form = uuid.uuid1()
        for section in sections:
            code_uid = uuid.uuid1()
            title=section["title"] 
            questions=section["questions"]
            for question in questions:
                if question["type"] =="multiple_choice" or question["type"] =="checkboxes":
                    for option in question["options"]:
                        choices = Choices.objects.create(code_uid = code_uid,option = option)
                    
                choices = Choices.objects.filter(code_uid = code_uid)
                questions = Question.objects.create(
                                                    code_uid = code_uid , 
                                                    label = question["label"],
                                                    question_type = question["type"],
                                                        required = True )
                questions.choices.set(choices)
                questions.save()
            questions = Question.objects.filter(code_uid = code_uid)
            categories = Categorie.objects.create(cat_form = cat_form,code_uid = code_uid,
                                                title = title,
                                                )
            categories.questions.set(questions)
            categories.save()
        cate = Categorie.objects.filter(cat_form = cat_form)
        formulaire = Form.objects.create(title = form)
        formulaire.categories.set(cate)
        formulaire.save()
        serializer = CustomCategorieSerializer(categories , many=False)
        data = serializer.data
        return Response(data)
    
class changestatus(APIView):
    permission_classes = (AllowAny,)
    def get(self, request,pk):
        form = Form.objects.get(id = pk)
        if (form.statut):
            form.statut = False
            form.save()
        else:
            form.statut = True
            form.save()
        serializer = CustomFormSerializer(form,many=False)
        data = serializer.data
        return Response(data)

class getFormbyid(APIView):
    permission_classes = (AllowAny,)
    def get(self, request,pk):
        form = Form.objects.get(id = pk)
        serializer = CustomFormSerializer(form,many=False)
        data = serializer.data
        return Response(data)

class Dashboard(APIView):
    permission_classes = (AllowAny,)
    def get(self, request):
        nombre_formulaire = Form.objects.all().count()
        nombre_user = User.objects.all().count()
        nombre_terminal = Terminal.objects.all().count()
        data = {
            "formulaire":nombre_formulaire,
            "user":nombre_user,
            "terminal":nombre_terminal
        }
        return Response(data)



class SaveRespone(APIView):
    permission_classes = (AllowAny,)
    def post(self, request):
        user = request.user
        response_courte = request.data["shortAnswers"]
        checkbox = request.data["checkboxAnswers"]
        radio = request.data["radioAnswers"]
        
        data = {
        "shortAnswers": [
        {"id": k, "rep": v} for k, v in response_courte.items()
         ]
        ,
        "checkboxAnswers": [
        {"id": k, "rep": v} for k, v in checkbox.items()
         ]
         ,
        "radioAnswers": [
        {"id": k, "rep": v} for k, v in radio.items()
         ]
         }
        
        for courte_rep in data["shortAnswers"]:
                 resp = Reponse.objects.create(question_id = int(courte_rep["id"]),
                                               rep =courte_rep["rep"],user = user  )
        for check in data["checkboxAnswers"]:
                 resp = Reponse.objects.create(question_id = int(check["id"]),
                                               rep =check["rep"],user = user  )
        for rad in data["radioAnswers"]:
                 resp = Reponse.objects.create(question_id = int(rad["id"]),
                                               rep =rad["rep"],user = user  )
                 
        return Response({"message":"Done!"})
    
class SaveForm(APIView):
    permission_classes = (AllowAny,)
    def post(self, request):
        user = request.user
        form_id = request.data["form"]
        saveform = ReponseUser.objects.create(form_id = form_id,user = user)
        return Response({"message":"Save done!"})

class Return_reponses_form(APIView):
    permission_classes = (AllowAny,)
    def get(self, request):
        rep = ReponseUser.objects.filter(user=request.user)
        serializer = ReponseUserSerializer(rep,context={'request': request},many=True)
        data = serializer.data
        return Response(data)
       
class Return_reponses(APIView):
    permission_classes = (AllowAny,)
    def get(self, request,u):
        rep = Reponse.objects.filter(user_id=u)
        serializer = ReponseSerializer(rep,many=True)
        data = serializer.data
        return Response(data)
    
class Return_reponses_formbyid(APIView):
    permission_classes = (AllowAny,)
    def get(self, request,f):
        rep = ReponseUser.objects.filter(user=request.user,form_id = f)
        serializer = ReponseUserSerializer(rep,context={'request': request},many=True)
        data = serializer.data
        return Response(data)

class ListeUsers(APIView):
    permission_classes = (AllowAny,)
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users,many=True)
        data = serializer.data
        return Response(data)
