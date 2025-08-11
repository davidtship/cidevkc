from django.db import models
from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import AbstractUser,BaseUserManager




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
        extra_fields.setdefault('type_user', 'super_admin')

        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    email = models.EmailField(unique=False)
    type_user = models.CharField(max_length=100)
    username = models.CharField(max_length=150, blank=True,unique=False)  # facultatif ou supprimé
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    objects = CustomUserManager()

    def __str__(self):
        return self.email

class Terminal(models.Model):
    device_uuid = models.CharField(max_length=255, unique=True)
    fingerprint = models.CharField(max_length=255)
    device_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.device_name
    


class Formulaire(models.Model):
    titre = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='formulaires')
    date_creation = models.DateTimeField(auto_now_add=True)
    etat = models.BooleanField(default=False)

    def __str__(self):
        return self.titre


class Section(models.Model):
    formulaire = models.ForeignKey(Formulaire, on_delete=models.CASCADE, related_name='sections')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='sous_sections')
    titre = models.CharField(max_length=255)

    def __str__(self):
        return self.titre


class Question(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='questions')
    texte = models.TextField()
    type = models.CharField(max_length=100)  # Exemple : 'text', 'paragraph', 'multiple_choice'

    def __str__(self):
        return self.texte


class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    texte = models.CharField(max_length=255)

    def __str__(self):
        return self.texte


class ReponseFormulaire(models.Model):
    formulaire = models.ForeignKey(Formulaire, on_delete=models.CASCADE, related_name='reponses')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reponses')  # 👈
    date_creation = models.DateTimeField(auto_now_add=True)

class ReponseQuestion(models.Model):
    reponse_formulaire = models.ForeignKey(ReponseFormulaire, on_delete=models.CASCADE, related_name='reponses')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    valeur = models.JSONField()