from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from .models import BlogPost, BlogComment, UserRole, Comment
from .forms import CommentForm
from django.contrib.auth.backends import ModelBackend
import logging
from django.http import HttpResponseRedirect
from django.urls import reverse

logger = logging.getLogger(__name__)

class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(email=username)
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        except User.DoesNotExist:
            return None

@login_required
def dashboard(request):
    try:
        user_role = UserRole.objects.get(user=request.user).role
    except ObjectDoesNotExist:
        return render(request, 'error.html', {'message': 'No tienes un rol asignado. Contacta al administrador.'})

    if request.method == 'POST':
        if 'comment' in request.POST:
            form = CommentForm(request.POST)
            if form.is_valid():
                form.save(commit=False).user = request.user
                form.save()
        elif 'upload' in request.POST and user_role in ['admin', 'editor']:
            FileSystemStorage(location='static/uploads/').save(request.FILES['file'].name, request.FILES['file'])
        elif 'html_upload' in request.POST and user_role == 'admin':
            FileSystemStorage(location='templates/common/').save(request.FILES['file'].name, request.FILES['file'])

    return render(request, 'dashboard.html', {'form': CommentForm(), 'comments': Comment.objects.all(), 'role': user_role})

@login_required
def user_dashboard(request, role):
    templates = {
        'redactor': 'usuarios/dashboard_redactor.html',
        'colaborador': 'usuarios/dashboard_colaborador.html',
        'suscriptor': 'usuarios/dashboard_suscriptor.html'
    }
    selected_template = templates.get(role, 'error.html')
    logger.debug(f"Rendering template: {selected_template} for role: {role}")
    context = {'posts': BlogPost.objects.filter(author=request.user)} if role in ['redactor', 'colaborador'] else {'comments': BlogComment.objects.filter(user=request.user)}
    return render(request, selected_template, context)

def login_view(request):
    if request.method == 'POST':
        user = authenticate(request, username=request.POST.get('email'), password=request.POST.get('password'))
        if user:
            login(request, user)
            return redirect('/')
        return render(request, 'usuarios/login.html', {'error': 'Credenciales inválidas'})
    return render(request, 'usuarios/login.html')

def register_view(request):
    if request.method == 'POST':
        username, email, password, confirm_password = (request.POST.get(key) for key in ['nombre', 'email', 'password', 'confirmar'])
        if password != confirm_password:
            error = 'Las contraseñas no coinciden'
        elif User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
            error = 'El usuario o email ya está registrado'
        else:
            login(request, User.objects.create_user(username=username, email=email, password=password))
            return redirect('/')
        return render(request, 'usuarios/login.html', {'error': error})
    return render(request, 'usuarios/login.html')

def logout_view(request):
    logout(request)
    return redirect('/')

def blog_post_view(request, post_id):
    try:
        post = BlogPost.objects.prefetch_related('comments').get(id=post_id)
    except BlogPost.DoesNotExist:
        return render(request, 'error.html', {'message': 'El post no existe.'})

    if request.method == 'POST' and request.user.is_authenticated:
        comment_content = request.POST.get('comment')
        if comment_content:
            BlogComment.objects.create(post=post, user=request.user, content=comment_content)

    return render(request, 'portal/blog.html', {'post': post, 'comments': post.comments.all()})

def submit_comment(request):
    if request.method == 'POST' and request.user.is_authenticated:
        comment_content = request.POST.get('comment')
        post_id = request.POST.get('post_id')
        if comment_content and post_id:
            try:
                post = BlogPost.objects.get(id=post_id)
                BlogComment.objects.create(
                    user=request.user,
                    content=comment_content,
                    post=post
                )
            except BlogPost.DoesNotExist:
                return HttpResponseRedirect(reverse('blog'))
        return HttpResponseRedirect(reverse('blog'))
    return HttpResponseRedirect(reverse('login'))