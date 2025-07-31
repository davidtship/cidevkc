from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from .models import Formulaire,ReponseFormulaire,ReponseQuestion,Question
from django.utils.decorators import method_decorator
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404
from django.http import JsonResponse
from .serializers import (
    CustomTokenObtainPairSerializer,
    FormulaireReadSerializer,
    TerminalSerializer,
    FormulaireWriteSerializer,
    ReponseFormulaireDetailSerializer,
    UserSerializer,)

from django.views.decorators.cache import cache_page
from django.contrib.auth import get_user_model
from rest_framework.generics import   ListCreateAPIView
from rest_framework.decorators import api_view
from .models import (Terminal)
from rest_framework import generics

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': '18'}, status=status.HTTP_200_OK)  # utilisateur non trouvé

        if not user.check_password(password):
            return Response({'error': '19'}, status=status.HTTP_200_OK)  # mot de passe invalide

        return super().post(request, *args, **kwargs)

@method_decorator(cache_page(10 * 1), name='dispatch')
class TerminalView(ListCreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = TerminalSerializer
    queryset = Terminal.objects.all() 
@method_decorator(cache_page(5 * 1), name='dispatch')

class Dashboard(APIView):
    permission_classes = (AllowAny,)
    def get(self, request):
        nombre_formulaire = Formulaire.objects.all().count()
        nombre_user = User.objects.all().count()
        nombre_terminal = Terminal.objects.all().count()
        data = {
            "formulaire":nombre_formulaire,
            "user":nombre_user,
            "terminal":nombre_terminal
        }
        return Response(data)

@method_decorator(cache_page(10 * 1), name='dispatch')
class ListeUsers(APIView):
    permission_classes = (AllowAny,)
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users,many=True)
        data = serializer.data
        return Response(data)

class RegisterTerminalView(APIView):
    def post(self, request):
        serializer = TerminalSerializer(data=request.data)
        if serializer.is_valid():
            device_uuid = serializer.validated_data['device_uuid']
            terminal, created = Terminal.objects.update_or_create(
                device_uuid=device_uuid,
                defaults={
                    'fingerprint': serializer.validated_data['fingerprint'],
                    'device_name': serializer.validated_data['device_name'],
                }
            )
            return Response({
                "detail": "Terminal enregistré." if created else "Terminal mis à jour."
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def check_device(request):
    permission_classes = (AllowAny,)
    fingerprint = request.GET.get('fingerprint')
    allowed = Terminal.objects.filter(fingerprint=fingerprint).exists()
    return Response({'allowed': allowed})


class FormulaireCreateAPIView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    queryset = Formulaire.objects.all()
    serializer_class = FormulaireWriteSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        # Ajoute automatiquement l'utilisateur connecté s'il n'est pas dans les données
        if not request.data.get('user') and request.user.is_authenticated:
            request.data._mutable = True  # nécessaire si c’est un QueryDict
            request.data['user'] = request.user.id
            request.data._mutable = False

        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

@method_decorator(cache_page(10 * 1), name='dispatch')
class FormulaireListAPIView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    queryset = Formulaire.objects.all().order_by('-date_creation')
    serializer_class = FormulaireReadSerializer
@method_decorator(cache_page(10 * 1), name='dispatch')
class FormulaireDetailAPIView(generics.RetrieveAPIView):
    permission_classes = (AllowAny,)
    queryset = Formulaire.objects.all()
    serializer_class = FormulaireReadSerializer
    lookup_field = 'pk'

class ReponseFormulaireCreateAPIView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        user = request.user
        data = request.data

        try:
            formulaire_id = data.get("formulaire")
            reponses_data = data.get("reponses", [])
            formulaire = Formulaire.objects.get(id=formulaire_id)

            # Création de l'objet ReponseFormulaire (réponse globale d'un utilisateur à un formulaire)
            reponse_formulaire = ReponseFormulaire.objects.create(
                formulaire=formulaire,
                user=user
            )

            for item in reponses_data:
                question_id = item.get("question")
                valeur = item.get("valeur")

                question = Question.objects.get(id=question_id)

                # Création de la réponse à une question
                ReponseQuestion.objects.create(
                    reponse_formulaire=reponse_formulaire,
                    question=question,
                    valeur=valeur  # valeur est un champ JSONField
                )

            return Response({"message": "Réponses enregistrées avec succès"}, status=status.HTTP_201_CREATED)

        except Formulaire.DoesNotExist:
            return Response({"error": "Formulaire introuvable"}, status=status.HTTP_400_BAD_REQUEST)
        except Question.DoesNotExist:
            return Response({"error": "Question introuvable"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@method_decorator(cache_page(10 * 1), name='dispatch')   
class ReponseDetailAPIView(APIView):
    permission_classes = (AllowAny,)
    def get(self, request, pk):
        instance = get_object_or_404(ReponseFormulaire, pk=pk)
        serializer = ReponseFormulaireDetailSerializer(instance)
        return Response(serializer.data)
    
@method_decorator(cache_page(10 * 1), name='dispatch')
class ReponseListeAPIView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    queryset = ReponseFormulaire.objects.all().order_by('-date_creation')
    serializer_class = ReponseFormulaireDetailSerializer
