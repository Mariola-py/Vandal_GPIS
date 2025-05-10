from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from .models import BlogPost, BlogComment, UserRole, Noticia
from .forms import CommentForm
from django.contrib.auth.backends import ModelBackend
import logging
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import get_object_or_404


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
        if 'upload' in request.POST and user_role in ['admin', 'editor']:
            FileSystemStorage(location='static/uploads/').save(request.FILES['file'].name, request.FILES['file'])
        elif 'html_upload' in request.POST and user_role == 'admin':
            FileSystemStorage(location='templates/common/').save(request.FILES['file'].name, request.FILES['file'])

    return render(request, 'dashboard.html', {'role': user_role})

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

# Vista de listado de posts
# Actualización para ordenar comentarios de más recientes a más antiguos
def blog_list_view(request):
    form = CommentForm(request.POST or None)

    if request.method == 'POST' and request.user.is_authenticated and form.is_valid():
        comment = form.save(commit=False)
        post_id = request.POST.get('post_id')
        comment.post = get_object_or_404(BlogPost, id=post_id) if post_id else None
        comment.user = request.user
        comment.save()
        return redirect('blog_list')

    posts = BlogPost.objects.prefetch_related('comments').all().order_by('-created_at')
    page_comments = BlogComment.objects.filter(post__isnull=True).order_by('-created_at')
    return render(request, 'portal/blog_list.html', {
        'posts': posts,
        'form': form,
        'page_comments': page_comments,
    })

# Vista de detalle de post con comentarios
# Actualización para ordenar comentarios de más recientes a más antiguos
def blog_post_view(request, post_id):
    post = get_object_or_404(BlogPost.objects.prefetch_related('comments'), id=post_id)
    form = CommentForm(request.POST or None)

    if request.method == 'POST' and request.user.is_authenticated and form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.user = request.user
        comment.save()
        return redirect('blog_post', post_id=post.id)

    comments = post.comments.all().order_by('-created_at')
    return render(request, 'portal/blog.html', {
        'post': post,
        'comments': comments,
        'form': form,
    })

# Vistas de autenticación
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
        error = None
        if password != confirm_password:
            error = 'Las contraseñas no coinciden'
        elif User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
            error = 'El usuario o email ya está registrado'
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            login(request, user)
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
def detalle_noticia(request, pk):
    noticia = get_object_or_404(Noticia, pk=pk)
    return render(request, 'portal/noticia_detalle.html', {'noticia': noticia})

def home(request):
    noticias = Noticia.objects.all().order_by('-fecha_publicacion')
    return render(request, 'common/home.html', {'noticias': noticias})
