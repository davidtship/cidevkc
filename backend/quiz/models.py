from django.db import models
from .choices import QUESTION_CHOICES,TYPE_USER_CHOICES
from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import AbstractUser,BaseUserManager
import uuid

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email requis')
        email = self.normalize_email(email)
        extra_fields.setdefault('username', email)  # pour que AbstractUser soit content
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('username', email)  # éviter l'erreur de username

        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    email = models.EmailField(unique=True)
    type_user = models.CharField(max_length=100)

    username = models.CharField(max_length=150, blank=True)  # facultatif ou supprimé
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = CustomUserManager()

    def __str__(self):
        return self.emailcl
    

class BaseModel(models.Model):
    created_at = models.DateField(auto_now_add=True)
    created_at = models.DateField(auto_now=True)
    class Meta:
        abstract = True
class Terminal(models.Model):
    device_uuid = models.CharField(max_length=255, unique=True)
    fingerprint = models.CharField(max_length=255)
    device_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.device_name
    
class Choices(BaseModel):
    option = models.CharField(max_length=100)
    code_uid = models.CharField(max_length=100,blank=True)
    def __str__(self):
        return self.option

class Question(BaseModel):
    code_uid = models.CharField(max_length=100,blank=True)
    label = models.CharField(max_length=100)
    question_type = models.CharField(max_length=100)
    required = models.BooleanField(default=True)
    choices = models.ManyToManyField(Choices, related_name="question_choices",blank=True)

    def __str__(self):
        return self.label
    
class Categorie(BaseModel):
    cat_form = models.CharField(max_length=100,blank=True)
    code_uid = models.CharField(max_length=100,blank=True)
    title = models.CharField(max_length=100,blank=True)
    questions = models.ManyToManyField(Question,related_name="questions")

    def __str__(self):
        return self.title
    
class Form(BaseModel):
    title = models.CharField(max_length=255)
    categories = models.ManyToManyField(Categorie,related_name="categories")
    statut = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    
    @property
    def lien(self):
        return "http://localhost:5173/formulaire/"+str(self.id)

class Reponse(BaseModel):
    question = models.ForeignKey(Question, on_delete=models.DO_NOTHING, null=False)
    rep = models.CharField( max_length=150,blank=True,default="")
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    
class ReponseUser(BaseModel):
    form = models.ForeignKey(Form, on_delete=models.DO_NOTHING, null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


