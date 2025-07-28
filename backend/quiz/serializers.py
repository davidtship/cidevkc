from djoser.serializers import (UserCreateSerializer as BaseUserCreateSerializer, 
                                UserSerializer as BaseUserSerializer)
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from .models import (Terminal,
                     Question,
                     Categorie,
                     Form,Choices,
                     Reponse,
                     ReponseUser)

user = get_user_model()
import ast


class UserCreateSerializer(BaseUserCreateSerializer):
    #image = Base64ImageField(required=False)
    class Meta(BaseUserCreateSerializer.Meta):
        
        fields = ['id', 'password', 'first_name','username', 'last_name',
                  'email','image','type_user']

    # you can grab the created user and do something with them here
    def create(self, validated_data):

        user = super().create(validated_data)

        return user
class UserSerializer(BaseUserSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        fields = ['id', 'first_name','username',
                  'last_name', 'email','type_user','date_joined'
                 
                  ]
    def validate(self, attrs):
        validated_attr = super().validate(attrs)
        username = validated_attr.get('username')
        user = user.objects.get(username=username)
        return validated_attr


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        obj = self.user

        data.update({
            'id': obj.id, 
            'first_name': obj.first_name,
            'last_name': obj.last_name, 
            'email': obj.email,
            'username': obj.username,
            'image':"http://localhost:8000/"+str(obj.image),
          
        })

        return data

class TerminalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Terminal
        fields = '__all__'

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'

class CategorieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categorie
        fields = '__all__'

class FormSerializer(serializers.ModelSerializer):
    class Meta:
        model = Form
        fields = '__all__'

class ChoisesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choices
        fields = '__all__'

class ReponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reponse
        fields = '__all__'

        
class CustomChoisesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choices
        fields = ['id','option']

class CustomQuestionSerializer(serializers.ModelSerializer):
    choices = CustomChoisesSerializer(many=True)
    class Meta:
        model = Question
        fields = ['id','label','choices','question_type']
class CustomCategorieSerializer(serializers.ModelSerializer):
    questions = CustomQuestionSerializer(many=True)
    class Meta:
        model = Categorie
        fields = '__all__'

class CustomFormSerializer(serializers.ModelSerializer):
    categories = CustomCategorieSerializer(many=True)
    class Meta:
        model = Form
        fields = ['id','categories','created_at','title','statut','lien']



class CustomQuestionSerializer2(serializers.ModelSerializer):
    choices = CustomChoisesSerializer(many=True)
    reponse=serializers.SerializerMethodField()
    class Meta:
        model = Question
        fields = ['id','label','choices','question_type','reponse']
    def get_reponse(self, obj):
        user = self.context['request'].user
        rep  = Reponse.objects.get(question_id = obj.id,user = user).rep
        rep = rep.replace('[', '').replace(']', '').replace("'", '')
        return rep
class CustomCategorieSerializer2(serializers.ModelSerializer):
    questions = CustomQuestionSerializer2(many=True)
    class Meta:
        model = Categorie
        fields = '__all__'



class CustomFormSerializer2(serializers.ModelSerializer):
    categories = CustomCategorieSerializer2(many=True)
    class Meta:
        model = Form
        fields = ['id','categories','created_at','title','statut','lien']
class ReponseUserSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    form = CustomFormSerializer2()
    class Meta:
        model = ReponseUser
        fields = '__all__'
