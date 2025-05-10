from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User

#Create your models here.

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.nombre

class Pagina(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, unique=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    imagen = models.ImageField(verbose_name = 'Imagen', null=True, blank=True)
    fecha_creacion = models.DateTimeField(default=now, editable=False)
    fecha_modificacion = models.DateTimeField(auto_now=True, editable=False)
    def __str__(self):
        return self.nombre

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class UserRole(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, choices=[('redactor', 'Redactor'), ('colaborador', 'Colaborador'), ('suscriptor', 'Suscriptor')])

class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, default=1)  # Default to user with ID 1
    created_at = models.DateTimeField(auto_now_add=True)

class BlogComment(models.Model):
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)