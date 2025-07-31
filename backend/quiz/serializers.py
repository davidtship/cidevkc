from djoser.serializers import (UserCreateSerializer as BaseUserCreateSerializer, 
                                UserSerializer as BaseUserSerializer)
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from .models import (Terminal,
                     Formulaire, 
                     Section, 
                     Question, 
                     Option, 
                     ReponseFormulaire, 
                     ReponseQuestion
)

user = get_user_model()



class UserCreateSerializer(BaseUserCreateSerializer):
    #image = Base64ImageField(required=False)
    class Meta(BaseUserCreateSerializer.Meta):
        
        fields = ['id', 'password', 'first_name', 'last_name',
                  'email','type_user']

    # you can grab the created user and do something with them here
    def create(self, validated_data):
        user = super().create(validated_data)

        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        obj = self.user

        data.update({
            'id': obj.id, 
            'first_name': obj.first_name,
            'last_name': obj.last_name, 
            'email': obj.email
          
        })

        return data

class TerminalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Terminal
        fields = '__all__'

class UserSerializer(BaseUserSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        fields = ['id', 'first_name',
                  'last_name', 'email','type_user','date_joined'
                 
                  ]
    def validate(self, attrs):
        validated_attr = super().validate(attrs)
        email = validated_attr.get('username')
        user = user.objects.get(email=email)
        return validated_attr

class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['id', 'texte']

class QuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True)

    class Meta:
        model = Question
        fields = ['id', 'texte', 'type', 'options']

class SectionSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)
    sous_sections = serializers.SerializerMethodField()

    class Meta:
        model = Section
        fields = ['id', 'titre', 'questions', 'sous_sections']

    def get_sous_sections(self, obj):
        serializer = SectionSerializer(obj.sous_sections.all(), many=True)
        return serializer.data

class FormulaireReadSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    sections = serializers.SerializerMethodField()

    class Meta:
        model = Formulaire
        fields = ['id', 'titre', 'user', 'sections', 'etat', 'date_creation']

    def get_sections(self, obj):
        root_sections = obj.sections.filter(parent__isnull=True)
        return SectionSerializer(root_sections, many=True).data

# Pour le POST
class OptionWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['texte']

class QuestionWriteSerializer(serializers.ModelSerializer):
    options = OptionWriteSerializer(many=True, required=False)

    class Meta:
        model = Question
        fields = ['texte', 'type', 'options']

class SectionWriteSerializer(serializers.ModelSerializer):
    questions = QuestionWriteSerializer(many=True, required=False)
    sous_sections = serializers.ListSerializer(child=serializers.DictField(), required=False)

    class Meta:
        model = Section
        fields = ['titre', 'questions', 'sous_sections']

class FormulaireWriteSerializer(serializers.ModelSerializer):
    sections = SectionWriteSerializer(many=True)
    user = serializers.PrimaryKeyRelatedField(queryset=user.objects.all())

    class Meta:
        model = Formulaire
        fields = ['titre', 'user', 'sections']

    def create(self, validated_data):
        sections_data = validated_data.pop('sections', [])
        formulaire = Formulaire.objects.create(**validated_data)

        def create_section(section_data, formulaire, parent=None):
            questions_data = section_data.pop('questions', [])
            sous_sections_data = section_data.pop('sous_sections', [])
            section = Section.objects.create(formulaire=formulaire, parent=parent, **section_data)

            for question_data in questions_data:
                options_data = question_data.pop('options', [])
                question = Question.objects.create(section=section, **question_data)
                for opt_data in options_data:
                    Option.objects.create(question=question, **opt_data)

            for sub_section_data in sous_sections_data:
                create_section(sub_section_data, formulaire, parent=section)

        for section_data in sections_data:
            create_section(section_data, formulaire)

        return formulaire
    
class ReponseQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReponseQuestion
        fields = ['question', 'valeur']

class ReponseFormulaireSerializer(serializers.ModelSerializer):
    reponses = ReponseQuestionSerializer(many=True)
    
    class Meta:
        model = ReponseFormulaire
        fields = ['formulaire', 'reponses']
    
    def create(self, validated_data):
        reponses_data = validated_data.pop('reponses')
        utilisateur = self.context['request'].user  # 👈 récupérer l'utilisateur connecté
        reponse_formulaire = ReponseFormulaire.objects.create(user=utilisateur, **validated_data)
        
        for reponse in reponses_data:
            ReponseQuestion.objects.create(reponse_formulaire=reponse_formulaire, **reponse)

        return reponse_formulaire
    
class ReponseQuestionDetailSerializer(serializers.ModelSerializer):
    question = serializers.CharField(source='question.texte')

    class Meta:
        model = ReponseQuestion
        fields = ['question', 'valeur']

class FormulaireSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    titre = serializers.CharField()

class ReponseFormulaireDetailSerializer(serializers.ModelSerializer):
    utilisateur = serializers.SerializerMethodField()
    formulaire = FormulaireSerializer()
    date_soumission = serializers.DateTimeField(source='date_creation')
    reponses = ReponseQuestionDetailSerializer(many=True, read_only=True)

    class Meta:
        model = ReponseFormulaire
        fields = ['id','formulaire', 'utilisateur', 'date_soumission', 'reponses']

    def get_utilisateur(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
