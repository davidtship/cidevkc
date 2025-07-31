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
    options = OptionSerializer(many=True, required=False)

    class Meta:
        model = Question
        fields = ['id', 'texte', 'type', 'options']

    def create(self, validated_data):
        options_data = validated_data.pop('options', [])
        question = Question.objects.create(**validated_data)
        for option_data in options_data:
            Option.objects.create(question=question, **option_data)
        return question

class RecursiveSectionSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, required=False)
    sous_sections = serializers.ListSerializer(child=serializers.SerializerMethodField(), required=False)

    class Meta:
        model = Section
        fields = ['id', 'titre', 'questions', 'sous_sections']

    def get_sous_sections(self, obj):
        children = obj.children.all()
        return RecursiveSectionSerializer(children, many=True).data

    def create(self, validated_data):
        questions_data = validated_data.pop('questions', [])
        sous_sections_data = validated_data.pop('sous_sections', [])
        parent = self.context.get('parent')
        formulaire = self.context['formulaire']

        section = Section.objects.create(titre=validated_data['titre'], parent=parent, formulaire=formulaire)

        for question_data in questions_data:
            options_data = question_data.pop('options', [])
            question = Question.objects.create(section=section, **question_data)
            for option_data in options_data:
                Option.objects.create(question=question, **option_data)

        for sous_section_data in sous_sections_data:
            serializer = RecursiveSectionSerializer(data=sous_section_data, context={'formulaire': formulaire, 'parent': section})
            serializer.is_valid(raise_exception=True)
            serializer.save()

        return section
class FormulaireWriteSerializer(serializers.ModelSerializer):
    sections = RecursiveSectionSerializer(many=True)

    class Meta:
        model = Formulaire
        fields = ['id', 'titre', 'user', 'sections']

    def create(self, validated_data):
        sections_data = validated_data.pop('sections', [])
        formulaire = Formulaire.objects.create(**validated_data)

        for section_data in sections_data:
            serializer = RecursiveSectionSerializer(data=section_data, context={'formulaire': formulaire, 'parent': None})
            serializer.is_valid(raise_exception=True)
            serializer.save()

        return formulaire
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
