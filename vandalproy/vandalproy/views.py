from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ObjectDoesNotExist
from .models import Comment, UserRole
from .forms import CommentForm

@login_required
def dashboard(request):
    try:
        user_role = UserRole.objects.get(user=request.user).role
    except ObjectDoesNotExist:
        return render(request, 'error.html', {'message': 'No tienes un rol asignado. Contacta al administrador.'})

    comments = Comment.objects.all()
    form = CommentForm()  # Inicializar el formulario por defecto

    if request.method == 'POST':
        if 'comment' in request.POST:
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.user = request.user
                comment.save()
                return redirect('dashboard')
        elif 'upload' in request.POST and user_role in ['admin', 'editor']:
            uploaded_file = request.FILES.get('file')
            if uploaded_file:
                fs = FileSystemStorage(location='c:/Users/sr118/Desktop/Vandal_GPIS/vandalproy/static/uploads/')
                fs.save(uploaded_file.name, uploaded_file)
        elif 'html_upload' in request.POST and user_role == 'admin':
            uploaded_file = request.FILES.get('file')
            if uploaded_file:
                fs = FileSystemStorage(location='c:/Users/sr118/Desktop/Vandal_GPIS/vandalproy/templates/common/')
                fs.save(uploaded_file.name, uploaded_file)

    return render(request, 'dashboard.html', {'form': form, 'comments': comments, 'role': user_role})