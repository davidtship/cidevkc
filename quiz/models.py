from django.db import models
from .choices import QUESTION_CHOICES,TYPE_USER_CHOICES
from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    adresse = models.CharField(max_length=255,blank=True)
    email = models.EmailField(unique=True,blank=True)
    image = models.ImageField(upload_to='media/', blank=True)
    type_user = models.CharField(max_length=100, choices=TYPE_USER_CHOICES)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username
    

class BaseModel(models.Model):
    created_at = models.DateField(auto_now_add=True)
    created_at = models.DateField(auto_now=True)
    class Meta:
        abstract = True
class Terminal(BaseModel):
    model = models.CharField(max_length=255,blank=True)
    adresse = models.CharField(max_length=255,blank=True)

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

    